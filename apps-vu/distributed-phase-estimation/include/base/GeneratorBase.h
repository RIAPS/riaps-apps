

#ifndef RIAPS_CORE_GENERATORBASE_H
#define RIAPS_CORE_GENERATORBASE_H

#include <pybind11/stl.h>
#include <pybind11/pybind11.h>
#include <componentmodel/r_componentbase.h>
#include <componentmodel/r_messagebuilder.h>
#include <componentmodel/r_messagereader.h>
#include <messages/timertest.capnp.h>

namespace py = pybind11;
constexpr auto PORT_TIMER_CLOCK = "clock";
constexpr auto PORT_PUB_SIGNALVALUE = "signalValue";

namespace timertest {
    namespace components {

        class GeneratorBase : public riaps::ComponentBase {

        public:

            GeneratorBase(const py::object*  parent_actor     ,
                          const py::dict     actor_spec       ,
                          const py::dict     type_spec        ,
                          const std::string& name             ,
                          const std::string& type_name        ,
                          const py::dict     args             ,
                          const std::string& application_name ,
                          const std::string& actor_name       ,
                          const py::list groups               );

            virtual void OnClock()=0;
            virtual timespec RecvClock() final;

            virtual riaps::ports::PortError SendSignalValue(MessageBuilder<messages::SignalValue>& message);

            virtual ~GeneratorBase() = default;

        protected:

            virtual void DispatchMessage(riaps::ports::PortBase *port) final;

            virtual void DispatchInsideMessage(zmsg_t* zmsg,riaps::ports::PortBase* port) final;


        };
    }
}

#endif
