#Publisher.py
from riaps.run.comp import Component
import os
import logging
import random

class Publisher(Component):
    def __init__(self):
        super(Publisher, self).__init__()	        
        self.pid = os.getpid()
        self.logger.info("(PID %s) - starting Publisher" % (str(self.pid),))
        

    def on_sampling(self):
        now = self.sampling.recv_pyobj()
        self.logger.info('PID(%s) - on_sampling(): %s' % (str(self.pid),str(now)))
        self.outgoing.send_pyobj(("RMS voltage level", random.random() * 110.0))
    
    def __destroy__(self):			
        self.logger.info("(PID %s) - stopping Publisher" % (str(self.pid),))   	        	        
