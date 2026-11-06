"""
LAN backup server bundle (`deploy/lan-backup/`).

This is deliberately separate from `deploy/digitalocean/`: the backup runs on a
laptop that is a *client* of the AEGIS hotspot — no Docker, no Nginx, port 8000
instead of 80, and no control token. The tests below pin the two things that
broke while getting it to start by hand: `python main.py` dies with
"lost sys.stderr" on that machine (the uvicorn CLI form does not), and the
scripts must not drift onto the droplet's port.
"""

import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BUNDLE = PROJECT_ROOT / "deploy" / "lan-backup"


class TestLanBackupBundle(unittest.TestCase):

    def test_start_script_uses_the_uvicorn_cli_form_on_port_8000(self):
        start = (BUNDLE / "start-backup.bat").read_text(encoding="utf-8")
        # PowerShell arg list: '-m','uvicorn','main:app'
        for token in ("'-m'", "'uvicorn'", "'main:app'", "0.0.0.0", "8000"):
            self.assertIn(token, start)
        # `python main.py` closes stderr after the model loads on this machine.
        self.assertNotIn("python main.py", start)

    def test_stop_script_frees_the_same_port(self):
        stop = (BUNDLE / "stop-backup.bat").read_text(encoding="utf-8")
        self.assertIn("8000", stop)
        self.assertIn("taskkill", stop)

    def test_readme_names_both_hosts_and_why_they_differ(self):
        readme = (BUNDLE / "README.md").read_text(encoding="utf-8")
        self.assertIn("10.187.70.201", readme)
        self.assertIn("165.245.191.33", readme)
        self.assertIn("SET SERVER", readme)
        # No token on the LAN: AEGIS_REQUIRE_AUTH stays 0 locally.
        self.assertIn("AEGIS_REQUIRE_AUTH", readme)


if __name__ == "__main__":
    unittest.main(verbosity=2)
