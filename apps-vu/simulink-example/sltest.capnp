@0x8a55f667bf0eecd1;

using Cxx = import "/capnp/c++.capnp";
$Cxx.namespace("sltest::messages");

# riaps:keep_position:begin
struct Position {
    position @0: Float64;
}
# riaps:keep_position:end

# riaps:keep_force:begin
struct Force {
    force @0: Float64;
}
# riaps:keep_force:end

