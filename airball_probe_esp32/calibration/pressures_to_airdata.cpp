#include "pressures_to_airdata.h"
#include <math.h>

struct abs_sign {
  float abs;
  int sign;
};

abs_sign get(float x) {
  abs_sign r;
  r.abs = fabs(x);
  r.sign = x < 0 ? -1 : 1;
  return r;
}

struct airdata_struct pressures_to_airdata(const calibration_surface* cs_alpha,
					   const calibration_surface* cs_beta,
					   const calibration_surface* cs_q_over_dp0,
					   const calibration_surface* cs_minus_s_over_dp0,
					   float dp0,
					   float dpa,
					   float dpb,
					   float raw_baro,
					   int* err) {
  airdata r;

  abs_sign rpa = get(dpa / dp0);
  abs_sign rpb = get(dpb / dp0);
  
  r.alpha = interpolate(cs_alpha, rpa.abs, rpb.abs, err);
  r.alpha *= rpa.sign;
  
  r.beta = interpolate(cs_beta, rpa.abs, rpb.abs, err);
  r.beta *= rpb.sign;

  float q_over_dp0 = interpolate(cs_q_over_dp0, rpa.abs, rpb.abs, err);  
  r.q = dp0 * q_over_dp0;

  float minus_s_over_dp0 = interpolate(cs_minus_s_over_dp0, rpa.abs, rpb.abs, err);
  r.p = raw_baro + minus_s_over_dp0 * dp0;

  return r;  
}
