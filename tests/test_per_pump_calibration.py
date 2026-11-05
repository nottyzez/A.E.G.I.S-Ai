# -*- coding: utf-8 -*-
"""
test_per_pump_calibration.py — per-pump flow rates must actually drive dosing.

Calibrating pump B to a different rate must change pump B's runtime and leave
pump A and C alone. This is the regression guard for the defect where
calibrate_pump() wrote pump_flow_rates[key] but compute_dosing() still used the
single global pump_flow_rate.
"""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

# Import exactly as main.py does. Importing `server.dosing_engine` instead would
# build a SECOND module object with its own `dosing_engine` singleton, so a
# calibration applied to one would be invisible to the other.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "server"))
import dosing_engine as engine_module  # noqa: E402
from dosing_engine import TwoTierDosingEngine, DEFAULT_FLOW_RATES  # noqa: E402


class TestPerPumpCalibration(unittest.TestCase):
    def setUp(self):
        # Point persistence at a scratch file: the repo's server/calibration.json
        # holds measurements from whoever last ran the wizard on this machine, and
        # a test that read it would pass here and fail on a clean clone.
        self._tmp = tempfile.TemporaryDirectory()
        self._patcher = mock.patch.object(
            engine_module, "CALIBRATION_FILE", Path(self._tmp.name) / "calibration.json"
        )
        self._patcher.start()
        self.addCleanup(self._patcher.stop)
        self.addCleanup(self._tmp.cleanup)

        self.engine = TwoTierDosingEngine()

    def test_defaults_are_per_pump(self):
        """With no saved file, the engine starts from DEFAULT_FLOW_RATES."""
        self.assertEqual(set(self.engine.pump_flow_rates), {"A", "B", "C"})
        self.assertEqual(self.engine.pump_flow_rates, dict(DEFAULT_FLOW_RATES))

    def test_calibration_survives_a_restart(self):
        """A measured rate must come back after the engine is rebuilt."""
        self.engine.calibrate_pump("A", collected_ml=9.0, test_duration_s=10.0, observed_prime_s=2.0)
        self.assertTrue((Path(self._tmp.name) / "calibration.json").exists())

        reloaded = TwoTierDosingEngine()
        self.assertAlmostEqual(reloaded.pump_flow_rates["A"], 1.125, places=3)

    def test_corrupt_calibration_file_is_ignored(self):
        """A garbage sidecar must not stop the rig from starting."""
        (Path(self._tmp.name) / "calibration.json").write_text("{not json", encoding="utf-8")
        recovered = TwoTierDosingEngine()
        self.assertEqual(recovered.pump_flow_rates, dict(DEFAULT_FLOW_RATES))

    def test_main_and_tests_share_one_singleton(self):
        """main.py and the tests must see the same engine instance.

        main.py imports `dosing_engine` as a bare module; importing
        `server.dosing_engine` builds a second module object with its own
        singleton, so a rate calibrated through one path never reaches the other.
        """
        import main
        import dosing_engine as bare_module

        self.assertIs(main.dosing_engine, engine_module.dosing_engine)
        self.assertIs(main.dosing_engine, bare_module.dosing_engine)

    def test_calibrating_pump_b_changes_only_pump_b(self):
        """Halving pump B's rate must lengthen pump2_ms and leave pumps 1 and 3 alone."""
        baseline = self.engine.compute_dosing(ec=1.20, ph=6.50, temp=26.0, ai_class="Control")
        base1 = baseline["dosing_plan"]["pump1_ms"]
        base2 = baseline["dosing_plan"]["pump2_ms"]
        base3 = baseline["dosing_plan"]["pump3_ms"]
        self.assertGreater(base2, 0, "baseline must dose pump B so the change is observable")

        # 4 mL in 10 s with a 2 s prime -> Q = 4 / 8 = 0.5 mL/s (defaults are 1.5)
        self.engine.calibrate_pump("B", collected_ml=4.0, test_duration_s=10.0, observed_prime_s=2.0)
        self.assertAlmostEqual(self.engine.pump_flow_rates["B"], 0.5, places=3)

        after = self.engine.compute_dosing(ec=1.20, ph=6.50, temp=26.0, ai_class="Control")
        self.assertEqual(after["dosing_plan"]["pump1_ms"], base1, "pump A must not move")
        self.assertEqual(after["dosing_plan"]["pump3_ms"], base3, "pump C must not move")
        self.assertGreater(after["dosing_plan"]["pump2_ms"], base2, "slower pump B must run longer")

    def test_runtime_matches_own_rate(self):
        """pump2_ms must equal prime + (v2 / rate_B), not prime + (v2 / global)."""
        self.engine.calibrate_pump("B", collected_ml=8.0, test_duration_s=10.0, observed_prime_s=2.0)
        res = self.engine.compute_dosing(ec=1.20, ph=6.50, temp=26.0, ai_class="Control")

        prime_ms = res["priming_delay_ms"]
        v2 = res["volumes_ml"]["pump2_ml"]
        rate_b = self.engine.pump_flow_rates["B"]
        expected = min(30000, round(prime_ms + (v2 / rate_b) * 1000))
        self.assertEqual(res["dosing_plan"]["pump2_ms"], expected)

    def test_calibration_reports_all_three_rates(self):
        """get_calibration() must expose the per-pump map so the dashboard can hydrate."""
        cal = self.engine.get_calibration()
        self.assertIn("pump_flow_rates", cal)
        self.assertEqual(set(cal["pump_flow_rates"]), {"A", "B", "C"})

    def test_dose_plan_result_carries_per_pump_rates(self):
        """The compute_dosing payload must show which rate produced each runtime."""
        res = self.engine.compute_dosing(ec=1.20, ph=6.50, temp=26.0, ai_class="Control")
        self.assertIn("pump_flow_rates_ml_s", res)
        self.assertEqual(set(res["pump_flow_rates_ml_s"]), {"A", "B", "C"})

    def test_cap_uses_the_slowest_pump(self):
        """The volume cap must respect the slowest pump, not the average.

        If the cap used a fast pump's rate, the slow pump would be asked for more
        time than the 30 s ceiling allows and the clamp would silently under-dose.
        """
        self.engine.calibrate_pump("C", collected_ml=1.0, test_duration_s=10.0, observed_prime_s=2.0)
        res = self.engine.compute_dosing(ec=0.10, ph=6.50, temp=26.0, ai_class="-K")
        plan = res["dosing_plan"]
        for key in ("pump1_ms", "pump2_ms", "pump3_ms"):
            self.assertLessEqual(plan[key], 30000)


if __name__ == "__main__":
    unittest.main()
