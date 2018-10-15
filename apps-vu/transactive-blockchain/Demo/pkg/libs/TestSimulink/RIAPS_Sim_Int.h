/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * File: RIAPS_Sim_Int.h
 *
 * Code generated for Simulink model 'RIAPS_Sim_Int'.
 *
 * Model version                  : 1.7
 * Simulink Coder version         : 8.12 (R2017a) 16-Feb-2017
 * C/C++ source code generated on : Thu Jul 12 13:06:01 2018
 *
 * Target selection: ert.tlc
 * Embedded hardware selection: AMD->x86-64 (Linux 64)
 * Code generation objectives:
 *    1. Execution efficiency
 *    2. RAM efficiency
 * Validation result: Not run
 */

#ifndef RTW_HEADER_RIAPS_Sim_Int_h_
#define RTW_HEADER_RIAPS_Sim_Int_h_
#ifndef RIAPS_Sim_Int_COMMON_INCLUDES_
# define RIAPS_Sim_Int_COMMON_INCLUDES_
#include "rtwtypes.h"
#endif                                 /* RIAPS_Sim_Int_COMMON_INCLUDES_ */

/* Macros for accessing real-time model data structure */

/* Block signals and states (auto storage) for system '<Root>' */
typedef struct {
  real_T PrevAggrEng_DSTATE;           /* '<Root>/PrevAggrEng' */
} DW;

/* Block signals and states (auto storage) */
extern DW rtDW;

/* Model entry point functions */
extern void RIAPS_Sim_Int_initialize(void);

/* Customized model step function */
extern real_T RIAPS_Sim_Int_step(real_T arg_InstEng);

/*-
 * These blocks were eliminated from the model due to optimizations:
 *
 * Block '<Root>/Scope' : Unused code path elimination
 */

/*-
 * The generated code includes comments that allow you to trace directly
 * back to the appropriate location in the model.  The basic format
 * is <system>/block_name, where system is the system number (uniquely
 * assigned by Simulink) and block_name is the name of the block.
 *
 * Use the MATLAB hilite_system command to trace the generated code back
 * to the model.  For example,
 *
 * hilite_system('<S3>')    - opens system 3
 * hilite_system('<S3>/Kp') - opens and selects block Kp which resides in S3
 *
 * Here is the system hierarchy for this model
 *
 * '<Root>' : 'RIAPS_Sim_Int'
 */
#endif                                 /* RTW_HEADER_RIAPS_Sim_Int_h_ */

/*
 * File trailer for generated code.
 *
 * [EOF]
 */
