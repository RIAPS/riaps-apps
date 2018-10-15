#LocalEstimator.py
from riaps.run.comp import Component
import os
import logging

import time

class LocalEstimator(Component):
    def __init__(self,frqArg):
        super(LocalEstimator, self).__init__()
        self.pid = os.getpid()
        self.logger.info("(PID %s) - starting LocalEstimator(frqArq=%f)",str(self.pid),frqArg)
        self.pending = 0
        self.freq = frqArg
        self.numQueries = 0
        self.queryRate = 2.0  # 2 Hz update rate based on on_ready
     

    def on_ready(self):
        msg = self.ready.recv_pyobj()
        self.logger.info("PID (%s) - on_ready():%s",str(self.pid), str(msg))
        while self.pending > 0:     # Handle the case when there is a pending request
            self.on_query()
        msg = "sensor_query"
        if self.query.send_pyobj(msg):
            self.pending += 1 
            

    def on_query(self):
        req = self.query.recv_pyobj()
        #self.logger.info("PID (%s) - on_query():%s",str(self.pid),str(req))
        (sTime,sensorVal) = req
        self.pending -= 1
       
        ''' Send message at frequency indicated in the deployment model '''
        self.numQueries += 1
        if self.numQueries == (self.queryRate / self.freq):
            self.logger.info("local_est(pid=%s, timeStamp=%s, value=%s)",str(self.pid),str(sTime),str(sensorVal))
            msgVal = (self.pid,sTime,sensorVal)
            self.estimate.send_pyobj(msgVal)
            self.numQueries = 0
            msg = 'BLINK'
            self.blink.send_pyobj(msg)            # Send it to the internal thread
    
    def __destroy__(self):
        self.logger.info("(PID %s) - stopping LocalEstimator",str(self.pid))   	        	        
                       
