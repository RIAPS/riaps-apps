from compute_interface import ComputeInterface
from riaps.run.comp import Component
import logging

class Backup(Component):
    def __init__(self):
        super(Backup, self).__init__()
        self.is_leader_down = False
        self.received_keepalive_msg = False
        self.last_received_values = None
        self.c_inf = ComputeInterface()
        self.logger.info("Backup initialized")

        
    def on_leadermsg(self):
        msg = self.leadermsg.recv_pyobj()
        self.received_keepalive_msg = True
        self.is_leader_down = False
        self.logger.info("Keepalive message received")
        
    def on_clock(self):
        msg = self.clock.recv_pyobj()
        if(self.received_keepalive_msg == False):
            #No message from leader in the last 3.5s
            self.logger.info("No keepalive messages received for the timeout, backup assuming leader role at %f", msg)
            self.is_leader_down = True
            
        self.received_keepalive_msg = False
        
        
    def on_providermsg(self):
        tempPG = self.providermsg.recv_pyobj()
        self.last_received_values = tempPG
        #Add additional checks for leader operation?
        if self.is_leader_down:
            x = self.c_inf.compute_result(tempPG)
            '''result = self.c_inf.compute_result(tempPG)
            if(result.success and result.x[1] <= 0.97 ):
                self.logger.info("result found, sending %f", result.x[1])
                self.resultready.send_pyobj(result.x[1])'''
            if x[1] <= 0.97:
                self.logger.info("result found, sending %f", x[1])
                self.resultready.send_pyobj(x[1])
            else:
                self.logger.info("stable state")