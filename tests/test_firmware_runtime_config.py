"""
Firmware network config is runtime-settable, not compile-time only.

A presentation on a phone hotspot gets its server IP by DHCP and may use a
different SSID than the lab. If those are baked in with #define, moving the rig
means recompiling at the venue — which this laptop has already failed to do
(cc1plus OOM). Both sketches must therefore read NVS first and accept the
`SET WIFI` / `SET SERVER` serial commands.

Reads only tracked files: config.h is gitignored.
"""

import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIRMWARE = PROJECT_ROOT / "firmware"

SKETCHES = (
    FIRMWARE / "esp32_main" / "esp32_main.ino",
    FIRMWARE / "esp32_cam" / "esp32_cam.ino",
)
TEMPLATES = (
    FIRMWARE / "esp32_main" / "config.example.h",
    FIRMWARE / "esp32_cam" / "config.example.h",
)


class TestFirmwareRuntimeConfig(unittest.TestCase):

    def test_both_sketches_read_nvs_overrides(self):
        for sketch in SKETCHES:
            src = sketch.read_text(encoding="utf-8")
            self.assertIn("#include <Preferences.h>", src, f"{sketch.name}: no NVS include")
            self.assertIn("loadRuntimeConfig", src, f"{sketch.name}: NVS never loaded")
            # setup() must load NVS before any capture round runs
            setup_start = src.index("void setup()")
            setup_body = src[setup_start:src.index("\n}", setup_start)]
            self.assertIn("loadRuntimeConfig();", setup_body,
                          f"{sketch.name}: NVS is never loaded in setup()")

    def test_serial_set_commands_preserve_case(self):
        """SSIDs and passwords are case-sensitive; an uppercase pass of the
        whole line would silently produce wrong credentials."""
        for sketch in SKETCHES:
            src = sketch.read_text(encoding="utf-8")
            for cmd in ('"SET WIFI "', '"SET SERVER "'):
                self.assertIn(cmd, src, f"{sketch.name}: missing {cmd} handler")
            self.assertIn("String raw = Serial.readStringUntil", src)
            self.assertIn("raw.substring(9)", src, f"{sketch.name}: SSID is uppercased")
            self.assertIn("raw.substring(11)", src, f"{sketch.name}: host is uppercased")

    def test_ssid_and_password_may_contain_spaces(self):
        """A phone hotspot is commonly called "Samsung S30 Ultra" — SET WIFI
        splits on the first space, so it would store "Samsung" and the rest as
        the password, and the board would fail to join with no useful error.
        SET SSID / SET PASS take the whole rest of the line instead."""
        for sketch in SKETCHES:
            src = sketch.read_text(encoding="utf-8")
            self.assertIn('input.startsWith("SET SSID ")', src,
                          f"{sketch.name}: no SET SSID handler")
            self.assertIn('input.startsWith("SET PASS ")', src,
                          f"{sketch.name}: no SET PASS handler")

            ssid_start = src.index('input.startsWith("SET SSID ")')
            ssid_body = src[ssid_start:src.index("ESP.restart()", ssid_start)]
            # the whole remainder, not a split on the first space
            self.assertIn("raw.substring(9)", ssid_body,
                          f"{sketch.name}: SET SSID does not take the whole line")
            self.assertNotIn("indexOf(' ')", ssid_body,
                             f"{sketch.name}: SET SSID still splits on a space")

            pass_start = src.index('input.startsWith("SET PASS ")')
            pass_body = src[pass_start:src.index("ESP.restart()", pass_start)]
            self.assertIn('prefs.putString("pass"', pass_body)

    def test_wifi_uses_the_stored_credentials(self):
        for sketch in SKETCHES:
            src = sketch.read_text(encoding="utf-8")
            start = src.index("void connectWiFi")
            body = src[start:src.index("\n}", start)]
            self.assertIn("cfgSsid.c_str()", body, f"{sketch.name}: connect uses the #define")
            self.assertNotIn("WiFi.begin(WIFI_SSID", body)

    def test_reconnects_after_a_late_hotspot(self):
        """The board is usually powered before the hotspot is up."""
        for sketch in SKETCHES:
            self.assertIn("WiFi.setAutoReconnect(true)", sketch.read_text(encoding="utf-8"))

        # The main board stays connected, so it needs an idle retry. The CAM
        # powers the radio off between rounds and reconnects each round.
        main_src = SKETCHES[0].read_text(encoding="utf-8")
        self.assertIn("lastWifiRetry", main_src)
        cam_src = SKETCHES[1].read_text(encoding="utf-8")
        round_start = cam_src.index("void runCaptureRound()")
        round_body = cam_src[round_start:cam_src.index("\n}", round_start)]
        self.assertIn("connectWiFi();", round_body,
                      "CAM: each capture round must bring the radio up again")

    def test_url_templates_are_no_longer_baked_in(self):
        """The URL_* / PREDICT_URL macros would silently override NVS if a
        future edit went back to using them."""
        for template in TEMPLATES:
            src = template.read_text(encoding="utf-8")
            self.assertNotIn('"http://" SERVER_HOST', src,
                             f"{template.name}: URL still baked at compile time")

    def test_port_is_settable_over_serial(self):
        """A Droplet serves through Nginx on 80, not 8000. A compile-time port
        would leave the board dialing a closed port, and HTTPClient reports a
        connection error that looks like a dead server."""
        for sketch in SKETCHES:
            src = sketch.read_text(encoding="utf-8")
            self.assertIn('prefs.getString("port"', src,
                          f"{sketch.name}: port is not persisted in NVS")
            self.assertNotIn("+ String(SERVER_PORT) +", src,
                             f"{sketch.name}: apiUrl still uses the compile-time port")
            # SET SERVER <host> [port]
            start = src.index('input.startsWith("SET SERVER ")')
            body = src[start:src.index("ESP.restart()", start)]
            self.assertIn('prefs.putString("port"', body,
                          f"{sketch.name}: SET SERVER does not store a port")


if __name__ == "__main__":
    unittest.main()
