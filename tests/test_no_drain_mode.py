"""
No-drain mode: the rig has no drip tray under the waste outlet, so opening the
GPIO 8 solenoid at Phase 6 puts water on the floor.

Draining is skipped, and the Phase 5 rinse is skipped with it: the rinse water
is what the drain would have removed, so keeping the rinse would add ~200 mL to
the chamber every cycle until it overflows.

Firmware + server + dashboard must agree — a dashboard toggle the firmware does
not read is the same bug the project already hit once with JUMP_CYCLE.
"""

import re
import unittest
from pathlib import Path

import main

ROOT = Path(__file__).resolve().parent.parent
ACTUATOR = ROOT / "firmware" / "esp32_main" / "actuator_controller.h"
FIRMWARE = ROOT / "firmware" / "esp32_main" / "esp32_main.ino"
DASHBOARD = ROOT / "server" / "static" / "index.html"


class TestNoDrainFirmware(unittest.TestCase):

    def setUp(self):
        self.actuator = ACTUATOR.read_text(encoding="utf-8")
        self.firmware = FIRMWARE.read_text(encoding="utf-8")

    def test_flag_and_setter_exist(self):
        self.assertIn("wasteDrainEnabled", self.actuator)
        self.assertRegex(self.actuator, r"void\s+setWasteDrainEnabled\(\s*bool")

    def test_phase_4_skips_rinse_and_drain_when_disabled(self):
        body = re.search(r"case\s+PHASE_4_DOSING:(.+?)break;", self.firmware, re.DOTALL)
        self.assertIsNotNone(body, "PHASE_4_DOSING case not found")
        code = body.group(1)
        self.assertIn("wasteDrainEnabled", code,
                      "Phase 4 must branch on the no-drain flag")
        self.assertRegex(
            code,
            r"PHASE_7_PROBE_PRESERVATION",
            "with the drain off, Phase 4 must go straight to the Phase 7 soak",
        )

    def test_dashboard_command_is_handled(self):
        branch = re.search(
            r'strcmp\(cmd,\s*"SET_DRAIN"\)\s*==\s*0\)\s*\{(.+?)\} else if',
            self.firmware,
            re.DOTALL,
        )
        self.assertIsNotNone(branch, "no SET_DRAIN branch in pollRemoteDashboardCommand()")
        self.assertIn("setWasteDrainEnabled", branch.group(1))


class TestNoDrainServer(unittest.TestCase):

    def setUp(self):
        self._saved = dict(main.current_command)

    def tearDown(self):
        main.current_command = self._saved

    def test_set_drain_keeps_enabled_flag(self):
        main.post_dashboard_command({"command": "SET_DRAIN", "enabled": False})
        self.assertEqual(main.current_command["command"], "SET_DRAIN")
        self.assertIs(main.current_command["enabled"], False)


class TestNoDrainDashboard(unittest.TestCase):

    def test_toggle_sends_set_drain(self):
        html = DASHBOARD.read_text(encoding="utf-8")
        self.assertIn("noDrainMode", html)
        self.assertIn("'SET_DRAIN'", html)


if __name__ == "__main__":
    unittest.main()
