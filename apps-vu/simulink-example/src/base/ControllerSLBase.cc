



#include <componentmodel/r_pyconfigconverter.h>
#include <base/ControllerSLBase.h>

using namespace std;
using namespace riaps::ports;

namespace sltest {
    namespace components {
        ControllerSLBase::ControllerSLBase(const py::object*  parent_actor     ,
                          const py::dict     actor_spec       ,
                          const py::dict     type_spec        ,
                          const std::string& name             ,
                          const std::string& type_name        ,
                          const py::dict     args             ,
                          const std::string& application_name ,
                          const std::string& actor_name       ,
                          const py::list groups) : ComponentBase(application_name, actor_name){
            auto conf = PyConfigConverter::convert(type_spec, actor_spec, args);
            auto gr = PyConfigConverter::ConvertGroups(groups);
            conf.component_name = name;
            conf.component_type = type_name;
            conf.is_device=false;
            set_config(conf,gr);
        }

        tuple<MessageReader<messages::Position>, PortError> ControllerSLBase::RecvPosition() {
            auto port = GetPortAs<riaps::ports::SubscriberPort>(PORT_SUB_POSITION);
            auto [msg_bytes, error] = port->Recv();
            MessageReader<messages::Position> reader(msg_bytes);
            return make_tuple(reader, error);
        }


        riaps::ports::PortError ControllerSLBase::SendForce(MessageBuilder<messages::Force>& message) {
            return SendMessageOnPort(message.capnp_builder(), PORT_PUB_FORCE);
        }


        void ControllerSLBase::DispatchMessage(riaps::ports::PortBase* port) {
            auto port_name = port->port_name();
            if (port_name == PORT_SUB_POSITION) {
                OnPosition();
            }
        }

        void ControllerSLBase::DispatchInsideMessage(zmsg_t *zmsg, riaps::ports::PortBase *port) { }
    }
}
