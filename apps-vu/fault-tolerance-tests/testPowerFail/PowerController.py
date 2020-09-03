# riaps:keep_import:begin
from riaps.run.comp import Component
import logging
import random
import os
# import capnp
# import powerfail_capnp

# riaps:keep_import:end

class PowerController(Component):

# riaps:keep_constr:begin
    def __init__(self):
        super(PowerController, self).__init__()
# riaps:keep_constr:end

# riaps:keep_reqport:begin
    def on_ReqPort(self):
        reply = self.ReqPort.recv_pyobj()
        self.logger.info("received from device component %s" % reply)
        
    def handleActivate(self):
        self.logger.info("starting shutdown timer")
        self.clock.setDelay(10.0)
        self.clock.launch()
# riaps:keep_reqport:end

# riaps:keep_clock:begin
    def on_clock(self):
        now = self.clock.recv_pyobj()
        self.logger.info("on_clock(): %s" % now)
        self.logger.info("sending request")
        msg = "shutdown"
        try:
            self.ReqPort.send_pyobj(msg)
            self.clock.halt()
        except:
            self.logger.info("send exception")
        
# riaps:keep_clock:end

# riaps:keep_trigger:begin
    def on_trigger(self):
        now = self.trigger.recv_pyobj()
        self.logger.info("on_trigger(): %s" % now)
        self.logger.info("publishing value")
        val = random.random()
        self.PubPort.send_pyobj(val)
# riaps:keep_trigger:end

# riaps:keep_impl:begin

# riaps:keep_impl:end