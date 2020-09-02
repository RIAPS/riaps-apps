

#ifndef SENSORBASE_H
#define SENSORBASE_H

#include <pybind11/stl.h>
#include <pybind11/pybind11.h>
#include <componentmodel/r_componentbase.h>
#include <componentmodel/r_messagebuilder.h>
#include <componentmodel/r_messagereader.h>
#include <messages/distributedestimator.capnp.h>

namespace py = pybind11;
constexpr auto PORT_PUB_READY = "ready";
constexpr auto PORT_REP_REQUEST = "request";
constexpr auto PORT_TIMER_CLOCK = "clock";


namespace distributedestimator {
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
                       const std::string& actor_name       ,
                       const py::list groups               );

            virtual void OnRequest()=0;
            virtual void OnClock()=0;


            virtual std::tuple<MessageReader<messages::SensorQuery>, riaps::ports::PortError> RecvRequest() final;
            virtual timespec RecvClock() final;

            virtual riaps::ports::PortError SendReady(MessageBuilder<messages::SensorReady>& message) final;
            virtual riaps::ports::PortError SendRequest(MessageBuilder<messages::SensorValue>& message) final;

            virtual ~SensorBase() = default;
        protected:
            virtual void DispatchMessage(riaps::ports::PortBase* port) final;

            virtual void DispatchInsideMessage(zmsg_t* zmsg, riaps::ports::PortBase* port) final;
        };
    }
}


#endif // SENSORBASE_H
