"""
/predict must return `ensemble_class` on both of its paths.

The endpoint logs `result['ensemble_class']`; the DEMO branch sets it but the
real ensemble branch never did, so the first successful inference on the
Droplet (2026-11-06) answered 500 `'ensemble_class'` — the model was right and
only the response key was missing.

The predictor is stubbed so this runs without the 1.2 GB ensemble; what is
under test is `run_ensemble_prediction`'s response mapping, not the model.
"""

import unittest

import cv2
import numpy as np

import main


class _StubPredictor:
    loaded = True
    classes = ["healthy", "nitrogen", "phosphorus", "potassium"]

    def predict_from_topdown_and_sensor(self, **kwargs):
        return {
            "final_class": "nitrogen",
            "final_confidence": 0.91,
            "diagnostic_stage": "SYMPTOMATIC_DEFICIENCY_CONFIRMED",
            "final_class_thai": "ขาดไนโตรเจน",
            "diagnostic_message_thai": "พบอาการขาดไนโตรเจน",
            "fusion_probabilities": {"healthy": 0.02, "nitrogen": 0.91,
                                     "phosphorus": 0.04, "potassium": 0.03},
            "visual_leaf_status": {"class": "nitrogen", "confidence": 0.88},
            "water_sensor_status": {"class": "nitrogen", "confidence": 0.94},
        }


class TestPredictResponseKeys(unittest.TestCase):

    def setUp(self):
        self._real_predictor = main.predictor
        self._real_demo = main.DEMO_MODE
        main.predictor = _StubPredictor()
        main.DEMO_MODE = False

    def tearDown(self):
        main.predictor = self._real_predictor
        main.DEMO_MODE = self._real_demo

    def test_real_ensemble_path_reports_ensemble_class(self):
        ok, buf = cv2.imencode(".png", np.zeros((32, 32, 3), dtype=np.uint8))
        self.assertTrue(ok, "could not build a test image")

        result = main.run_ensemble_prediction(
            image_bytes=buf.tobytes(), ec=1.2, ph=6.5, temp=28.0
        )

        self.assertEqual(result["ensemble_class"], "nitrogen")
        self.assertEqual(result["stage"], "SYMPTOMATIC_DEFICIENCY_CONFIRMED")


if __name__ == "__main__":
    unittest.main(verbosity=2)
