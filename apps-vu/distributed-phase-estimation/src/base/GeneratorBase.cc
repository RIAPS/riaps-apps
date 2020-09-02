//
// Created by istvan on 3/10/17.
//

#include <base/GeneratorBase.h>
#include <componentmodel/r_pyconfigconverter.h>

using namespace std;
using namespace riaps::ports;

namespace timertest {
    namespace components {

        GeneratorBase::GeneratorBase(const py::object *parent_actor,
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

        void GeneratorBase::DispatchMessage(riaps::ports::PortBase *port) {
            auto port_name = port->port_name();
            if (port_name == PORT_TIMER_CLOCK) {
                OnClock();
            }
        }

        timespec GeneratorBase::RecvClock() {
            auto port = GetPortAs<riaps::ports::PeriodicTimer>(PORT_TIMER_CLOCK);
            return port->Recv();
        }

        void GeneratorBase::DispatchInsideMessage(zmsg_t* zmsg,riaps::ports::PortBase* port){}

        riaps::ports::PortError GeneratorBase::SendSignalValue(MessageBuilder<messages::SignalValue>& message) {
            return SendMessageOnPort(message.capnp_builder(), PORT_PUB_SIGNALVALUE);
        }
    }
}
