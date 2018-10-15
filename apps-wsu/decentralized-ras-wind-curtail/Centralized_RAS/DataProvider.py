from riaps.run.comp import Component
import logging
from pmu_connection import PMUConnection

class DataProvider(Component):
    def __init__(self):
        super(DataProvider, self).__init__()
        self.pmu_connection = PMUConnection()
        self.logger.info("DataProvider initialized")
        
    def on_clock(self):
        msg = self.clock.recv_pyobj()
        self.logger.info("Clock Event")
        self.phasorPort.send_pyobj(self.pmu_connection.get_V_I())

    def on_resultPort(self):
        result = self.resultPort.recv_pyobj()
        self.pmuConnection.send_pyobj()
