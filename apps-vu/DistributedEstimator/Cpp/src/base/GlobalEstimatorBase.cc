



#include <componentmodel/r_pyconfigconverter.h>
#include <base/GlobalEstimatorBase.h>

using namespace std;
using namespace riaps::ports;

namespace distributedestimator {
    namespace components {
        GlobalEstimatorBase::GlobalEstimatorBase(const py::object*  parent_actor     ,
                          const py::dict     actor_spec       ,
                          const py::dict     type_spec        ,
                          const std::string& name             ,
                          const std::string& type_name        ,
                          const py::dict     args             ,
                          const std::string& application_name ,
                          const std::string& actor_name       ) : ComponentBase(application_name, actor_name){
            auto conf = PyConfigConverter::convert(type_spec, actor_spec, args);
            conf.component_name = name;
            conf.component_type = type_name;
            conf.is_device=false;
            set_config(conf);
        }

        tuple<MessageReader<messages::Estimate>, PortError> GlobalEstimatorBase::RecvEstimate() {
            auto port = GetPortAs<riaps::ports::SubscriberPort>(PORT_SUB_ESTIMATE);
            auto [msg_bytes, error] = port->Recv();
            MessageReader<messages::Estimate> reader(msg_bytes);
            return make_tuple(reader, error);
        }

        timespec GlobalEstimatorBase::RecvWakeup() {
            auto port = GetPortAs<riaps::ports::PeriodicTimer>(PORT_TIMER_WAKEUP);
            return port->Recv();
        }


        void GlobalEstimatorBase::DispatchMessage(riaps::ports::PortBase* port) {
            auto port_name = port->port_name();
            if (port_name == PORT_SUB_ESTIMATE) {
                OnEstimate();
            }
            if (port_name == PORT_TIMER_WAKEUP) {
                OnWakeup();
            }
        }

        void GlobalEstimatorBase::DispatchInsideMessage(zmsg_t *zmsg, riaps::ports::PortBase *port) { }
    }
}
