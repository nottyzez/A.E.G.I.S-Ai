#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compile the dashboard's Babel block with a real JSX parser.

`server/static/index.html` has no build step: React 18 + Babel standalone transform
the inline `<script type="text/babel">` at page load. A structural test can assert
on source text, but only a parser can prove the JSX is still well-formed after an
edit — brace-balance heuristics pass on code that Babel rejects.

Exits 0 when the block compiles, 1 when it does not (printing esbuild's message),
and 2 when esbuild itself is unavailable (so a caller can tell "broken JSX" from
"no tooling" rather than reading both as a pass).
"""

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INDEX_HTML = PROJECT_ROOT / "server" / "static" / "index.html"

BABEL_OPEN = '<script type="text/babel">'
BABEL_CLOSE = "</script>"


def extract_babel_block(html: str) -> str:
    start = html.index(BABEL_OPEN) + len(BABEL_OPEN)
    end = html.index(BABEL_CLOSE, start)
    return html[start:end]


def main() -> int:
    html = INDEX_HTML.read_text(encoding="utf-8")
    block = extract_babel_block(html)

    npx = shutil.which("npx")
    if not npx:
        print("SKIP: npx not found — cannot compile JSX", file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "dashboard.jsx"
        source.write_text(block, encoding="utf-8")
        outfile = Path(tmp) / "out.js"
        proc = subprocess.run(
            [npx, "--yes", "esbuild", f"--outfile={outfile}", str(source)],
            capture_output=True,
            text=True,
        )

    if proc.returncode != 0:
        # esbuild's own diagnostic is the useful part; everything from the
        # "node:child_process" traceback onward is the npx wrapper reporting the
        # same failure a second time. Keep the former, drop the latter.
        diagnostic = proc.stderr.split("\nnode:child_process")[0].strip()
        print("FAIL: the Babel block does not compile as JSX", file=sys.stderr)
        print(diagnostic, file=sys.stderr)
        return 1

    lines = block.count("\n") + 1
    print(f"OK: JSX compiles ({lines} lines, {len(block):,} chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
