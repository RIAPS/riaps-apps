'''
Created on Jan 25, 2017

@author: metelko
'''
from riaps.run.comp import Component
import logging
import time
import os


class TempSensor(Component):
    def __init__(self):
        super(TempSensor, self).__init__()
        self.pid = os.getpid()
        self.temperature = 65
        now = time.ctime(int(time.time()))
        self.logger.info("(PID %s)-starting TempSensor, %s",str(self.pid),str(now))
        self.logger.info("Initial temp:%d, %s",self.temperature,str(now))
        
    def on_clock(self):
        now = time.ctime(int(time.time()))
        msg = self.clock.recv_pyobj()
        self.temperature = self.temperature + 1
        msg = str(self.temperature)
        msg = (now,msg)       
        self.logger.info("on_clock(): Temperature - %s, PID %s, %s",str(msg[1]),str(self.pid),str(now))
        self.ready.send_pyobj(msg)
               
    def __destroy__(self):
        now = time.time()
        self.logger.info("%s - stopping TempSensor, %s",str(self.pid),now)         

