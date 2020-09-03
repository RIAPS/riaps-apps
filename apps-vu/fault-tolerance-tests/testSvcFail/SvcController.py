# riaps:keep_import:begin
from riaps.run.comp import Component
import logging
# import capnp
# import deplofail_capnp
import random

# riaps:keep_import:end

class SvcController(Component):

# riaps:keep_constr:begin
    def __init__(self, service):
        super(SvcController, self).__init__()
        if service == "deplo":
            self.service = "riaps_deplo"
        elif service == "disco":
            self.service = "riaps_disco"
        
    def handleActivate(self):
        self.logger.info("starting deplo stop timer")
        self.clock.setDelay(30.0)
        self.clock.launch()
# riaps:keep_constr:end

# riaps:keep_reqport:begin
    def on_reqport(self):
        reply = self.reqport.recv_pyobj()
        self.logger.info("received from device component %s" % reply)
# riaps:keep_reqport:end

# riaps:keep_clock:begin
    def on_clock(self):
        now = self.clock.recv_pyobj()
        self.logger.info("on_clock(): %s" % now)
        self.logger.info("sending request")
        self.logger.info("service = %s" % self.service)
        msg = self.service
        try:
            self.reqport.send_pyobj(msg)
        except:
            self.logger.info("send exception")
        else:
            self.clock.halt()
# riaps:keep_clock:end

# riaps:keep_trigger:begin
    def on_trigger(self):
        now = self.trigger.recv_pyobj()
        self.logger.info("on_trigger(): %s" % now)
        val = random.randint(0,100)
        self.logger.info("publishing value %s" % val)
        self.pubport.send_pyobj(val)
# riaps:keep_trigger:end

# riaps:keep_impl:begin

# riaps:keep_impl:end