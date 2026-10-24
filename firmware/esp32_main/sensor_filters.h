#ifndef SENSOR_FILTERS_H
#define SENSOR_FILTERS_H

#include <Arduino.h>
#include "config.h"

// ------------------------------------------------------------------------------
// Median Filter: Samples ADC N times, sorts values, returns median
// Effectively eliminates random electrical noise spikes from nearby pumps/relays
// ------------------------------------------------------------------------------
inline int readMedianADC(int pin, int samples = 15) {
    if (samples < 3) samples = 3;
    if (samples > 31) samples = 31;
    
    int buffer[32];
    for (int i = 0; i < samples; i++) {
        buffer[i] = analogRead(pin);
        delay(10);
    }

    // Simple Insertion Sort
    for (int i = 1; i < samples; i++) {
        int key = buffer[i];
        int j = i - 1;
        while (j >= 0 && buffer[j] > key) {
            buffer[j + 1] = buffer[j];
            j = j - 1;
        }
        buffer[j + 1] = key;
    }

    // Return the middle value
    return buffer[samples / 2];
}

// ------------------------------------------------------------------------------
// Convert ADC counts to Millivolts (ESP32-S3 12-bit ADC with 3.3V reference)
// ------------------------------------------------------------------------------
inline float adcToVoltage(int adcRaw) {
    return (float)adcRaw * (ADC_REF_VOLTAGE / ADC_MAX_COUNT);
}

// ------------------------------------------------------------------------------
// Calculate pH from analog voltage with calibrated formula
// Formula: pH = -8.487 * Voltage + 29.59
// ------------------------------------------------------------------------------
inline float calculatePH(float voltage) {
    float ph = (PH_CALIB_SLOPE * voltage) + PH_CALIB_INTERCEPT;
    if (ph < 0.0f) ph = 0.0f;
    if (ph > 14.0f) ph = 14.0f;
    return ph;
}

// ------------------------------------------------------------------------------
// Calculate EC (mS/cm) with Temperature Compensation (standardized to 25°C)
// Standard formula: EC25 = EC_raw / (1.0 + 0.019 * (Temp - 25.0))
// ------------------------------------------------------------------------------
inline float calculateEC(float voltage, float waterTempC) {
    // Typical analog EC sensor conversion: (Voltage / 3.3) * max_range
    // Assuming standard 0-5 mS/cm industrial analog transmitter probe
    float rawEC = (voltage / 3.3f) * 4.5f; // Standard scaling
    if (rawEC < 0.0f) rawEC = 0.0f;

    // Apply temperature compensation
    float tempCoefficient = 1.0f + 0.019f * (waterTempC - 25.0f);
    if (tempCoefficient <= 0.1f) tempCoefficient = 0.1f;

    float ec25 = rawEC / tempCoefficient;
    return ec25;
}

#endif // SENSOR_FILTERS_H
