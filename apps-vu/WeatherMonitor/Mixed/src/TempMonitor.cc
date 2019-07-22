


#include <TempMonitor.h>
// riaps:keep_header:begin

// riaps:keep_header:end

namespace weathermonitor {
    namespace components {

        // riaps:keep_construct:begin
        TempMonitor::TempMonitor(const py::object*  parent_actor     ,
                      const py::dict     actor_spec       ,
                      const py::dict     type_spec        ,
                      const std::string& name             ,
                      const std::string& type_name        ,
                      const py::dict     args             ,
                      const std::string& application_name ,
                      const std::string& actor_name       )
            : TempMonitorBase(parent_actor, actor_spec, type_spec, name, type_name, args, application_name, actor_name) {

        }
        // riaps:keep_construct:end

        void TempMonitor::OnTempupdate() {
            // riaps:keep_ontempupdate:begin
            auto [msg, err] = RecvTempupdate();
            if (!err)
                component_logger()->info("{}:{}", __func__, msg->getTemperature());
            else
                component_logger()->warn("Recv() error in {}, errorcode: {}", __func__, err.error_code());
            // riaps:keep_ontempupdate:end
        }

        // riaps:keep_impl:begin
        void TempMonitor::HandlePeerStateChange(const std::string& state, const std::string& uuid) {

        }
        // riaps:keep_impl:end

        // riaps:keep_destruct:begin
        TempMonitor::~TempMonitor() {

        }
        // riaps:keep_destruct:end

    }
}

std::unique_ptr<weathermonitor::components::TempMonitor>
create_component_py(const py::object *parent_actor,
                    const py::dict actor_spec,
                    const py::dict type_spec,
                    const std::string &name,
                    const std::string &type_name,
                    const py::dict args,
                    const std::string &application_name,
                    const std::string &actor_name) {
    auto ptr = new weathermonitor::components::TempMonitor(parent_actor, actor_spec, type_spec, name, type_name, args,
                                                                     application_name,
                                                                     actor_name);
    return std::move(std::unique_ptr<weathermonitor::components::TempMonitor>(ptr));
}

PYBIND11_MODULE(libtempmonitor, m) {
    py::class_<weathermonitor::components::TempMonitor> testClass(m, "TempMonitor");
    testClass.def(py::init<const py::object*, const py::dict, const py::dict, const std::string&, const std::string&, const py::dict, const std::string&, const std::string&>());

    testClass.def("setup"                 , &weathermonitor::components::TempMonitor::Setup);
    testClass.def("activate"              , &weathermonitor::components::TempMonitor::Activate);
    testClass.def("terminate"             , &weathermonitor::components::TempMonitor::Terminate);
    testClass.def("handlePortUpdate"      , &weathermonitor::components::TempMonitor::HandlePortUpdate);
    testClass.def("handleCPULimit"        , &weathermonitor::components::TempMonitor::HandleCPULimit);
    testClass.def("handleMemLimit"        , &weathermonitor::components::TempMonitor::HandleMemLimit);
    testClass.def("handleSpcLimit"        , &weathermonitor::components::TempMonitor::HandleSpcLimit);
    testClass.def("handleNetLimit"        , &weathermonitor::components::TempMonitor::HandleNetLimit);
    testClass.def("handleNICStateChange"  , &weathermonitor::components::TempMonitor::HandleNICStateChange);
    testClass.def("handlePeerStateChange" , &weathermonitor::components::TempMonitor::HandlePeerStateChange);
    testClass.def("handleReinstate"       , &weathermonitor::components::TempMonitor::HandleReinstate);

    m.def("create_component_py", &create_component_py, "Instantiates the component from python configuration");
}
