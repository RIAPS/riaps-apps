'''
Created on Jan 25, 2017

@author: metelko
'''
# import riaps
# riaps:keep_import:begin
from riaps.run.comp import Component
import logging
import time
import os
# riaps:keep_import:end

class TempMonitor(Component):
# riaps:keep_constr:begin
    def __init__(self):
        super(TempMonitor, self).__init__()
        self.pid = os.getpid()
        now = time.ctime(int(time.time()))
        self.logger.info("(PID %s)-starting TempMonitor, %s",str(self.pid),str(now))
# riaps:keep_constr:end

# riaps:keep_tempupdate:begin
    def on_tempupdate(self):
        # Receive: timestamp,temperature
        msg = self.tempupdate.recv_pyobj()
        now = time.ctime(int(time.time()))
        temperatureTime, temperatureValue = msg
        self.logger.info("on_tempupdate(): Temperature:%s, PID %s, Timestamp:%s", temperatureValue, str(now), temperatureTime)
# riaps:keep_tempupdate:end

# riaps:keep_impl:begin
    def __destroy__(self):
        now = time.time()
        self.logger.info("%s - stopping TempMonitor, %s",str(self.pid),now)
# riaps:keep_impl:end
