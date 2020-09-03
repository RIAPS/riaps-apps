# riaps:keep_import:begin
from riaps.run.comp import Component
import logging
# import capnp
# import powerfail_capnp

# riaps:keep_import:end

class PowerMonitor(Component):

# riaps:keep_constr:begin
    def __init__(self):
        super(PowerMonitor, self).__init__()
# riaps:keep_constr:end

# riaps:keep_subport:begin
    def on_SubPort(self):
        msg = self.SubPort.recv_pyobj()
        self.logger.info("received subscribed message : %s" % msg)
# riaps:keep_subport:end

# riaps:keep_impl:begin
    def handlePeerStateChange(self, state, uuid):
        self.logger.info("peer %s state changed to %s" % (uuid, state))

# riaps:keep_impl:end