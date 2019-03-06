


#include <Sensor.h>
// riaps:keep_header:begin

// riaps:keep_header:end

namespace sltest {
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

        	// SetDebugLevel(component_logger(), spdlog::level::level_enum::debug);

        	const char* hostname="0.0.0.0"; /* wildcard */
        	const char* portname="51000";
        	memset(&hints,0,sizeof(hints));
        	hints.ai_family=AF_UNSPEC;
        	hints.ai_socktype=SOCK_DGRAM;
        	hints.ai_protocol=0;
        	hints.ai_flags=AI_PASSIVE|AI_ADDRCONFIG;
        	int err=getaddrinfo(hostname,portname,&hints,&res);
        	if (err!=0) {
        		component_logger()->error("failed to resolve local socket address (err={}, line:{})",err, __LINE__);
        	} else {
        		socketfd=socket(res->ai_family,res->ai_socktype,res->ai_protocol);
        		if (socketfd==-1) {
        			component_logger()->error("{}, line: {}",strerror(errno), __LINE__);
        		} else {
        			if (bind(socketfd,res->ai_addr,res->ai_addrlen)==-1) {
        				component_logger()->error("{}, line: {}",strerror(errno), __LINE__);
        			}
        			/** Define socket timeout here
                   	else {
                    	// set timeout, 1sec
                      	struct timeval tv;
                      	tv.tv_sec = 1;
                      	tv.tv_usec = 0;
                      	if (setsockopt(socketfd, SOL_SOCKET, SO_RCVTIMEO,&tv,sizeof(tv)) < 0) {
                          component_logger()->error("Couldn't set timeout on socket");
                        }
                    }
                    **/
        		}
        	}
        	component_logger()->debug("constructor finished");
        }
        // riaps:keep_construct:end

        void Sensor::OnClock() {
            // riaps:keep_onclock:begin
            auto msg = RecvClock();

            component_logger()->info("{}",__FUNCTION__);
            if (socketfd == -1) return;
            double buffer;
            struct sockaddr_storage src_addr;
            socklen_t src_addr_len=sizeof(src_addr);
            //component_logger()->debug("{}->{} is waiting for UDP package", __FUNCTION__, "recvfrom()");
            ssize_t count=recvfrom(socketfd,&buffer,sizeof(buffer),0,(struct sockaddr*)&src_addr,&src_addr_len);
            //component_logger()->debug("{}->{} UDP package arrived", __FUNCTION__, "recvfrom()");
            if (count==-1) {
                component_logger()->error("{}, line: {}",strerror(errno), __LINE__);
            } else {
            	// UDPPAckage -> capnpMessage
            	MessageBuilder<messages::Position> builder;
            	builder->setPosition(buffer);
            	auto pub_error = SendPosition(builder);
            	if (pub_error){
            		component_logger()->warn("Error publishing Position: {}, errorcode: {}", __func__, pub_error.error_code());
            	}
            }
            // riaps:keep_onclock:end
        }


        // riaps:keep_impl:begin

        // riaps:keep_impl:end

        // riaps:keep_destruct:begin
        Sensor::~Sensor() {

        }
        // riaps:keep_destruct:end

    }
}

std::unique_ptr<sltest::components::Sensor>
create_component_py(const py::object *parent_actor,
                    const py::dict actor_spec,
                    const py::dict type_spec,
                    const std::string &name,
                    const std::string &type_name,
                    const py::dict args,
                    const std::string &application_name,
                    const std::string &actor_name) {
    auto ptr = new sltest::components::Sensor(parent_actor, actor_spec, type_spec, name, type_name, args,
                                                                     application_name,
                                                                     actor_name);
    return std::move(std::unique_ptr<sltest::components::Sensor>(ptr));
}

PYBIND11_MODULE(libsensor, m) {
    py::class_<sltest::components::Sensor> testClass(m, "Sensor");
    testClass.def(py::init<const py::object*, const py::dict, const py::dict, const std::string&, const std::string&, const py::dict, const std::string&, const std::string&>());

    testClass.def("setup"                 , &sltest::components::Sensor::Setup);
    testClass.def("activate"              , &sltest::components::Sensor::Activate);
    testClass.def("terminate"             , &sltest::components::Sensor::Terminate);
    testClass.def("handlePortUpdate"      , &sltest::components::Sensor::HandlePortUpdate);
    testClass.def("handleCPULimit"        , &sltest::components::Sensor::HandleCPULimit);
    testClass.def("handleMemLimit"        , &sltest::components::Sensor::HandleMemLimit);
    testClass.def("handleSpcLimit"        , &sltest::components::Sensor::HandleSpcLimit);
    testClass.def("handleNetLimit"        , &sltest::components::Sensor::HandleNetLimit);
    testClass.def("handleNICStateChange"  , &sltest::components::Sensor::HandleNICStateChange);
    testClass.def("handlePeerStateChange" , &sltest::components::Sensor::HandlePeerStateChange);
    testClass.def("handleReinstate"       , &sltest::components::Sensor::HandleReinstate);

    m.def("create_component_py", &create_component_py, "Instantiates the component from python configuration");
}



