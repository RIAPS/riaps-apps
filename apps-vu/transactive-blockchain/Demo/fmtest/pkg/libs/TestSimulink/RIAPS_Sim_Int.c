/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * File: RIAPS_Sim_Int.c
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

#include "RIAPS_Sim_Int.h"

/* Block signals and states (auto storage) */
DW rtDW;

/* Model step function */
real_T RIAPS_Sim_Int_step(real_T arg_InstEng)
{
  real_T rtb_Sum;

  /* specified return value */
  real_T arg_AggrEng;

  /* Sum: '<Root>/Sum' incorporates:
   *  Inport: '<Root>/InstEng'
   *  UnitDelay: '<Root>/PrevAggrEng'
   */
  rtb_Sum = rtDW.PrevAggrEng_DSTATE + arg_InstEng;

  /* Outport: '<Root>/AggrEng' */
  arg_AggrEng = rtb_Sum;

  /* Update for UnitDelay: '<Root>/PrevAggrEng' */
  rtDW.PrevAggrEng_DSTATE = rtb_Sum;
  return arg_AggrEng;
}

/* Model initialize function */
void RIAPS_Sim_Int_initialize(void)
{
  /* (no initialization code required) */
}

/*
 * File trailer for generated code.
 *
 * [EOF]
 */
