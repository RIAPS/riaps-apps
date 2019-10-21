# import riaps
from riaps.run.comp import Component
import os
import logging

class PubSim(Component):
    def __init__(self, logfile):
        super(PubSim, self).__init__()
        self.pid = os.getpid()
        self.sendagain = False #wait for subscriber to connect

        logpath = '/tmp/' + logfile + '.log'
        try: os.remove(logpath)
        except OSError: pass
        self.fh = logging.FileHandler(logpath)
        self.fh.setLevel(logging.WARNING)
        self.fh.setFormatter(self.logformatter)
        self.logger.addHandler(self.fh)

    def on_clock(self):
        now = self.clock.recv_pyobj()   # Receive time.time() as float
        self.logger.warning('on_clock(): %s',str(now))
        msg = 5 #set value to be published
        if self.sendagain: #check if previous cycle has finished
            self.logger.warning('sending value')
            self.pubSimPort.send_pyobj(msg)
            self.sendagain = False #reset flag to prevent sending until ack is received

    def on_ready(self):
        rep = self.ready.recv_pyobj() #receive ack from subscriber
        self.logger.warning('[%d] recv rep: %s' % (self.pid,rep))
        if rep == 'sub_up': #subscriber is up
            rep = 'pub_up'  #acknowledge subscriber
        else:
            rep = 'done'
        self.ready.send_pyobj(rep)
        self.sendagain = True #start sending

    def __destroy__(self):
        self.logger.warning("[%d] destroyed" % self.pid)
        

