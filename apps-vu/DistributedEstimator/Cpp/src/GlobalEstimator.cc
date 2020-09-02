


#include <GlobalEstimator.h>
// riaps:keep_header:begin

// riaps:keep_header:end

namespace distributedestimator {
    namespace components {

        // riaps:keep_construct:begin
        GlobalEstimator::GlobalEstimator(const py::object*  parent_actor     ,
                      const py::dict     actor_spec       ,
                      const py::dict     type_spec        ,
                      const std::string& name             ,
                      const std::string& type_name        ,
                      const py::dict     args             ,
                      const std::string& application_name ,
                      const std::string& actor_name       ,
                      const py::list groups)
            : GlobalEstimatorBase(parent_actor, actor_spec, type_spec, name, type_name, args, application_name, actor_name, groups) {

        }
        // riaps:keep_construct:end

        void GlobalEstimator::OnEstimate() {
            // riaps:keep_onestimate:begin
            auto [msg, error] = RecvEstimate();
            if (!error)
                component_logger()->info("{}:{}", __func__, msg->getMsg().cStr());
            else
                component_logger()->warn("Recv() error in {}, errorcode: {}", __func__, error.error_code());
            // riaps:keep_onestimate:end
        }

        void GlobalEstimator::OnWakeup() {
            // riaps:keep_onwakeup:begin
            auto time = RecvWakeup();
            char buffer[80];
            std::strftime(buffer, 80, "%T", std::localtime(&time.tv_sec));
            component_logger()->info("{}: {}:{}", __func__, buffer, time.tv_nsec/1000);
            // riaps:keep_onwakeup:end
        }

        // riaps:keep_impl:begin
        void GlobalEstimator::HandlePeerStateChange(const std::string& state, const std::string& uuid) {

        }
        // riaps:keep_impl:end

        // riaps:keep_destruct:begin
        GlobalEstimator::~GlobalEstimator() {

        }
        // riaps:keep_destruct:end

    }
}

std::unique_ptr<distributedestimator::components::GlobalEstimator>
create_component_py(const py::object *parent_actor,
                    const py::dict actor_spec,
                    const py::dict type_spec,
                    const std::string &name,
                    const std::string &type_name,
                    const py::dict args,
                    const std::string &application_name,
                    const std::string &actor_name,
                    const py::list groups) {
    auto ptr = new distributedestimator::components::GlobalEstimator(parent_actor, actor_spec, type_spec, name, type_name, args,
                                                                     application_name,
                                                                     actor_name,
                                                                     groups);
    return std::move(std::unique_ptr<distributedestimator::components::GlobalEstimator>(ptr));
}

PYBIND11_MODULE(libglobalestimator, m) {
    py::class_<distributedestimator::components::GlobalEstimator> testClass(m, "GlobalEstimator");
    testClass.def(py::init<const py::object*, const py::dict, const py::dict, const std::string&, const std::string&, const py::dict, const std::string&, const std::string&, const py::list>());

    testClass.def("setup"                 , &distributedestimator::components::GlobalEstimator::Setup);
    testClass.def("activate"              , &distributedestimator::components::GlobalEstimator::Activate);
    testClass.def("terminate"             , &distributedestimator::components::GlobalEstimator::Terminate);
    testClass.def("handlePortUpdate"      , &distributedestimator::components::GlobalEstimator::HandlePortUpdate);
    testClass.def("handleCPULimit"        , &distributedestimator::components::GlobalEstimator::HandleCPULimit);
    testClass.def("handleMemLimit"        , &distributedestimator::components::GlobalEstimator::HandleMemLimit);
    testClass.def("handleSpcLimit"        , &distributedestimator::components::GlobalEstimator::HandleSpcLimit);
    testClass.def("handleNetLimit"        , &distributedestimator::components::GlobalEstimator::HandleNetLimit);
    testClass.def("handleNICStateChange"  , &distributedestimator::components::GlobalEstimator::HandleNICStateChange);
    testClass.def("handlePeerStateChange" , &distributedestimator::components::GlobalEstimator::HandlePeerStateChange);
    testClass.def("handleReinstate"       , &distributedestimator::components::GlobalEstimator::HandleReinstate);
    testClass.def("handleActivate"        , &distributedestimator::components::GlobalEstimator::HandleActivate);

    m.def("create_component_py", &create_component_py, "Instantiates the component from python configuration");
}
