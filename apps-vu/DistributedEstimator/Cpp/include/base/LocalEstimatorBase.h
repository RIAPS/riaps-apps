

#ifndef LOCALESTIMATORBASE_H
#define LOCALESTIMATORBASE_H

#include <pybind11/stl.h>
#include <pybind11/pybind11.h>
#include <componentmodel/r_componentbase.h>
#include <componentmodel/r_messagebuilder.h>
#include <componentmodel/r_messagereader.h>
#include <messages/distributedestimator.capnp.h>

namespace py = pybind11;
constexpr auto PORT_REQ_QUERY = "query";
constexpr auto PORT_PUB_ESTIMATE = "estimate";
constexpr auto PORT_SUB_READY = "ready";


namespace distributedestimator {
    namespace components {
        class LocalEstimatorBase : public riaps::ComponentBase {
        public:
            LocalEstimatorBase(const py::object*  parent_actor     ,
                          const py::dict     actor_spec       ,
                          const py::dict     type_spec        ,
                          const std::string& name             ,
                          const std::string& type_name        ,
                          const py::dict     args             ,
                          const std::string& application_name ,
                          const std::string& actor_name       );

            virtual void OnQuery()=0;
            virtual void OnReady()=0;


            virtual std::tuple<MessageReader<messages::SensorValue>, riaps::ports::PortError> RecvQuery() final;

            virtual std::tuple<MessageReader<messages::SensorReady>, riaps::ports::PortError> RecvReady() final;

            virtual riaps::ports::PortError SendQuery(MessageBuilder<messages::SensorQuery>& message) final;
            virtual riaps::ports::PortError SendEstimate(MessageBuilder<messages::Estimate>& message) final;

            virtual ~LocalEstimatorBase() = default;
        protected:
            virtual void DispatchMessage(riaps::ports::PortBase* port) final;

            virtual void DispatchInsideMessage(zmsg_t* zmsg, riaps::ports::PortBase* port) final;
        };
    }
}


#endif // LOCALESTIMATORBASE_H
