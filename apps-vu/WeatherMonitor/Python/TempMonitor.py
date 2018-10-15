'''
Created on Jan 25, 2017

@author: metelko
'''
# import riaps
from riaps.run.comp import Component
import logging
import time
import os


class TempMonitor(Component):
    def __init__(self):
        super(TempMonitor, self).__init__()
        self.pid = os.getpid()
        now = time.ctime(int(time.time()))
        self.logger.info("(PID %s)-starting TempMonitor, %s",str(self.pid),str(now))
        
    def on_tempupdate(self):
        # Receive: timestamp,temperature
        msg = self.tempupdate.recv_pyobj()   
        now = time.ctime(int(time.time()))     
        temperatureTime, temperatureValue = msg
        self.logger.info("on_tempupdate(): Temperature:%s, PID %s, Timestamp:%s", temperatureValue, str(now), temperatureTime)
        
    def __destroy__(self):
        now = time.time()
        self.logger.info("%s - stopping TempMonitor, %s",str(self.pid),now)