# -*- coding: utf-8 -*-
"""
test_presentation_override.py — Automated TDD Suite for Non-Destructive Presentation Override
Tests:
1. Schedule Coexistence: Manual commands (MANUAL_RELAY, JUMP_PHASE, MANUAL_DOSE, START_CYCLE)
   activate presentation override WITHOUT turning off schedule.enabled.
2. Collision Protection (Hold/Queue): If scheduled timer reaches 0 while presentation override
   is active, scheduled cycle is queued (queued_during_override = True) instead of colliding.
3. Cancel Override Only / Resume Auto Now: Immediately clears active override and resumes schedule
   (and triggers any queued auto cycle) without disabling scheduled automation.
4. Live AI & Sensor Scenario Simulation (/api/override/simulate): Computes Two-Factor Dosing
   for Healthy, -N, -P, -K, and triggers LOCKED_OUT for High EC (>=3.2) or Low pH (<=4.2).
5. Zero-Volume Priming Rule: Manual dose with 0 mL on a pump channel yields 0 ms for that channel.
6. Frontend ElectronicControlTabView DOM & Hybrid Priority Override Engine verification.
"""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SERVER_DIR = PROJECT_ROOT / "server"
STATIC_DIR = SERVER_DIR / "static"
for p in [str(PROJECT_ROOT), str(SERVER_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

import main


class TestBackendPresentationOverride(unittest.TestCase):
    def setUp(self):
        if hasattr(main, "reset_presentation_override_state"):
            main.reset_presentation_override_state()

    def test_1_schedule_stays_active_during_manual_relay_and_phase_jump(self):
        """Manual relay and phase jump commands must keep schedule.enabled = True."""
        status_before = main.get_hardware_status()
        self.assertIn("schedule", status_before, "current_hardware_status must contain 'schedule'")
        self.assertTrue(status_before["schedule"]["enabled"])

        # Trigger manual relay R1 for 5000ms
        res = main.post_dashboard_command({
            "command": "MANUAL_RELAY",
            "relay": 1,
            "duration_ms": 5000,
            "preserve_schedule": True,
        })
        self.assertEqual(res["status"], "ok")
        status_after = main.get_hardware_status()
        self.assertTrue(status_after["schedule"]["enabled"], "Schedule must remain enabled during manual relay override")
        self.assertTrue(status_after["override"]["active"], "Override must be marked active")
        self.assertIn(1, status_after["override"]["active_relays"])

        # Trigger phase jump to Phase 3
        res_phase = main.post_dashboard_command({
            "command": "JUMP_PHASE",
            "phase_id": 3,
            "duration_ms": 8000,
            "preserve_schedule": True,
        })
        self.assertEqual(res_phase["status"], "ok")
        status_phase = main.get_hardware_status()
        self.assertTrue(status_phase["schedule"]["enabled"], "Schedule must remain enabled during phase jump")
        self.assertEqual(status_phase["phase_id"], 3)

    def test_2_schedule_collision_queues_auto_cycle_during_active_override(self):
        """When auto schedule timer hits 0 during an active override, it enters Hold/Queue state."""
        self.assertTrue(hasattr(main, "post_schedule_control"), "main.py must expose post_schedule_control (/api/schedule)")
        main.post_dashboard_command({
            "command": "MANUAL_RELAY",
            "relay": 4,
            "duration_ms": 10000,
            "preserve_schedule": True,
        })
        res = main.post_schedule_control({"action": "SIMULATE_COLLISION"})
        self.assertEqual(res["status"], "ok")
        status = main.get_hardware_status()
        self.assertTrue(status["schedule"]["enabled"])
        self.assertTrue(status["schedule"]["queued_during_override"], "Scheduled cycle must be queued during active override")

        # Now cancel/finish override -> queued cycle should automatically release/run
        main.post_dashboard_command({"command": "RESUME_AUTO"})
        status_resumed = main.get_hardware_status()
        self.assertFalse(status_resumed["override"]["active"])
        self.assertFalse(status_resumed["schedule"]["queued_during_override"])
        self.assertTrue(status_resumed["schedule"]["enabled"])

    def test_3_cancel_override_only_preserves_schedule(self):
        """CANCEL_OVERRIDE stops active override relays without disabling schedule.enabled."""
        main.post_dashboard_command({
            "command": "MANUAL_RELAY",
            "relay": 2,
            "duration_ms": 15000,
        })
        main.post_dashboard_command({"command": "CANCEL_OVERRIDE"})
        status = main.get_hardware_status()
        self.assertFalse(status["override"]["active"])
        self.assertEqual(status["override"]["active_relays"], [])
        self.assertTrue(status["schedule"]["enabled"])

    def test_4_live_scenario_simulation_and_safety_lockouts(self):
        """/api/override/simulate computes Two-Factor dosing and enforces High EC / Low pH lockouts."""
        self.assertTrue(hasattr(main, "post_override_simulate"), "main.py must expose post_override_simulate (/api/override/simulate)")

        # Confirmed -N deficiency
        res_n = main.post_override_simulate({
            "ec": 1.35,
            "ph": 6.15,
            "temp": 27.5,
            "ai_class": "-N",
            "ai_confidence": 0.96,
            "ai_stage": "SYMPTOMATIC_DEFICIENCY_CONFIRMED",
            "apply_to_status": True,
        })
        self.assertEqual(res_n["safety_status"], "NORMAL")
        self.assertEqual(res_n["ratios"]["r1_pct"], 55.0)
        self.assertGreater(res_n["dosing_plan"]["pump1_ms"], res_n["dosing_plan"]["pump2_ms"])

        # High EC Lockout (>= 3.2)
        res_lock_ec = main.post_override_simulate({
            "ec": 3.45,
            "ph": 6.20,
            "temp": 28.0,
            "ai_class": "-K",
            "ai_stage": "SYMPTOMATIC_DEFICIENCY_CONFIRMED",
            "apply_to_status": True,
        })
        self.assertEqual(res_lock_ec["safety_status"], "LOCKED_OUT")
        self.assertEqual(res_lock_ec["tier1_status"], "HIGH_EC_LOCKOUT")
        self.assertEqual(res_lock_ec["dosing_plan"]["pump1_ms"], 0)
        self.assertEqual(res_lock_ec["dosing_plan"]["pump2_ms"], 0)
        self.assertEqual(res_lock_ec["dosing_plan"]["pump3_ms"], 0)

        # Low pH Lockout (<= 4.2)
        res_lock_ph = main.post_override_simulate({
            "ec": 1.60,
            "ph": 4.05,
            "temp": 27.0,
            "ai_class": "-P",
            "ai_stage": "PRE_SYMPTOMATIC_EARLY_WARNING",
            "apply_to_status": True,
        })
        self.assertEqual(res_lock_ph["safety_status"], "LOCKED_OUT")
        self.assertEqual(res_lock_ph["tier1_status"], "LOW_PH_LOCKOUT")
        self.assertEqual(res_lock_ph["dosing_plan"]["pump1_ms"], 0)

    def test_5_manual_dose_zero_volume_channel_has_zero_ms(self):
        """Manual dosing with 0 mL on Stock B/C must yield 0 ms on pump2/pump3 (no priming delay on 0 mL)."""
        res = main.post_dashboard_command({
            "command": "MANUAL_DOSE",
            "volumes_ml": {"A": 6.0, "B": 0.0, "C": 0.0},
            "preserve_schedule": True,
        })
        self.assertEqual(res["status"], "ok")
        dosing_ms = res["queued_command"]["dosing_ms"]
        self.assertGreater(dosing_ms["pump1_ms"], 2000)
        self.assertEqual(dosing_ms["pump2_ms"], 0)
        self.assertEqual(dosing_ms["pump3_ms"], 0)
        # Relay 5 corresponds to Stock A (GPIO 9) in the 7-relay architecture
        self.assertIn(5, res["override"]["active_relays"])

    def test_5b_manual_dose_all_channels_maps_to_relays_5_6_7(self):
        """Manual dosing with Stock A, B, C must activate Relays 5, 6, 7 (GPIO 9, 10, 11)."""
        res = main.post_dashboard_command({
            "command": "MANUAL_DOSE",
            "volumes_ml": {"A": 5.0, "B": 5.0, "C": 5.0},
            "preserve_schedule": True,
        })
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["override"]["active_relays"], [5, 6, 7])


class TestFrontendPresentationOverrideDOM(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")

    def test_6_dual_state_schedule_and_override_banner_present(self):
        """Verify ElectronicControlTabView contains AUTO SCHEDULE: ACTIVE, Hold/Queue, and Resume/Cancel controls."""
        self.assertIn("AUTO SCHEDULE: ACTIVE", self.html)
        self.assertIn("AUTO CYCLE QUEUED", self.html)
        self.assertIn("คืนค่าตารางอัตโนมัติทันที", self.html)
        self.assertIn("หยุดเฉพาะคำสั่งสาธิต", self.html)
        self.assertIn("Test 15s", self.html)

    def test_7_hardware_commands_and_esp32_cam_wired(self):
        """Verify ElectronicControlTabView wires /api/command, /api/cam_command, and /api/override/simulate."""
        self.assertIn("/api/command", self.html)
        self.assertIn("/api/cam_command", self.html)
        self.assertIn("/api/override/simulate", self.html)
        self.assertIn("MANUAL_RELAY", self.html)
        self.assertIn("JUMP_PHASE", self.html)
        self.assertIn("MANUAL_DOSE", self.html)
        self.assertIn("CAPTURE", self.html)

    def test_8_live_ai_scenario_simulator_and_command_log_present(self):
        """Verify Live AI & Sensor Scenario Simulator, Priming Delay calculation, and Telemetry Log exist."""
        self.assertIn("Live AI & Sensor Scenario Simulator", self.html)
        self.assertIn("HIGH_EC_LOCKOUT", self.html)
        self.assertIn("Peristaltic Fertilizer Dosing Deck (5 Cols)", self.html)
        self.assertIn("Live Command & Coexistence Telemetry Log", self.html)

    def test_9_hardware_pinouts_and_calibration_formulas_present(self):
        """Verify ESP32-S3 Hardware Pinout card contains GPIO 1-11, pH calibration formula, and OneWire pullup."""
        self.assertIn("ESP32-S3 Hardware Pinout &amp; Calibration Specifications", self.html)
        self.assertIn("GPIO 1 (ADC1_CH0)", self.html)
        self.assertIn("pH = -8.487", self.html)
        self.assertIn("GPIO 2 (ADC1_CH1)", self.html)
        self.assertIn("GPIO 4 (OneWire)", self.html)
        self.assertIn("Pull-up 4.7 kΩ", self.html)
        self.assertIn("GPIO 5", self.html)
        self.assertIn("Diaphragm Pump 1 (Sample Inflow)", self.html)
        self.assertIn("Diaphragm Pump 2 (Sample Return)", self.html)
        self.assertIn("Diaphragm Pump 3 (Probe Rinse)", self.html)
        self.assertIn("Solenoid Valve (Drain Valve)", self.html)
        self.assertIn("Peristaltic Pump 1 (Stock A: High-N)", self.html)
        self.assertIn("Peristaltic Pump 2 (Stock B: High-P)", self.html)
        self.assertIn("Peristaltic Pump 3 (Stock C: High-K)", self.html)


if __name__ == "__main__":
    unittest.main()
