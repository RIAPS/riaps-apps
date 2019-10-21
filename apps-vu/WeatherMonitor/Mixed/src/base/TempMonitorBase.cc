


#include <componentmodel/r_pyconfigconverter.h>
#include <base/TempMonitorBase.h>

using namespace std;
using namespace riaps::ports;

namespace weathermonitor {
    namespace components {
        TempMonitorBase::TempMonitorBase(const py::object*  parent_actor     ,
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

        tuple<MessageReader<messages::TempData>, PortError> TempMonitorBase::RecvTempupdate() {
            auto port = GetPortAs<riaps::ports::SubscriberPort>(PORT_SUB_TEMPUPDATE);
            auto [msg_bytes, error] = port->Recv();
            MessageReader<messages::TempData> reader(msg_bytes);
            return make_tuple(reader, error);
        }



        void TempMonitorBase::DispatchMessage(riaps::ports::PortBase* port) {
            auto port_name = port->port_name();
            if (port_name == PORT_SUB_TEMPUPDATE) {
                OnTempupdate();
            }
        }

        void TempMonitorBase::DispatchInsideMessage(zmsg_t *zmsg, riaps::ports::PortBase *port) { }
    }
}