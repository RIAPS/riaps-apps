/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * File: Controller.h
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

#ifndef RTW_HEADER_Controller_h_
#define RTW_HEADER_Controller_h_
#include <string.h>
#ifndef Controller_COMMON_INCLUDES_
# define Controller_COMMON_INCLUDES_
#include "rtwtypes.h"
#endif                                 /* Controller_COMMON_INCLUDES_ */

#include "Controller_types.h"
#include "rt_defines.h"

/* Macros for accessing real-time model data structure */
#ifndef rtmGetErrorStatus
# define rtmGetErrorStatus(rtm)        ((rtm)->errorStatus)
#endif

#ifndef rtmSetErrorStatus
# define rtmSetErrorStatus(rtm, val)   ((rtm)->errorStatus = (val))
#endif

/* Block signals (auto storage) */
typedef struct {
  real_T TargetPosition;               /* '<S1>/Target Position' */
  real_T Sum2;                         /* '<S1>/Sum2' */
  real_T Kp;                           /* '<S1>/Kp' */
  real_T DiscreteTimeIntegrator;       /* '<S1>/Discrete-Time Integrator' */
  real_T Kd;                           /* '<S1>/Kd' */
  real_T TSamp;                        /* '<S2>/TSamp' */
  real_T Uk1;                          /* '<S2>/UD' */
  real_T Diff;                         /* '<S2>/Diff' */
  real_T Ki;                           /* '<S1>/Ki' */
} B_Controller_T;

/* Block states (auto storage) for system '<Root>' */
typedef struct {
  real_T DiscreteTimeIntegrator_DSTATE;/* '<S1>/Discrete-Time Integrator' */
  real_T UD_DSTATE;                    /* '<S2>/UD' */
  int32_T clockTickCounter;            /* '<S1>/Target Position' */
} DW_Controller_T;

/* External inputs (root inport signals with auto storage) */
typedef struct {
  real_T Position;                     /* '<Root>/Position ' */
} ExtU_Controller_T;

/* External outputs (root outports fed by signals with auto storage) */
typedef struct {
  real_T Force;                        /* '<Root>/Force' */
} ExtY_Controller_T;

/* Real-time Model Data Structure */
struct tag_RTM_Controller_T {
  const char_T * volatile errorStatus;
  B_Controller_T *blockIO;
  ExtU_Controller_T *inputs;
  ExtY_Controller_T *outputs;
  DW_Controller_T *dwork;
};

/* Model entry point functions */
extern void Controller_initialize(RT_MODEL_Controller_T *const Controller_M);
extern void Controller_step(RT_MODEL_Controller_T *const Controller_M);
extern void Controller_terminate(RT_MODEL_Controller_T *const Controller_M);

/*-
 * These blocks were eliminated from the model due to optimizations:
 *
 * Block '<S2>/Data Type Duplicate' : Unused code path elimination
 * Block '<S1>/Rate Transition' : Eliminated since input and output rates are identical
 */

/*-
 * The generated code includes comments that allow you to trace directly
 * back to the appropriate location in the model.  The basic format
 * is <system>/block_name, where system is the system number (uniquely
 * assigned by Simulink) and block_name is the name of the block.
 *
 * Note that this particular code originates from a subsystem build,
 * and has its own system numbers different from the parent model.
 * Refer to the system hierarchy for this subsystem below, and use the
 * MATLAB hilite_system command to trace the generated code back
 * to the parent model.  For example,
 *
 * hilite_system('mass_spring_damper_net/Controller ')    - opens subsystem mass_spring_damper_net/Controller
 * hilite_system('mass_spring_damper_net/Controller /Kp') - opens and selects block Kp
 *
 * Here is the system hierarchy for this model
 *
 * '<Root>' : 'mass_spring_damper_net'
 * '<S1>'   : 'mass_spring_damper_net/Controller '
 * '<S2>'   : 'mass_spring_damper_net/Controller /Discrete Derivative'
 */

/*-
 * Requirements for '<Root>': Controller
 */
#endif                                 /* RTW_HEADER_Controller_h_ */

/*
 * File trailer for generated code.
 *
 * [EOF]
 */
