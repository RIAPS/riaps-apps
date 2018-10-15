from compute_interface import ComputeInterface
from riaps.run.comp import Component
import logging

class Leader(Component):
    def __init__(self):
        super(Leader, self).__init__()
        self.c_inf = ComputeInterface()
        self.logger.info("Leader initialized")
        
    def on_clock(self):
        msg = self.clock.recv_pyobj()
        self.logger.info("sending keepalive")
        self.backuplink.send_pyobj(msg)
        
    def on_providermsg(self):
        tempPG = self.providermsg.recv_pyobj()
        x = self.c_inf.compute_result(tempPG)
        self.logger.info(str(x))
        if x[1] <= 0.97:
            self.logger.info("result found, sending %f", x[1])
            self.resultready.send_pyobj(x[1])
        else:
            self.logger.info("stable state")
