"""Check every all-caps identifier used by tracked firmware is defined somewhere.

`config.h` is gitignored; only `config.example.h` ships. A macro defined solely in
`config.h` compiles here and fails on a clean clone, so the template is the reference.

Comments and string literals are stripped in one pass first — otherwise `"http://"`
loses its tail to the `//` comment rule, the unterminated quote swallows the next line,
and a real `#define` on that line disappears from the set.
"""

import re
from pathlib import Path

FIRMWARE_DIR = Path(__file__).resolve().parent.parent / "firmware" / "esp32_main"


def strip_comments_and_strings(src: str) -> str:
    out = []
    i, n = 0, len(src)
    while i < n:
        c = src[i]
        if c == "/" and i + 1 < n and src[i + 1] == "/":
            while i < n and src[i] != "\n":
                i += 1
        elif c == "/" and i + 1 < n and src[i + 1] == "*":
            i += 2
            while i + 1 < n and not (src[i] == "*" and src[i + 1] == "/"):
                i += 1
            i += 2
        elif c in "\"'":
            quote = c
            i += 1
            while i < n:
                if src[i] == "\\":
                    i += 2
                    continue
                if src[i] == quote:
                    i += 1
                    break
                i += 1
        else:
            out.append(c)
            i += 1
    return "".join(out)


def main() -> int:
    template = (FIRMWARE_DIR / "config.example.h").read_text(encoding="utf-8")
    defined = set(re.findall(r"^\s*#define\s+(\w+)", template, re.M))

    used = set()
    sources = list(FIRMWARE_DIR.glob("*.ino")) + list(FIRMWARE_DIR.glob("*.h"))
    for path in sources:
        if path.name == "config.h":  # gitignored: never the reference
            continue
        used |= set(re.findall(r"\b([A-Z][A-Z0-9_]{2,})\b", strip_comments_and_strings(path.read_text(encoding="utf-8"))))

    # An identifier is fine if it is defined anywhere in tracked firmware, not just the
    # template: include guards, CyclePhase enum members and local consts all live in the
    # tracked sources. Only what is defined NOWHERE is a clean-clone compile break.
    declared = set()
    for path in sources:
        if path.name == "config.h":
            continue
        body = strip_comments_and_strings(path.read_text(encoding="utf-8"))
        declared |= set(re.findall(r"#define\s+(\w+)", body))
        # `const unsigned long NAME = ...` — the type may be several words.
        declared |= set(re.findall(r"\bconst\s+(?:\w+\s+)+([A-Z][A-Z0-9_]{2,})\s*=", body))
        # enum members: every CAPS token inside an enum block
        for block in re.findall(r"enum\b[^{]*\{([^}]*)\}", body):
            declared |= set(re.findall(r"\b([A-Z][A-Z0-9_]{2,})\b", block))

    # Provided by the Arduino/ESP32 core (WiFi.h, Arduino.h, esp32-hal-gpio.h). They are
    # not in this repo by design, so their absence from the template is not a defect.
    core_api = {
        "GET", "POST", "HIGH", "LOW", "OUTPUT", "INPUT", "INPUT_PULLUP",
        "WIFI_STA", "WL_CONNECTED", "LED_BUILTIN", "SERIAL_8N1",
    }

    unresolved = sorted(used - defined - declared - core_api)
    if not unresolved:
        print(
            f"OK: no identifier used by tracked firmware is undefined "
            f"({len(defined)} defines in the template)"
        )
        return 0

    print("UNRESOLVED — used by tracked firmware, defined in neither the template nor a tracked source:")
    for name in unresolved:
        print("  ", name)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
