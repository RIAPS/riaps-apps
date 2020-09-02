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
        self.group = None
        self.uuid = ''
        
    def handleActivate(self):
        self.group = self.joinGroup("ReplicaGroup", 'market')
        self.uuid = self.getUUID()
        
    def on_notify(self):
        now = self.notify.recv_pyobj()
        if self.group.hasLeader():
            if self.group.isLeader():
                self.logger.info("leader of group %s : %s" % (self.group.getGroupId(), self.uuid))
                if self.pulse == 0:
                    self.logger.info('starting new round')
                    msg = 'start'
                    self.announce.send_pyobj(msg)
                self.pulse += 1
                self.group.send_pyobj(self.pulse)
                if self.pulse == 300:
                    self.logger.info('bidding period expired')
                    self.announce.send_pyobj('stop')
                if self.pulse == 600:
                    self.pulse = 0
        else:
            self.logger.info("group has no leader")
             
    def on_statusport(self):
        msg = self.statusport.recv_pyobj()
        self.logger.info(msg)
        
    def handleGroupMessage(self, group):
        assert (group == self.group)
        msg = group.recv_pyobj()
        if not self.group.isLeader():
            self.logger.info("received from leader : %s" % msg)
            self.pulse = int(msg)
            
    def handlePeerStateChange(self, state, uuid):
        if state == 'off':
            if self.group.hasLeader():
                self.logger.info("replica died")
            else:
                self.logger.info("leader died")
                       
    def __destroy__(self):
        now = time.time()
        self.logger.info("%s - stopping Market, %s" %(str(self.pid),now))         

