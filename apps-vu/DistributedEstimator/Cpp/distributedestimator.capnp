@0x8a2627b288c128db;

using Cxx = import "/capnp/c++.capnp";
$Cxx.namespace("distributedestimator::messages");

# riaps:keep_estimate:begin
struct Estimate {
    msg @0 : Text;
}
# riaps:keep_estimate:end

# riaps:keep_sensorvalue:begin
struct SensorValue {
    msg @0 : Text;
}
# riaps:keep_sensorvalue:end

# riaps:keep_sensorready:begin
struct SensorReady {
    msg @0 : Text;
}
# riaps:keep_sensorready:end

# riaps:keep_sensorquery:begin
struct SensorQuery {
    msg @0 : Text;
}
# riaps:keep_sensorquery:end
