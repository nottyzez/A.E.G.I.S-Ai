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
        self.assertEqual(int(pre_return_match.group(1)), 4000, "TIME_PRE_RETURN_MS should be 4000ms")

        soak_match = re.search(r"#define\s+TIME_PRESERVATION_SOAK_MS\s+(\d+)", self.config_content)
        self.assertIsNotNone(soak_match)
        self.assertEqual(int(soak_match.group(1)), 3000, "TIME_PRESERVATION_SOAK_MS should be 3000ms")

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


if __name__ == "__main__":
    unittest.main()
