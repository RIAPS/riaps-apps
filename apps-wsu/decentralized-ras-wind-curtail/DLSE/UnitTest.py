import time
from riaps.run.comp import Component
import logging
    
class UnitTest(Component):
    def __init__(self):
        super(UnitTest, self).__init__()
        self.logger.info("Initialized Component")
    
    def on_clock(self):
        msg = self.clock.recv_pyobj()
        self.logger.info("Clock event")
        
    def on_phasorPort(self):
        msg = self.phasorPort.recv_pyobj()
        self.logger.info(str(msg))