from riaps.run.comp import Component
import logging
import threading
from multiprocessing import Queue
from collections import namedtuple
import socket
from select import select
import time
import struct
from pypmu.frame import CommonFrame, CommandFrame, ConfigFrame2, DataFrame, HeaderFrame

ClientInfo = namedtuple('ClientInfo', ['buffer', 'streaming', 'socket', 'address'])

class C37Sender(Component):
    def __init__(self, listen_port):
        super().__init__()
        self.logger.setLevel(logging.INFO)
        
        self.port = listen_port
        self.ip = '0.0.0.0' # TODO: should be customizable
        self.pmu_id = listen_port # TODO: should be customizable
        
        # TODO: should be customizable
        self.cfg_frame = ConfigFrame2(pmu_id_code=self.pmu_id, time_base=1000000, num_pmu=1,
                            station_name="opal_io.py", id_code=self.pmu_id,
                            data_format=(True, True, True, True),
                            phasor_num=6, analog_num=5, digital_num=1,
                            channel_names=["VAGPM", "VBYPM", "VCYPM", "VASPM", "VBZPM", "VCZPM",
                                           "VAGM", "VAGA", "VASM", "VASA", "SLIP1",
                                           "BRKPCCTR", "RMB1", "RMB2", "",
                                           "", "", "", "",
                                           "", "", "", "",
                                           "", "", "", ""],
                            ph_units=[(1, 'v'), (1, 'v'), (1, 'v'), (1, 'v'), (1, 'v'), (1, 'v')],
                            an_units=[(1, 'pow'), (1, 'pow'), (1, 'pow'), (1, 'pow'), (1, 'pow')],
                            dig_units=[(0x0000, 0x0007)],
                            f_nom=60,
                            cfg_count=1,
                            data_rate=120).convert2bytes()
        self.header_frame = HeaderFrame(self.pmu_id, 'C37Sender').convert2bytes()
        
        self.terminated = threading.Event()
        self.terminated.clear()
        self.clients = []
        self.listener = None

        
    def on_clock(self):
        now = self.clock.recv_pyobj()   # Receive time (as float)
        self.logger.info('on_clock():%s', now)
        if self.listener == None:
            self.listener = threading.Thread(target=self.acceptor)  # Run acceptor thread to handle new connection
            self.listener.daemon = True
            self.listener.start()
        
    def client_handler(self, client_info):
        address_info = '%s:%d' % (client_info.address[0], client_info.address[1])
        try:
            while True:

                command = None
                received_data = b''
                
                if self.terminated.is_set():
                    break;
                    
                readable, _, _ = select([client_info.socket], [], [], 0)  # Check for client commands

                if readable:
                    """
                    Keep receiving until SYNC + FRAMESIZE is received, 4 bytes in total.
                    Should get this in first iteration. FRAMESIZE is needed to determine when one complete message
                    has been received.
                    """
                    while len(received_data) < 4:
                        received_data += client_info.socket.recv(4 - len(received_data))

                    bytes_received = len(received_data)
                    total_frame_size = int.from_bytes(received_data[2:4], byteorder='big', signed=False)

                    # Keep receiving until every byte of that message is received
                    while bytes_received < total_frame_size:
                        message_chunk = client_info.socket.recv(total_frame_size - bytes_received)
                        if not message_chunk:
                            break
                        received_data += message_chunk
                        bytes_received += len(message_chunk)

                    # If complete message is received try to decode it
                    if len(received_data) == total_frame_size:
                        try:
                            received_message = CommonFrame.convert2frame(received_data)  # Try to decode received data

                            if isinstance(received_message, CommandFrame):
                                command = received_message.get_command()
                                self.logger.info("[%d] - Received command: [%s] <- (%s)", self.pmu_id, command,
                                                 address_info)
                            else:
                                self.logger.info("[%d] - Received [%s] <- (%s)", self.pmu_id,
                                                 type(received_message).__name__, address_info)
                        except FrameError:
                            self.logger.warning("[%d] - Received unknown message <- (%s)", self.pmu_id,
                                                address_info)
                    else:
                        self.logger.warning("[%d] - Message not received completely <- (%s)", self.pmu_id,
                                            address_info)

                if command:
                    if command == 'start':
                        while not client_info.buffer.empty():
                            client_info.buffer.get()
                        client_info.streaming.set()
                        self.logger.info("[%d] - Start sending -> (%s)", self.pmu_id, address_info)

                    elif command == 'stop':
                        client_info.streaming.clear()
                        self.logger.info("[%d] - Stop sending -> (%s)", self.pmu_id, address_info)

                    elif command == 'header':
                        self.logger.info("[%d] - Replying Header request -> (%s)",
                                         self.pmu_id, address_info)
                        client_info.socket.sendall(self.header_frame)

                    elif command == 'cfg2':
                        self.logger.info("[%d] - Replying Configuration frame 2 request -> (%s)", self.pmu_id,
                                         address_info)
                        client_info.socket.sendall(self.cfg_frame)
                        
                    else:
                        self.logger.warn("[%d] - Unsupported request: %s from (%s)",
                                         self.pmu_id, command, address_info)
                        

                if client_info.streaming.is_set() and not client_info.buffer.empty():
                    self.logger.debug("[%d] - Sending data frame -> (%s)", self.pmu_id, address_info)
                    frame = client_info.buffer.get()
                    client_info.socket.sendall(frame)

        except Exception as e:
            self.logger.exception('Critical error in client_handler')
        finally:
            client_info.socket.close()
            self.clients.remove(client_info)
            self.logger.info("[%d] - Connection from %s has been closed.", self.pmu_id, address_info)
            

    def acceptor(self):
            listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listen_socket.bind((self.ip, self.port))
            listen_socket.listen()
            
            while True:
                # TODO: due to the blocking accept() call, this is not very effective
                if self.terminated.is_set():
                    listen_socket.close()
                    return None
                
                self.logger.info("[%d] - Waiting for connection on %s:%d", self.pmu_id, self.ip, self.port)
                conn, address = listen_socket.accept()
                self.logger.info('[%d] - Incoming connection from (%s:%d)', self.pmu_id, address[0], address[1])
    
                client_info = ClientInfo(Queue(), threading.Event(), conn, address)
                client_thread = threading.Thread(target=self.client_handler, args=((client_info),))
                client_thread.daemon = True            
                self.clients.append(client_info)
                client_thread.start()
        
    def __destroy__(self):
        self.logger.info("__destroy__")
        self.terminated.set()
        
    def on_c37data(self):
        raw, interpreted = self.c37data.recv_pyobj()
        for client in self.clients:
            if client.streaming.is_set() and not client.buffer.full():
                client.buffer.put(raw)
                
    def on_c37config(self):
        raw, interpreted = self.c37config.recv_pyobj()
        self.cfg_frame = raw
        
    def on_c37header(self):
        raw, interpreted = self.c37header.recv_pyobj()
        self.header_frame = raw