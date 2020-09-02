

#ifndef RIAPS_CORE_RECEIVERBASE_H
#define RIAPS_CORE_RECEIVERBASE_H

#include <pybind11/stl.h>
#include <pybind11/pybind11.h>
#include <componentmodel/r_componentbase.h>
#include <componentmodel/r_messagebuilder.h>
#include <componentmodel/r_messagereader.h>
#include <messages/timertest.capnp.h>

namespace py = pybind11;

constexpr auto PORT_SUB_SIGNALVALUE = "signalValue";

namespace timertest {
    namespace components {

        class ReceiverBase : public riaps::ComponentBase {

        public:

            ReceiverBase(const py::object *parent_actor,
                         const py::dict actor_spec, // Actor json config
                         const py::dict type_spec,  // component json config
                         const std::string &name,
                         const std::string &type_name,
                         const py::dict args,
                         const std::string &application_name,
                         const std::string &actor_name,
                         const py::list groups);

            virtual void OnSignalValue()=0;
            virtual std::tuple<MessageReader<messages::SignalValue>, riaps::ports::PortError> RecvSignalValue() final;


            virtual ~ReceiverBase() = default;

        protected:

            virtual void DispatchMessage(riaps::ports::PortBase *port) final;

            virtual void DispatchInsideMessage(zmsg_t* zmsg,riaps::ports::PortBase* port) final;


        };
    }
}

#endif
