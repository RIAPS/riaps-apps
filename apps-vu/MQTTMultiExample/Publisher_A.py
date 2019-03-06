from riaps.run.comp import Component
import os
import logging
import random

class Publisher_A(Component):
    def __init__(self):
        super(Publisher_A, self).__init__()	        
        self.pid = os.getpid()
        self.logger.info("(PID %s) - starting Publisher_A" % (str(self.pid),))
        

    def on_sampling(self):
        now = self.sampling.recv_pyobj()
        self.logger.info('PID(%s) - on_sampling(): %s' % (str(self.pid),str(now)))
        self.outgoing.send_pyobj(("RMS voltage level", random.random() * 110.0))
    
    def __destroy__(self):			
        self.logger.info("(PID %s) - stopping Publisher_A" % (str(self.pid),))   	        	        
