#include "calibration_surface.h"

#if defined(__cplusplus)
extern "C"
{
#endif

typedef struct airdata_struct {
  float alpha;
  float beta;
  float q;
  float p;  
} airdata;

struct airdata_struct pressures_to_airdata(const calibration_surface* cs_alpha,
					   const calibration_surface* cs_beta,
					   const calibration_surface* cs_q_over_dp0,
					   const calibration_surface* cs_minus_s_over_dp0,
					   float dp0,
					   float dpa,
					   float dpb,
					   float raw_baro,
					   int* err);
  
#if defined(__cplusplus)
}
#endif
