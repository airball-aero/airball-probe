#ifndef PRESSURE_AUTOZERO_H
#define PRESSURE_AUTOZERO_H

#include <array>
#include <Preferences.h>

class PressureAutozero {
public:
  PressureAutozero();

  void begin();

  std::array<float, 3> autozero(std::array<float, 3> input);
private:
  std::array<float, 3> load();
  void store(std::array<float, 3> offsets);

  Preferences preferences_;

  std::array<float, 3> offsets_;

  bool accumulating_;
  int accumulated_points_;
  std::array<float, 3> accumulator_;
};

#endif //PRESSURE_AUTOZERO_H
