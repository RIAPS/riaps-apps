from riaps.run.comp import Component
import os
import logging

class Subscriber_B(Component):
    def __init__(self):
        super(Subscriber_B, self).__init__()	        
        self.pid = os.getpid()
        self.logger.info("(PID %s) - starting Subscriber_B" % (str(self.pid),))
        

    def on_incoming(self):
        msg = self.incoming.recv_pyobj()
        self.logger.info("PID (%s) - on_incoming():%s" % (str(self.pid),str(msg)))

    def __destroy__(self):			
        self.logger.info("(PID %s) - stopping Subscriber_B" % (str(self.pid),))   	        	        
