"""
Camera test-mode vs real-mode.

Test mode archives a frame for framing/lighting checks and must NOT run the
ensemble; real mode must. The mode travels dashboard -> /api/cam_command ->
firmware -> /predict as a multipart field. Firmware and dashboard halves are
checked structurally; the server half is exercised directly (no httpx here, so
no TestClient).
"""

import asyncio
import io
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import main as app_main  # noqa: E402
from starlette.datastructures import UploadFile  # noqa: E402

CAM_SKETCH = PROJECT_ROOT / "firmware" / "esp32_cam" / "esp32_cam.ino"
CAM_CONFIG = PROJECT_ROOT / "firmware" / "esp32_cam" / "config.example.h"
MAIN_CONFIG = PROJECT_ROOT / "firmware" / "esp32_main" / "config.example.h"
DASHBOARD = PROJECT_ROOT / "server" / "static" / "index.html"


def _upload(data=b"\xff\xd8fake-jpeg-bytes"):
    return UploadFile(file=io.BytesIO(data), filename="topdown.jpg")


class TestCamCommandCarriesMode(unittest.TestCase):

    def test_mode_survives_the_queue(self):
        app_main.post_cam_command({"command": "CAPTURE", "mode": "test"})
        pending = app_main.get_pending_cam_command()
        self.assertEqual(pending["command"], "CAPTURE")
        self.assertEqual(pending["mode"], "test")
        # consumed exactly once
        self.assertEqual(app_main.get_pending_cam_command()["command"], "IDLE")

    def test_mode_defaults_to_real(self):
        app_main.post_cam_command({"command": "CAPTURE"})
        self.assertEqual(app_main.get_pending_cam_command()["mode"], "real")


class TestPredictModes(unittest.TestCase):

    def _run(self, mode, side_effect):
        tmpdir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmpdir, True)
        static = tmpdir / "static"
        static.mkdir()
        with patch.object(app_main, "TEST_CAPTURES_DIR", tmpdir), \
             patch.object(app_main, "STATIC_DIR", static), \
             patch.object(app_main, "run_ensemble_prediction", side_effect=side_effect) as ens:
            result = asyncio.run(app_main.predict(
                image=_upload(), device_id="cam-test", mode=mode))
        return result, ens, tmpdir

    def test_test_mode_stores_the_frame_without_running_the_ai(self):
        result, ens, tmpdir = self._run("test", lambda **kw: self.fail("ensemble ran in test mode"))
        ens.assert_not_called()
        self.assertEqual(result["status"], "test_only")
        self.assertEqual(result["mode"], "test")
        saved = tmpdir / Path(result["saved_test_file"]).name
        self.assertTrue(saved.exists(), "test capture was not written to disk")

    def test_real_mode_runs_the_ai(self):
        fake = {"ensemble_class": "Control", "stage": "healthy"}
        result, ens, _ = self._run("real", lambda **kw: dict(fake))
        ens.assert_called_once()
        self.assertEqual(result["ensemble_class"], "Control")


class TestFirmwareAndUiHalves(unittest.TestCase):

    def test_firmware_sends_the_mode_field(self):
        src = CAM_SKETCH.read_text(encoding="utf-8")
        self.assertIn('name=\\"mode\\"', src)

    def test_firmware_powers_the_radio_only_for_a_capture_round(self):
        src = CAM_SKETCH.read_text(encoding="utf-8")
        self.assertIn("WiFi.mode(WIFI_OFF)", src)
        self.assertIn("esp_light_sleep_start", src)
        # the old 1.5 s command poll is what kept the board hot
        self.assertNotIn(">= 1500", src)

    def test_camera_is_down_between_rounds(self):
        """Left initialised, the sensor's DMA fills both frame buffers during the
        15 s idle wait — the log fills with "cam_hal: FB-OVF" and the board
        stays hot with the radio already off."""
        src = CAM_SKETCH.read_text(encoding="utf-8")
        # setup() must not init the camera; runCaptureRound() owns its lifetime
        setup_start = src.index("void setup()")
        setup_body = src[setup_start:src.index("\n}", setup_start)]
        self.assertNotIn("initCamera();", setup_body,
                         "camera is initialised in setup(); it must be up only during a round")
        self.assertIn("initCamera();", src, "runCaptureRound lost its camera init")
        # and the sensor is released before the idle wait
        round_start = src.index("void runCaptureRound()")
        round_body = src[round_start:src.index("\n}", round_start)]
        self.assertIn("esp_camera_deinit();", round_body,
                      "runCaptureRound must release the camera before idling")
        # WHEN_EMPTY parks the DMA once the buffers are full
        self.assertIn("CAMERA_GRAB_WHEN_EMPTY", src,
                      "CAMERA_GRAB_LATEST floods the buffers when idle")

    def test_sleep_settings_are_configurable(self):
        cam = CAM_CONFIG.read_text(encoding="utf-8")
        self.assertIn("#define SLEEP_INTERVAL_S", cam)
        self.assertIn("#define CAM_SLEEP_ENABLED", cam)
        main = MAIN_CONFIG.read_text(encoding="utf-8")
        self.assertIn("#define ENABLE_AUTO_LIGHT_SLEEP", main)

    def test_dashboard_offers_both_modes(self):
        html = DASHBOARD.read_text(encoding="utf-8")
        self.assertIn("handleTriggerCamCapture('test')", html)
        self.assertIn("handleTriggerCamCapture('real')", html)


if __name__ == "__main__":
    unittest.main()
