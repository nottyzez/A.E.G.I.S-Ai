"""
The ensemble must fail loudly when its pickles did not load.

On the Droplet (2026-11-06) `_load()` swallowed an unpickling error, so
`main.predictor` looked alive while `self.scalers` stayed `None`; `/predict`
then died deep inside `predict_vision_patch_batch` with the opaque
"'NoneType' object is not subscriptable". A caller cannot tell that apart from
a real model bug, so `_load` must record why it failed and every inference
entry point must refuse to run without it.
"""

import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "Ai มหาปลัย" / "model"))


class TestEnsembleLoadGuard(unittest.TestCase):

    def test_inference_refuses_to_run_when_the_model_files_are_missing(self):
        import numpy as np
        import predict_ensemble as pe

        with tempfile.TemporaryDirectory() as empty_dir:
            predictor = pe.HydroponicEnsemblePredictor(model_dir=Path(empty_dir))
            self.assertFalse(predictor.loaded)

            with self.assertRaises(RuntimeError) as caught:
                predictor.predict_from_topdown_and_sensor(
                    img_bgr=np.zeros((64, 64, 3), dtype=np.uint8),
                    ec=1.2,
                    ph=6.5,
                    water_temp=28.0,
                )

        self.assertIn("not loaded", str(caught.exception))
        self.assertIn("missing", str(caught.exception).lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
