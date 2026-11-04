#ifndef ACTUATOR_CONTROLLER_H
#define ACTUATOR_CONTROLLER_H

#include <Arduino.h>
#include "config.h"

// ------------------------------------------------------------------------------
// Operational State Machine Phases
// ------------------------------------------------------------------------------
enum CyclePhase {
    PHASE_IDLE = 0,
    PHASE_0_PRE_RETURN = 1,          // Diaphragm 2 returns resting storage water back to tank (Zero Waste)
    PHASE_1_SAMPLING_IN = 2,         // Diaphragm 1 draws fresh sample into chamber
    PHASE_2_MEASURING = 3,           // Wait settling delay + read pH/EC/Temp & send AI telemetry
    PHASE_3_SAMPLING_RETURN = 4,     // Diaphragm 2 pumps tested sample back into tank
    PHASE_4_DOSING = 5,              // Peristaltic pumps 1, 2, 3 dose formulas
    PHASE_5_PROBE_RINSE = 6,         // Diaphragm 3 rinses probes with clean RO water
    PHASE_6_DRAIN_WASTE = 7,         // Solenoid valve drains rinse wastewater out
    PHASE_7_PROBE_PRESERVATION = 8,  // Diaphragm 1 draws small soak water to preserve pH probe (No reading)
    PHASE_8_POST_CIRCULATION = 9,    // Optional circulation delay
    PHASE_9_POST_VERIFY = 10         // Optional post-dosing verification
};

class ActuatorController {
public:
    CyclePhase currentPhase;
    unsigned long phaseStartTime;
    unsigned long phaseDuration;

    // Planned Dosing durations (ms) computed by AI
    unsigned long dosePump1Ms;
    unsigned long dosePump2Ms;
    unsigned long dosePump3Ms;

    // Per-relay manual override windows (relay index 1..7 -> slot 0..6).
    // A manual command stores its runtime here and returns immediately, so the
    // main loop keeps polling WiFi, reading sensors and serving serial input.
    struct RelayOverride {
        bool active;
        int pin;
        unsigned long startMs;
        unsigned long durationMs;
    };
    RelayOverride overrides[7];

    ActuatorController() {
        currentPhase = PHASE_IDLE;
        phaseStartTime = 0;
        phaseDuration = 0;
        dosePump1Ms = 0;
        dosePump2Ms = 0;
        dosePump3Ms = 0;
        for (int i = 0; i < 7; i++) {
            overrides[i] = {false, -1, 0, 0};
        }
    }

    void initPins() {
        // Pre-write OFF state before enabling OUTPUT to prevent boot glitch
        int pins[] = {
            PIN_RELAY_SAMPLE_IN, PIN_RELAY_SAMPLE_RETURN, PIN_RELAY_PROBE_RINSE,
            PIN_RELAY_VALVE_DRAIN, PIN_RELAY_PERISTALTIC_1, PIN_RELAY_PERISTALTIC_2,
            PIN_RELAY_PERISTALTIC_3
        };
        for (int p : pins) {
            digitalWrite(p, RELAY_OFF);
            pinMode(p, OUTPUT);
            digitalWrite(p, RELAY_OFF);
        }
    }

    void allRelaysOff() {
        digitalWrite(PIN_RELAY_SAMPLE_IN, RELAY_OFF);
        digitalWrite(PIN_RELAY_SAMPLE_RETURN, RELAY_OFF);
        digitalWrite(PIN_RELAY_PROBE_RINSE, RELAY_OFF);
        digitalWrite(PIN_RELAY_VALVE_DRAIN, RELAY_OFF);
        digitalWrite(PIN_RELAY_PERISTALTIC_1, RELAY_OFF);
        digitalWrite(PIN_RELAY_PERISTALTIC_2, RELAY_OFF);
        digitalWrite(PIN_RELAY_PERISTALTIC_3, RELAY_OFF);
    }

    void startFullPresentationCycle() {
        // A cycle may be requested while another is mid-flight (the dashboard's
        // START_CYCLE button is always live). Quiesce first: the FSM only turns a
        // relay off on the way OUT of its owning phase, so jumping straight to
        // PHASE_0 would leave peristaltic pumps energized and re-dose the tank.
        allRelaysOff();
        clearManualOverrides();
        Serial.println("\n>>> [CYCLE START] Beginning 7-Phase Automated Presentation & Preservation Cycle <<<");
        setPhase(PHASE_0_PRE_RETURN, TIME_PRE_RETURN_MS);
        digitalWrite(PIN_RELAY_SAMPLE_RETURN, RELAY_ON);
        Serial.printf("[Phase 0] Diaphragm 2 (Pre-Return Storage Water) active for %lu ms\n", TIME_PRE_RETURN_MS);
    }

    void setPhase(CyclePhase newPhase, unsigned long durationMs) {
        currentPhase = newPhase;
        phaseStartTime = millis();
        phaseDuration = durationMs;
    }

    void stopCycle() {
        allRelaysOff();
        currentPhase = PHASE_IDLE;
        Serial.println("[CYCLE ABORTED] All relays forced OFF.");
    }

    // Manual test function for live judge demonstrations.
    // Non-blocking: records the runtime window and returns; updateManualOverrides()
    // turns the relay off once the window elapses.
    void manualTriggerRelay(int relayIndex, unsigned long durationMs) {
        if (durationMs > MAX_SAFETY_DOSING_MS) {
            durationMs = MAX_SAFETY_DOSING_MS;
        }

        int pin = getPinFromIndex(relayIndex);
        if (pin == -1 || relayIndex < 1 || relayIndex > 7) return;

        int slot = relayIndex - 1;
        overrides[slot].active = true;
        overrides[slot].pin = pin;
        overrides[slot].startMs = millis();
        overrides[slot].durationMs = durationMs;

        Serial.printf("[MANUAL] Relay #%d (GPIO %d) ON for %lu ms (non-blocking)\n",
                      relayIndex, pin, durationMs);
        digitalWrite(pin, RELAY_ON);
    }

    // Call every loop(): releases each relay whose manual window has elapsed.
    void updateManualOverrides(unsigned long now) {
        for (int i = 0; i < 7; i++) {
            if (!overrides[i].active) continue;
            if (now - overrides[i].startMs >= overrides[i].durationMs) {
                digitalWrite(overrides[i].pin, RELAY_OFF);
                overrides[i].active = false;
                Serial.printf("[MANUAL] Relay #%d turned OFF after %lu ms\n",
                              i + 1, overrides[i].durationMs);
            }
        }
    }

    bool isManualOverrideActive(int relayIndex) {
        if (relayIndex < 1 || relayIndex > 7) return false;
        return overrides[relayIndex - 1].active;
    }

    void clearManualOverrides() {
        for (int i = 0; i < 7; i++) {
            if (overrides[i].active) {
                digitalWrite(overrides[i].pin, RELAY_OFF);
                overrides[i].active = false;
            }
        }
    }

    int getPinFromIndex(int index) {
        switch (index) {
            case 1: return PIN_RELAY_SAMPLE_IN;
            case 2: return PIN_RELAY_SAMPLE_RETURN;
            case 3: return PIN_RELAY_PROBE_RINSE;
            case 4: return PIN_RELAY_VALVE_DRAIN;
            case 5: return PIN_RELAY_PERISTALTIC_1;
            case 6: return PIN_RELAY_PERISTALTIC_2;
            case 7: return PIN_RELAY_PERISTALTIC_3;
            default: return -1;
        }
    }

    const char* getPhaseName() {
        switch (currentPhase) {
            case PHASE_IDLE: return "STANDBY_PRESERVED";
            case PHASE_0_PRE_RETURN: return "0_PRE_RETURN";
            case PHASE_1_SAMPLING_IN: return "1_SAMPLING_IN";
            case PHASE_2_MEASURING: return "2_MEASURING_AI";
            case PHASE_3_SAMPLING_RETURN: return "3_SAMPLE_RETURN";
            case PHASE_4_DOSING: return "4_TWO_TIER_DOSING";
            case PHASE_5_PROBE_RINSE: return "5_PROBE_RINSE";
            case PHASE_6_DRAIN_WASTE: return "6_DRAIN_WASTE";
            case PHASE_7_PROBE_PRESERVATION: return "7_PROBE_PRESERVATION";
            case PHASE_8_POST_CIRCULATION: return "8_POST_CIRCULATION";
            case PHASE_9_POST_VERIFY: return "9_POST_VERIFY";
            default: return "UNKNOWN";
        }
    }
};

#endif // ACTUATOR_CONTROLLER_H
