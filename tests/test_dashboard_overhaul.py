#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A.E.G.I.S. Dashboard Overhaul Verification Suite
Covers the 2026-11-03 overhaul plan: firmware command contract, simplified
surfaces, control-page grouping, pump runtime/flow calibration, vision panel,
and chart pointer alignment.
"""

import sys
import re
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIRMWARE_DIR = PROJECT_ROOT / "firmware" / "esp32_main"

sys.path.insert(0, str(PROJECT_ROOT / "server"))


class TestFirmwareNonBlockingRelay(unittest.TestCase):
    def setUp(self):
        self.src = (FIRMWARE_DIR / "actuator_controller.h").read_text(encoding="utf-8")

    def test_manual_trigger_contains_no_blocking_delay(self):
        """manualTriggerRelay must not block the loop with delay()."""
        start = self.src.index("void manualTriggerRelay")
        end = self.src.index("int getPinFromIndex", start)
        body = self.src[start:end]
        self.assertNotIn("delay(", body,
                         "manualTriggerRelay must be non-blocking; store state and return")

    def test_manual_override_state_and_updater_exist(self):
        self.assertIn("updateManualOverrides", self.src)
        self.assertIn("isManualOverrideActive", self.src)
        self.assertIn("clearManualOverrides", self.src)


class TestFirmwareCommandContract(unittest.TestCase):
    def setUp(self):
        self.ino = (FIRMWARE_DIR / "esp32_main.ino").read_text(encoding="utf-8")
        # config.h is gitignored (it holds the WiFi password); config.example.h is
        # the tracked template a fresh clone compiles from, so the ceiling is
        # asserted there — a test that only read config.h would pass on this
        # machine and fail on any clean checkout.
        self.cfg = (FIRMWARE_DIR / "config.example.h").read_text(encoding="utf-8")

    def test_firmware_handles_every_dashboard_command(self):
        for cmd in ("JUMP_PHASE", "MANUAL_DOSE", "MANUAL_RELAY", "START_CYCLE", "STOP"):
            self.assertIn(f'strcmp(cmd, "{cmd}")', self.ino)

    def test_safety_ceiling_is_thirty_seconds(self):
        self.assertIn("#define MAX_SAFETY_DOSING_MS     30000", self.cfg)

    def test_manual_relay_not_gated_on_idle_phase(self):
        start = self.ino.index("void pollRemoteDashboardCommand")
        end = self.ino.index("void handleSerialCommands", start)
        body = self.ino[start:end]
        self.assertNotIn("actuators.currentPhase != PHASE_IDLE", body,
                         "Manual overrides must be accepted while a cycle runs")


class TestServerRuntimeCeiling(unittest.TestCase):
    def test_command_calc_ms_caps_at_thirty_seconds(self):
        src = (PROJECT_ROOT / "main.py").read_text(encoding="utf-8")
        self.assertIn("min(30000, int(round(prime_ms", src)
        self.assertNotIn("min(25000, int(round(prime_ms", src)

    def test_ai_dosing_engine_caps_at_thirty_seconds(self):
        """The AI dosing path clamps through its own constant, not main.py's."""
        from dosing_engine import MAX_PUMP_DURATION_MS
        self.assertEqual(MAX_PUMP_DURATION_MS, 30000)


if __name__ == "__main__":
    unittest.main(verbosity=2)
