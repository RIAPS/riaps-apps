

#ifndef SENSORBASE_H
#define SENSORBASE_H

#include <pybind11/stl.h>
#include <pybind11/pybind11.h>
#include <componentmodel/r_componentbase.h>
#include <componentmodel/r_messagebuilder.h>
#include <componentmodel/r_messagereader.h>
#include <messages/sltest.capnp.h>

namespace py = pybind11;
constexpr auto PORT_PUB_POSITION = "position";
constexpr auto PORT_TIMER_CLOCK = "clock";


namespace sltest {
    namespace components {
        class SensorBase : public riaps::ComponentBase {
        public:
            SensorBase(const py::object*  parent_actor     ,
                          const py::dict     actor_spec       ,
                          const py::dict     type_spec        ,
                          const std::string& name             ,
                          const std::string& type_name        ,
                          const py::dict     args             ,
                          const std::string& application_name ,
                          const std::string& actor_name       );

            virtual void OnClock()=0;

            virtual timespec RecvClock() final;

            virtual riaps::ports::PortError SendPosition(MessageBuilder<messages::Position>& message) final;

            virtual ~SensorBase() = default;
        protected:
            virtual void DispatchMessage(riaps::ports::PortBase* port) final;

            virtual void DispatchInsideMessage(zmsg_t* zmsg, riaps::ports::PortBase* port) final;
        };
    }
}


#endif // SENSORBASE_H
