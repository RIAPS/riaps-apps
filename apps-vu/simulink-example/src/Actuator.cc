


#include <Actuator.h>
// riaps:keep_header:begin

// riaps:keep_header:end

namespace sltest {
    namespace components {

        // riaps:keep_construct:begin
        Actuator::Actuator(const py::object*  parent_actor     ,
                      const py::dict     actor_spec       ,
                      const py::dict     type_spec        ,
                      const std::string& name             ,
                      const std::string& type_name        ,
                      const py::dict     args             ,
                      const std::string& application_name ,
                      const std::string& actor_name       )
            : ActuatorBase(parent_actor, actor_spec, type_spec, name, type_name, args, application_name, actor_name) {

        	//const char* hostname="127.0.0.1"; /* localhost */
            const char* hostname="10.76.0.144"; /* localhost */
            const char* portname="52000";

            memset(&hints,0,sizeof(hints));
            hints.ai_family=AF_UNSPEC;
            hints.ai_socktype=SOCK_DGRAM;
            hints.ai_protocol=0;
            hints.ai_flags=AI_ADDRCONFIG;
            int err=getaddrinfo(hostname,portname,&hints,&res);
            if (err!=0) {
                component_logger()->error("failed to resolve remote socket address (err={}, line:{})",err, __LINE__);
            } else {
            	sockfd=socket(res->ai_family,res->ai_socktype,res->ai_protocol);
            	if (sockfd==-1) {
            		component_logger()->error("{} line: {}",strerror(errno), __LINE__);
            	}
            }
            component_logger()->info("constructor finished");

        }
        // riaps:keep_construct:end

        void Actuator::OnForce() {
            // riaps:keep_onforce:begin
            auto [msg, err] = RecvForce();

            if (sockfd!=-1){
                if (sendto(sockfd,&msg,sizeof(msg),0, res->ai_addr,res->ai_addrlen)==-1) {
                  component_logger()->error("{} line:{}",strerror(errno), __LINE__);
                } else {

                }

            } else {
              component_logger()->error("Invalid sockfd");
            }
            // riaps:keep_onforce:end
        }


        // riaps:keep_impl:begin

        // riaps:keep_impl:end

        // riaps:keep_destruct:begin
        Actuator::~Actuator() {

        }
        // riaps:keep_destruct:end

    }
}

std::unique_ptr<sltest::components::Actuator>
create_component_py(const py::object *parent_actor,
                    const py::dict actor_spec,
                    const py::dict type_spec,
                    const std::string &name,
                    const std::string &type_name,
                    const py::dict args,
                    const std::string &application_name,
                    const std::string &actor_name) {
    auto ptr = new sltest::components::Actuator(parent_actor, actor_spec, type_spec, name, type_name, args,
                                                                     application_name,
                                                                     actor_name);
    return std::move(std::unique_ptr<sltest::components::Actuator>(ptr));
}

PYBIND11_MODULE(libactuator, m) {
    py::class_<sltest::components::Actuator> testClass(m, "Actuator");
    testClass.def(py::init<const py::object*, const py::dict, const py::dict, const std::string&, const std::string&, const py::dict, const std::string&, const std::string&>());

    testClass.def("setup"                 , &sltest::components::Actuator::Setup);
    testClass.def("activate"              , &sltest::components::Actuator::Activate);
    testClass.def("terminate"             , &sltest::components::Actuator::Terminate);
    testClass.def("handlePortUpdate"      , &sltest::components::Actuator::HandlePortUpdate);
    testClass.def("handleCPULimit"        , &sltest::components::Actuator::HandleCPULimit);
    testClass.def("handleMemLimit"        , &sltest::components::Actuator::HandleMemLimit);
    testClass.def("handleSpcLimit"        , &sltest::components::Actuator::HandleSpcLimit);
    testClass.def("handleNetLimit"        , &sltest::components::Actuator::HandleNetLimit);
    testClass.def("handleNICStateChange"  , &sltest::components::Actuator::HandleNICStateChange);
    testClass.def("handlePeerStateChange" , &sltest::components::Actuator::HandlePeerStateChange);
    testClass.def("handleReinstate"       , &sltest::components::Actuator::HandleReinstate);

    m.def("create_component_py", &create_component_py, "Instantiates the component from python configuration");
}

