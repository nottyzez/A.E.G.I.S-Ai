#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Behavioural test for the hand-written MotionShim in index.html.

The shim stands in for framer-motion inside the single-file dashboard, so it is
plain JS with no test runner around it. This test extracts the `MotionShim`
IIFE from the page, runs it in Node against a fake rAF clock, and asserts what
the segmented control depends on: starting a new animation on a motion value
must cancel the one already driving it, and `.stop()` must actually stop it.
"""

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INDEX_HTML = PROJECT_ROOT / "server" / "static" / "index.html"

OPEN = "const MotionShim = (() => {"
CLOSE = "\n    })();"

HARNESS = """
const useState = i => [typeof i === 'function' ? i() : i, () => {}];
const useRef = v => ({ current: v });
const useEffect = () => {};
let now = 0, nextId = 1;
const queue = new Map();
globalThis.requestAnimationFrame = cb => { const id = nextId++; queue.set(id, cb); return id; };
globalThis.cancelAnimationFrame = id => queue.delete(id);
globalThis.performance = { now: () => now };
globalThis.window = { matchMedia: () => ({ matches: false }) };
function tick(ms) {
  now += ms;
  const due = [...queue.entries()];
  queue.clear();
  for (const [, cb] of due) cb(now);
}

__SHIM__

const { animate, useMotionValue } = MotionShim;
const v = useMotionValue(0);
animate(v, 100, { duration: 1 });
tick(300);
const midway = v.get();

// A newer animation starts before the old one finished — as when the operator
// flicks the thumb and then clicks another chip.
animate(v, 0, { duration: 0.19 });
tick(190);
tick(600);
const afterNewer = v.get();

const w = useMotionValue(0);
animate(w, 100, { duration: 1 });
tick(200);
w.stop();
const atStop = w.get();
tick(900);

console.log(JSON.stringify({ midway, afterNewer, atStop, afterStop: w.get() }));
"""


class TestMotionShim(unittest.TestCase):
    def _run(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("node is not installed")
        html = INDEX_HTML.read_text(encoding="utf-8")
        start = html.index(OPEN)
        end = html.index(CLOSE, start) + len(CLOSE)
        shim = html[start:end].strip() + ";"
        script = HARNESS.replace("__SHIM__", shim)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "shim.mjs"
            path.write_text(script, encoding="utf-8")
            out = subprocess.run(
                [node, str(path)], capture_output=True, text=True, timeout=60
            )
        self.assertEqual(out.returncode, 0, out.stderr)
        return json.loads(out.stdout.strip().splitlines()[-1])

    def test_newer_animation_wins_on_the_same_motion_value(self):
        r = self._run()
        self.assertAlmostEqual(r["midway"], 30, delta=12)
        self.assertAlmostEqual(
            r["afterNewer"], 0, delta=1,
            msg="a superseded animation kept writing: the thumb lands on the old slot",
        )

    def test_stop_halts_the_running_animation(self):
        r = self._run()
        self.assertAlmostEqual(r["atStop"], 20, delta=12)
        self.assertAlmostEqual(
            r["afterStop"], r["atStop"], delta=1,
            msg="stop() did not cancel the rAF loop",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
