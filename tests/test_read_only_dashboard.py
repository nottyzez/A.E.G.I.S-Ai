"""
`/dashboard?readonly` must stop every mutation from reaching the rig.

Every command goes through `sendApiRequest(endpoint, payload)` — a payload means
a POST, no payload means a GET read. Guarding that one function makes the whole
cockpit read-only without touching a dozen handlers, and a showcase visitor
cannot actuate a pump by pressing a button.
"""

import re
import unittest
from pathlib import Path

DASHBOARD = Path(__file__).resolve().parent.parent / "server" / "static" / "index.html"


class TestReadOnlyDashboard(unittest.TestCase):

    def setUp(self):
        self.html = DASHBOARD.read_text(encoding="utf-8")

    def test_flag_reads_the_query_string(self):
        self.assertRegex(
            self.html,
            r"const\s+VIEW_ONLY\s*=\s*new URLSearchParams\(window\.location\.search\)",
        )

    def test_mutations_are_refused_before_fetch(self):
        body = re.search(r"const\s+sendApiRequest\s*=\s*async[^{]+\{(.+?)const token", self.html, re.DOTALL)
        self.assertIsNotNone(body, "sendApiRequest() not found")
        code = body.group(1)
        self.assertRegex(code, r"if\s*\(\s*VIEW_ONLY\s*&&\s*payload\s*!==\s*undefined\s*\)")

    def test_banner_visible_when_read_only(self):
        self.assertIn("{VIEW_ONLY && (", self.html)


if __name__ == "__main__":
    unittest.main()
