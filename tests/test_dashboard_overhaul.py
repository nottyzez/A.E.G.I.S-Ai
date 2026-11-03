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


if __name__ == "__main__":
    unittest.main(verbosity=2)
