



#include <componentmodel/r_pyconfigconverter.h>
#include <base/SensorBase.h>

using namespace std;
using namespace riaps::ports;

namespace distributedestimator {
    namespace components {
        SensorBase::SensorBase(const py::object*  parent_actor     ,
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

        tuple<MessageReader<messages::SensorQuery>, PortError> SensorBase::RecvRequest() {
            auto port = GetPortAs<riaps::ports::ResponsePort>(PORT_REP_REQUEST);
            auto [msg_bytes, error] = port->Recv();
            MessageReader<messages::SensorQuery> reader(msg_bytes);
            return make_tuple(reader, error);
        }

        timespec SensorBase::RecvClock() {
            auto port = GetPortAs<riaps::ports::PeriodicTimer>(PORT_TIMER_CLOCK);
            return port->Recv();
        }

        riaps::ports::PortError SensorBase::SendReady(MessageBuilder<messages::SensorReady>& message) {
            return SendMessageOnPort(message.capnp_builder(), PORT_PUB_READY);
        }

        riaps::ports::PortError SensorBase::SendRequest(MessageBuilder<messages::SensorValue>& message) {
            return SendMessageOnPort(message.capnp_builder(), PORT_REP_REQUEST);
        }


        void SensorBase::DispatchMessage(riaps::ports::PortBase* port) {
            auto port_name = port->port_name();
            if (port_name == PORT_REP_REQUEST) {
                OnRequest();
            }
            if (port_name == PORT_TIMER_CLOCK) {
                OnClock();
            }
        }

        void SensorBase::DispatchInsideMessage(zmsg_t *zmsg, riaps::ports::PortBase *port) { }
    }
}
