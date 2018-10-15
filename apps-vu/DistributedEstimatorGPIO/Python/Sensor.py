#Sensor.py
from riaps.run.comp import Component
import os
import logging
import random

class Sensor(Component):
    def __init__(self,value):
        super(Sensor, self).__init__()
        self.pid = os.getpid()
        self.logger.info("(PID %s) - starting Sensor",str(self.pid))
        if value == 0.0: 
            self.myValue = (10.0 * random.random()) - 5.0
        else:
            self.myValue = value
        
    def on_clock(self):
        now = self.clock.recv_pyobj()
        # self.logger.info('PID(%s) - on_clock(): %s',str(self.pid),str(now))
        msg = "data_ready"
        self.ready.send_pyobj(msg)

    def on_request(self):
        msg = self.request.recv_pyobj()
        self.logger.info("PID (%s) - on_query():%s",str(self.pid),str(msg))
        rep = (msg,self.myValue)        # Send (timestamp,value) 
        self.request.send_pyobj(rep)

    def __destroy__(self):
        self.logger.info("(PID %s) - stopping Sensor",str(self.pid))   	        	        
