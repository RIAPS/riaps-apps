


#include <LocalEstimator.h>
// riaps:keep_header:begin

// riaps:keep_header:end

namespace distributedestimator {
    namespace components {

        // riaps:keep_construct:begin
        LocalEstimator::LocalEstimator(const py::object*  parent_actor     ,
                      const py::dict     actor_spec       ,
                      const py::dict     type_spec        ,
                      const std::string& name             ,
                      const std::string& type_name        ,
                      const py::dict     args             ,
                      const std::string& application_name ,
                      const std::string& actor_name       ,
                      const py::list groups               )
            : LocalEstimatorBase(parent_actor, actor_spec, type_spec, name, type_name, args, application_name, actor_name, groups) {

        }
        // riaps:keep_construct:end

        void LocalEstimator::OnQuery() {
            // riaps:keep_onquery:begin
            auto [msg, err] = RecvQuery();
            if (!err)
                component_logger()->info("{}: [{}]", msg->getMsg().cStr(), ::getpid());
            else
                component_logger()->warn("Recv() error in {}, errorcode: {}", __func__, err.error_code());
            // riaps:keep_onquery:end
        }

        void LocalEstimator::OnReady() {
            // riaps:keep_onready:begin
            auto [msg_ready, err] = RecvReady();
            if (!err) {
                component_logger()->info("{}: {} {}", __func__, msg_ready->getMsg().cStr(), ::getpid());

                MessageBuilder<messages::SensorQuery> query_builder;
                query_builder->setMsg("sensor_query");
                auto query_error = SendQuery(query_builder);
                if (!query_error) {
                    auto [query_reader, query_error] = RecvQuery();
                    MessageBuilder<messages::Estimate> msg_estimate;
                    msg_estimate->setMsg(fmt::format("local_est({})", ::getpid()));
                    auto estimate_error = SendEstimate(msg_estimate);
                    if (estimate_error) {
                        component_logger()->warn("Error sending message: {}, errorcode: {}", __func__, estimate_error.error_code());
                    }
                } else {
                    component_logger()->warn("Error sending message: {}, errorcode: {}", __func__, query_error.error_code());
                }

            }
            // riaps:keep_onready:end
        }

        // riaps:keep_impl:begin
        void LocalEstimator::HandlePeerStateChange(const std::string& state, const std::string& uuid) {

        }
        // riaps:keep_impl:end

        // riaps:keep_destruct:begin
        LocalEstimator::~LocalEstimator() {

        }
        // riaps:keep_destruct:end

    }
}

std::unique_ptr<distributedestimator::components::LocalEstimator>
create_component_py(const py::object *parent_actor,
                    const py::dict actor_spec,
                    const py::dict type_spec,
                    const std::string &name,
                    const std::string &type_name,
                    const py::dict args,
                    const std::string &application_name,
                    const std::string &actor_name,
                    const py::list groups               ) {
    auto ptr = new distributedestimator::components::LocalEstimator(parent_actor, actor_spec, type_spec, name, type_name, args,
                                                                     application_name,
                                                                     actor_name,
                                                                     groups);
    return std::move(std::unique_ptr<distributedestimator::components::LocalEstimator>(ptr));
}

PYBIND11_MODULE(liblocalestimator, m) {
    py::class_<distributedestimator::components::LocalEstimator> testClass(m, "LocalEstimator");
    testClass.def(py::init<const py::object*, const py::dict, const py::dict, const std::string&, const std::string&, const py::dict, const std::string&, const std::string&, const py::list>());

    testClass.def("setup"                 , &distributedestimator::components::LocalEstimator::Setup);
    testClass.def("activate"              , &distributedestimator::components::LocalEstimator::Activate);
    testClass.def("terminate"             , &distributedestimator::components::LocalEstimator::Terminate);
    testClass.def("handlePortUpdate"      , &distributedestimator::components::LocalEstimator::HandlePortUpdate);
    testClass.def("handleCPULimit"        , &distributedestimator::components::LocalEstimator::HandleCPULimit);
    testClass.def("handleMemLimit"        , &distributedestimator::components::LocalEstimator::HandleMemLimit);
    testClass.def("handleSpcLimit"        , &distributedestimator::components::LocalEstimator::HandleSpcLimit);
    testClass.def("handleNetLimit"        , &distributedestimator::components::LocalEstimator::HandleNetLimit);
    testClass.def("handleNICStateChange"  , &distributedestimator::components::LocalEstimator::HandleNICStateChange);
    testClass.def("handlePeerStateChange" , &distributedestimator::components::LocalEstimator::HandlePeerStateChange);
    testClass.def("handleReinstate"       , &distributedestimator::components::LocalEstimator::HandleReinstate);
    testClass.def("handleActivate"        , &distributedestimator::components::LocalEstimator::HandleActivate);

    m.def("create_component_py", &create_component_py, "Instantiates the component from python configuration");
}
