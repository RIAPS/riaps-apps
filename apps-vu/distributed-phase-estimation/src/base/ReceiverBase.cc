//
// Created by istvan on 3/10/17.
//

#include <base/ReceiverBase.h>
#include <componentmodel/r_pyconfigconverter.h>

using namespace std;

namespace timertest {
    namespace components {

        ReceiverBase::ReceiverBase(const py::object *parent_actor,
                                   const py::dict actor_spec, // Actor json config
                                   const py::dict type_spec,  // component json config
                                   const std::string &name,
                                   const std::string &type_name,
                                   const py::dict args,
                                   const std::string &application_name,
                                   const std::string &actor_name,
                                   const py::list groups)
                : ComponentBase(application_name, actor_name) {
            auto conf = PyConfigConverter::convert(type_spec, actor_spec, args);
            auto gr = PyConfigConverter::ConvertGroups(groups);
            conf.component_name = name;
            conf.component_type = type_name;
            conf.is_device=false;
            set_config(conf,gr);
        }

        std::tuple<MessageReader<messages::SignalValue>, riaps::ports::PortError> ReceiverBase::RecvSignalValue() {
            auto port = GetPortAs<riaps::ports::RequestPort>(PORT_SUB_SIGNALVALUE);
            auto [msg_bytes, error] = port->Recv();
            MessageReader<messages::SignalValue> reader(msg_bytes);
            return make_tuple(reader, error);
        }

        void ReceiverBase::DispatchMessage(riaps::ports::PortBase *port) {
            auto port_name = port->port_name();
            if (port_name == PORT_SUB_SIGNALVALUE) {
                OnSignalValue();
            }
        }

        void ReceiverBase::DispatchInsideMessage(zmsg_t* zmsg,riaps::ports::PortBase* port){}

    }
}
