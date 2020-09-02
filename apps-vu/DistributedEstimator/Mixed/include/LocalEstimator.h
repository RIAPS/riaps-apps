

#ifndef LOCALESTIMATOR_H
#define LOCALESTIMATOR_H
#include <base/LocalEstimatorBase.h>
// riaps:keep_header:begin

// riaps:keep_header:end>>

namespace distributedestimator {
    namespace components {
        class LocalEstimator : public LocalEstimatorBase {
        public:
            LocalEstimator(const py::object*  parent_actor     ,
                           const py::dict     actor_spec       ,
                           const py::dict     type_spec        ,
                           const std::string& name             ,
                           const std::string& type_name        ,
                           const py::dict     args             ,
                           const std::string& application_name ,
                           const std::string& actor_name       ,
                           const py::list groups               );


            virtual void OnQuery() override;
            virtual void OnReady() override;

            virtual ~LocalEstimator();

            // riaps:keep_decl:begin
            virtual void HandlePeerStateChange(const std::string& state, const std::string& uuid) override;
            // riaps:keep_decl:end
        };
    }
}

std::unique_ptr<distributedestimator::components::LocalEstimator>
create_component_py(const py::object *parent_actor,
                    const py::dict actor_spec,
                    const py::dict type_spec,
                    const std::string &name,
                    const std::string &type_name,
                    const py::dict args,
                    const std::string &application_name,
                    const std::string &actor_name,
                    const py::list groups);

#endif // LOCALESTIMATOR_H
