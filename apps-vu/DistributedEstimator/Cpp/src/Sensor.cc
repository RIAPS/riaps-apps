


#include <Sensor.h>
// riaps:keep_header:begin

// riaps:keep_header:end

namespace distributedestimator {
    namespace components {

        // riaps:keep_construct:begin
        Sensor::Sensor(const py::object*  parent_actor     ,
                      const py::dict     actor_spec       ,
                      const py::dict     type_spec        ,
                      const std::string& name             ,
                      const std::string& type_name        ,
                      const py::dict     args             ,
                      const std::string& application_name ,
                      const std::string& actor_name       )
            : SensorBase(parent_actor, actor_spec, type_spec, name, type_name, args, application_name, actor_name) {

        }
        // riaps:keep_construct:end

        void Sensor::OnClock() {
            // riaps:keep_onclock:begin
            auto time = RecvClock();

            char buffer[80];
            std::strftime(buffer, 80, "%T", std::localtime(&time.tv_sec));
            component_logger()->info("{}: {}:{}", __func__, buffer, time.tv_nsec/1000);

            MessageBuilder<messages::SensorReady> builder;
            builder->setMsg("data_ready");
            auto error = SendReady(builder);
            if (error) {
                component_logger()->warn("Error sending message: {}, errorcode: {}", __func__, error.error_code());
            }
            // riaps:keep_onclock:end
        }

        void Sensor::OnRequest() {
            // riaps:keep_onrequest:begin
            auto [msg, err] = RecvRequest();

            component_logger()->info("{}: {}", __func__, msg->getMsg().cStr());

            MessageBuilder<messages::SensorValue> msg_sensor_value;
            msg_sensor_value->setMsg("sensor_rep");
            auto send_error = SendRequest(msg_sensor_value);
            if (send_error){
                component_logger()->warn("Error sending message: {}, errorcode: {}", __func__, send_error.error_code());
            }
            // riaps:keep_onrequest:end
        }

        // riaps:keep_impl:begin
        void Sensor::HandlePeerStateChange(const std::string& state, const std::string& uuid) {

        }
        // riaps:keep_impl:end

        // riaps:keep_destruct:begin
        Sensor::~Sensor() {

        }
        // riaps:keep_destruct:end

    }
}

std::unique_ptr<distributedestimator::components::Sensor>
create_component_py(const py::object *parent_actor,
                    const py::dict actor_spec,
                    const py::dict type_spec,
                    const std::string &name,
                    const std::string &type_name,
                    const py::dict args,
                    const std::string &application_name,
                    const std::string &actor_name) {
    auto ptr = new distributedestimator::components::Sensor(parent_actor, actor_spec, type_spec, name, type_name, args,
                                                                     application_name,
                                                                     actor_name);
    return std::move(std::unique_ptr<distributedestimator::components::Sensor>(ptr));
}

PYBIND11_MODULE(libsensor, m) {
    py::class_<distributedestimator::components::Sensor> testClass(m, "Sensor");
    testClass.def(py::init<const py::object*, const py::dict, const py::dict, const std::string&, const std::string&, const py::dict, const std::string&, const std::string&>());

    testClass.def("setup"                 , &distributedestimator::components::Sensor::Setup);
    testClass.def("activate"              , &distributedestimator::components::Sensor::Activate);
    testClass.def("terminate"             , &distributedestimator::components::Sensor::Terminate);
    testClass.def("handlePortUpdate"      , &distributedestimator::components::Sensor::HandlePortUpdate);
    testClass.def("handleCPULimit"        , &distributedestimator::components::Sensor::HandleCPULimit);
    testClass.def("handleMemLimit"        , &distributedestimator::components::Sensor::HandleMemLimit);
    testClass.def("handleSpcLimit"        , &distributedestimator::components::Sensor::HandleSpcLimit);
    testClass.def("handleNetLimit"        , &distributedestimator::components::Sensor::HandleNetLimit);
    testClass.def("handleNICStateChange"  , &distributedestimator::components::Sensor::HandleNICStateChange);
    testClass.def("handlePeerStateChange" , &distributedestimator::components::Sensor::HandlePeerStateChange);
    testClass.def("handleReinstate"       , &distributedestimator::components::Sensor::HandleReinstate);

    m.def("create_component_py", &create_component_py, "Instantiates the component from python configuration");
}
