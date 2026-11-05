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
#include <Preferences.h>
#include <esp_pm.h>

#include "config.h"

// Fallback so a config.h copied before the power work still compiles.
#ifndef ENABLE_AUTO_LIGHT_SLEEP
#define ENABLE_AUTO_LIGHT_SLEEP 1
#endif

#include "sensor_filters.h"
#include "actuator_controller.h"

// Hardware instances
OneWire oneWire(PIN_TEMP_ONEWIRE);
DallasTemperature tempSensors(&oneWire);
ActuatorController actuators;

// State and Timing
unsigned long lastCommandPollTime = 0;
unsigned long lastWifiRetry = 0;
const unsigned long COMMAND_POLL_INTERVAL_MS = 1500;

float latestPH = 6.20f;
float latestEC = 1.80f;
float latestTemp = 26.5f;

// ------------------------------------------------------------------------------
// Runtime Config (NVS)
// Set over Serial so moving the rig to another network never needs a recompile:
//   SET WIFI <ssid> <password>   SET SERVER <ip>   SHOW   RESET
// config.h values are the fallback used when NVS is empty.
// ------------------------------------------------------------------------------
Preferences prefs;
String cfgSsid = WIFI_SSID;
String cfgPass = WIFI_PASSWORD;
String cfgHost = SERVER_HOST;
String cfgPort = String(SERVER_PORT);

void loadRuntimeConfig() {
    prefs.begin("aegis", true);
    cfgSsid = prefs.getString("ssid", WIFI_SSID);
    cfgPass = prefs.getString("pass", WIFI_PASSWORD);
    cfgHost = prefs.getString("host", SERVER_HOST);
    cfgPort = prefs.getString("port", String(SERVER_PORT));
    prefs.end();
}

// Endpoints are built from the NVS values, so SET SERVER takes effect without
// a recompile. The old URL_* macros baked SERVER_HOST in at compile time.
// The port is NVS too: a Droplet serves through Nginx on 80, not 8000, and
// forgetting that would leave the board dialing a closed port with no error.
String apiUrl(const char* path) {
    return String("http://") + cfgHost + ":" + cfgPort + path;
}

// ------------------------------------------------------------------------------
// WiFi Connection Helper
// ------------------------------------------------------------------------------
void connectWiFi() {
    Serial.printf("\nConnecting to Wi-Fi SSID: %s ", cfgSsid.c_str());
    WiFi.mode(WIFI_STA);
    WiFi.setAutoReconnect(true);
    WiFi.begin(cfgSsid.c_str(), cfgPass.c_str());

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
    http.begin(apiUrl("/api/sensor"));
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
    http.begin(apiUrl("/api/status"));
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
    // Polled even while a cycle runs: manual overrides are non-blocking windows
    // (see ActuatorController::manualTriggerRelay), so a presenter's button press
    // must never be silently dropped mid-cycle.
    if (WiFi.status() != WL_CONNECTED) return;

    HTTPClient http;
    http.begin(apiUrl("/api/command"));
    int code = http.GET();

    if (code == 200) {
        String payload = http.getString();
        StaticJsonDocument<512> doc;
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
            } else if (strcmp(cmd, "JUMP_PHASE") == 0) {
                // Dashboard phase 1..6 -> the physical relays that phase drives.
                int phase = doc["phase_id"] | 1;
                unsigned long dur = doc["duration_ms"] | 6000;
                Serial.printf("[REMOTE DASHBOARD] Jump to demo phase %d (%lu ms)\n", phase, dur);
                switch (phase) {
                    case 1: actuators.manualTriggerRelay(1, dur); break;               // Sample inflow
                    case 2: break;                                                     // Vision capture: no relay
                    case 3: break;                                                     // AI fusion: no relay
                    case 4: actuators.manualTriggerRelay(2, dur); break;               // Sample return
                    case 5: actuators.manualTriggerRelay(5, dur);                      // Stock A
                            actuators.manualTriggerRelay(6, dur);                      // Stock B
                            actuators.manualTriggerRelay(7, dur); break;               // Stock C
                    case 6: actuators.manualTriggerRelay(3, dur);                      // Probe rinse
                            actuators.manualTriggerRelay(4, dur); break;               // Drain valve
                    default: break;
                }
            } else if (strcmp(cmd, "MANUAL_DOSE") == 0) {
                // Server sends per-pump runtimes; each runs as its own window.
                unsigned long p1 = doc["dosing_ms"]["pump1_ms"] | 0;
                unsigned long p2 = doc["dosing_ms"]["pump2_ms"] | 0;
                unsigned long p3 = doc["dosing_ms"]["pump3_ms"] | 0;
                Serial.printf("[REMOTE DASHBOARD] Manual dose: A=%lu ms, B=%lu ms, C=%lu ms\n", p1, p2, p3);
                if (p1 > 0) actuators.manualTriggerRelay(5, p1);
                if (p2 > 0) actuators.manualTriggerRelay(6, p2);
                if (p3 > 0) actuators.manualTriggerRelay(7, p3);
            } else if (strcmp(cmd, "STOP") == 0) {
                actuators.clearManualOverrides();
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
        String raw = Serial.readStringUntil('\n');
        raw.trim();

        // SET carries the rest of the line verbatim — an SSID or password is
        // case-sensitive, so it must never go through toUpperCase().
        String input = raw;
        input.toUpperCase();

        if (input.startsWith("SET WIFI ")) {
            String rest = raw.substring(9);
            int sep = rest.indexOf(' ');
            if (sep < 1) {
                Serial.println("[NVS] Usage: SET WIFI <ssid> <password>");
                return;
            }
            prefs.begin("aegis", false);
            prefs.putString("ssid", rest.substring(0, sep));
            prefs.putString("pass", rest.substring(sep + 1));
            prefs.end();
            Serial.printf("[NVS] Wi-Fi saved (%s). Rebooting...\n", rest.substring(0, sep).c_str());
            delay(300);
            ESP.restart();
        } else if (input.startsWith("SET SSID ")) {
            // The whole rest of the line is the SSID: phone hotspots are
            // commonly named "Samsung S30 Ultra", and SET WIFI would split on
            // the first space and store "Samsung" as the network name.
            String ssid = raw.substring(9);
            if (ssid.length() == 0) {
                Serial.println("[NVS] Usage: SET SSID <network name, spaces allowed>");
                return;
            }
            prefs.begin("aegis", false);
            prefs.putString("ssid", ssid);
            prefs.end();
            Serial.printf("[NVS] SSID saved (%s). Rebooting...\n", ssid.c_str());
            delay(300);
            ESP.restart();
        } else if (input.startsWith("SET PASS ")) {
            // Same reason as SET SSID: a password may contain spaces.
            String pass = raw.substring(9);
            if (pass.length() == 0) {
                Serial.println("[NVS] Usage: SET PASS <password, spaces allowed>");
                return;
            }
            prefs.begin("aegis", false);
            prefs.putString("pass", pass);
            prefs.end();
            Serial.printf("[NVS] Password saved (%u chars). Rebooting...\n", pass.length());
            delay(300);
            ESP.restart();
        } else if (input.startsWith("SET SERVER ")) {
            // Usage: SET SERVER <host> [port]  — the port defaults to SERVER_PORT.
            String rest = raw.substring(11);
            int sep = rest.indexOf(' ');
            String host = (sep < 0) ? rest : rest.substring(0, sep);
            String port = (sep < 0) ? String(SERVER_PORT) : rest.substring(sep + 1);
            if (host.length() == 0 || port.length() == 0) {
                Serial.println("[NVS] Usage: SET SERVER <ip> [port]");
                return;
            }
            prefs.begin("aegis", false);
            prefs.putString("host", host);
            prefs.putString("port", port);
            prefs.end();
            Serial.printf("[NVS] Server set to %s:%s. Rebooting...\n", host.c_str(), port.c_str());
            delay(300);
            ESP.restart();
        } else if (input == "SHOW") {
            Serial.printf("[CFG] SSID: %s | SERVER: %s:%s\n",
                          cfgSsid.c_str(), cfgHost.c_str(), cfgPort.c_str());
        } else if (input == "RESET") {
            prefs.begin("aegis", false);
            prefs.clear();
            prefs.end();
            Serial.println("[NVS] Cleared, back to config.h defaults. Rebooting...");
            delay(300);
            ESP.restart();
        } else if (input == "START" || input == "RUN") {
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
            Serial.println("\nCommands: START | STOP | READ | TEST <1-7> <ms>");
            Serial.println("          SET SSID <name> | SET PASS <password>   (spaces OK)");
            Serial.println("          SET WIFI <ssid> <password> | SET SERVER <ip> [port] | SHOW | RESET");
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

    // NVS overrides (Serial-set) then connect WiFi
    loadRuntimeConfig();
    connectWiFi();

#if ENABLE_AUTO_LIGHT_SLEEP
    // Idle the CPU in light sleep instead of spinning. millis() is corrected
    // by the RTC across a light sleep, so the FSM's phase timers stay true.
    esp_pm_config_t pm_config = {};
    pm_config.max_freq_mhz = 240;
    pm_config.min_freq_mhz = 80;
    pm_config.light_sleep_enable = true;
    esp_err_t pm_err = esp_pm_configure(&pm_config);
    Serial.printf("[POWER] Auto light sleep: %s\n",
                  pm_err == ESP_OK ? "on" : "unavailable (core built without CONFIG_PM_ENABLE)");
#endif

    // Report initial ready status
    reportStatusToServer();
}

// ------------------------------------------------------------------------------
// Non-blocking Main Loop (FSM Execution)
// ------------------------------------------------------------------------------
void loop() {
    unsigned long now = millis();

    // Release any manual relay whose runtime window has elapsed
    actuators.updateManualOverrides(now);

    // The hotspot may come up after the board does; without this the board
    // stays offline for the whole session after its one 10 s boot attempt.
    if (WiFi.status() != WL_CONNECTED && now - lastWifiRetry > 5000) {
        lastWifiRetry = now;
        WiFi.reconnect();
    }

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
            // Standby waiting for dashboard or physical trigger (pH probe safely hydrated in sample water)
            break;

        case PHASE_0_PRE_RETURN:
            if (now - actuators.phaseStartTime >= actuators.phaseDuration) {
                digitalWrite(PIN_RELAY_SAMPLE_RETURN, RELAY_OFF);
                Serial.println("[Phase 0 DONE] Resting storage water returned to culture tank (Zero Waste).");

                // Transition to Phase 1: Draw Fresh Sample Water
                actuators.setPhase(PHASE_1_SAMPLING_IN, TIME_SAMPLE_IN_MS);
                digitalWrite(PIN_RELAY_SAMPLE_IN, RELAY_ON);
                Serial.printf("[Phase 1] Diaphragm 1 (Fresh Sample IN) active for %lu ms\n", TIME_SAMPLE_IN_MS);
                reportStatusToServer();
            }
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
                // The firmware enforces the pump runtime ceiling itself; never
                // trust the server plan to have clamped a peristaltic runtime.
                actuators.dosePump1Ms = min(actuators.dosePump1Ms, (unsigned long)MAX_SAFETY_DOSING_MS);
                actuators.dosePump2Ms = min(actuators.dosePump2Ms, (unsigned long)MAX_SAFETY_DOSING_MS);
                actuators.dosePump3Ms = min(actuators.dosePump3Ms, (unsigned long)MAX_SAFETY_DOSING_MS);
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

                // Transition to Phase 7: Probe Preservation Soak (Draw small sample water to soak pH bulb)
                actuators.setPhase(PHASE_7_PROBE_PRESERVATION, TIME_PRESERVATION_SOAK_MS);
                digitalWrite(PIN_RELAY_SAMPLE_IN, RELAY_ON);
                Serial.printf("[Phase 7] Diaphragm 1 (Probe Preservation Soak) active for %lu ms\n", TIME_PRESERVATION_SOAK_MS);
                reportStatusToServer();
            }
            break;

        case PHASE_7_PROBE_PRESERVATION:
            if (now - actuators.phaseStartTime >= actuators.phaseDuration) {
                digitalWrite(PIN_RELAY_SAMPLE_IN, RELAY_OFF);
                Serial.println("[Phase 7 DONE] Chamber filled with small sample volume for probe preservation.");

                // Cycle Complete -> Back to Standby (Strictly NO measurement during preservation soak)
                actuators.setPhase(PHASE_IDLE, 0);
                Serial.println("\n🎉 >>> [CYCLE COMPLETE] System in Standby. pH probe hydrated in sample water (No Reading during soak). <<<\n");
                reportStatusToServer();
            }
            break;
    }
}
