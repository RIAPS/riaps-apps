#
from riaps.run.comp import Component
import logging

class GlobalEstimator(Component):
    def __init__(self,iArg,fArg,sArg,bArg):
        super(GlobalEstimator, self).__init__()
        self.logger.info("GlobalEstimator(iArg=%d,fArg=%f,sArg=%s,bArg=%s)" 
                         %(iArg,fArg,sArg,str(bArg)))

    def on_wakeup(self):
        msg = self.wakeup.recv_pyobj()
        self.logger.info("on_wakeup():%s",msg)
        
    def on_estimate(self):
        msg = self.estimate.recv_pyobj()
        self.logger.info("on_estimate():%s",msg)
    
