#
# riaps:keep_import:begin
from riaps.run.comp import Component
import logging
import os

# riaps:keep_import:end

class LocalEstimator(Component):
# riaps:keep_constr:begin
    def __init__(self,iArg,fArg,sArg,bArg):
        super(LocalEstimator, self).__init__()
        self.pid = os.getpid()
        self.pending = 0
        self.logger.info("LocalEstimator(iArg=%d,fArg=%f,sArg=%s,bArg=%s"
                         %(iArg,fArg,sArg,str(bArg)))
        self.logger.info("name,typeName,localID,actorName,appName,actorID = (%s,%s,%s,%s,%s,%s)"
                         % (self.getName(),self.getTypeName(),hex(self.getLocalID()),
                            self.getActorName(),self.getAppName(),
                            hex(int.from_bytes(self.getActorID(),'big'))))
# riaps:keep_constr:end

# riaps:keep_ready:begin
    def on_ready(self):
        msg = self.ready.recv_pyobj()
        self.logger.info("on_ready():%s [%d]", msg, self.pid)
        while self.pending > 0:     # Handle the case when there is a pending request
            self.on_query()
        msg = "sensor_query"
        if self.query.send_pyobj(msg):
            self.pending += 1
# riaps:keep_ready:end

# riaps:keep_query:begin
    def on_query(self):
        msg = self.query.recv_pyobj()
        self.logger.info("on_query():%s", msg)
        self.pending -= 1
        msg = "local_est(" + str(self.pid) + ")"
        self.estimate.send_pyobj(msg)
# riaps:keep_query:end

# riaps:keep_impl:begin
    def handleActivate(self):
        self.logger.info("activate: UUID = %s" % self.getUUID())

    def handleNICStateChange(self, state):
        self.logger.info("NIC is %s" % state)
# riaps:keep_impl:end
