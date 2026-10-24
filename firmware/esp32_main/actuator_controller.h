#ifndef ACTUATOR_CONTROLLER_H
#define ACTUATOR_CONTROLLER_H

#include <Arduino.h>
#include "config.h"

// ------------------------------------------------------------------------------
// Operational State Machine Phases
// ------------------------------------------------------------------------------
enum CyclePhase {
    PHASE_IDLE = 0,
    PHASE_1_SAMPLING_IN = 1,      // Diaphragm 1 draws sample into cup
    PHASE_2_MEASURING = 2,        // Wait settling delay + read pH/EC/Temp
    PHASE_3_SAMPLING_RETURN = 3,  // Diaphragm 2 pumps sample back into tank
    PHASE_4_DOSING = 4,           // Peristaltic pumps 1, 2, 3 dose formulas
    PHASE_5_PROBE_RINSE = 5,      // Diaphragm 3 rinses probes with clean water
    PHASE_6_DRAIN_WASTE = 6,      // Solenoid valve drains rinse water out
    PHASE_7_POST_CIRCULATION = 7, // Circulation delay before post-dosing verification
    PHASE_8_POST_VERIFY = 8       // Post-dosing verification measurement
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

    ActuatorController() {
        currentPhase = PHASE_IDLE;
        phaseStartTime = 0;
        phaseDuration = 0;
        dosePump1Ms = 0;
        dosePump2Ms = 0;
        dosePump3Ms = 0;
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
        Serial.println("\n>>> [CYCLE START] Beginning 6-Phase Automated Presentation Cycle <<<");
        setPhase(PHASE_1_SAMPLING_IN, TIME_SAMPLE_IN_MS);
        digitalWrite(PIN_RELAY_SAMPLE_IN, RELAY_ON);
        Serial.printf("[Phase 1] Diaphragm 1 (Sample IN) active for %lu ms\n", TIME_SAMPLE_IN_MS);
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

    // Manual test function for live judge demonstrations
    void manualTriggerRelay(int relayIndex, unsigned long durationMs) {
        if (durationMs > MAX_SAFETY_DOSING_MS) {
            durationMs = MAX_SAFETY_DOSING_MS;
        }

        int pin = getPinFromIndex(relayIndex);
        if (pin == -1) return;

        Serial.printf("[MANUAL] Triggering Relay #%d (GPIO %d) for %lu ms\n", relayIndex, pin, durationMs);
        digitalWrite(pin, RELAY_ON);
        delay(durationMs);
        digitalWrite(pin, RELAY_OFF);
        Serial.printf("[MANUAL] Relay #%d turned OFF\n", relayIndex);
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
            case PHASE_IDLE: return "STANDBY";
            case PHASE_1_SAMPLING_IN: return "1_SAMPLING_IN";
            case PHASE_2_MEASURING: return "2_MEASURING_AI";
            case PHASE_3_SAMPLING_RETURN: return "3_SAMPLE_RETURN";
            case PHASE_4_DOSING: return "4_TWO_TIER_DOSING";
            case PHASE_5_PROBE_RINSE: return "5_PROBE_RINSE";
            case PHASE_6_DRAIN_WASTE: return "6_DRAIN_WASTE";
            case PHASE_7_POST_CIRCULATION: return "7_POST_CIRCULATION";
            case PHASE_8_POST_VERIFY: return "8_POST_VERIFY";
            default: return "UNKNOWN";
        }
    }
};

#endif // ACTUATOR_CONTROLLER_H
