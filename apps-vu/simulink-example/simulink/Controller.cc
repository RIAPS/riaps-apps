/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * File: Controller.c
 *
 * Code generated for Simulink model 'Controller'.
 *
 * Model version                  : 1.7
 * Simulink Coder version         : 8.13 (R2017b) 24-Jul-2017
 * C/C++ source code generated on : Wed Apr 11 13:41:47 2018
 *
 * Target selection: ert.tlc
 * Embedded hardware selection: Intel->x86-64 (Windows64)
 * Code generation objectives:
 *    1. Debugging
 *    2. Traceability
 * Validation result: Passed (0), Warning (1), Error (0)
 */

#include "Controller.h"
#include "Controller_private.h"

/* Model step function */
void Controller_step(RT_MODEL_Controller_T *const Controller_M)
{
  B_Controller_T *Controller_B = ((B_Controller_T *) Controller_M->blockIO);
  DW_Controller_T *Controller_DW = ((DW_Controller_T *) Controller_M->dwork);
  ExtU_Controller_T *Controller_U = (ExtU_Controller_T *) Controller_M->inputs;
  ExtY_Controller_T *Controller_Y = (ExtY_Controller_T *) Controller_M->outputs;

  /* DiscretePulseGenerator: '<S1>/Target Position' */
  Controller_B->TargetPosition = (Controller_DW->clockTickCounter < 250) &&
    (Controller_DW->clockTickCounter >= 0) ? 0.5 : 0.0;
  if (Controller_DW->clockTickCounter >= 499) {
    Controller_DW->clockTickCounter = 0;
  } else {
    Controller_DW->clockTickCounter++;
  }

  /* End of DiscretePulseGenerator: '<S1>/Target Position' */

  /* Sum: '<S1>/Sum2' incorporates:
   *  Inport: '<Root>/Position '
   */
  Controller_B->Sum2 = Controller_B->TargetPosition - Controller_U->Position;

  /* Gain: '<S1>/Kp' */
  Controller_B->Kp = 792.0 * Controller_B->Sum2;

  /* DiscreteIntegrator: '<S1>/Discrete-Time Integrator' */
  Controller_B->DiscreteTimeIntegrator =
    Controller_DW->DiscreteTimeIntegrator_DSTATE;

  /* Gain: '<S1>/Kd' */
  Controller_B->Kd = 34.0 * Controller_B->Sum2;

  /* SampleTimeMath: '<S2>/TSamp'
   *
   * About '<S2>/TSamp':
   *  y = u * K where K = 1 / ( w * Ts )
   */
  Controller_B->TSamp = Controller_B->Kd * 100.0;

  /* UnitDelay: '<S2>/UD'
   *
   * Block description for '<S2>/UD':
   *
   *  Store in Global RAM
   */
  Controller_B->Uk1 = Controller_DW->UD_DSTATE;

  /* Sum: '<S2>/Diff'
   *
   * Block description for '<S2>/Diff':
   *
   *  Add in CPU
   */
  Controller_B->Diff = Controller_B->TSamp - Controller_B->Uk1;

  /* Outport: '<Root>/Force' incorporates:
   *  Sum: '<S1>/Sum1'
   */
  Controller_Y->Force = (Controller_B->Kp + Controller_B->DiscreteTimeIntegrator)
    + Controller_B->Diff;

  /* Gain: '<S1>/Ki' */
  Controller_B->Ki = 4545.0 * Controller_B->Sum2;

  /* Update for DiscreteIntegrator: '<S1>/Discrete-Time Integrator' */
  Controller_DW->DiscreteTimeIntegrator_DSTATE += 0.01 * Controller_B->Ki;

  /* Update for UnitDelay: '<S2>/UD'
   *
   * Block description for '<S2>/UD':
   *
   *  Store in Global RAM
   */
  Controller_DW->UD_DSTATE = Controller_B->TSamp;
}

/* Model initialize function */
void Controller_initialize(RT_MODEL_Controller_T *const Controller_M)
{
  DW_Controller_T *Controller_DW = ((DW_Controller_T *) Controller_M->dwork);
  B_Controller_T *Controller_B = ((B_Controller_T *) Controller_M->blockIO);
  ExtU_Controller_T *Controller_U = (ExtU_Controller_T *) Controller_M->inputs;
  ExtY_Controller_T *Controller_Y = (ExtY_Controller_T *) Controller_M->outputs;

  /* Registration code */

  /* block I/O */
  (void) memset(((void *) Controller_B), 0,
                sizeof(B_Controller_T));

  /* states (dwork) */
  (void) memset((void *)Controller_DW, 0,
                sizeof(DW_Controller_T));

  /* external inputs */
  Controller_U->Position = 0.0;

  /* external outputs */
  Controller_Y->Force = 0.0;

  /* InitializeConditions for DiscretePulseGenerator: '<S1>/Target Position' */
  Controller_DW->clockTickCounter = -3;
}

/* Model terminate function */
void Controller_terminate(RT_MODEL_Controller_T *const Controller_M)
{
  /* (no terminate code required) */
  UNUSED_PARAMETER(Controller_M);
}

/*
 * File trailer for generated code.
 *
 * [EOF]
 */
