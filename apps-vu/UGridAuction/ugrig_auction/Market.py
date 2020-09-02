'''
Created on Oct 12, 2018

@author: purboday
'''
from riaps.run.comp import Component
import logging
import time
import os


class Market(Component):
    def __init__(self):
        super(Market, self).__init__()
        self.pid = os.getpid()
        now = time.ctime(int(time.time()))
        self.logger.info("(PID %s)-starting Market, %s" %(str(self.pid),str(now)))
        self.price = [0, 0, 0]
        self.pulse = 0
        
    def on_notify(self):
        now = self.notify.recv_pyobj()
        if self.pulse == 0:
            self.logger.info('starting new round')
            msg = 'start'
            self.announce.send_pyobj(msg)
        self.pulse += 1
        if self.pulse == 300:
            self.logger.info('bidding period expired')
            self.announce.send_pyobj('stop')
        if self.pulse == 600:
            self.pulse = 0
             
    def on_statusport(self):
        msg = self.statusport.recv_pyobj()
        self.logger.info(msg)
            
                       
    def __destroy__(self):
        now = time.time()
        self.logger.info("%s - stopping Market, %s" %(str(self.pid),now))         

