# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A.E.G.I.S. — a symptom-gated ensemble pipeline that classifies nitrogen/phosphorus/potassium deficiency in hydroponic water spinach (ผักกาด/ผักบุ้ง) from camera images plus sensor readings, and drives peristaltic nutrient dosing on an ESP32-S3 rig.

## Commands

```bash
python main.py                      # FastAPI server on :8000 (dashboard at /dashboard)
python scripts/verify_figma_implementation.py   # 26 structural UI checks; must stay 26/26
python -m unittest discover -s tests -p "test_*.py"   # full suite (unittest, not pytest)
python -m unittest tests.test_dashboard_overhaul -v   # one module
```

There is no build step for the frontend: `server/static/index.html` is a single self-contained file using React 18 + Babel standalone from CDN, Tailwind from CDN, and Three.js r128.

## Architecture

- `main.py` — FastAPI app; in-memory `current_hardware_status` dict is the single source of dashboard state. Endpoints: `/api/sensor` (ESP32 telemetry), `/api/command` (GET = ESP32 polls, POST = dashboard queues), `/api/status` (GET = dashboard polls), `/api/schedule`, `/api/override/simulate`, `/api/calibration*`, `/api/cam_command`.
- `server/dosing_engine.py` — `TwoTierDosingEngine`. Factor 1 = total volume from EC deficit; Factor 2 = N/P/K ratios from the AI class; plus priming-delay compensation `t = t_prime + V/Q`. Global `dosing_engine` singleton.
- `server/static/index.html` — the entire dashboard: `HomeView`, `AnalyzeTabView`, `ElectronicControlTabView`, `App`, plus React Bits components (JellyRadio, BranchedMenu, AnimatedContent, MagicBento) and inline SVG icons.
- `firmware/esp32_main/` — Arduino sketch; `actuator_controller.h` holds the relay/FSM class, `config.h` holds credentials (gitignored), `config.example.h` is the tracked template.
- `firmware/esp32_cam/` — separate capture-and-upload sketch.

## Gotchas

- **`firmware/*/config.h` is gitignored** (WiFi password inside). Changes to constants must also land in `config.example.h`, and tests should assert against the example file — a test reading only `config.h` passes locally and fails on a clean clone.
- **Dashboard commands must be handled in firmware.** `JUMP_PHASE` and `MANUAL_DOSE` were sent by the UI but unhandled by firmware until 2026-11-03; when adding a dashboard control, add its `strcmp(cmd, ...)` branch too.
- **Manual relay overrides are non-blocking.** `manualTriggerRelay()` records a window; `updateManualOverrides(now)` must be called every `loop()`. Never reintroduce `delay()` in the actuator class.
- **Pump runtime ceiling is 30 000 ms** and is duplicated in **five** places: `firmware/esp32_main/config.h` (`MAX_SAFETY_DOSING_MS`), `server/dosing_engine.py` (`MAX_PUMP_DURATION_MS`), `main.py`'s `calc_ms`, and two in `server/static/index.html` — `calcPumpMs` (dosing deck mL→ms) and `calcMs` inside `computeLocalTwoFactorDosing` (the Control page's offline dose preview). Change all five together, or the preview silently disagrees with the hardware.
- **`file://` must work.** Every fetch goes through `sendApiRequest`, which short-circuits when `window.location.protocol === 'file:'`. Assets go through `window.__AEGIS_ASSET_RESOLVER__`.
- **A referenced asset must be tracked.** `server/static/back.jpg` (the Home backdrop) was referenced for two tasks before anyone noticed it had never been added to git — tests passed locally and a clean clone 404'd the hero. Same failure shape as the gitignored `config.h` above: before asserting on an asset, confirm `git ls-files` lists it.
- **All Thai plant terminology is ผักบุ้ง (Water Spinach).** Never ผักกาด.
- Chart spline points are drawn between x=20 and x=540 in a 560-wide viewBox; pointer→index mapping must invert that inset, not the raw element ratio.

## Current work (2026-11-05)

**UI pass (2026-11-06, commit `ea401e4`).** Eleven React Bits components
landed in `server/static/index.html`, each wrapped in its own IIFE
(`const X = (() => { ... })()`) so their private helpers (`clamp`, `compile`,
`link`, `VERTEX`, `FONT`) cannot collide. Home's `back.jpg` photograph is
gone; the hero is `GradientASCII` + `Particles` + `TechText` + `Crosshair` +
`SpecularButton`. `ElectronicControlTabView` is now four sub-tabs
(`controlSubTab`: pumps / vision / simulation / pinout) — all five
`id="settings-*"` strings survive, the pinout `<details>` moved into its own
`<section id="settings-pinout">`. **There is no framer-motion or GSAP CDN
tag**: `MotionShim` (~150 lines, `animate`/`cubicBezier`/`useInView`/
`useMotionValue`/`useTransform`/`useReducedMotion`/`motion`) and `gsap.to()`
shim the API subset those components call. `file://` still works, and
`check_jsx.py` still gates. Three suites
(`test_figma_r1_r2_r3_reviewer`, `test_figma_r2_independent_stress`,
`test_figma_r3_independent_audit`) plus `verify_figma_implementation.py` used
to assert the photographic backdrop; they now assert the ASCII/particle hero,
which is why verify stayed at 26/26. New tests: `tests/test_control_ux_cleanup.py`
(7, incl. "no `text-[10px]`/`text-[11px]` in ElectronicControlTabView") and
`tests/test_motion_shim.py` (2 — runs the extracted shim IIFE in Node against a
fake rAF clock; it pins that a newer tween on a motion value cancels the older
one and that `.stop()` really stops). **The cursor spotlight is global, not
per-grid** (`e33418c`): `MagicBento`'s own pointer engine only sees cards inside
its wrapper, so `App` runs a document-level rAF loop that sets `--mb-x`/`--mb-y`/
`--mb-hot` on *every* `.magic-bento-card`, re-querying each frame (Analyze cards
never sit inside a `<MagicBento>` wrapper, so their spotlight was dead before).
It deliberately applies **no** `--mb-tilt-*`/`--mb-magnet-*`: a transform shifts
`getBoundingClientRect()`, and the chart's pointer → index mapping depends on that
rect. It is disabled under `prefers-reduced-motion`, and a touch gets a 700 ms
flash on tap (there is no hover on a phone). `test_5_every_bento_card_can_light_up` fails if a card loses its
`<span className="magic-bento__light">` child. Suite is **238 tests OK**. Relay Thai roles follow
`firmware/esp32_main/config.example.h` (GPIO 6 = sample return), not the
spec's air-agitator label.

**The automatic cycle is back to the full 8 phases: P0 → P1 → P2 → P3 → P4 →
P5 (Probe Rinse, GPIO 7) → P6 (Drain Waste, GPIO 8) → P7 → IDLE.**
Phase 5/6 were skipped in `d92a2bf` after the GPIO 7 pump brown-out; that pump's
reversed flyback diode was the fault, not the pump, so the rinse was re-linked
on 2026-11-05 (working tree, uncommitted) and **verified on the rig the same
day: GPIO 7 runs clean with no brown-out**. `test_11` in
`tests/test_chamber_fsm_preservation.py` now pins the full chain. The Control
page's demo deck is still the 5-step version that dropped its rinse+drain card
(that card fired GPIO 7 and GPIO 8 together — the combination that browns out
the 12 V rail); it needs the firmware's separated sequence, not that old card.

**Flow calibration (2026-11-05, measured on the rig).** Peristaltic A/B/C =
**1.0 mL/s each** (`DEFAULT_FLOW_RATE` in `server/dosing_engine.py`, and the
three 1.5 fallbacks in `index.html`). This **halves** every dose runtime for the
same mL — `MANUAL_DOSE` and the local preview agree because both read it.
Diaphragms: GPIO 5 = 30 mL/s, GPIO 6 = 38 mL/s, GPIO 7 = 30 mL/s, recorded as
`DIAPHRAGM{1,2,3}_ML_S` in `config.example.h`. Target volumes: chamber
fill/return/rinse **and the standby soak** are all 300 mL (the soak must submerse
the pH bulb too). Phase timings re-derived from those rates: **P0 8 000, P1
10 000, P3 8 000, P5 10 000, P7 10 000 ms** (P2 settling 3 000 and P6 drain
6 000 unchanged — drain is gravity, flow-independent). **P0 must return exactly
what P7 leaves behind** (300 mL @ 38 mL/s = 8 000 ms); shrink P0 without
shrinking P7 and water accumulates in the chamber every cycle.
`setPhase()` now clamps P0/P1/P3/P5/P7 at `MAX_SAFETY_PUMP_MS` (15 000) — that
macro was declared but never enforced until 2026-11-05. `test_12` fails if any
`TIME_*` diaphragm runtime exceeds it, so raising a phase time means raising the
ceiling in the same edit. The firmware never computes these from flow itself; the mL/s
values are documentation a human re-derives the times from. `docs/chamber_operation_guide.md`
is synced. **The poster is frozen:** it was printed and submitted before this
calibration, and `scripts/generate_poster_blueprints.py` still emits the old
4/6/7/5/3 s timings on purpose. Do not regenerate it to match the firmware.

**The ESP32-S3 needs re-flashing** for both the phase chain and these timings.

**DigitalOcean deployment bundle (2026-11-05, uncommitted).** Only the
*infrastructure* workstream of the cloud plan is done — `Dockerfile`,
`.dockerignore`, `docker-compose.digitalocean.yml`, `deploy/digitalocean/{nginx.conf,
.env.example,setup_droplet.sh}`, `docs/digitalocean_deployment_guide.md`, pinned
by `tests/test_digitalocean_cloud_backend.py`. The cloud broker
(`server/cloud_broker.py`), the state store, the firmware ACK/auth path and the
UI cockpit are **not** implemented; `AEGIS_REQUIRE_AUTH` defaults to 0 and
nothing reads `CONTROL_TOKEN`/`DEVICE_API_KEY` yet. So the deployed URL exposes
every pump button to anyone who loads it — do not leave a Droplet running
unattended with the rig attached. `CONTROL_TOKEN` is in `.env.example` only;
the real `.env` is gitignored (`*.env`).

**Network config is now runtime, not compile-time (2026-11-05, uncommitted).**
The presentation runs on a phone hotspot, where the laptop's IP comes from
DHCP and the SSID differs from the lab. Both sketches therefore read
`Preferences` (NVS namespace `aegis`) at boot and accept serial commands:
`SET WIFI <ssid> <password>`, `SET SERVER <ip> [port]`, `SHOW`, `RESET`. The
`config.h` values are only the fallback when NVS is empty. Endpoints are built
by `apiUrl()` at runtime — the `URL_*` / `PREDICT_URL` macros are gone from
both `config.example.h` files (a local `config.h` still defining them is now
dead text). `WiFi.setAutoReconnect(true)` plus a 5 s `WiFi.reconnect()` in
`loop()` cover the board booting before the hotspot. Pinned by
`tests/test_firmware_runtime_config.py`. **Both boards still need one flash**
for this code; after that the SSID/host/port are changeable over serial (115200) with
no compiler — the presentation laptop has run out of RAM mid-compile before.

**The port is NVS too (2026-11-06).** `SET SERVER <host> [port]` stores both;
`apiUrl()` reads `cfgPort` instead of `SERVER_PORT`, which is now only the
fallback default. This matters because a Droplet serves through Nginx on **80**
while a laptop running `main.py` serves on **8000** — a compile-time port would
have left the board dialing a closed port and reporting a connection error that
looks like a dead server. `SHOW` prints `IP:PORT`; check it before every run.

State: 227 tests OK, verify_figma 26/26, check_jsx OK.

**Everything is committed and pushed (2026-11-06).** Branch
`feature/dashboard-overhaul` is at `aeec72b` on origin, tracking is set. Three
commits: `d2a62a5` (firmware runtime network config, CAM power + modes,
port override), `077e24e` (DigitalOcean bundle + `scripts/check_jsx.py`),
`aeec72b` (poster blueprints, plans, notes). A clean clone on another path was
checked: neither `config.h` nor `.env` leaks, and both `#ifndef` fallbacks
survive, so the sketches compile from the clone. **The stack that has NOT been
re-verified is the clean clone's test suite** — the run was blocked as
external code; run it yourself in an empty clone before trusting the deploy.

**ESP32-CAM power + two capture modes (2026-11-05, uncommitted).** The board
ran hot because `loop()` polled `/api/cam_command` every 1.5 s forever. The
radio is now powered only for a capture round: `runCaptureRound()` brings WiFi
up, polls once, captures if a command is queued or the auto interval elapsed,
then `WiFi.disconnect(true)` + `WiFi.mode(WIFI_OFF)`. Between rounds the board
`esp_light_sleep_start()`s for `SLEEP_INTERVAL_S` (15 s) — light sleep, not
deep, so the USB CDC port stays enumerated and `SET WIFI`/`SET SERVER` still
work. Two modes now travel dashboard → `/api/cam_command` (`mode`) → firmware
→ `/predict` (multipart field `mode`): **`test`** stores the image in
`captured/test_captures/` and returns `{"status":"test_only"}` **without**
running the ensemble; **`real`** runs the AI exactly as before. `/predict`
always ran the AI, so "test mode" is a server-side early return, not a new
pipeline. `captureAndUpload()` discards one frame after wake (the sensor's XCLK
stops during sleep) and re-inits the camera if the grab still fails. The main
board added `ENABLE_AUTO_LIGHT_SLEEP` (`esp_pm_configure`); if the core lacks
`CONFIG_PM_ENABLE` the boot log says so and nothing else changes. Both macros
have `#ifndef` fallbacks in the sketches, so a gitignored `config.h` copied
before this change still compiles. Pinned by `tests/test_cam_modes.py`.

**Flash note:** the CAM board now waits up to 15 s for a dashboard button —
the operator must hold the pose until the status line says it captured.

### Prior state (2026-11-04)

Branch `feature/dashboard-overhaul` — **all 11 tasks of `docs/superpowers/plans/2026-11-03-dashboard-overhaul.md` are implemented and committed** (`84e9320..60b4964`), and the final whole-branch review's four must-fix findings are fixed (`d2c2576..d2e246d`). Full suite: **199 tests, OK** (189 tracked + 10 in `tests/test_chamber_fsm_preservation.py`, now tracked). `scripts/verify_figma_implementation.py`: **26/26** — and the script is now committed, so `git show HEAD:scripts/verify_figma_implementation.py` scores 26/26 too.

- Landed: non-blocking relay override, `JUMP_PHASE`/`MANUAL_DOSE` handling + 30 s ceiling (firmware/server/UI), per-pump flow calibration (`POST /api/calibration/flow/{pump_key}`), simplified Home, All Sample removed, Control page regrouped into four `#settings-*` sections, 30 s runtime selector + flow calculator, live ESP32-CAM panel with saved gallery, chart pointer/`__masterIdx` fix, 12 stale structural assertions repaired (the plan counted 10; Task 6's All Sample removal added two).
- **Not yet merged.** The final whole-branch review ran; its four criticals are fixed and verified. Detail: `.superpowers/sdd/2026-11-03-dashboard-overhaul/final-fixes-report.md`. Every `Ruling:` and `minor (deferred)` line is in `.superpowers/sdd/2026-11-03-dashboard-overhaul/progress.md` (gitignored — read it to resume or to audit the decisions).
- Two firmware lessons from that review, both now covered by tests: `startFullPresentationCycle()` must `allRelaysOff()` + `clearManualOverrides()` before `setPhase()` (the FSM only de-energizes a relay on the way out of its owning phase), and `PHASE_4` entry clamps `dosePump1/2/3Ms` with `min(..., MAX_SAFETY_DOSING_MS)` so the firmware enforces the 30 s ceiling itself. New `#define`s belong in `config.example.h` in the same commit — `TIME_PRE_RETURN_MS`/`TIME_PRESERVATION_SOAK_MS` sat in gitignored `config.h` only and broke the clean-clone compile.
- **The firmware changes require re-flashing the ESP32-S3** before the new buttons do anything on real hardware.
- `scripts/check_jsx.py` compiles the whole `<script type="text/babel">` block with esbuild. Run it after any `index.html` edit — structural tests pass on JSX that Babel rejects at page load.

## Progress logging protocol

Every significant milestone — a plan task finished, a decision taken, a session
ending mid-task — is written to disk before replying, not just reported in chat.
Write to, in order: this file's "Current work" section (state a fresh session
needs immediately), the active plan's ledger under `.superpowers/sdd/<plan>/progress.md`
(task detail and `Ruling:` lines), and the plan document itself when progress
changes its shape.

## Task Observer activation

Before the first tool call of any session — and before writing or proposing a
plan, not merely before executing one — invoke the `task-observer` skill AND
execute its Session Start Protocol (storage check and workspace creation, the
starter-set reconciliation when due, frontmatter scan, review trigger). Loading
the skill and running the protocol are separate steps; a session that loads the
file and stops has activated nothing. Any turn that will involve a tool call
counts; do not classify the session as "too simple" from its opening message.

Copy the protocol's seven `- [ ]` items into your first reply and tick each as it
runs; an item you cannot tick is the step you report. A step you did not run is
reported before the answer, in one line — never after it, where it reads as a
suggestion. If the skill does not resolve on this turn, say which probe told you
so (the skill listing, or the skill directory on disk), re-check the listing on
every later turn that makes a tool call, and run the protocol the first time it
resolves — a "not installed" verdict holds for one turn. Listed on disk but
refused by the Skill tool ("Unknown skill"): read its SKILL.md directly and run
the protocol; the lookup call rides with that read, never with the refused call.
