#ifndef CONFIG_H
#define CONFIG_H

#include <Arduino.h>

// ==============================================================================
// 1. Wi-Fi & Central Server Network Configuration
// ==============================================================================
#define WIFI_SSID           "YOUR_WIFI_SSID"
#define WIFI_PASSWORD       "YOUR_WIFI_PASSWORD" // <-- Replace with your Wi-Fi password
#define SERVER_HOST         "192.168.1.100"      // Central PC IP running main.py (FastAPI)
#define SERVER_PORT         8000
#define DEVICE_ID           "esp32-s3-demo-box-01"

// API Endpoints
#define URL_TELEMETRY       "http://" SERVER_HOST ":8000/api/sensor"
#define URL_POLL_COMMAND    "http://" SERVER_HOST ":8000/api/command"
#define URL_UPDATE_STATUS   "http://" SERVER_HOST ":8000/api/status"

// ==============================================================================
// 2. Sensor Pinout Configuration (ESP32-S3 N16R8)
// ==============================================================================
#define PIN_PH_SENSOR       1   // GPIO 1: ADC1_CH0 (12-bit ADC, 0-4095)
#define PIN_EC_SENSOR       2   // GPIO 2: ADC1_CH1 (12-bit ADC, 0-4095)
#define PIN_TEMP_ONEWIRE    4   // GPIO 4: DS18B20 Digital OneWire bus (requires 4.7kΩ pullup)

// ==============================================================================
// 3. Actuator Relay Pinout Configuration (7-Relay Architecture - Active LOW)
// ==============================================================================
// Relay Logic Level (Most standard relay boards are Active-LOW)
#define RELAY_ON            HIGH
#define RELAY_OFF           LOW

// Diaphragm Sampling & Probe Maintenance Pumps (12V)
#define PIN_RELAY_SAMPLE_IN      5   // Diaphragm 1: Draw culture water into measuring cup
#define PIN_RELAY_SAMPLE_RETURN  6   // Diaphragm 2: Return sampled water back to plant box
#define PIN_RELAY_PROBE_RINSE    7   // Diaphragm 3: Clean water to rinse/store probes

// Electric Solenoid Valve (12V)
#define PIN_RELAY_VALVE_DRAIN    8   // Solenoid Valve: Drain rinse wastewater out of system

// Peristaltic Nutrient Dosing Pumps (12V)
#define PIN_RELAY_PERISTALTIC_1  9   // Peristaltic 1: Formula 1 (Nitrogen / Stock A)
#define PIN_RELAY_PERISTALTIC_2  10  // Peristaltic 2: Formula 2 (Phosphorus / Stock B)
#define PIN_RELAY_PERISTALTIC_3  11  // Peristaltic 3: Formula 3 (Potassium / Stock C)

// ==============================================================================
// 4. Default Phase Timings & Safety Watchdogs (in Milliseconds)
// ==============================================================================
#define TIME_SAMPLE_IN_MS        6000    // 6 seconds to fill measuring cup to probe level
#define TIME_SETTLING_DELAY_MS   3000    // 3 seconds wait for water to stabilize before ADC read
#define TIME_SAMPLE_RETURN_MS    7000    // 7 seconds to pump water back into main box
#define TIME_RINSE_PROBE_MS      5000    // 5 seconds rinse with clean water
#define TIME_DRAIN_VALVE_MS      6000    // 6 seconds open solenoid valve to drain wash water
#define TIME_PRE_CIRCULATION_MS  120000  // 2 minutes pre-circulation delay for water mixing
#define TIME_POST_CIRCULATION_MS 300000  // 5 minutes post-dosing circulation delay before re-verify

// Hardware Safety Guardrails
#define MAX_SAFETY_DOSING_MS     25000   // Hard cutoff: No dosing pump may run > 25 seconds
#define MAX_SAFETY_PUMP_MS       15000   // Hard cutoff for sampling pumps
#define HARD_MAX_EC_MS_CM        3.5     // If EC exceeds 3.5 mS/cm, abort all nutrient dosing
#define HARD_MIN_PH              4.0     // Extreme acidity safety lockout

// Calibration Constants (Derived from experimental handoff calibration)
// Formula: pH = -8.487 * Voltage + 29.59
#define PH_CALIB_SLOPE          -8.487f
#define PH_CALIB_INTERCEPT       29.59f
#define ADC_REF_VOLTAGE          3.3f
#define ADC_MAX_COUNT            4095.0f

#endif // CONFIG_H
