from riaps.run.comp import Component
from rtds_connection import RTDSConnection
import logging
from random import random

class RTDSDataProvider(Component):
    def __init__(self):
        super(RTDSDataProvider, self).__init__()
        self.r_conn = RTDSConnection()
        if not self.r_conn.connect_pmu():
            self.logger.info("Error connecting to PMU")
        self.logger.info("Dataprovider initialized")
        
    def on_clock(self):
        time = self.clock.recv_pyobj()
        #msg = self.r_conn.get_meter_values()
        msg = self.r_conn.get_pmu_values()
        self.logger.info("sending %s", str(msg))
        self.tempport.send_pyobj(msg)
        
    def on_commandmsg(self):
        msg = self.commandmsg.recv_pyobj()
        self.logger.info('SetSlider "SL3"= %f;', msg)
        self.r_conn.send_command('SetSlider "SL3" = {};'.format(msg))
        