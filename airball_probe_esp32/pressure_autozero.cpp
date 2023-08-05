#include "pressure_autozero.h"
#include <cmath>
#include <string>
#include <HardwareSerial.h>

extern HardwareSerial Serial;

// Number of readings to accumulate to compute a new autozero point.
constexpr int kAccumulatorReadings = 100;

// If the autozero offset for any pressure reading is greater than this
// value (in Pascals), then we cowardly decide not to perform autozero.
// This protects against an inflight autozero with non-zero data.
constexpr float kReasonableZeroOffset = 50.0;

constexpr char* kPrefsName = "autozero";
constexpr char* kPrefs0 = "dp0";
constexpr char* kPrefs1 = "dpa";
constexpr char* kPrefs2 = "dpb";

void println(const std::string &msg, const std::array<float, 3>& a) {
  Serial.print(msg.c_str());
  for (int i = 0; i < a.size(); i++) {
    Serial.print(" ");
    Serial.print(a[i]);
  }
  Serial.println();
}

std::array<float, 3>
operator+(const std::array<float, 3>& x, const std::array<float, 3>& y) {
  return {
      x[0] + y[0],
      x[1] + y[1],
      x[2] + y[2],
  };
}

std::array<float, 3>
operator*(const std::array<float, 3>& x, const float& y) {
  return {
      x[0] * y,
      x[1] * y,
      x[2] * y,
  };
}

std::array<float, 3>
fabs(const std::array<float, 3>& x) {
  return {
      fabs(x[0]),
      fabs(x[1]),
      fabs(x[2]),
  };
}

std::array<float, 3>
reduce(std::array<float, 3> accumulator) {
  return accumulator * (-1.0 / kAccumulatorReadings);
}

bool is_reasonable(std::array<float, 3> offsets) {
  auto magnitudes = fabs(offsets);
  for (auto i = magnitudes.begin(); i != magnitudes.end(); i++) {
    if (*i > kReasonableZeroOffset) {
      return false;
    }
  }
  return true;
}

PressureAutozero::PressureAutozero()
 : offsets_({ 0, 0, 0 }),
   accumulating_(true),
   accumulated_points_(0),
   accumulator_({ 0, 0, 0 }) {
   }

void
PressureAutozero::begin() {
  preferences_.begin(kPrefsName);
  auto candidate_offsets = load();
  if (is_reasonable(candidate_offsets)) {
    offsets_ = candidate_offsets;
    println("Starting with loaded offsets: ", offsets_);
  } else {
    println("Starting with default offsets: ", offsets_);
  }
}

std::array<float, 3>
PressureAutozero::load() {
  std::array<float, 3> offsets = {
      preferences_.getFloat(kPrefs0, 0.0f),
      preferences_.getFloat(kPrefs1, 0.0f),
      preferences_.getFloat(kPrefs2, 0.0f),
  };
  println("Read from preferences: ", offsets);
  return offsets;
}

void
PressureAutozero::store(std::array<float, 3> offsets) {
  preferences_.putFloat(kPrefs0, offsets[0]);
  preferences_.putFloat(kPrefs1, offsets[1]);
  preferences_.putFloat(kPrefs2, offsets[2]);
  println("Wrote to preferences: ", offsets);
}

std::array<float, 3>
PressureAutozero::autozero(std::array<float, 3> input) {
  if (accumulating_) {
    accumulator_ = accumulator_ + input;
    accumulated_points_++;

    if (accumulated_points_ == kAccumulatorReadings) {
      accumulating_ = false;
      auto candidate_offsets = reduce(accumulator_);
      if (is_reasonable(candidate_offsets)) {
        offsets_ = candidate_offsets;
        println("Calculated new offsets: ", offsets_);
        store(offsets_);
      }
    }
  }

  return input + offsets_;
}
