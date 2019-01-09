# GlobalEstimator.py
# riaps:keep_import:begin
from riaps.run.comp import Component
import os
import logging
import time

# riaps:keep_import:end

class GlobalEstimator(Component):
# riaps:keep_constr:begin
    def __init__(self):
        super(GlobalEstimator, self).__init__()
        self.pid = os.getpid()
        self.logger.info("(PID %s) - starting GlobalEstimator()" % str(self.pid))

        self.availNumEst = 0
        self.runningSum = 0
# riaps:keep_constr:end

# riaps:keep_estimate:begin
    def on_estimate(self):
        msg = self.estimate.recv_pyobj()
        self.logger.info("PID (%s) - on_estimate():%s" % (str(self.pid),str(msg)))
        (estPid,sTime,sensorVal) = msg
        self.runningSum += sensorVal
        self.availNumEst += 1
# riaps:keep_estimate:end

# riaps:keep_wakeup:begin
    def on_wakeup(self):
        now = self.wakeup.recv_pyobj()
        #self.logger.info('PID(%s) - on_wakeup(): %s',str(self.pid),str(now))

        ''' Average existing estimate '''
        if self.availNumEst != 0:
            averageEst = self.runningSum / self.availNumEst
            self.logger.info("global_est(value=%s)" % averageEst)
# riaps:keep_wakeup:end

# riaps:keep_impl:begin
    def __destroy__(self):
        self.logger.info("(PID %s) - stopping GlobalEstimator" % str(self.pid))  
# riaps:keep_impl:end
