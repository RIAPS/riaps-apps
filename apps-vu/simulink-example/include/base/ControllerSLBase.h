

#ifndef CONTROLLERSLBASE_H
#define CONTROLLERSLBASE_H

#include <pybind11/stl.h>
#include <pybind11/pybind11.h>
#include <componentmodel/r_componentbase.h>
#include <componentmodel/r_messagebuilder.h>
#include <componentmodel/r_messagereader.h>
#include <messages/sltest.capnp.h>

namespace py = pybind11;
constexpr auto PORT_PUB_FORCE = "force";
constexpr auto PORT_SUB_POSITION = "position";


namespace sltest {
    namespace components {
        class ControllerSLBase : public riaps::ComponentBase {
        public:
            ControllerSLBase(const py::object*  parent_actor     ,
                          const py::dict     actor_spec       ,
                          const py::dict     type_spec        ,
                          const std::string& name             ,
                          const std::string& type_name        ,
                          const py::dict     args             ,
                          const std::string& application_name ,
                          const std::string& actor_name       ,
                          const py::list groups               );

            virtual void OnPosition()=0;


            virtual std::tuple<MessageReader<messages::Position>, riaps::ports::PortError> RecvPosition() final;

            virtual riaps::ports::PortError SendForce(MessageBuilder<messages::Force>& message) final;

            virtual ~ControllerSLBase() = default;
        protected:
            virtual void DispatchMessage(riaps::ports::PortBase* port) final;

            virtual void DispatchInsideMessage(zmsg_t* zmsg, riaps::ports::PortBase* port) final;
        };
    }
}


#endif // CONTROLLERSLBASE_H
