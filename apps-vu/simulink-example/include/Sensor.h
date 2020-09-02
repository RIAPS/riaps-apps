

#ifndef SENSOR_H
#define SENSOR_H
#include <base/SensorBase.h>
// riaps:keep_header:begin

// riaps:keep_header:end>>

namespace sltest {
    namespace components {
        class Sensor : public SensorBase {
        public:
            Sensor(const py::object*  parent_actor     ,
                          const py::dict     actor_spec       ,
                          const py::dict     type_spec        ,
                          const std::string& name             ,
                          const std::string& type_name        ,
                          const py::dict     args             ,
                          const std::string& application_name ,
                          const std::string& actor_name       ,
                          const py::list groups               );


            virtual void OnClock() override;

            virtual ~Sensor();

            // riaps:keep_decl:begin
        private:
            addrinfo hints;
            addrinfo* res=0;
            int socketfd=-1;
            // riaps:keep_decl:end
        };
    }
}

std::unique_ptr<sltest::components::Sensor>
create_component_py(const py::object *parent_actor,
                    const py::dict actor_spec,
                    const py::dict type_spec,
                    const std::string &name,
                    const std::string &type_name,
                    const py::dict args,
                    const std::string &application_name,
                    const std::string &actor_name,
                    const py::list groups);

#endif // SENSOR_H
