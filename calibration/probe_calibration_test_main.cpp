#include <iostream>

#include "probe_calibration.h"
#include "pressures_to_airdata.h"

int main(int argc, char** argv) {
  if (argc != 5) {
    std::cerr << "Usage: " << argv[0] << " dp0 dpa dpb raw_baro" << std::endl;
    return -1;
  }
  
  float dp0 = atof(argv[1]);
  float dpa = atof(argv[2]);
  float dpb = atof(argv[3]);
  float s = atof(argv[4]);

  int err = 0;

  airdata d = pressures_to_airdata(&probe_alpha,
				   &probe_beta,
				   &probe_q_over_dp0,
				   &probe_minus_s_over_dp0,
				   dp0,
				   dpa,
				   dpb,
				   s,
				   &err);

  if (err != 0) {
    return -1;
  }

  std::cout <<
    d.alpha << "," <<
    d.beta << "," <<
    d.q << "," <<
    d.p << std::endl;
}
