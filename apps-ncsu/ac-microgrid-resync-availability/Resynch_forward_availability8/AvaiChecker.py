#
from riaps.run.comp import Component
import logging
import uuid
import time
import os
import pprint
from datetime import datetime


class AvaiChecker(Component):
    def __init__(self, priority=0, availablity=1, ip = 111):
        super().__init__()
        self.uuid = uuid.uuid4().int
        self.pid = os.getpid()
        self.priority = priority
        self.resyncAvailablity = availablity
        self.ip = ip
        self.dataValues = {}
        self.resyncDerDecision = 0
        self.logger.info("%s - starting with priority : %f and availablity %f" % (str(self.pid),self.priority,self.resyncAvailablity ))
  
    # get the availablity from GPIO(MODBUS IN THE FUTURE)
    def on_resyncFromGPIO(self):
        #self.resyncAvailablity = 1
        msg = self.resyncFromGPIO.recv_pyobj()
        now = time.time()
        self.resyncAvailablity = float(msg)
        msg = (self.uuid, now, self.priority, self.resyncAvailablity)
        self.thisResyncAvai.send_pyobj(msg)
        self.logger.info("on_resyncFromGPIO :availablity %f" % (self.resyncAvailablity))
    
    def on_resyncAvai(self):
        msg = self.resyncAvai.recv_pyobj()  # Receive (actorID,timestamp,value)
        # self.logger.info("on_otherReady():%s",str(msg[2]))
        otherId,otherTimestamp,otherPriority,otherAvailablity = msg
        if otherId != self.uuid:
            self.dataValues[otherId] = (otherPriority, otherAvailablity)
        
    def on_clock(self):
        msg = self.clock.recv_pyobj()
        self.resyncDerDecision = 0
        if self.resyncAvailablity == 1:
            self.resyncDerDecision = 1
        if len(self.dataValues) != 0:
            self.logger.info('on clock resyncAvailablity:%f' % self.resyncAvailablity)
            for priority,availablity in self.dataValues.values():
                if availablity == 1 and priority < self.priority:
                    print (priority,self.priority)
                    self.resyncDerDecision = 0;
        msg = (self.resyncDerDecision,)
        self.avaiResyncDecision.send_pyobj(msg)
        globalmsg=(self.ip, self.resyncDerDecision)
        self.globalAvaiResyncDecision.send_pyobj(globalmsg) 
        self.logger.info('resyncDerDecision:%f of IP: %f' % (self.resyncDerDecision,self.ip))
       
        