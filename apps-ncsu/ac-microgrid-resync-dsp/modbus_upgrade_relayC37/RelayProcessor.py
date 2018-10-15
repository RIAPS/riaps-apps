#
from riaps.run.comp import Component
import logging
import uuid
import time
import os
import pprint
from datetime import datetime


class RelayProcessor(Component):
    def __init__(self):
        super().__init__()
        self.uuid = uuid.uuid4().int
        self.pid = os.getpid()
        self.logger.info("%s - starting",str(self.pid))
        
       
    def on_dataToOpal(self):
        Id,otherTimestamp,Value_OMEAG = self.dataToOpal.recv_pyobj() # Receive Header (raw, interpreted)
        self.logger.info("dataToOpal[%s]: %s", str(Id), str(Value_OMEAG))
               
    def on_relay_c37data(self):
        data = self.relay_c37data.recv_pyobj() # Receive Data (raw, interpreted)
        #self.logger.info("on_rx_c37data()[%s]: magdiff %s, anglediff %s, d1 %s   d2 %s", str(self.pid), repr(data['mag_diff']), repr(data['angle_diff']), repr(data['DIGITALS']), repr(data['DIGITALS1']))
        #timestamp = datetime.utcfromtimestamp(data['timestamp'])
        #timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S.%f").rstrip('0')
        #self.logger.debug('%s: %s',  timestamp_str, pprint.pformat(data))
        #self.logger.debug('%s: VAGA = %f deg, VASA = %f deg',  timestamp_str, data['VAGA'], data['VASA'])
        #on_clock_end = time.time()
        #on_clock_start = data['start_time']
        self.relay_phasorData.send_pyobj(data)
        '''
        try:
            time_all  = on_clock_end - on_clock_start
            filename = "t_cal_c37"
            file = open(filename, "a")
            file.write(str(time_all)+'\n')
            file.close()
            #self.logger.info("t cal: C37 %f ", time_all)
        except:
            pass
        '''
        
        #self.logger.info("on_rx_c37data()[%s]: %s", str(self.pid), repr('data'))
        
        '''
        DataDG1 = (data['f1'], data['Q1'])
        self.global_datadg1.send_pyobj(DataDG1)
        DataDG2 = (data['f2'], data['V2'])
        self.global_datadg2.send_pyobj(DataDG2)
        DataDG3 = (data['f3'], data['Q3'])
        self.global_datadg3.send_pyobj(DataDG3)
        DataDG4 = (data['f4'], data['Q4'])
        self.global_datadg4.send_pyobj(DataDG4)
        '''
        
    def on_relay_c37header(self):
        header = self.relay_c37header.recv_pyobj() # Receive Header (raw, interpreted)
        self.logger.info("on_rx_c37header()[%s]: %s", str(self.pid), repr(header))
        
    def on_relay_c37config(self):
        raw, config = self.relay_c37config.recv_pyobj() # Receive Config (raw, interpreted)
        self.logger.info("on_rx_c37config()[%s]: %s", str(self.pid), repr(config))