



#include <componentmodel/r_pyconfigconverter.h>
#include <base/ActuatorBase.h>

using namespace std;
using namespace riaps::ports;

namespace sltest {
    namespace components {
        ActuatorBase::ActuatorBase(const py::object*  parent_actor     ,
                          const py::dict     actor_spec       ,
                          const py::dict     type_spec        ,
                          const std::string& name             ,
                          const std::string& type_name        ,
                          const py::dict     args             ,
                          const std::string& application_name ,
                          const std::string& actor_name       ) : ComponentBase(application_name, actor_name){
            auto conf = PyConfigConverter::convert(type_spec, actor_spec);
            conf.component_name = name;
            conf.component_type = type_name;
            conf.is_device=false;
            set_config(conf);
        }

        tuple<MessageReader<messages::Force>, PortError> ActuatorBase::RecvForce() {
            auto port = GetPortAs<riaps::ports::SubscriberPort>(PORT_SUB_FORCE);
            auto [msg_bytes, error] = port->Recv();
            MessageReader<messages::Force> reader(msg_bytes);
            return make_tuple(reader, error);
        }



        void ActuatorBase::DispatchMessage(riaps::ports::PortBase* port) {
            auto port_name = port->port_name();
            if (port_name == PORT_SUB_FORCE) {
                OnForce();
            }
        }

        void ActuatorBase::DispatchInsideMessage(zmsg_t *zmsg, riaps::ports::PortBase *port) { }
    }
}
