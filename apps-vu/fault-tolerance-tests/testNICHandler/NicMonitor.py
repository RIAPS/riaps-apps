from riaps.run.comp import Component
import logging

class NicMonitor(Component):
    def __init__(self):
        super(NicMonitor, self).__init__()
        
    def on_recvval(self):
        msg = self.recvval.recv_pyobj()
        self.logger.info("received %s" % msg)
        
    def handlePeerStateChange(self, state, uuid):
        self.logger.info("peer %s state changed to %s" %(uuid, state))
        
    def __destroy__(self):
        self.logger.info("Stopping NicMonitor")