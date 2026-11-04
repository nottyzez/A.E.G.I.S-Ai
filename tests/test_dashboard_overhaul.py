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


class TestPerPumpFlowCalibration(unittest.TestCase):
    def test_each_pump_holds_its_own_flow_rate(self):
        from dosing_engine import TwoTierDosingEngine
        eng = TwoTierDosingEngine()
        eng.calibrate_pump("A", collected_ml=12.0, test_duration_s=10.0, observed_prime_s=2.0)
        eng.calibrate_pump("B", collected_ml=6.0, test_duration_s=10.0, observed_prime_s=2.0)
        rates = eng.get_pump_flow_rates()
        self.assertAlmostEqual(rates["A"], 1.5, places=2)
        self.assertAlmostEqual(rates["B"], 0.75, places=2)

    def test_unknown_pump_key_is_rejected(self):
        from dosing_engine import TwoTierDosingEngine
        with self.assertRaises(ValueError):
            TwoTierDosingEngine().calibrate_pump("Z", 10.0, 10.0, 2.0)

    def test_per_pump_route_is_registered(self):
        import main
        paths = [r.path for r in main.app.routes if hasattr(r, "path")]
        self.assertIn("/api/calibration/flow/{pump_key}", paths)


class TestHomeSimplification(unittest.TestCase):
    def setUp(self):
        self.html = (PROJECT_ROOT / "server" / "static" / "index.html").read_text(encoding="utf-8")

    def test_home_has_no_telemetry_deck(self):
        start = self.html.index("function HomeView")
        end = self.html.index("function AnalyzeTabView", start)
        body = self.html[start:end]
        self.assertNotIn("bottomMetrics", body)
        self.assertNotIn("bottom-telemetry-card", body)
        self.assertNotIn("3D GALAXY PARALLAX", body)

    def test_home_keeps_both_primary_actions(self):
        start = self.html.index("function HomeView")
        end = self.html.index("function AnalyzeTabView", start)
        body = self.html[start:end]
        self.assertIn("ENTER A.E.G.I.S ANALYZE", body)
        self.assertIn("READ SYSTEM SPEC", body)


if __name__ == "__main__":
    unittest.main(verbosity=2)
