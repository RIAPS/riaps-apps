# riaps:keep_import:begin
from riaps.run.comp import Component
import logging

# riaps:keep_import:end

class Sensor(Component):
# riaps:keep_constr:begin
    def __init__(self):
        super(Sensor, self).__init__()
# riaps:keep_constr:end

# riaps:keep_clock:begin
    def on_clock(self):
        now = self.clock.recv_pyobj()   # Receive time.time() as float
        self.logger.info('on_clock(): %s' % str(now))
        msg = "data_ready"
        self.ready.send_pyobj(msg)
# riaps:keep_clock:end

# riaps:keep_request:begin
    def on_request(self):
        req = self.request.recv_pyobj()
        self.logger.info("on_request():%s" % req)
        rep = "sensor_rep"
        self.request.send_pyobj(rep)
# riaps:keep_request:end

# riaps:keep_impl:begin

# riaps:keep_impl:end
