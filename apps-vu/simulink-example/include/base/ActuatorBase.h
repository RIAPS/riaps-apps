

#ifndef ACTUATORBASE_H
#define ACTUATORBASE_H

#include <pybind11/stl.h>
#include <pybind11/pybind11.h>
#include <componentmodel/r_componentbase.h>
#include <componentmodel/r_messagebuilder.h>
#include <componentmodel/r_messagereader.h>
#include <messages/sltest.capnp.h>

namespace py = pybind11;
constexpr auto PORT_SUB_FORCE = "force";


namespace sltest {
    namespace components {
        class ActuatorBase : public riaps::ComponentBase {
        public:
            ActuatorBase(const py::object*  parent_actor     ,
                          const py::dict     actor_spec       ,
                          const py::dict     type_spec        ,
                          const std::string& name             ,
                          const std::string& type_name        ,
                          const py::dict     args             ,
                          const std::string& application_name ,
                          const std::string& actor_name       );

            virtual void OnForce()=0;


            virtual std::tuple<MessageReader<messages::Force>, riaps::ports::PortError> RecvForce() final;


            virtual ~ActuatorBase() = default;
        protected:
            virtual void DispatchMessage(riaps::ports::PortBase* port) final;

            virtual void DispatchInsideMessage(zmsg_t* zmsg, riaps::ports::PortBase* port) final;
        };
    }
}


#endif // ACTUATORBASE_H
