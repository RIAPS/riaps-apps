@0xb92f2989446fe96c;

using Cxx = import "/capnp/c++.capnp";
$Cxx.namespace("distributedestimator::messages");

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

# riaps:keep_sensorvalue:begin
struct SensorValue {
    msg @0 : Text;
}
# riaps:keep_sensorvalue:end

# riaps:keep_estimate:begin
struct Estimate {
    msg @0 : Text;
}
# riaps:keep_estimate:end

