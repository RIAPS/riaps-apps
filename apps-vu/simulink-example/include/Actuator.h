

#ifndef ACTUATOR_H
#define ACTUATOR_H
#include <base/ActuatorBase.h>
// riaps:keep_header:begin

// riaps:keep_header:end>>

namespace sltest {
    namespace components {
        class Actuator : public ActuatorBase {
        public:
            Actuator(const py::object*  parent_actor     ,
                          const py::dict     actor_spec       ,
                          const py::dict     type_spec        ,
                          const std::string& name             ,
                          const std::string& type_name        ,
                          const py::dict     args             ,
                          const std::string& application_name ,
                          const std::string& actor_name       ,
                          const py::list groups               );


            virtual void OnForce() override;

            virtual ~Actuator();

            // riaps:keep_decl:begin
        private:

            int sockfd=-1;
            addrinfo hints;
            addrinfo* res=0;

            // riaps:keep_decl:end
        };
    }
}

std::unique_ptr<sltest::components::Actuator>
create_component_py(const py::object *parent_actor,
                    const py::dict actor_spec,
                    const py::dict type_spec,
                    const std::string &name,
                    const std::string &type_name,
                    const py::dict args,
                    const std::string &application_name,
                    const std::string &actor_name,
                    const py::list groups);

#endif // ACTUATOR_H
