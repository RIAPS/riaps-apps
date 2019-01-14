

#ifndef TEMPMONITOR_H
#define TEMPMONITOR_H
#include <base/TempMonitorBase.h>
// riaps:keep_header:begin

// riaps:keep_header:end>>

namespace weathermonitor {
    namespace components {
        class TempMonitor : public TempMonitorBase {
        public:
            TempMonitor(const py::object*  parent_actor     ,
                          const py::dict     actor_spec       ,
                          const py::dict     type_spec        ,
                          const std::string& name             ,
                          const std::string& type_name        ,
                          const py::dict     args             ,
                          const std::string& application_name ,
                          const std::string& actor_name       );


            virtual void OnTempupdate() override;

            virtual ~TempMonitor();

            // riaps:keep_decl:begin
            virtual void HandlePeerStateChange(const std::string& state, const std::string& uuid) override;
            // riaps:keep_decl:end
        };
    }
}

std::unique_ptr<weathermonitor::components::TempMonitor>
create_component_py(const py::object *parent_actor,
                    const py::dict actor_spec,
                    const py::dict type_spec,
                    const std::string &name,
                    const std::string &type_name,
                    const py::dict args,
                    const std::string &application_name,
const std::string &actor_name);

#endif // TEMPMONITOR_H
