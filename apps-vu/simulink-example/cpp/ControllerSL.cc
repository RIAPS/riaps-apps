#include <ControllerSL.h>

namespace sltest {
  namespace components {

    ControllerSL::ControllerSL(_component_conf &config, riaps::Actor &actor)
        : ControllerSLBase(config, actor) {

        
            


      /* Pack model data into RTM */
      Controller_M->blockIO = &Controller_B;
      Controller_M->dwork = &Controller_DW;
      Controller_M->inputs = &Controller_U;
      Controller_M->outputs = &Controller_Y;

      /* Initialize model */
      Controller_initialize(Controller_M);
      _logger->info("{} constructor finished", GetComponentName());
    }

    void ControllerSL::OnPosition(const PositionType::Reader &message,
                                  riaps::ports::PortBase *port) {
        
            
        Controller_M->inputs->Position = message.getValue();        
        rt_OneStep(Controller_M);

        capnp::MallocMessageBuilder builder;
        auto msgForce = builder.initRoot<ForceType>();
        msgForce.setValue(Controller_M->outputs->Force);
        SendForce(builder, msgForce);
    }

    void
    ControllerSL::OnGroupMessage(const riaps::groups::GroupId &groupId,
                                 capnp::FlatArrayMessageReader &capnpreader,
                                 riaps::ports::PortBase *port) {}

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

    ControllerSL::~ControllerSL() {}
  } // namespace components
} // namespace sltest

riaps::ComponentBase *create_component(_component_conf &config,
                                       riaps::Actor &actor) {
  auto result = new sltest::components::ControllerSL(config, actor);
  return result;
}

void destroy_component(riaps::ComponentBase *comp) { delete comp; }
