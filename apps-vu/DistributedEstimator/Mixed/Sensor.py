# riaps:keep_import:begin
from riaps.run.comp import Component
import logging
import capnp
import distributedestimator_capnp

# riaps:keep_import:end

class Sensor(Component):

# riaps:keep_constr:begin
    def __init__(self):
        super(Sensor, self).__init__()
# riaps:keep_constr:end

# riaps:keep_request:begin
    def on_request(self):
        bytes = self.request.recv()
        req = distributedestimator_capnp.SensorQuery.from_bytes(bytes)
        self.logger.info("on_request():%s", req.msg)
        rep = distributedestimator_capnp.SensorValue.new_message()
        rep.msg = "sensor_rep"
        repBytes = rep.to_bytes()
        self.request.send(repBytes)
# riaps:keep_request:end

# riaps:keep_clock:begin
    def on_clock(self):
        msg = self.clock.recv_pyobj()
        self.logger.info('on_clock(): %s',str(msg))
        msg = distributedestimator_capnp.SensorReady.new_message()
        msg.msg = "data_ready"
        msgBytes = msg.to_bytes()
        self.ready.send(msgBytes)
# riaps:keep_clock:end

# riaps:keep_impl:begin

# riaps:keep_impl:end