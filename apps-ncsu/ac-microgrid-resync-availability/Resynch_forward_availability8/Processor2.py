#
from riaps.run.comp import Component
import logging
import uuid
import time
import os
import pprint
from datetime import datetime


class Processor2(Component):
    def __init__(self):
        super().__init__()
        self.uuid = uuid.uuid4().int
        self.pid = os.getpid()
        self.logger.info("%s - starting",str(self.pid))

    def on_rx_phasorData2(self):
        raw, data = self.rx_phasorData2.recv_pyobj() # Receive Data (raw, interpreted)
        #self.logger.info("on_rx_c37data()[%s]: %s", str(self.pid), repr(data))
        #timestamp = datetime.utcfromtimestamp(data['timestamp'])
        #timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S.%f").rstrip('0')
        #self.logger.debug('%s: %s',  timestamp_str, pprint.pformat(data))
        #self.logger.debug('%s: VAGA = %f deg, VASA = %f deg',  timestamp_str, data['VAGA'], data['VASA'])
        self.tx_c37data2.send_pyobj((raw, data))
        
    def on_rx_headerData2(self):
        header = self.rx_headerData2.recv_pyobj() # Receive Header (raw, interpreted)
        self.logger.info("on_rx_c37header()[%s]: %s", str(self.pid), repr(header))
        self.tx_c37header2.send_pyobj(header)
        
    def on_rx_configData2(self):
        raw, config = self.rx_configData2.recv_pyobj() # Receive Config (raw, interpreted)
        self.logger.info("on_rx_c37config()[%s]: %s", str(self.pid), repr(config))
        self.tx_c37config2.send_pyobj((raw, config))