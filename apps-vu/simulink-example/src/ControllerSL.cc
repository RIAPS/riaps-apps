


#include <ControllerSL.h>
// riaps:keep_header:begin

// riaps:keep_header:end

namespace sltest {
    namespace components {

        // riaps:keep_construct:begin
        ControllerSL::ControllerSL(const py::object*  parent_actor     ,
                      const py::dict     actor_spec       ,
                      const py::dict     type_spec        ,
                      const std::string& name             ,
                      const std::string& type_name        ,
                      const py::dict     args             ,
                      const std::string& application_name ,
                      const std::string& actor_name       ,
                      const py::list groups)
            : ControllerSLBase(parent_actor, actor_spec, type_spec, name, type_name, args, application_name, actor_name, groups) {

        	/* Pack model data into RTM */
            Controller_M->blockIO = &Controller_B;
            Controller_M->dwork = &Controller_DW;
            Controller_M->inputs = &Controller_U;
            Controller_M->outputs = &Controller_Y;

            /* Initialize model */
            Controller_initialize(Controller_M);
            component_logger()->info("constructor finished");

        }
        // riaps:keep_construct:end

        void ControllerSL::OnPosition(){
            // riaps:keep_onposition:begin
            auto [msg, err] = RecvPosition();
        	Controller_M->inputs->Position = msg->getPosition();
        	rt_OneStep(Controller_M);

        	MessageBuilder<messages::Force> builder;
        	builder->setForce(Controller_M->outputs->Force);
        	auto pub_error = SendForce(builder);
        	if (pub_error){
        		component_logger()->warn("Error publishing force: {}, errorcode: {}", __func__, pub_error.error_code());
        	}
            // riaps:keep_onposition:end
        }

        // riaps:keep_impl:begin
    	void ControllerSL::rt_OneStep(RT_MODEL_Controller_T *const Controller_M) {
    		static boolean_T OverrunFlag = false;

    		/* Disable interrupts here */

    		/* Check for overrun */
    		if (OverrunFlag) {
    			rtmSetErrorStatus(Controller_M, "Overrun");
    			return;
    		}

    		OverrunFlag = true;

    		/* Save FPU context here (if necessary) */
    		/* Re-enable timer or interrupt here */
    		/* Set model inputs here */

    		/* Step the model */
    		Controller_step(Controller_M);

    		/* Get model outputs here */

    		/* Indicate task complete */
    		OverrunFlag = false;

    		/* Disable interrupts here */
    		/* Restore FPU context here (if necessary) */
    		/* Enable interrupts here */
    	}
        // riaps:keep_impl:end

        // riaps:keep_destruct:begin
        ControllerSL::~ControllerSL() {

        }
        // riaps:keep_destruct:end

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
                    const std::string &actor_name,
                    const py::list groups) {
    auto ptr = new sltest::components::ControllerSL(parent_actor, actor_spec, type_spec, name, type_name, args,
                                                                     application_name,
                                                                     actor_name,
                                                                     groups);
    return std::move(std::unique_ptr<sltest::components::ControllerSL>(ptr));
}

PYBIND11_MODULE(libcontrollersl, m) {
    py::class_<sltest::components::ControllerSL> testClass(m, "ControllerSL");
    testClass.def(py::init<const py::object*, const py::dict, const py::dict, const std::string&, const std::string&, const py::dict, const std::string&, const std::string&, const py::list>());

    testClass.def("setup"                 , &sltest::components::ControllerSL::Setup);
    testClass.def("activate"              , &sltest::components::ControllerSL::Activate);
    testClass.def("terminate"             , &sltest::components::ControllerSL::Terminate);
    testClass.def("handlePortUpdate"      , &sltest::components::ControllerSL::HandlePortUpdate);
    testClass.def("handleCPULimit"        , &sltest::components::ControllerSL::HandleCPULimit);
    testClass.def("handleMemLimit"        , &sltest::components::ControllerSL::HandleMemLimit);
    testClass.def("handleSpcLimit"        , &sltest::components::ControllerSL::HandleSpcLimit);
    testClass.def("handleNetLimit"        , &sltest::components::ControllerSL::HandleNetLimit);
    testClass.def("handleNICStateChange"  , &sltest::components::ControllerSL::HandleNICStateChange);
    testClass.def("handlePeerStateChange" , &sltest::components::ControllerSL::HandlePeerStateChange);
    testClass.def("handleReinstate"       , &sltest::components::ControllerSL::HandleReinstate);
    testClass.def("handleActivate"        , &sltest::components::ControllerSL::HandleActivate);

    m.def("create_component_py", &create_component_py, "Instantiates the component from python configuration");
}
