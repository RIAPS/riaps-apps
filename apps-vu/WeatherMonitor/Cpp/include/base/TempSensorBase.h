

#ifndef TEMPSENSORBASE_H
#define TEMPSENSORBASE_H

#include <pybind11/stl.h>
#include <pybind11/pybind11.h>
#include <componentmodel/r_componentbase.h>
#include <componentmodel/r_messagebuilder.h>
#include <componentmodel/r_messagereader.h>
#include <messages/weathermonitor.capnp.h>

namespace py = pybind11;
constexpr auto PORT_PUB_READY = "ready";
constexpr auto PORT_TIMER_CLOCK = "clock";


namespace weathermonitor {
    namespace components {
        class TempSensorBase : public riaps::ComponentBase {
        public:
            TempSensorBase(const py::object*  parent_actor     ,
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

            virtual riaps::ports::PortError SendReady(MessageBuilder<messages::TempData>& message) final;

            virtual ~TempSensorBase() = default;
        protected:
            virtual void DispatchMessage(riaps::ports::PortBase* port) final;

            virtual void DispatchInsideMessage(zmsg_t* zmsg, riaps::ports::PortBase* port) final;
        };
    }
}


#endif // TEMPSENSORBASE_H
