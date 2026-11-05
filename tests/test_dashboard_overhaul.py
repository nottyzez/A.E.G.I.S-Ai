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
    def setUp(self):
        # calibrate_pump() persists; without this the run overwrites the real
        # server/calibration.json with the made-up values below.
        import tempfile
        from unittest import mock
        import dosing_engine as engine_module

        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        patcher = mock.patch.object(
            engine_module, "CALIBRATION_FILE", Path(self._tmp.name) / "calibration.json"
        )
        patcher.start()
        self.addCleanup(patcher.stop)

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


class TestAllSampleRemoval(unittest.TestCase):
    def setUp(self):
        self.html = (PROJECT_ROOT / "server" / "static" / "index.html").read_text(encoding="utf-8")

    def test_all_sample_view_is_gone(self):
        self.assertNotIn("function AllSampleTabView", self.html)
        self.assertNotIn('id: "All Sample"', self.html)
        self.assertNotIn("'All Sample'", self.html)

    def test_control_label_is_not_rendered(self):
        self.assertNotIn("Control (สมบูรณ์)", self.html)
        self.assertNotIn("{unitSummary.label}: {unitSummary.npkStatus}", self.html)

    def test_quick_unit_selector_is_removed(self):
        self.assertNotIn("quickUnits", self.html)


class TestControlPageGrouping(unittest.TestCase):
    def setUp(self):
        self.html = (PROJECT_ROOT / "server" / "static" / "index.html").read_text(encoding="utf-8")
        start = self.html.index("function ElectronicControlTabView")
        self.body = self.html[start:self.html.index("function AllSampleTabView", start)
                               if "function AllSampleTabView" in self.html
                               else self.html.index("function App()", start)]

    def test_four_subsystem_groups_exist(self):
        for anchor in ("settings-schedule", "settings-pumps", "settings-vision", "settings-simulation"):
            self.assertIn(f'id="{anchor}"', self.body)

    def test_no_body_copy_below_twelve_pixels(self):
        sizes = [int(m) for m in re.findall(r"text-\[(\d+)px\]", self.body)]
        self.assertTrue(all(s >= 12 for s in sizes if s < 12),
                        f"Found undersized copy: {[s for s in sizes if s < 12]}")


class TestPumpRuntimeAndFlow(unittest.TestCase):
    def setUp(self):
        self.html = (PROJECT_ROOT / "server" / "static" / "index.html").read_text(encoding="utf-8")

    def test_runtime_presets_top_out_at_thirty_seconds(self):
        for label in ("2s", "5s", "10s", "15s", "30s"):
            self.assertIn(f"label: '{label}'", self.html)
        self.assertNotIn("label: '60s'", self.html)

    def test_runtime_is_clamped_at_thirty_seconds(self):
        self.assertIn("Math.min(30000,", self.html)

    def test_flow_calculator_calls_per_pump_route(self):
        self.assertIn("/api/calibration/flow/", self.html)


class TestVisionPanel(unittest.TestCase):
    def setUp(self):
        self.html = (PROJECT_ROOT / "server" / "static" / "index.html").read_text(encoding="utf-8")
        self.main_py = (PROJECT_ROOT / "main.py").read_text(encoding="utf-8")

    def test_frontend_reads_latest_image_url(self):
        self.assertIn("latest_image_url", self.html)

    def test_gallery_helper_exists(self):
        self.assertIn("function getSavedGallery", self.html)

    def test_backend_timestamps_the_capture(self):
        self.assertIn("latest_capture_at", self.main_py)

    def test_image_error_falls_back_to_gallery(self):
        start = self.html.index("function getSavedGallery")
        self.assertIn("onError", self.html[start:start + 6000])


class TestChartPointerMapping(unittest.TestCase):
    def setUp(self):
        self.html = (PROJECT_ROOT / "server" / "static" / "index.html").read_text(encoding="utf-8")

    def test_pointer_helper_accounts_for_viewbox_inset(self):
        self.assertIn("function pointIndexFromPointer", self.html)

    def test_ec_chart_uses_the_series_it_draws(self):
        self.assertIn("ptsEcR2", self.html)
        start = self.html.index("const activeEcPt")
        body = self.html[start:start + 900]
        self.assertIn("__masterIdx", body)

    def test_mapping_clamps_at_both_edges(self):
        self.assertIn("Math.max(0, Math.min(count - 1", self.html)


if __name__ == "__main__":
    unittest.main(verbosity=2)
