"""
Unit test for ESP32-S3 Closed-Loop Fluidic Chamber FSM with pH Probe Preservation.
Verifies Phase 0 (Pre-Return) and Phase 7 (Probe Preservation Soak) invariants.
"""

import unittest
from pathlib import Path
import re

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
# Assert against the TRACKED template, not the gitignored config.h: a clean
# clone has no config.h, and a test that reads only the local file passes on the
# developer machine while failing everywhere else (see CLAUDE.md gotchas).
CONFIG_PATH = WORKSPACE_DIR / "firmware" / "esp32_main" / "config.example.h"
ACTUATOR_PATH = WORKSPACE_DIR / "firmware" / "esp32_main" / "actuator_controller.h"
INO_PATH = WORKSPACE_DIR / "firmware" / "esp32_main" / "esp32_main.ino"

class TestChamberFSMPreservation(unittest.TestCase):

    def setUp(self):
        self.assertTrue(CONFIG_PATH.exists(), f"Missing config template file: {CONFIG_PATH}")
        self.assertTrue(ACTUATOR_PATH.exists(), f"Missing actuator file: {ACTUATOR_PATH}")
        self.assertTrue(INO_PATH.exists(), f"Missing ino file: {INO_PATH}")

        self.config_content = CONFIG_PATH.read_text(encoding="utf-8")
        self.actuator_content = ACTUATOR_PATH.read_text(encoding="utf-8")
        self.ino_content = INO_PATH.read_text(encoding="utf-8")

    def test_01_timing_macros_defined(self):
        """Verify timing macros for Phase 0 Pre-Return and Phase 7 Preservation Soak."""
        self.assertIn("#define TIME_PRE_RETURN_MS", self.config_content)
        self.assertIn("#define TIME_PRESERVATION_SOAK_MS", self.config_content)

        pre_return_match = re.search(r"#define\s+TIME_PRE_RETURN_MS\s+(\d+)", self.config_content)
        self.assertIsNotNone(pre_return_match)
        self.assertEqual(int(pre_return_match.group(1)), 8000, "TIME_PRE_RETURN_MS should be 8000ms (300 mL @ 38 mL/s)")

        soak_match = re.search(r"#define\s+TIME_PRESERVATION_SOAK_MS\s+(\d+)", self.config_content)
        self.assertIsNotNone(soak_match)
        self.assertEqual(int(soak_match.group(1)), 10000, "TIME_PRESERVATION_SOAK_MS should be 10000ms (300 mL @ 30 mL/s)")

    def test_02_cycle_phase_enum(self):
        """Verify CyclePhase enum includes Phase 0 and Phase 7."""
        self.assertIn("PHASE_0_PRE_RETURN", self.actuator_content)
        self.assertIn("PHASE_7_PROBE_PRESERVATION", self.actuator_content)

        # Check phase names in getPhaseName()
        self.assertIn('"0_PRE_RETURN"', self.actuator_content)
        self.assertIn('"7_PROBE_PRESERVATION"', self.actuator_content)
        self.assertIn('"STANDBY_PRESERVED"', self.actuator_content)

    def test_03_cycle_starts_at_phase_0(self):
        """Verify startFullPresentationCycle() initiates at PHASE_0_PRE_RETURN."""
        cycle_start_match = re.search(
            r"void\s+startFullPresentationCycle\(\)\s*\{([^}]+)\}",
            self.actuator_content,
            re.DOTALL
        )
        self.assertIsNotNone(cycle_start_match)
        body = cycle_start_match.group(1)
        self.assertIn("PHASE_0_PRE_RETURN", body)
        self.assertIn("TIME_PRE_RETURN_MS", body)
        self.assertIn("PIN_RELAY_SAMPLE_RETURN", body)
        self.assertIn("RELAY_ON", body)

    def test_04_phase_0_transition_to_phase_1(self):
        """Verify Phase 0 completes and transitions to Phase 1 Sampling In."""
        self.assertIn("case PHASE_0_PRE_RETURN:", self.ino_content)
        p0_match = re.search(
            r"case\s+PHASE_0_PRE_RETURN:\s*(.+?)break;",
            self.ino_content,
            re.DOTALL
        )
        self.assertIsNotNone(p0_match)
        p0_code = p0_match.group(1)
        self.assertIn("PIN_RELAY_SAMPLE_RETURN, RELAY_OFF", p0_code)
        self.assertIn("PHASE_1_SAMPLING_IN", p0_code)
        self.assertIn("PIN_RELAY_SAMPLE_IN, RELAY_ON", p0_code)

    def test_05_phase_6_transition_to_phase_7(self):
        """Verify Phase 6 Drain transitions to Phase 7 Probe Preservation Soak."""
        self.assertIn("case PHASE_6_DRAIN_WASTE:", self.ino_content)
        p6_match = re.search(
            r"case\s+PHASE_6_DRAIN_WASTE:\s*(.+?)break;",
            self.ino_content,
            re.DOTALL
        )
        self.assertIsNotNone(p6_match)
        p6_code = p6_match.group(1)
        self.assertIn("PIN_RELAY_VALVE_DRAIN, RELAY_OFF", p6_code)
        self.assertIn("PHASE_7_PROBE_PRESERVATION", p6_code)
        self.assertIn("PIN_RELAY_SAMPLE_IN, RELAY_ON", p6_code)

    def test_06_phase_7_completes_to_idle(self):
        """Verify Phase 7 completes, turns off pump, and transitions to PHASE_IDLE."""
        self.assertIn("case PHASE_7_PROBE_PRESERVATION:", self.ino_content)
        p7_match = re.search(
            r"case\s+PHASE_7_PROBE_PRESERVATION:\s*(.+?)break;",
            self.ino_content,
            re.DOTALL
        )
        self.assertIsNotNone(p7_match)
        p7_code = p7_match.group(1)
        self.assertIn("PIN_RELAY_SAMPLE_IN, RELAY_OFF", p7_code)
        self.assertIn("PHASE_IDLE", p7_code)

    def test_07_no_measurement_during_soak_invariant(self):
        """Invariant: performSensorReadings() must NEVER be called in Phase 7 or Phase Idle."""
        p7_match = re.search(
            r"case\s+PHASE_7_PROBE_PRESERVATION:\s*(.+?)break;",
            self.ino_content,
            re.DOTALL
        )
        self.assertIsNotNone(p7_match)
        p7_code = p7_match.group(1)
        self.assertNotIn("performSensorReadings", p7_code, "Sensors must NOT be measured during Phase 7 soak!")
        self.assertNotIn("sendTelemetryAndGetDosingPlan", p7_code, "No telemetry should be sent during Phase 7!")

        # Measurements must only occur in PHASE_2_MEASURING
        p2_match = re.search(
            r"case\s+PHASE_2_MEASURING:\s*(.+?)break;",
            self.ino_content,
            re.DOTALL
        )
        self.assertIsNotNone(p2_match)
        p2_code = p2_match.group(1)
        self.assertIn("performSensorReadings()", p2_code)
        self.assertIn("sendTelemetryAndGetDosingPlan()", p2_code)

    def test_08_serial_commands_available(self):
        """Verify interactive serial command interface supports testing."""
        self.assertIn('input == "START"', self.ino_content)
        self.assertIn('input == "STOP"', self.ino_content)
        self.assertIn('input == "READ"', self.ino_content)
        self.assertIn('input.startsWith("TEST ")', self.ino_content)
        self.assertIn("manualTriggerRelay", self.ino_content)

    def test_09_cycle_start_quiesces_running_cycle(self):
        """A START_CYCLE pressed mid-cycle must de-energize every relay first.

        The FSM only turns a relay off on the way OUT of its owning phase, so a
        jump straight to PHASE_0 would leave peristaltic pumps running and
        re-dose the tank past the 30 s ceiling.
        """
        cycle_start_match = re.search(
            r"void\s+startFullPresentationCycle\(\)\s*\{([^}]+)\}",
            self.actuator_content,
            re.DOTALL
        )
        self.assertIsNotNone(cycle_start_match)
        body = cycle_start_match.group(1)
        self.assertIn("allRelaysOff();", body, "Must force every relay OFF before starting")
        self.assertIn("clearManualOverrides();", body, "Must clear stale override windows")
        self.assertLess(
            body.index("allRelaysOff();"), body.index("setPhase("),
            "Relays must be quiesced BEFORE the phase jump"
        )

    def test_10_dosing_pumps_clamped_to_safety_ceiling(self):
        """The firmware itself must clamp dose runtimes, not just the server."""
        p3_match = re.search(
            r"case\s+PHASE_3_SAMPLING_RETURN:\s*(.+?)break;",
            self.ino_content,
            re.DOTALL
        )
        self.assertIsNotNone(p3_match)
        p3_code = p3_match.group(1)
        for pump in ("dosePump1Ms", "dosePump2Ms", "dosePump3Ms"):
            self.assertRegex(
                p3_code,
                rf"min\(\s*actuators\.{pump}\s*,\s*\(unsigned long\)MAX_SAFETY_DOSING_MS\s*\)",
                f"{pump} must be clamped to MAX_SAFETY_DOSING_MS before energizing"
            )

        # The ceiling value itself must stay at the documented 30 000 ms.
        ceiling_match = re.search(r"#define\s+MAX_SAFETY_DOSING_MS\s+(\d+)", self.config_content)
        self.assertIsNotNone(ceiling_match)
        self.assertEqual(int(ceiling_match.group(1)), 30000)

    def test_11_phase_4_transitions_to_phase_5(self):
        """Phase 4 Dosing hands off to Phase 5 Probe Rinse in the automatic cycle.

        The full chain is P0 -> P1 -> P2 -> P3 -> P4 -> P5 -> P6 -> P7 -> IDLE.
        Phase 5/6 were briefly cut (2026-11-05) when the GPIO 7 pump's reversed
        flyback diode shorted the 12 V rail; the diode was the fault, not the
        pump, so the rinse is back. If someone cuts it again, this test names
        the chain that broke rather than leaving a silently shortened cycle.
        """
        p4_match = re.search(
            r"case\s+PHASE_4_DOSING:\s*(.+?)break;",
            self.ino_content,
            re.DOTALL
        )
        self.assertIsNotNone(p4_match)
        p4_code = p4_match.group(1)
        self.assertIn("PHASE_5_PROBE_RINSE", p4_code)
        self.assertIn("TIME_RINSE_PROBE_MS", p4_code)
        self.assertIn("PIN_RELAY_PROBE_RINSE, RELAY_ON", p4_code)

    def test_12_sampling_phases_clamped_to_safety_ceiling(self):
        """The firmware must enforce MAX_SAFETY_PUMP_MS itself.

        Phase times are derived from flow rate x target volume; a config edit or
        a future server value above the ceiling would hold a diaphragm past the
        chamber's capacity and overflow it. setPhase() is the one choke point
        every transition goes through, so the clamp lives there.
        """
        ceiling_match = re.search(r"#define\s+MAX_SAFETY_PUMP_MS\s+(\d+)", self.config_content)
        self.assertIsNotNone(ceiling_match)
        ceiling = int(ceiling_match.group(1))

        set_phase_match = re.search(
            r"void\s+setPhase\(CyclePhase[^)]*\)\s*\{(.+?)\n    \}",
            self.actuator_content,
            re.DOTALL,
        )
        self.assertIsNotNone(set_phase_match, "setPhase() not found in actuator_controller.h")
        body = set_phase_match.group(1)
        for phase in ("PHASE_0_PRE_RETURN", "PHASE_1_SAMPLING_IN",
                      "PHASE_3_SAMPLING_RETURN", "PHASE_5_PROBE_RINSE",
                      "PHASE_7_PROBE_PRESERVATION"):
            self.assertIn(phase, body, f"{phase} must be capped by MAX_SAFETY_PUMP_MS")
        self.assertIn("min(durationMs, (unsigned long)MAX_SAFETY_PUMP_MS)", body)

        # Every configured diaphragm runtime has to fit under that cap, or the
        # clamp silently shortens it and the delivered volume is not 300 mL.
        for macro in ("TIME_PRE_RETURN_MS", "TIME_SAMPLE_IN_MS",
                      "TIME_SAMPLE_RETURN_MS", "TIME_RINSE_PROBE_MS",
                      "TIME_PRESERVATION_SOAK_MS"):
            value = re.search(rf"#define\s+{macro}\s+(\d+)", self.config_content)
            self.assertIsNotNone(value, f"{macro} missing")
            self.assertLessEqual(int(value.group(1)), ceiling, f"{macro} exceeds {ceiling} ms")


if __name__ == "__main__":
    unittest.main()
