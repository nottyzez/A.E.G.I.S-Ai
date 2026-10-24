/*
 * esp32_main.ino — Automated Hydroponic Presentation Station Firmware
 * Board: ESP32-S3 Dev Module / N16R8
 * Features:
 *   - Custom Measuring Chamber with pH, EC, and DS18B20 Temp
 *   - 7-Relay Control: 3 Diaphragm Pumps, 1 Drain Solenoid Valve, 3 Peristaltic Fertilizer Pumps
 *   - 6-Phase Non-blocking Automated Presentation State Machine
 *   - REST API Integration with FastAPI Server & Interactive Web Dashboard
 */

#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <OneWire.h>
#include <DallasTemperature.h>

#include "config.h"
#include "sensor_filters.h"
#include "actuator_controller.h"

// Hardware instances
OneWire oneWire(PIN_TEMP_ONEWIRE);
DallasTemperature tempSensors(&oneWire);
ActuatorController actuators;

// State and Timing
unsigned long lastCommandPollTime = 0;
const unsigned long COMMAND_POLL_INTERVAL_MS = 1500;

float latestPH = 6.20f;
float latestEC = 1.80f;
float latestTemp = 26.5f;

// ------------------------------------------------------------------------------
// WiFi Connection Helper
// ------------------------------------------------------------------------------
void connectWiFi() {
    Serial.printf("\nConnecting to Wi-Fi SSID: %s ", WIFI_SSID);
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    unsigned long startAttempt = millis();
    while (WiFi.status() != WL_CONNECTED && millis() - startAttempt < 10000) {
        delay(500);
        Serial.print(".");
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.println(" CONNECTED!");
        Serial.print("ESP32-S3 IP Address: ");
        Serial.println(WiFi.localIP());
    } else {
        Serial.println(" [TIMEOUT] Running in Offline / Testbench Mode.");
    }
}

// ------------------------------------------------------------------------------
// Sensor Measurement Routine
// ------------------------------------------------------------------------------
void performSensorReadings() {
    // 1. Read DS18B20 Water Temperature
    tempSensors.requestTemperatures();
    float t = tempSensors.getTempCByIndex(0);
    if (t > -50.0f && t < 80.0f) {
        latestTemp = t;
    } else {
        latestTemp = 26.0f; // Default room water temp fallback
    }

    // 2. Read pH Analog (Median Filter)
    int rawPH = readMedianADC(PIN_PH_SENSOR, 21);
    float vPH = adcToVoltage(rawPH);
    latestPH = calculatePH(vPH);

    // 3. Read EC Analog (Median Filter + Temperature Compensation)
    int rawEC = readMedianADC(PIN_EC_SENSOR, 21);
    float vEC = adcToVoltage(rawEC);
    latestEC = calculateEC(vEC, latestTemp);

    Serial.println("\n----------------------------------------");
    Serial.printf(" [MEASUREMENT READINGS] in Measuring Cup:\n");
    Serial.printf("   • Water Temp: %.2f °C\n", latestTemp);
    Serial.printf("   • Solution pH: %.2f (ADC: %d, %.3f V)\n", latestPH, rawPH, vPH);
    Serial.printf("   • EC Reading:  %.2f mS/cm (Temp-Compensated)\n", latestEC);
    Serial.println("----------------------------------------");
}

// ------------------------------------------------------------------------------
// HTTP API: Send Telemetry & Query Two-Tier Dosing Engine
// ------------------------------------------------------------------------------
bool sendTelemetryAndGetDosingPlan() {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("[HTTP] Wi-Fi not connected. Using default demo dosing (Pump 1: 5s, Pump 2: 5s).");
        actuators.dosePump1Ms = 5000;
        actuators.dosePump2Ms = 5000;
        actuators.dosePump3Ms = 2000;
        return true;
    }

    HTTPClient http;
    http.begin(URL_TELEMETRY);
    http.addHeader("Content-Type", "application/json");

    StaticJsonDocument<256> doc;
    doc["device_id"] = DEVICE_ID;
    doc["tank"] = "SingleDemoBox";
    doc["ec"] = latestEC;
    doc["ph"] = latestPH;
    doc["temp"] = latestTemp;
    doc["source"] = "esp32_measurement_cup";

    String requestBody;
    serializeJson(doc, requestBody);

    Serial.println("[HTTP] Uploading telemetry & querying Two-Tier Dosing Engine...");
    int httpResponseCode = http.POST(requestBody);

    if (httpResponseCode == 200) {
        String response = http.getString();
        StaticJsonDocument<512> resDoc;
        DeserializationError err = deserializeJson(resDoc, response);

        if (!err) {
            JsonObject dosing = resDoc["dosing_plan"];
            actuators.dosePump1Ms = dosing["pump1_ms"] | 0;
            actuators.dosePump2Ms = dosing["pump2_ms"] | 0;
            actuators.dosePump3Ms = dosing["pump3_ms"] | 0;

            const char* reason = resDoc["ai_reason"] | "Standard adjustment";
            const char* diagClass = resDoc["deficiency_class"] | "Balanced";

            Serial.printf(" [AI DOSING DIRECTIVE] Diagnosis: %s\n", diagClass);
            Serial.printf("   • AI Reasoning: %s\n", reason);
            Serial.printf("   • Pump 1 (N): %lu ms\n", actuators.dosePump1Ms);
            Serial.printf("   • Pump 2 (P): %lu ms\n", actuators.dosePump2Ms);
            Serial.printf("   • Pump 3 (K): %lu ms\n", actuators.dosePump3Ms);
            http.end();
            return true;
        }
    } else {
        Serial.printf("[HTTP ERROR] Telemetry POST failed with code: %d\n", httpResponseCode);
    }

    http.end();
    // Safe fallback dosing if server unreachable
    actuators.dosePump1Ms = 4000;
    actuators.dosePump2Ms = 4000;
    actuators.dosePump3Ms = 2000;
    return false;
}

// ------------------------------------------------------------------------------
// HTTP API: Report Current State to Server & Web Dashboard
// ------------------------------------------------------------------------------
void reportStatusToServer() {
    if (WiFi.status() != WL_CONNECTED) return;

    HTTPClient http;
    http.begin(URL_UPDATE_STATUS);
    http.addHeader("Content-Type", "application/json");

    StaticJsonDocument<256> doc;
    doc["phase"] = actuators.getPhaseName();
    doc["phase_id"] = (int)actuators.currentPhase;
    doc["ec"] = latestEC;
    doc["ph"] = latestPH;
    doc["temp"] = latestTemp;
    doc["uptime_sec"] = millis() / 1000;

    String body;
    serializeJson(doc, body);
    http.POST(body);
    http.end();
}

// ------------------------------------------------------------------------------
// HTTP API: Poll for Remote Dashboard Commands (e.g. "START_CYCLE")
// ------------------------------------------------------------------------------
void pollRemoteDashboardCommand() {
    if (WiFi.status() != WL_CONNECTED || actuators.currentPhase != PHASE_IDLE) return;

    HTTPClient http;
    http.begin(URL_POLL_COMMAND);
    int code = http.GET();

    if (code == 200) {
        String payload = http.getString();
        StaticJsonDocument<256> doc;
        if (!deserializeJson(doc, payload)) {
            const char* cmd = doc["command"] | "";
            if (strcmp(cmd, "START_CYCLE") == 0 || strcmp(cmd, "START_REFILL_CYCLE") == 0) {
                Serial.println("[REMOTE DASHBOARD] 'Start AI Cycle / Refill Cycle' command received!");
                actuators.startFullPresentationCycle();
            } else if (strcmp(cmd, "SKIP_CIRCULATION") == 0) {
                Serial.println("[REMOTE DASHBOARD] 'Skip Circulation' command received!");
                actuators.phaseStartTime = 0; // Trigger advance to next phase immediately
            } else if (strcmp(cmd, "READ_SENSORS") == 0) {
                Serial.println("[REMOTE DASHBOARD] 'Read Sensors' command received!");
                performSensorReadings();
                sendTelemetryAndGetDosingPlan();
                reportStatusToServer();
            } else if (strcmp(cmd, "MANUAL_RELAY") == 0) {
                int relay = doc["relay"] | 1;
                unsigned long dur = doc["duration_ms"] | 2000;
                actuators.manualTriggerRelay(relay, dur);
            } else if (strcmp(cmd, "STOP") == 0) {
                actuators.stopCycle();
            }
        }
    }
    http.end();
}

// ------------------------------------------------------------------------------
// Serial Command Interface (Terminal Testbench)
// ------------------------------------------------------------------------------
void handleSerialCommands() {
    if (Serial.available() > 0) {
        String input = Serial.readStringUntil('\n');
        input.trim();
        input.toUpperCase();

        if (input == "START" || input == "RUN") {
            actuators.startFullPresentationCycle();
        } else if (input == "STOP") {
            actuators.stopCycle();
        } else if (input.startsWith("TEST ")) {
            // Usage: TEST <Relay_1-7> <Duration_ms>
            int spaceIdx = input.indexOf(' ', 5);
            int relay = input.substring(5, spaceIdx > 0 ? spaceIdx : input.length()).toInt();
            unsigned long dur = (spaceIdx > 0) ? input.substring(spaceIdx + 1).toInt() : 2000;
            actuators.manualTriggerRelay(relay, dur);
        } else if (input == "READ") {
            performSensorReadings();
        } else {
            Serial.println("\nCommands: START (run full cycle) | STOP | READ | TEST <1-7> <ms>");
        }
    }
}

// ------------------------------------------------------------------------------
// Setup
// ------------------------------------------------------------------------------
void setup() {
    Serial.begin(115200);
    delay(1000);

    Serial.println("\n=======================================================");
    Serial.println("  🌱 HYDROSYNC: SINGLE-BOX DEMO AUTOMATION FIRMWARE");
    Serial.println("  Architecture: 3 Diaphragms + 1 Valve + 3 Peristaltics");
    Serial.println("=======================================================");

    // Initialize Relays & Pins
    actuators.initPins();

    // Physical BOOT Button (GPIO 0) for manual sensor reading
    pinMode(0, INPUT_PULLUP);

    // Initialize DS18B20
    tempSensors.begin();

    // Configure 12-bit ADC on ESP32-S3
    analogReadResolution(12);
    analogSetAttenuation(ADC_11db); // Full range ~0 - 3.1V

    // Connect WiFi
    connectWiFi();

    // Report initial ready status
    reportStatusToServer();
}

// ------------------------------------------------------------------------------
// Non-blocking Main Loop (FSM Execution)
// ------------------------------------------------------------------------------
void loop() {
    unsigned long now = millis();

    // Check Serial Inputs & Remote Dashboard Polling
    handleSerialCommands();

    // Check Physical BOOT Button (GPIO 0) for On-Demand Sensor Reading
    if (digitalRead(0) == LOW && actuators.currentPhase == PHASE_IDLE) {
        delay(50); // Debounce
        if (digitalRead(0) == LOW) {
            Serial.println("[BUTTON PRESSED] Physical BOOT button pressed -> Measuring sensors now!");
            performSensorReadings();
            sendTelemetryAndGetDosingPlan();
            reportStatusToServer();
            while (digitalRead(0) == LOW) delay(10); // Wait release
        }
    }

    if (now - lastCommandPollTime > COMMAND_POLL_INTERVAL_MS) {
        lastCommandPollTime = now;
        pollRemoteDashboardCommand();
    }

    // --------------------------------------------------------------------------
    // 6-Phase State Machine Transitions
    // --------------------------------------------------------------------------
    switch (actuators.currentPhase) {
        case PHASE_IDLE:
            // Standby waiting for dashboard or physical trigger
            break;

        case PHASE_1_SAMPLING_IN:
            // Check if sampling pump time elapsed
            if (now - actuators.phaseStartTime >= actuators.phaseDuration) {
                digitalWrite(PIN_RELAY_SAMPLE_IN, RELAY_OFF);
                Serial.println("[Phase 1 DONE] Measuring cup filled with sample water.");

                // Transition to Phase 2: Settling & Measuring
                actuators.setPhase(PHASE_2_MEASURING, TIME_SETTLING_DELAY_MS);
                Serial.printf("[Phase 2] Waiting %lu ms for water settling before reading...\n", TIME_SETTLING_DELAY_MS);
                reportStatusToServer();
            }
            break;

        case PHASE_2_MEASURING:
            if (now - actuators.phaseStartTime >= actuators.phaseDuration) {
                // Perform sensor readings
                performSensorReadings();

                // Send to Server & Get Two-Tier AI Dosing Plan
                sendTelemetryAndGetDosingPlan();

                // Transition to Phase 3: Sample Return
                actuators.setPhase(PHASE_3_SAMPLING_RETURN, TIME_SAMPLE_RETURN_MS);
                digitalWrite(PIN_RELAY_SAMPLE_RETURN, RELAY_ON);
                Serial.printf("[Phase 3] Diaphragm 2 (Sample RETURN) active for %lu ms\n", TIME_SAMPLE_RETURN_MS);
                reportStatusToServer();
            }
            break;

        case PHASE_3_SAMPLING_RETURN:
            if (now - actuators.phaseStartTime >= actuators.phaseDuration) {
                digitalWrite(PIN_RELAY_SAMPLE_RETURN, RELAY_OFF);
                Serial.println("[Phase 3 DONE] Sample water returned to culture tank.");

                // Transition to Phase 4: Two-Tier Dosing
                unsigned long maxDosingDuration = max(actuators.dosePump1Ms, max(actuators.dosePump2Ms, actuators.dosePump3Ms));
                actuators.setPhase(PHASE_4_DOSING, maxDosingDuration);

                // Fire peristaltic pumps according to AI calculated times
                if (actuators.dosePump1Ms > 0) digitalWrite(PIN_RELAY_PERISTALTIC_1, RELAY_ON);
                if (actuators.dosePump2Ms > 0) digitalWrite(PIN_RELAY_PERISTALTIC_2, RELAY_ON);
                if (actuators.dosePump3Ms > 0) digitalWrite(PIN_RELAY_PERISTALTIC_3, RELAY_ON);

                Serial.printf("[Phase 4] Peristaltic Dosing started (Max runtime %lu ms)\n", maxDosingDuration);
                reportStatusToServer();
            }
            break;

        case PHASE_4_DOSING:
            // Individual pump shutoffs based on specific target durations
            if (now - actuators.phaseStartTime >= actuators.dosePump1Ms) {
                digitalWrite(PIN_RELAY_PERISTALTIC_1, RELAY_OFF);
            }
            if (now - actuators.phaseStartTime >= actuators.dosePump2Ms) {
                digitalWrite(PIN_RELAY_PERISTALTIC_2, RELAY_OFF);
            }
            if (now - actuators.phaseStartTime >= actuators.dosePump3Ms) {
                digitalWrite(PIN_RELAY_PERISTALTIC_3, RELAY_OFF);
            }

            // Phase complete when the longest dosing pump finishes
            if (now - actuators.phaseStartTime >= actuators.phaseDuration) {
                actuators.allRelaysOff();
                Serial.println("[Phase 4 DONE] Fertilizer dosing complete and mixed.");

                // Transition to Phase 5: Probe Rinse
                actuators.setPhase(PHASE_5_PROBE_RINSE, TIME_RINSE_PROBE_MS);
                digitalWrite(PIN_RELAY_PROBE_RINSE, RELAY_ON);
                Serial.printf("[Phase 5] Diaphragm 3 (Clean Water Rinse) active for %lu ms\n", TIME_RINSE_PROBE_MS);
                reportStatusToServer();
            }
            break;

        case PHASE_5_PROBE_RINSE:
            if (now - actuators.phaseStartTime >= actuators.phaseDuration) {
                digitalWrite(PIN_RELAY_PROBE_RINSE, RELAY_OFF);
                Serial.println("[Phase 5 DONE] Probes rinsed with fresh clean water.");

                // Transition to Phase 6: Drain Rinse Water
                actuators.setPhase(PHASE_6_DRAIN_WASTE, TIME_DRAIN_VALVE_MS);
                digitalWrite(PIN_RELAY_VALVE_DRAIN, RELAY_ON);
                Serial.printf("[Phase 6] Solenoid Valve open to drain wastewater for %lu ms\n", TIME_DRAIN_VALVE_MS);
                reportStatusToServer();
            }
            break;

        case PHASE_6_DRAIN_WASTE:
            if (now - actuators.phaseStartTime >= actuators.phaseDuration) {
                digitalWrite(PIN_RELAY_VALVE_DRAIN, RELAY_OFF);
                Serial.println("[Phase 6 DONE] Rinse wastewater completely drained.");

                // Cycle Complete -> Back to Standby
                actuators.setPhase(PHASE_IDLE, 0);
                Serial.println("\n🎉 >>> [CYCLE COMPLETE] Presentation cycle finished successfully! <<<\n");
                reportStatusToServer();
            }
            break;
    }
}
