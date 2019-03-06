

#ifndef CONTROLLERSL_H
#define CONTROLLERSL_H
#include <base/ControllerSLBase.h>
// riaps:keep_header:begin
#include "../simulink/Controller.h"
// riaps:keep_header:end>>

namespace sltest {
    namespace components {
        class ControllerSL : public ControllerSLBase {
        public:
            ControllerSL(const py::object*  parent_actor     ,
                          const py::dict     actor_spec       ,
                          const py::dict     type_spec        ,
                          const std::string& name             ,
                          const std::string& type_name        ,
                          const py::dict     args             ,
                          const std::string& application_name ,
                          const std::string& actor_name       );


            virtual void OnPosition() override;

            virtual ~ControllerSL();

            // riaps:keep_decl:begin
        private:
            RT_MODEL_Controller_T Controller_M_;
            RT_MODEL_Controller_T *const Controller_M = &Controller_M_;/* Real-time model */
            B_Controller_T Controller_B;    /* Observable signals */
            DW_Controller_T Controller_DW;  /* Observable states */
            ExtU_Controller_T Controller_U; /* External inputs */
            ExtY_Controller_T Controller_Y; /* External outputs */


            void rt_OneStep(RT_MODEL_Controller_T *const Controller_M);
            // riaps:keep_decl:end
        };
    }
}

std::unique_ptr<sltest::components::ControllerSL>
create_component_py(const py::object *parent_actor,
                    const py::dict actor_spec,
                    const py::dict type_spec,
                    const std::string &name,
                    const std::string &type_name,
                    const py::dict args,
                    const std::string &application_name,
const std::string &actor_name);

#endif // CONTROLLERSL_H
