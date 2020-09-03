# riaps:keep_import:begin
from riaps.run.comp import Component
import logging
import random
# import capnp
# import memfail_capnp

# riaps:keep_import:end

class MemPublisher(Component):

# riaps:keep_constr:begin
    def __init__(self):
        super(MemPublisher, self).__init__()
# riaps:keep_constr:end

# riaps:keep_trigger:begin
    def on_trigger(self):
        now = self.trigger.recv_pyobj()
        self.logger.info("on_trigger(): %s" % now)
        self.logger.info("publishing value")
        val = random.random()
        self.pubport.send_pyobj(val)
# riaps:keep_trigger:end

# riaps:keep_impl:begin

# riaps:keep_impl:end