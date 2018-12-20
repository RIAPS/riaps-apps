# riaps:keep_import:begin
from riaps.run.comp import Component
import logging
import capnp
import distributedestimator_capnp

# riaps:keep_import:end

class GlobalEstimator(Component):

# riaps:keep_constr:begin
    def __init__(self, iArg, fArg, sArg, bArg):
        super(GlobalEstimator, self).__init__()
        self.logger.info("GlobalEstimator(iArg=%d,fArg=%f,sArg=%s,bArg=%s)" 
                         %(iArg,fArg,sArg,str(bArg)))
# riaps:keep_constr:end

# riaps:keep_estimate:begin
    def on_estimate(self):
        msg_bytes = self.estimate.recv()
        msgEstimate = distributedestimator_capnp.Estimate.from_bytes(msg_bytes)
        self.logger.info("on_estimate():%s",msgEstimate.msg)
# riaps:keep_estimate:end

# riaps:keep_wakeup:begin
    def on_wakeup(self):
        msg = self.wakeup.recv_pyobj()
        self.logger.info("on_wakeup():%s",msg)
# riaps:keep_wakeup:end

# riaps:keep_impl:begin

# riaps:keep_impl:end