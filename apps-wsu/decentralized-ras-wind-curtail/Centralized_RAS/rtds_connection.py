from pypmu.pdc import Pdc

import socket
import threading
import struct
import time
import math

RTDS_IP = "192.168.1.102"
RTDS_PORT = 4575

PMU_IP = "192.168.1.111"
PMU_PORTS = [4712, 4722, 4732, 4742]

PMUS = [[PMU_IP, 4712, 1], [PMU_IP, 4722, 2], ['192.168.1.51', 5011, 11],  [PMU_IP, 4732, 3]]# ['192.168.1.51', 5011, 11]]


class RTDSConnection():

    def __init__(self):
        self.s = None
        self.pdc = None
        self.dframes = None
        self.lock = threading.Lock()
        self.connect_RTDS()

    def connect_RTDS(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((RTDS_IP, RTDS_PORT))
        self.s.send('Start;'.encode())

        msg = self.s.recv(64)
        print(msg)

    def parse_message(self, msg):
        msg_str = msg.decode()
        pg_str = msg_str.split(' ')[2]
        return float(pg_str)

    def get_meter_values(self):
        tempPG = list()
        for i in range(1,5):
            string1 = 'temp_float = MeterCapture("PG{}");'.format(i).encode()
            string2 = 'sprintf(temp_string, "PG{} = %f END", temp_float);'.format(i).encode()
            string3 = "ListenOnPortHandshake(temp_string);".encode()


            self.s.send(string1)
            self.s.send(string2)
            self.s.send(string3)

            msg = ''.encode()

            while("PG" not in msg.decode()):
                msg = self.s.recv(64)
                print(msg)
            pg_value = self.parse_message(msg)
            tempPG.append(pg_value)

        return tempPG

    def connect_pmu(self):
        #Connect to all the PMUs
        if self.pdc is None:
            self.pdc = list()
            for PMU in PMUS:
                pmu = Pdc(pmu_ip = PMU[0], pdc_id = PMU[2], pmu_port = PMU[1])
                pmu.run()
                self.pdc.append(pmu)

        for pmu in self.pdc:
            if not pmu.is_connected():
                return False
            pmu.start()

        dframe_thread = threading.Thread(target = self.get_dframes)
        dframe_thread.start()

        return True

    def get_dframes(self):
        if self.pdc is None:
            return False
        while(True):
            dataframelist = list()
            for pmu in self.pdc:
                dataframelist.append(pmu.get())
            self.lock.acquire()
            self.dframes = dataframelist[:]
            self.lock.release()

    def calculatePG(self, v_mag, v_ang, i_mag, i_ang):
        v_vect = (v_mag * math.cos(v_ang)) + (v_mag * math.sin(v_ang) * 1j)
        i_vect = (i_mag * math.cos(i_ang)) + (i_mag * math.sin(i_ang) * -1j)

        res = v_vect * i_vect * 3
        return res.real / 1000000.0

    def parse_data_frame(self, data):
        v_mag = struct.unpack('>f', data[16:20])
        v_ang = struct.unpack('>f', data[20:24])
        i_mag = struct.unpack('>f', data[24:28])
        i_ang = struct.unpack('>f', data[28:32])

        return v_mag[0], v_ang[0], i_mag[0], i_ang[0]


    def get_pmu_values(self):
        #returns a list of 4 values, PG for each PMU
        if self.dframes is None:
            return None

        self.lock.acquire()
        dataframes = self.dframes[:]
        self.lock.release()

        tempPG = list()

        data0 = dataframes[0]
        v_mag0, v_ang0, i_mag0, i_ang0 = self.parse_data_frame(data0)

        tempPG.append(self.calculatePG(v_mag0, 0, i_mag0, i_ang0 - v_ang0))

        for data in dataframes[1:]:
            v_mag, v_ang, i_mag, i_ang = self.parse_data_frame(data)
            v_ang -= v_ang0
            i_ang -= v_ang0

            tempPG.append(self.calculatePG(v_mag, v_ang, i_mag, i_ang))

        print(tempPG)
        return tempPG[:4]


    def send_command(self, cmd):
        self.s.send(cmd.encode())
