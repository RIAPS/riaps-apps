



#include <componentmodel/r_pyconfigconverter.h>
#include <base/LocalEstimatorBase.h>

using namespace std;
using namespace riaps::ports;

namespace distributedestimator {
    namespace components {
        LocalEstimatorBase::LocalEstimatorBase(const py::object*  parent_actor     ,
                          const py::dict     actor_spec       ,
                          const py::dict     type_spec        ,
                          const std::string& name             ,
                          const std::string& type_name        ,
                          const py::dict     args             ,
                          const std::string& application_name ,
                          const std::string& actor_name       ,
                          const py::list groups               ) : ComponentBase(application_name, actor_name){
            auto conf = PyConfigConverter::convert(type_spec, actor_spec, args);
            auto gr = PyConfigConverter::ConvertGroups(groups);
            conf.component_name = name;
            conf.component_type = type_name;
            conf.is_device=false;
            set_config(conf,gr);
        }

        tuple<MessageReader<messages::SensorValue>, PortError> LocalEstimatorBase::RecvQuery() {
            auto port = GetPortAs<riaps::ports::RequestPort>(PORT_REQ_QUERY);
            auto [msg_bytes, error] = port->Recv();
            MessageReader<messages::SensorValue> reader(msg_bytes);
            return make_tuple(reader, error);
        }

        tuple<MessageReader<messages::SensorReady>, PortError> LocalEstimatorBase::RecvReady() {
            auto port = GetPortAs<riaps::ports::SubscriberPort>(PORT_SUB_READY);
            auto [msg_bytes, error] = port->Recv();
            MessageReader<messages::SensorReady> reader(msg_bytes);
            return make_tuple(reader, error);
        }


        riaps::ports::PortError LocalEstimatorBase::SendEstimate(MessageBuilder<messages::Estimate>& message) {
            return SendMessageOnPort(message.capnp_builder(), PORT_PUB_ESTIMATE);
        }

        riaps::ports::PortError LocalEstimatorBase::SendQuery(MessageBuilder<messages::SensorQuery>& message) {
            return SendMessageOnPort(message.capnp_builder(), PORT_REQ_QUERY);
        }


        void LocalEstimatorBase::DispatchMessage(riaps::ports::PortBase* port) {
            auto port_name = port->port_name();
            if (port_name == PORT_REQ_QUERY) {
                OnQuery();
            }
            if (port_name == PORT_SUB_READY) {
                OnReady();
            }
        }

        void LocalEstimatorBase::DispatchInsideMessage(zmsg_t *zmsg, riaps::ports::PortBase *port) { }
    }
}
