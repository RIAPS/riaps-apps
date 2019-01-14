


#include <TempSensor.h>
// riaps:keep_header:begin

// riaps:keep_header:end

namespace weathermonitor {
    namespace components {

        // riaps:keep_construct:begin
        TempSensor::TempSensor(const py::object*  parent_actor     ,
                      const py::dict     actor_spec       ,
                      const py::dict     type_spec        ,
                      const std::string& name             ,
                      const std::string& type_name        ,
                      const py::dict     args             ,
                      const std::string& application_name ,
                      const std::string& actor_name       )
            : TempSensorBase(parent_actor, actor_spec, type_spec, name, type_name, args, application_name, actor_name) {
        		this->temperature = 65;
        }
        // riaps:keep_construct:end

        void TempSensor::OnClock() {
            // riaps:keep_onclock:begin
            auto msg = RecvClock();
            component_logger()->info("{}", __func__);

            this->temperature += 1;
            MessageBuilder<messages::TempData> builder;
            builder->setTemperature(this->temperature);

            auto pub_error = SendReady(builder);
            if (pub_error){
                component_logger()->warn("Error publishing temperature: {}, errorcode: {}", __func__, pub_error.error_code());
            }
            // riaps:keep_onclock:end
        }

        // riaps:keep_impl:begin
        void TempSensor::HandlePeerStateChange(const std::string& state, const std::string& uuid) {

        }
        // riaps:keep_impl:end

        // riaps:keep_destruct:begin
        TempSensor::~TempSensor() {

        }
        // riaps:keep_destruct:end

    }
}

std::unique_ptr<weathermonitor::components::TempSensor>
create_component_py(const py::object *parent_actor,
                    const py::dict actor_spec,
                    const py::dict type_spec,
                    const std::string &name,
                    const std::string &type_name,
                    const py::dict args,
                    const std::string &application_name,
                    const std::string &actor_name) {
    auto ptr = new weathermonitor::components::TempSensor(parent_actor, actor_spec, type_spec, name, type_name, args,
                                                                     application_name,
                                                                     actor_name);
    return std::move(std::unique_ptr<weathermonitor::components::TempSensor>(ptr));
}

PYBIND11_MODULE(libtempsensor, m) {
    py::class_<weathermonitor::components::TempSensor> testClass(m, "TempSensor");
    testClass.def(py::init<const py::object*, const py::dict, const py::dict, const std::string&, const std::string&, const py::dict, const std::string&, const std::string&>());

    testClass.def("setup"                 , &weathermonitor::components::TempSensor::Setup);
    testClass.def("activate"              , &weathermonitor::components::TempSensor::Activate);
    testClass.def("terminate"             , &weathermonitor::components::TempSensor::Terminate);
    testClass.def("handlePortUpdate"      , &weathermonitor::components::TempSensor::HandlePortUpdate);
    testClass.def("handleCPULimit"        , &weathermonitor::components::TempSensor::HandleCPULimit);
    testClass.def("handleMemLimit"        , &weathermonitor::components::TempSensor::HandleMemLimit);
    testClass.def("handleSpcLimit"        , &weathermonitor::components::TempSensor::HandleSpcLimit);
    testClass.def("handleNetLimit"        , &weathermonitor::components::TempSensor::HandleNetLimit);
    testClass.def("handleNICStateChange"  , &weathermonitor::components::TempSensor::HandleNICStateChange);
    testClass.def("handlePeerStateChange" , &weathermonitor::components::TempSensor::HandlePeerStateChange);
    testClass.def("handleReinstate"       , &weathermonitor::components::TempSensor::HandleReinstate);

    m.def("create_component_py", &create_component_py, "Instantiates the component from python configuration");
}
