

#ifndef GLOBALESTIMATOR_H
#define GLOBALESTIMATOR_H
#include <base/GlobalEstimatorBase.h>
// riaps:keep_header:begin

// riaps:keep_header:end>>

namespace distributedestimator {
    namespace components {
        class GlobalEstimator : public GlobalEstimatorBase {
        public:
            GlobalEstimator(const py::object*  parent_actor     ,
                          const py::dict     actor_spec       ,
                          const py::dict     type_spec        ,
                          const std::string& name             ,
                          const std::string& type_name        ,
                          const py::dict     args             ,
                          const std::string& application_name ,
                          const std::string& actor_name       );


            virtual void OnEstimate() override;
            virtual void OnWakeup() override;

            virtual ~GlobalEstimator();

            // riaps:keep_decl:begin

            // riaps:keep_decl:end
        };
    }
}

std::unique_ptr<distributedestimator::components::GlobalEstimator>
create_component_py(const py::object *parent_actor,
                    const py::dict actor_spec,
                    const py::dict type_spec,
                    const std::string &name,
                    const std::string &type_name,
                    const py::dict args,
                    const std::string &application_name,
const std::string &actor_name);

#endif // GLOBALESTIMATOR_H
