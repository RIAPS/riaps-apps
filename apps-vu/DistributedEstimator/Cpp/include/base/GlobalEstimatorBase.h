

#ifndef GLOBALESTIMATORBASE_H
#define GLOBALESTIMATORBASE_H

#include <pybind11/stl.h>
#include <pybind11/pybind11.h>
#include <componentmodel/r_componentbase.h>
#include <componentmodel/r_messagebuilder.h>
#include <componentmodel/r_messagereader.h>
#include <messages/distributedestimator.capnp.h>

namespace py = pybind11;
constexpr auto PORT_SUB_ESTIMATE = "estimate";
constexpr auto PORT_TIMER_WAKEUP = "wakeup";


namespace distributedestimator {
    namespace components {
        class GlobalEstimatorBase : public riaps::ComponentBase {
        public:
            GlobalEstimatorBase(const py::object*  parent_actor     ,
                                const py::dict     actor_spec       ,
                                const py::dict     type_spec        ,
                                const std::string& name             ,
                                const std::string& type_name        ,
                                const py::dict     args             ,
                                const std::string& application_name ,
                                const std::string& actor_name       ,
                                const py::list groups               );

            virtual void OnEstimate()=0;
            virtual void OnWakeup()=0;


            virtual std::tuple<MessageReader<messages::Estimate>, riaps::ports::PortError> RecvEstimate() final;
            virtual timespec RecvWakeup() final;


            virtual ~GlobalEstimatorBase() = default;
        protected:
            virtual void DispatchMessage(riaps::ports::PortBase* port) final;

            virtual void DispatchInsideMessage(zmsg_t* zmsg, riaps::ports::PortBase* port) final;
        };
    }
}


#endif // GLOBALESTIMATORBASE_H
