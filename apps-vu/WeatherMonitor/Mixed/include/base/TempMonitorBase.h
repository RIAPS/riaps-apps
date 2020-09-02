

#ifndef TEMPMONITORBASE_H
#define TEMPMONITORBASE_H

#include <pybind11/stl.h>
#include <pybind11/pybind11.h>
#include <componentmodel/r_componentbase.h>
#include <componentmodel/r_messagebuilder.h>
#include <componentmodel/r_messagereader.h>
#include <messages/weathermonitor.capnp.h>

namespace py = pybind11;
constexpr auto PORT_SUB_TEMPUPDATE = "tempupdate";


namespace weathermonitor {
    namespace components {
        class TempMonitorBase : public riaps::ComponentBase {
        public:
            TempMonitorBase(const py::object*  parent_actor     ,
                          const py::dict     actor_spec       ,
                          const py::dict     type_spec        ,
                          const std::string& name             ,
                          const std::string& type_name        ,
                          const py::dict     args             ,
                          const std::string& application_name ,
                          const std::string& actor_name       ,
                          const py::list groups);

            virtual void OnTempupdate()=0;


            virtual std::tuple<MessageReader<messages::TempData>, riaps::ports::PortError> RecvTempupdate() final;


            virtual ~TempMonitorBase() = default;
        protected:
            virtual void DispatchMessage(riaps::ports::PortBase* port) final;

            virtual void DispatchInsideMessage(zmsg_t* zmsg, riaps::ports::PortBase* port) final;
        };
    }
}


#endif // TEMPMONITORBASE_H
