"""
Control-plane auth guard.

The droplet serves the dashboard over a public IP. With AEGIS_REQUIRE_AUTH=1
every browser-facing write endpoint must require `Authorization: Bearer
<CONTROL_TOKEN>`; the device paths (GET /api/command, POST /api/sensor) and all
other reads stay open so the ESP32 needs no re-flash. Auth on with no token
configured must fail closed, not fall open.

No httpx in this environment, so the guard is exercised as a plain function
against stub requests instead of through TestClient.
"""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import main as app_main  # noqa: E402
from fastapi import HTTPException  # noqa: E402

DASHBOARD = PROJECT_ROOT / "server" / "static" / "index.html"


class _Req:
    """Just the two attributes the guard reads."""

    def __init__(self, method, path, token=None):
        self.method = method
        self.url = type("U", (), {"path": path})()
        self.headers = {} if token is None else {"authorization": f"Bearer {token}"}


AUTH_ON = {"AEGIS_REQUIRE_AUTH": "1", "CONTROL_TOKEN": "s3cret"}


class TestControlAuthGuard(unittest.TestCase):

    def _check(self, req, env):
        with patch.dict(os.environ, env, clear=False):
            return app_main.require_control_token(req)

    def test_auth_off_leaves_everything_open(self):
        self._check(_Req("POST", "/api/command"), {"AEGIS_REQUIRE_AUTH": "0"})

    def test_guarded_post_without_token_is_rejected(self):
        with self.assertRaises(HTTPException) as ctx:
            self._check(_Req("POST", "/api/command"), AUTH_ON)
        self.assertEqual(ctx.exception.status_code, 401)

    def test_guarded_post_with_wrong_token_is_rejected(self):
        with self.assertRaises(HTTPException):
            self._check(_Req("POST", "/api/command", token="nope"), AUTH_ON)

    def test_guarded_post_with_right_token_passes(self):
        self._check(_Req("POST", "/api/command", token="s3cret"), AUTH_ON)

    def test_every_browser_write_endpoint_is_guarded(self):
        for path in (
            "/api/command",
            "/api/schedule",
            "/api/override/simulate",
            "/api/calibration",
            "/api/calibration/calculate",
            "/api/calibration/flow/pump1",
            "/api/cam_command",
        ):
            with self.subTest(path=path):
                with self.assertRaises(HTTPException):
                    self._check(_Req("POST", path), AUTH_ON)

    def test_device_paths_stay_open(self):
        """The ESP32 has no token in its flash; these two must not 401 it."""
        self._check(_Req("GET", "/api/command"), AUTH_ON)
        self._check(_Req("POST", "/api/sensor"), AUTH_ON)

    def test_auth_on_without_a_configured_token_fails_closed(self):
        with self.assertRaises(HTTPException):
            self._check(_Req("POST", "/api/command", token=""), {"AEGIS_REQUIRE_AUTH": "1"})

    def test_dashboard_sends_the_token_and_asks_when_refused(self):
        html = DASHBOARD.read_text(encoding="utf-8")
        start = html.index("const sendApiRequest =")
        body = html[start:start + 1400]
        self.assertIn("headers.Authorization = `Bearer ${token}`", body)
        self.assertIn("res.status === 401", body)
        self.assertIn("aegis_control_token", html)


if __name__ == "__main__":
    unittest.main(verbosity=2)
