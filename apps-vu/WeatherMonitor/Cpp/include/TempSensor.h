

#ifndef TEMPSENSOR_H
#define TEMPSENSOR_H
#include <base/TempSensorBase.h>
// riaps:keep_header:begin

// riaps:keep_header:end>>

namespace weathermonitor {
    namespace components {
        class TempSensor : public TempSensorBase {
        public:
            TempSensor(const py::object*  parent_actor     ,
                       const py::dict     actor_spec       ,
                       const py::dict     type_spec        ,
                       const std::string& name             ,
                       const std::string& type_name        ,
                       const py::dict     args             ,
                       const std::string& application_name ,
                       const std::string& actor_name       ,
                       const py::list groups               );


            virtual void OnClock() override;

            virtual ~TempSensor();

            // riaps:keep_decl:begin
            virtual void HandlePeerStateChange(const std::string& state, const std::string& uuid) override;

        private:
            double temperature;
            // riaps:keep_decl:end
        };
    }
}

std::unique_ptr<weathermonitor::components::TempSensor>
create_component_py(const py::object *parent_actor,
                    const py::dict actor_spec,
                    const py::dict type_spec,
                    const std::string &name,
                    const std::string &type_name,
                    const py::dict args,
                    const std::string &application_name,
                    const std::string &actor_name,
                    const py::list groups);

#endif // TEMPSENSOR_H
