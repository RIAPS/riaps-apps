@0xfcb4fba25418455c;

using Cxx = import "/capnp/c++.capnp";
$Cxx.namespace("weathermonitor::messages");

# riaps:keep_tempdata:begin
struct TempData {
    temperature @0: Float64;
}
# riaps:keep_tempdata:end
