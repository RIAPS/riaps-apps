import logging
import socket

from .frame import *
from .utils import frame_to_ascii

__author__ = "Stevan Sandi"
__copyright__ = "Copyright (c) 2016, Tomo Popovic, Stevan Sandi, Bozo Krstajic"
__credits__ = []
__license__ = "BSD-3"
__version__ = "0.1.1"


class Pdc(object):

    logger = logging.getLogger(__name__)

    def __init__(self, pdc_id=1, pmu_ip='127.0.0.1', pmu_port=4712, buffer_size=2048, method='tcp'):

        self.pdc_id = pdc_id
        self.buffer_size = buffer_size
        self.method = method

        self.pmu_ip = pmu_ip
        self.pmu_port = pmu_port
        self.pmu_address = (pmu_ip, pmu_port)
        self.pmu_socket = None

    def run(self):

        if self.pmu_socket:
            self.logger.info("[%d] - PDC already connected to PMU (%s:%d)", self.pdc_id, self.pmu_ip, self.pmu_port)
        else:
            try:
                # Connect to PMU
                self.pmu_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.pmu_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.pmu_socket.connect(self.pmu_address)
                self.logger.info("[%d] - PDC successfully connected to PMU (%s:%d)",
                                 self.pdc_id, self.pmu_ip, self.pmu_port)
            except Exception as e:
                self.logger.error("[%d] - Error while connecting to (%s:%d)", self.pdc_id, self.pmu_ip, self.pmu_port)
                self.logger.error(str(e))
                self.pmu_socket = None

    def is_connected(self):
        return self.pmu_socket != None

    def start(self):
        """
        Request from PMU to start sending data
        :return: NoneType
        """
        self.logger.info("[%d] - Requesting to start sending from PMU (%s:%d)", self.pdc_id, self.pmu_ip, self.pmu_port)
        start = CommandFrame(self.pdc_id, 'start')
        frame = start.convert2bytes()
        self.pmu_socket.sendall(frame)
        self.logger.debug("sent: " + frame_to_ascii(frame))

    def stop(self):
        """
        Request from PMU to start sending data
        :return: NoneType
        """
        self.logger.info("[%d] - Requesting to stop sending from PMU (%s:%d)", self.pdc_id, self.pmu_ip, self.pmu_port)
        stop = CommandFrame(self.pdc_id, 'stop')
        frame = stop.convert2bytes()
        self.pmu_socket.sendall(frame)
        self.logger.debug("sent: " + frame_to_ascii(frame))

    def get_header(self):
        """
        Request for PMU header message
        :return: HeaderFrame
        """
        self.logger.info("[%d] - Requesting header frame from PMU (%s:%d)", self.pdc_id, self.pmu_ip, self.pmu_port)
        get_header = CommandFrame(self.pdc_id, 'header')
        frame = get_header.convert2bytes()
        self.pmu_socket.sendall(frame)
        self.logger.debug("sent: " + frame_to_ascii(frame))

        header = self.get()
        if isinstance(header, HeaderFrame):
            self.logger.info("[%d] - Proper header frame received from PMU (%s:%d)", self.pdc_id, self.pmu_ip, self.pmu_port)
            return header
        else:
            raise PdcError('Invalid Header message received')

    def get_config(self, version='cfg2'):
        """
        Request for Configuration frame.
        :param version: string Possible values 'cfg1', 'cfg2' and 'cfg3'
        :return: ConfigFrame
        """
        self.logger.info("[%d] - Requesting config frame from PMU (%s:%d)", self.pdc_id, self.pmu_ip, self.pmu_port)
        get_config = CommandFrame(self.pdc_id, version)
        frame = get_config.convert2bytes()
        self.pmu_socket.sendall(frame)
        self.logger.debug("sent: " + frame_to_ascii(frame))

        config = self.get()
        if isinstance(config, ConfigFrame):
            self.logger.info("[%d] - Proper config frame received from PMU (%s:%d)", self.pdc_id, self.pmu_ip, self.pmu_port)
            return config
        elif isinstance(config, bytes):
            return config
        else:
            # TODO: raise PdcError('Invalid Configuration message received')
            return None

    def get(self):
        """
        Decoding received messages from PMU
        :return: CommonFrame
        """

        received_data = b''
        received_message = None

        """
        Keep receiving until SYNC + FRAMESIZE is received, 4 bytes in total.
        Should get this in first iteration. FRAMESIZE is needed to determine when one complete message
        has been received.
        """

        while len(received_data) < 4:
            received_data += self.pmu_socket.recv(4 - len(received_data))

        bytes_received = len(received_data)
        total_frame_size = int.from_bytes(received_data[2:4], byteorder='big', signed=False)

        # Keep receiving until every byte of that message is received
        while bytes_received < total_frame_size:
            message_chunk = self.pmu_socket.recv(min(total_frame_size - bytes_received, self.buffer_size))
            if not message_chunk:
                break
            received_data += message_chunk
            bytes_received += len(message_chunk)

        self.logger.debug("received: " + frame_to_ascii(received_data))
        # If complete message is received try to decode it
        if len(received_data) == total_frame_size:
            try:
                received_message = CommonFrame.convert2frame(received_data)  # Try to decode received data
                self.logger.debug("[%d] - Received %s from PMU (%s:%d)", self.pdc_id, type(received_message).__name__,
                                  self.pmu_ip, self.pmu_port)
            except FrameError:
                self.logger.warning("[%d] - Received unknown message from PMU (%s:%d)",
                                    self.pdc_id, self.pmu_ip, self.pmu_port)
        else:
            self.logger.warning("[%d] - Received incomplete message from PMU (%s:%d)",
                                    self.pdc_id, self.pmu_ip, self.pmu_port)
        return received_message

    def quit(self):
        """
        Close connection to PMU
        :return: NoneType
        """
        self.pmu_socket.close()
        self.pmu_socket = None
        self.logger.info("[%d] - Connection to PMU closed (%s:%d)", self.pdc_id, self.pmu_ip, self.pmu_port)


class PdcError(BaseException):
    pass
