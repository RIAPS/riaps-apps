from riaps.run.comp import Component
import logging
from random import random
from pypmu.pdc import Pdc
import threading
import time
import struct
import math



class ComtradeDataProvider(Component):
    def __init__(self):
        super(ComtradeDataProvider, self).__init__()
        self.r_conn = RTDSConnection()
        if not self.r_conn.connect_pmu():
            self.logger.info("Error connecting to PMU")
        self.logger.info("Dataprovider initialized")
        
    def on_clock(self):
        self.clock.recv_pyobj()
        #msg = self.r_conn.get_meter_values()
        msg = self.r_conn.get_pmu_values()
        self.logger.info("sending %s", str(msg))
        self.start_time = time.time()
        self.tempport.send_pyobj(msg)
        #self.r_conn.send_command('SetSlider "SL3" = 0.76724;')
        
    def on_commandmsg(self):
        msg = self.commandmsg.recv_pyobj()
        end_time = time.time()
        diff = end_time - self.start_time
        self.logger.info("Time Taken = " + str(diff))
        self.logger.info('SetSlider "SL3"= %f;', msg)
        #self.r_conn.send_command('SetSlider "SL3" = {};'.format(msg))
        

PMUS = [["192.168.1.119", 4712, 9]]


class RTDSConnection():

    def __init__(self):
        self.s = None
        self.pdc = None 
        self.dframes = None
        self.lock = threading.Lock()


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
        #Call the get() on all the connected PMUs
        if self.pdc is None:
            return False
        while(True):
            dataframelist = list()
            for pmu in self.pdc:
                dataframelist.append(pmu.get())
            self.lock.acquire()
            self.dframes = dataframelist[:]
            self.lock.release()

    def calculatePG(self, phasors):
        # Convert a list of phasors to power generation values.
        vaypm, vaypa, vbypm, vbypa, vcypm, vcypa, vazpm, vazpa, vbzpm, vbzpa, iawpm, iawpa, ibwpm, ibwpa, icwpm, icwpa, iaypm, iaypa, ibypm, ibypa = phasors
        pg_list = []
        pg1 = 3 * vaypm * iawpm * math.cos(vaypa - iawpa)
        pg2 = 3 * vbypm * ibwpm * math.cos(vbypa - ibwpa)
        pg3 = 3 * vazpm * icwpm * math.cos(vazpa - icwpa)
        pg4 = 3 * vbzpm * ibypm * math.cos(vbzpa - iaypa)

        return [pg1, pg2, pg3, pg4]

    def parse_data_frame(self, data):
        vaypm = struct.unpack('>f', data[16:20])[0] / 7.5
        vaypa = struct.unpack('>f', data[20:24])[0] 
        vbypm = struct.unpack('>f', data[24:28])[0] / 7.5
        vbypa = struct.unpack('>f', data[28:32])[0]
        vcypm = struct.unpack('>f', data[32:36])[0] / 37.5
        vcypa = struct.unpack('>f', data[36:40])[0]
        vazpm = struct.unpack('>f', data[40:44])[0] / 37.5
        vazpa = struct.unpack('>f', data[44:48])[0]
        vbzpm = struct.unpack('>f', data[48:52])[0] / 37.5
        vbzpa = struct.unpack('>f', data[52:56])[0]
        iawpm = struct.unpack('>f', data[56:60])[0] * 3.333
        iawpa = struct.unpack('>f', data[60:64])[0]
        ibwpm = struct.unpack('>f', data[64:68])[0] * 0.533
        ibwpa = struct.unpack('>f', data[68:72])[0]
        icwpm = struct.unpack('>f', data[72:76])[0] * 10
        icwpa = struct.unpack('>f', data[76:80])[0]
        iaypm = struct.unpack('>f', data[80:84])[0] * 6.667
        iaypa = struct.unpack('>f', data[84:88])[0]
        ibypm = struct.unpack('>f', data[88:92])[0] * 6.667
        ibypa = struct.unpack('>f', data[92:96])[0]

        return [vaypm, vaypa, vbypm, vbypa, vcypm, vcypa, vazpm, vazpa, vbzpm, vbzpa, iawpm, iawpa, ibwpm, ibwpa, icwpm, icwpa, iaypm, iaypa, ibypm, ibypa]

    def get_pmu_values(self):
        #returns a list of 4 values, PG for each PMU
        if self.dframes is None:
            return None

        dataframes = self.dframes[:]

        tempPG = list()

        data = dataframes[-1]
        phasors = self.parse_data_frame(data)

        tempPG = self.calculatePG(phasors)
        
        return tempPG


    def send_command(self, cmd):
        self.s.send(cmd.encode())

    
