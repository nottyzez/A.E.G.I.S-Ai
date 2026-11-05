# A.E.G.I.S. Dashboard Overhaul Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Simplify the Home and Control views, remove the All Sample surface, add safe ≤30 s pump runtime and per-pump flow calibration, redesign the camera/gallery display, and make every Control-page button drive the real ESP32-S3 firmware.

**Architecture:** Four sequential phases. Phase 1 fixes the hardware command contract (firmware + server) so the Control page has something real to call. Phase 2 simplifies the navigable surfaces. Phase 3 redesigns the Control page and the image display on top of that contract. Phase 4 repairs the chart pointer math. Tests follow the project's existing convention: `unittest` classes that assert against `server/static/index.html` source text and live FastAPI handlers.

**Tech Stack:** Python 3.12, FastAPI, vanilla React 18 via Babel (no build step), Tailwind CDN, Three.js r128, Arduino/ESP32-S3 framework.

**Spec:** This plan implements the user request captured in `docs/superpowers/specs/2026-10-31-presentation-override-control-design.md` plus the 2026-11-03 design decisions recorded in the Direction Contract below. Read both before starting Task 1.

---

## Global Constraints

- All Thai plant terminology must exclusively use **ผักบุ้ง (Water Spinach)**.
- The dashboard must keep working when opened directly via `file://` (dual-path asset resolver `window.__AEGIS_ASSET_RESOLVER__`). Every new fetch must short-circuit when `window.location.protocol === 'file:'`.
- Do not change GPIO pin assignments in `firmware/esp32_main/config.h` (GPIO 1, 2, 4 sensors; 5–11 relays).
- `scripts/verify_figma_implementation.py` must report `26/26 Passed` after every task.
- Relay logic stays Active-HIGH as currently defined (`RELAY_ON = HIGH`, `RELAY_OFF = LOW` in `config.h`).
- No build step is permitted for the frontend: `server/static/index.html` stays a single self-contained file.
- Manual pump runtime may never exceed **30 000 ms**; this is a hard ceiling enforced independently in firmware, server, and UI.

## Review Focus

These are the input classes most likely to break in use. Each has a test in the task that owns the code.

1. **Runtime exactly 30 s** — a user selects the max and the relay must run 30 000 ms, not be silently clamped back to 25 000 ms by an older constant. Owned by Tasks 1, 2, 4.
2. **Manual button pressed during an active auto cycle** — the firmware currently returns early from `pollRemoteDashboardCommand()` unless `currentPhase == PHASE_IDLE`, so the button appears dead. Owned by Task 2.
3. **Chart pointer at the extreme left/right edge** — first and last data points must be selectable and the tooltip must sit under the cursor, not 3.6 % inward. Owned by Task 10.
4. **ESP32-CAM image missing or slow** — the browser cannot load `latest_capture.jpg`; the panel must fall back to the saved gallery with no broken-image icon and no layout shift. Owned by Task 9.
5. **A unit with zero sensor readings** — charts, sparklines and KPI cards must render an empty state rather than emit `NaN` into SVG path data. Owned by Task 10.

---

## Direction Contract

- **THESIS:** The dashboard is an instrument panel for one plant box, not a catalog of twelve experiments. Every surface earns its place by being operated, not browsed.
- **OWN-WORLD:** SnowUI night-glass on the milky-way backdrop: `#0a1120` grounds, `rgba(255,255,255,0.05)` cards with 16 px radius, `#C6C7F8` primary accent, `#A8C5DA` data accent, `#EAB308/#A855F7/#F97316` for Stock A/B/C. Type voices: Space Grotesk for display, Inter for UI, JetBrains Mono for measurements.
- **STORY:** The presenter opens Home, sees one name and two doors. Inside, every control is grouped by what it physically does, and pressing one moves real hardware within 1.5 s.
- **FIRST VIEWPORT:** Home is the wordmark over the dawn ridge with exactly two actions — enter the dashboard, read the spec. Control opens on a grouped settings index, not a wall of cards.
- **FORM:** Simplification of an existing world, not a replacement. Position 1 of 1: subtract, do not restyle.
- **FINISH:** unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance.

---

## File Structure

| File | Responsibility | Tasks |
|---|---|---|
| `firmware/esp32_main/actuator_controller.h` | Non-blocking manual relay override; per-relay runtime state | 1 |
| `firmware/esp32_main/esp32_main.ino` | Command dispatch for `JUMP_PHASE`, `MANUAL_DOSE`, `MANUAL_RELAY` | 2 |
| `firmware/esp32_main/config.h` | 30 000 ms safety ceiling | 2 |
| `server/dosing_engine.py` | Per-pump flow calibration storage | 4 |
| `main.py` | Per-pump calibration endpoints, 30 s cap alignment, capture freshness | 3, 4 |
| `server/static/index.html` | All four views + chart math | 5, 6, 7, 8, 9, 10 |
| `scripts/verify_figma_implementation.py` | Keeps the 26 structural checks true | 5, 6 |
| `tests/test_dashboard_overhaul.py` | New coverage for this work | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 |
| `tests/test_figma_r1_r2_r3_reviewer.py`, `tests/test_figma_r2_independent_stress.py`, `tests/test_figma_r3_independent_audit.py` | Repair 10 assertions left stale by the backdrop change | 11 |

---

## Phase 1 — Hardware command contract

### Task 1: Non-blocking manual relay override in firmware

**Files:**
- Modify: `firmware/esp32_main/actuator_controller.h:88-101`
- Test: `tests/test_dashboard_overhaul.py`

**Interfaces:**
- Consumes: `getPinFromIndex(int) -> int` (existing), `RELAY_ON`/`RELAY_OFF` (existing).
- Produces: `void manualTriggerRelay(int relayIndex, unsigned long durationMs)` — now returns immediately; `void updateManualOverrides(unsigned long now)` — must be called every `loop()`; `bool isManualOverrideActive(int relayIndex)`; `void clearManualOverrides()`.

**Why:** `manualTriggerRelay` currently calls `delay(durationMs)`, which blocks the whole `loop()` for up to 25 s — no WiFi polling, no telemetry, no serial input during a demo.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_dashboard_overhaul.py
class TestFirmwareNonBlockingRelay(unittest.TestCase):
    def setUp(self):
        self.src = (FIRMWARE_DIR / "actuator_controller.h").read_text(encoding="utf-8")

    def test_manual_trigger_contains_no_blocking_delay(self):
        """manualTriggerRelay must not block the loop with delay()."""
        start = self.src.index("void manualTriggerRelay")
        end = self.src.index("int getPinFromIndex", start)
        body = self.src[start:end]
        self.assertNotIn("delay(", body,
                         "manualTriggerRelay must be non-blocking; store state and return")

    def test_manual_override_state_and_updater_exist(self):
        self.assertIn("updateManualOverrides", self.src)
        self.assertIn("isManualOverrideActive", self.src)
        self.assertIn("clearManualOverrides", self.src)
```

`FIRMWARE_DIR = Path(__file__).resolve().parent.parent / "firmware" / "esp32_main"` goes at the top of the file.

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_dashboard_overhaul.TestFirmwareNonBlockingRelay -v`
Expected: FAIL — `delay(` found inside `manualTriggerRelay`, and `updateManualOverrides` missing.

- [ ] **Step 3: Implement the non-blocking override**

Add a private array to `ActuatorController`:

```cpp
struct RelayOverride { bool active; int pin; unsigned long startMs; unsigned long durationMs; };
RelayOverride overrides[7];
```

Replace the body of `manualTriggerRelay` so it writes `digitalWrite(pin, RELAY_ON)`, records `{active=true, pin, startMs=millis(), durationMs}` at slot `relayIndex - 1`, and returns. Add `updateManualOverrides(unsigned long now)` that loops the seven slots, turns off any whose `now - startMs >= durationMs`, and logs one line per shutoff. `clearManualOverrides()` turns every active slot off and clears the flags. Initialise all slots to `{false, -1, 0, 0}` in the constructor.

- [ ] **Step 4: Call the updater from `loop()`**

Run: `grep -n "updateManualOverrides" firmware/esp32_main/esp32_main.ino`
Expected: no match yet.

Add `actuators.updateManualOverrides(now);` immediately after `unsigned long now = millis();` in `loop()` (`esp32_main.ino:278-279`).

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m unittest tests.test_dashboard_overhaul.TestFirmwareNonBlockingRelay -v`
Expected: PASS (2 tests).

- [ ] **Step 6: Commit**

```bash
git add firmware/esp32_main/actuator_controller.h firmware/esp32_main/esp32_main.ino tests/test_dashboard_overhaul.py
git commit -m "fix(firmware): make manual relay override non-blocking"
```

---

### Task 2: Handle JUMP_PHASE and MANUAL_DOSE, raise the ceiling to 30 s

**Files:**
- Modify: `firmware/esp32_main/esp32_main.ino:180-213`
- Modify: `firmware/esp32_main/config.h:61`
- Test: `tests/test_dashboard_overhaul.py`

**Interfaces:**
- Consumes: `manualTriggerRelay`, `updateManualOverrides` (Task 1).
- Produces: firmware command strings `"JUMP_PHASE"`, `"MANUAL_DOSE"`; `MAX_SAFETY_DOSING_MS` becomes `30000`.

**Why:** the dashboard sends `JUMP_PHASE` and `MANUAL_DOSE` (`index.html:3584`, `3658`) but the firmware only recognises `START_CYCLE`, `SKIP_CIRCULATION`, `READ_SENSORS`, `MANUAL_RELAY`, `STOP`. Worse, `pollRemoteDashboardCommand()` returns immediately unless `actuators.currentPhase == PHASE_IDLE` (`esp32_main.ino:181`), so during a cycle every button is silently ignored.

- [ ] **Step 1: Write the failing test**

```python
class TestFirmwareCommandContract(unittest.TestCase):
    def setUp(self):
        self.ino = (FIRMWARE_DIR / "esp32_main.ino").read_text(encoding="utf-8")
        self.cfg = (FIRMWARE_DIR / "config.h").read_text(encoding="utf-8")

    def test_firmware_handles_every_dashboard_command(self):
        for cmd in ("JUMP_PHASE", "MANUAL_DOSE", "MANUAL_RELAY", "START_CYCLE", "STOP"):
            self.assertIn(f'strcmp(cmd, "{cmd}")', self.ino)

    def test_safety_ceiling_is_thirty_seconds(self):
        self.assertIn("#define MAX_SAFETY_DOSING_MS     30000", self.cfg)

    def test_manual_relay_not_gated_on_idle_phase(self):
        start = self.ino.index("void pollRemoteDashboardCommand")
        end = self.ino.index("void handleSerialCommands", start)
        body = self.ino[start:end]
        self.assertNotIn("actuators.currentPhase != PHASE_IDLE", body,
                         "Manual overrides must be accepted while a cycle runs")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_dashboard_overhaul.TestFirmwareCommandContract -v`
Expected: FAIL on all three.

- [ ] **Step 3: Remove the idle gate and add the two handlers**

Change the guard so only a stopped system skips polling was the intent — replace the early return with no gate at all (the relay override is non-blocking and safe mid-cycle by Task 1). Add:

```cpp
} else if (strcmp(cmd, "JUMP_PHASE") == 0) {
    int phase = doc["phase_id"] | 1;
    // Map dashboard phase 1..6 onto the firmware FSM, then fire its relays.
    // Phase 5 (dosing) uses the MANUAL_DOSE durations if present.
} else if (strcmp(cmd, "MANUAL_DOSE") == 0) {
    unsigned long p1 = doc["dosing_ms"]["pump1_ms"] | 0;
    unsigned long p2 = doc["dosing_ms"]["pump2_ms"] | 0;
    unsigned long p3 = doc["dosing_ms"]["pump3_ms"] | 0;
    if (p1) actuators.manualTriggerRelay(5, p1);
    if (p2) actuators.manualTriggerRelay(6, p2);
    if (p3) actuators.manualTriggerRelay(7, p3);
}
```

The `JUMP_PHASE` body must re-use the existing `phaseRelayMap` from the dashboard: phase 1 → relay 1, phase 2 → none, phase 3 → none, phase 4 → relay 2, phase 5 → relays 5/6/7, phase 6 → relays 3/4. Fire each with `actuators.manualTriggerRelay(n, 6000)`.

- [ ] **Step 4: Raise the ceiling**

Change `config.h:61` to `#define MAX_SAFETY_DOSING_MS     30000`. Leave `MAX_SAFETY_PUMP_MS` at 15000 — it stays unused by manual overrides.

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m unittest tests.test_dashboard_overhaul.TestFirmwareCommandContract -v`
Expected: PASS (3 tests).

- [ ] **Step 6: Commit**

```bash
git add firmware/esp32_main/esp32_main.ino firmware/esp32_main/config.h tests/test_dashboard_overhaul.py
git commit -m "feat(firmware): accept JUMP_PHASE and MANUAL_DOSE, 30s ceiling"
```

---

### Task 3: Align the server's 25 s cap with the new 30 s

**Files:**
- Modify: `main.py:487-490`
- Test: `tests/test_dashboard_overhaul.py`

**Interfaces:**
- Consumes: `dosing_engine.get_calibration()`.
- Produces: `POST /api/command` returns `dosing_plan` values that may reach 30000 ms.

- [ ] **Step 1: Write the failing test**

```python
class TestServerRuntimeCeiling(unittest.TestCase):
    def test_command_calc_ms_caps_at_thirty_seconds(self):
        src = (PROJECT_ROOT / "main.py").read_text(encoding="utf-8")
        self.assertIn("min(30000, int(round(prime_ms", src)
        self.assertNotIn("min(25000, int(round(prime_ms", src)
```

Add `PROJECT_ROOT = Path(__file__).resolve().parent.parent` at the top of the test file.

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_dashboard_overhaul.TestServerRuntimeCeiling -v`
Expected: FAIL.

- [ ] **Step 3: Change the constant**

In `main.py` `calc_ms`, replace `min(25000, ...)` with `min(30000, ...)`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests.test_dashboard_overhaul.TestServerRuntimeCeiling -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add main.py tests/test_dashboard_overhaul.py
git commit -m "fix(server): align pump runtime ceiling to 30s"
```

---

### Task 4: Per-pump flow calibration

**Files:**
- Modify: `server/dosing_engine.py:27-90`
- Modify: `main.py` (add `POST /api/calibration/flow/<pump>`)
- Test: `tests/test_dashboard_overhaul.py`

**Interfaces:**
- Consumes: nothing new.
- Produces: `TwoTierDosingEngine.pump_flow_rates: Dict[str, float]` keyed `"A"|"B"|"C"`; `get_pump_flow_rates() -> Dict[str, float]`; `calibrate_pump(pump_key: str, collected_ml: float, test_duration_s: float, observed_prime_s: float) -> Dict[str, Any]`; route `POST /api/calibration/flow/{pump_key}`.

**Why:** today `pump_flow_rate_ml_s` is one global number used for all three peristaltic pumps, so the "calculate flow for each pump" request cannot be honoured.

- [ ] **Step 1: Write the failing test**

```python
class TestPerPumpFlowCalibration(unittest.TestCase):
    def test_each_pump_holds_its_own_flow_rate(self):
        from dosing_engine import TwoTierDosingEngine
        eng = TwoTierDosingEngine()
        eng.calibrate_pump("A", collected_ml=12.0, test_duration_s=10.0, observed_prime_s=2.0)
        eng.calibrate_pump("B", collected_ml=6.0, test_duration_s=10.0, observed_prime_s=2.0)
        rates = eng.get_pump_flow_rates()
        self.assertAlmostEqual(rates["A"], 1.5, places=2)
        self.assertAlmostEqual(rates["B"], 0.75, places=2)

    def test_unknown_pump_key_is_rejected(self):
        from dosing_engine import TwoTierDosingEngine
        with self.assertRaises(ValueError):
            TwoTierDosingEngine().calibrate_pump("Z", 10.0, 10.0, 2.0)
```

Add `sys.path.insert(0, str(PROJECT_ROOT / "server"))` before the imports at the top of the test module.

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_dashboard_overhaul.TestPerPumpFlowCalibration -v`
Expected: FAIL — `calibrate_pump` not defined.

- [ ] **Step 3: Implement per-pump storage**

Add `self.pump_flow_rates = {"A": DEFAULT_FLOW_RATE, "B": DEFAULT_FLOW_RATE, "C": DEFAULT_FLOW_RATE}` to `__init__`. Implement:

```python
def calibrate_pump(self, pump_key, collected_ml, test_duration_s=10.0, observed_prime_s=2.0):
    key = str(pump_key).upper()
    if key not in self.pump_flow_rates:
        raise ValueError(f"Unknown pump key: {pump_key}")
    effective = max(0.5, float(test_duration_s) - float(observed_prime_s))
    q = max(0.1, round(float(collected_ml) / effective, 3))
    self.pump_flow_rates[key] = q
    return {"pump": key, "calculated_flow_rate_ml_s": q, "priming_delay_s": round(float(observed_prime_s), 2)}

def get_pump_flow_rates(self):
    return dict(self.pump_flow_rates)
```

Keep the existing global `pump_flow_rate` untouched so `compute_dosing` behaviour does not change.

- [ ] **Step 4: Add the route**

```python
@app.post("/api/calibration/flow/{pump_key}")
def calibrate_single_pump(pump_key: str, payload: dict):
    try:
        res = dosing_engine.calibrate_pump(
            pump_key,
            payload.get("collected_ml", 12.0),
            payload.get("test_duration_s", 10.0),
            payload.get("observed_prime_s", 2.0),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    current_hardware_status["pump_flow_rates"] = dosing_engine.get_pump_flow_rates()
    append_command_log("CALIBRATION", f"ปรับ Flow ปั๊ม {pump_key} = {res['calculated_flow_rate_ml_s']} mL/s", True)
    return res
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m unittest tests.test_dashboard_overhaul.TestPerPumpFlowCalibration -v`
Expected: PASS (2 tests).

- [ ] **Step 6: Commit**

```bash
git add server/dosing_engine.py main.py tests/test_dashboard_overhaul.py
git commit -m "feat(server): per-pump flow calibration"
```

---

## Phase 2 — Simplify the surfaces

### Task 5: Reduce Home to the wordmark and two actions

**Files:**
- Modify: `server/static/index.html:2199-2265` (`HomeView` return block)
- Modify: `scripts/verify_figma_implementation.py`
- Test: `tests/test_dashboard_overhaul.py`

**Interfaces:**
- Produces: `HomeView` renders no `bottomMetrics`, no `.bottom-telemetry-card`, no `MagicBento` wrapper.

**Why:** the user asked for the Home page to lose its density. The four-card telemetry deck duplicates the dashboard and buries the primary action.

- [ ] **Step 1: Write the failing test**

```python
class TestHomeSimplification(unittest.TestCase):
    def setUp(self):
        self.html = (PROJECT_ROOT / "server" / "static" / "index.html").read_text(encoding="utf-8")

    def test_home_has_no_telemetry_deck(self):
        start = self.html.index("function HomeView")
        end = self.html.index("function AnalyzeTabView", start)
        body = self.html[start:end]
        self.assertNotIn("bottomMetrics", body)
        self.assertNotIn("bottom-telemetry-card", body)
        self.assertNotIn("3D GALAXY PARALLAX", body)

    def test_home_keeps_both_primary_actions(self):
        start = self.html.index("function HomeView")
        end = self.html.index("function AnalyzeTabView", start)
        body = self.html[start:end]
        self.assertIn("ENTER A.E.G.I.S ANALYZE", body)
        self.assertIn("READ SYSTEM SPEC", body)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_dashboard_overhaul.TestHomeSimplification -v`
Expected: FAIL.

- [ ] **Step 3: Delete the deck and its data**

Delete the `bottomMetrics` array (`index.html:2138-2161`) and the entire block from `{/* Bottom Interactive Floating Telemetry Bar */}` through its closing `</div>` before the modal (`index.html:2241-2276`). Keep the nav, the hero title, the paragraph, and both buttons. Reduce the hero paragraph to one sentence:

```
ระบบปัญญาประดิษฐ์แบบ Closed-Loop สำหรับวินิจฉัยภาวะขาดธาตุอาหาร N-P-K ในผักบุ้งไฮโดรโปนิกส์
```

- [ ] **Step 4: Update the verify script**

Remove the now-invalid `check(...)` line in `scripts/verify_figma_implementation.py` whose key is `"Mouse parallax horizon bloom"` only if the class is still referenced elsewhere; otherwise leave it (the backdrop still uses `home-backdrop__bloom`). Confirm the count stays 26:

Run: `python scripts/verify_figma_implementation.py`
Expected: `26/26 Passed`.

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m unittest tests.test_dashboard_overhaul.TestHomeSimplification -v`
Expected: PASS (2 tests).

- [ ] **Step 6: Commit**

```bash
git add server/static/index.html scripts/verify_figma_implementation.py tests/test_dashboard_overhaul.py
git commit -m "refactor(home): reduce to wordmark and two primary actions"
```

---

### Task 6: Remove All Sample and the Control labels

**Files:**
- Modify: `server/static/index.html` (`AllSampleTabView` 4418-4506; sidebar 4617-4650; tab cycle 4749-4756; render block 4795-4805; quick-unit chips 2549)
- Modify: `scripts/verify_figma_implementation.py`
- Test: `tests/test_dashboard_overhaul.py`

**Interfaces:**
- Produces: `activeTab` union becomes `'Analyze' | 'Electronic Control'`. `selectedUnit` stays `'Control'` internally but is never surfaced as a visible label.

**Why:** the user wants a single-box dashboard that does not advertise itself as the Control arm of a 12-unit study.

- [ ] **Step 1: Write the failing test**

```python
class TestAllSampleRemoval(unittest.TestCase):
    def setUp(self):
        self.html = (PROJECT_ROOT / "server" / "static" / "index.html").read_text(encoding="utf-8")

    def test_all_sample_view_is_gone(self):
        self.assertNotIn("function AllSampleTabView", self.html)
        self.assertNotIn('id: "All Sample"', self.html)
        self.assertNotIn("'All Sample'", self.html)

    def test_control_label_is_not_rendered(self):
        self.assertNotIn("Control (สมบูรณ์)", self.html)
        self.assertNotIn("{unitSummary.label}: {unitSummary.npkStatus}", self.html)

    def test_quick_unit_selector_is_removed(self):
        self.assertNotIn("quickUnits", self.html)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_dashboard_overhaul.TestAllSampleRemoval -v`
Expected: FAIL (3 tests).

- [ ] **Step 3: Delete the view, menu entry, and render branch**

- Remove `function AllSampleTabView(...) { ... }` in full (`index.html:4418-4506`).
- Remove the `All Sample` object from the `"Dashboards"` children array (`index.html:4643-4648`) and the `Projects` menu item (`index.html:4620-4629`).
- Rewrite the tab-cycle ternary (`index.html:4749-4756`) to alternate `'Analyze'` ↔ `'Electronic Control'`.
- Remove the `activeTab === 'All Sample'` render block (`index.html:4795-4805`).
- Change the `activeTab` comment at `index.html:4513`.
- Delete `quickUnits` (`index.html:2343`) and the `JellyRadio items=` prop that consumes it (`index.html:2549`); replace the selector with a static status pill reading `ผักบุ้ง (Water Spinach)`.

- [ ] **Step 4: Replace the Control label**

In the Analyze header pill (`index.html:2533-2535`), change `{unitSummary.label}: {unitSummary.npkStatus}` to `สถานะ: {unitSummary.npkStatus}`. Leave the sidebar breadcrumb (`Dashboards / Analyze`) alone.

- [ ] **Step 5: Update the verify script**

Any `check()` referencing `All Sample` must be deleted. Re-run:

Run: `python scripts/verify_figma_implementation.py`
Expected: `26/26 Passed` — if the count drops, replace the removed check with one asserting `analyze` view exists.

- [ ] **Step 6: Run tests to verify they pass**

Run: `python -m unittest tests.test_dashboard_overhaul.TestAllSampleRemoval -v`
Expected: PASS (3 tests).

- [ ] **Step 7: Commit**

```bash
git add server/static/index.html scripts/verify_figma_implementation.py tests/test_dashboard_overhaul.py
git commit -m "refactor(dashboard): remove All Sample surface and Control labels"
```

---

## Phase 3 — Control page and imagery

### Task 7: Rebuild the Control page as a grouped settings index

**Files:**
- Modify: `server/static/index.html:3804-4411` (`ElectronicControlTabView` return block)
- Test: `tests/test_dashboard_overhaul.py`

**Interfaces:**
- Consumes: existing handlers `handleSetSchedulePreset`, `handleJumpPhase`, `handleStartFullCycleDemo`, `handleTriggerCamCapture`, `handleExecuteManualDose`, `handleCancelOverride`, `toggleRelay`.
- Produces: four `<section>` groups with ids `#settings-schedule`, `#settings-pumps`, `#settings-vision`, `#settings-simulation`.

**Why:** the page is a pile of dense cards with 10–11 px Thai copy; the user reports it is hard to operate. Grouping by physical subsystem and raising the type floor fixes that without changing behaviour.

- [ ] **Step 1: Write the failing test**

```python
class TestControlPageGrouping(unittest.TestCase):
    def setUp(self):
        self.html = (PROJECT_ROOT / "server" / "static" / "index.html").read_text(encoding="utf-8")
        start = self.html.index("function ElectronicControlTabView")
        self.body = self.html[start:self.html.index("function AllSampleTabView", start)
                               if "function AllSampleTabView" in self.html
                               else self.html.index("function App()", start)]

    def test_four_subsystem_groups_exist(self):
        for anchor in ("settings-schedule", "settings-pumps", "settings-vision", "settings-simulation"):
            self.assertIn(f'id="{anchor}"', self.body)

    def test_no_body_copy_below_twelve_pixels(self):
        import re
        sizes = [int(m) for m in re.findall(r"text-\[(\d+)px\]", self.body)]
        self.assertTrue(all(s >= 12 for s in sizes if s < 12),
                        f"Found undersized copy: {[s for s in sizes if s < 12]}")
```

Note: `text-[10px]`/`text-[11px]` may remain on monospace *labels* only if the test is narrowed — keep the strict version and raise all copy to 12 px.

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_dashboard_overhaul.TestControlPageGrouping -v`
Expected: FAIL.

- [ ] **Step 3: Restructure the view**

Wrap the existing blocks into four sections in this order, each with a `<h2>` and a one-line Thai subtitle:
1. `#settings-schedule` — coexistence banner, schedule presets, override controls (existing 3823-3910).
2. `#settings-pumps` — relay matrix, runtime selector, flow calculator, manual dosing (Tasks 8 wraps this).
3. `#settings-vision` — 6-phase stepper, CAM trigger, image panel (Task 9).
4. `#settings-simulation` — scenario simulator and command log (existing 4244-4410).

Move the pinout specification card (3912-4012) into a `<details>` collapsed by default inside `#settings-pumps`. Raise every `text-[10px]`/`text-[11px]` *copy* string to `text-xs`; leave monospace pin labels at `text-[11px]` only inside the collapsed spec table.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m unittest tests.test_dashboard_overhaul.TestControlPageGrouping -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add server/static/index.html tests/test_dashboard_overhaul.py
git commit -m "refactor(control): group settings by subsystem, raise type floor"
```

---

### Task 8: Pump runtime selector (≤30 s) and per-pump flow calculator

**Files:**
- Modify: `server/static/index.html` (state at 3343-3352; `calcPumpMs` 3409-3415; `#settings-pumps` group from Task 7)
- Test: `tests/test_dashboard_overhaul.py`

**Interfaces:**
- Consumes: `POST /api/calibration/flow/{pump}` (Task 4); `sendApiRequest` (3384).
- Produces: `const [pumpRuntimeMs, setPumpRuntimeMs] = useState(5000)`; `const [pumpFlowRates, setPumpFlowRates] = useState({A:1.5,B:1.5,C:1.5})`; `const estimateVolumeMl = (ms) => Math.max(0, ((ms - calibration.priming_delay_s * 1000) / 1000) * flowRate)`.

**Why:** the user asked for a runtime control capped at 30 s and a per-pump flow calculation. The backend already exposes the global calculator at `/api/calibration/calculate`; Task 4 adds the per-pump one.

- [ ] **Step 1: Write the failing test**

```python
class TestPumpRuntimeAndFlow(unittest.TestCase):
    def setUp(self):
        self.html = (PROJECT_ROOT / "server" / "static" / "index.html").read_text(encoding="utf-8")

    def test_runtime_presets_top_out_at_thirty_seconds(self):
        for label in ("2s", "5s", "10s", "15s", "30s"):
            self.assertIn(f"label: '{label}'", self.html)
        self.assertNotIn("label: '60s'", self.html)

    def test_runtime_is_clamped_at_thirty_seconds(self):
        self.assertIn("Math.min(30000,", self.html)

    def test_flow_calculator_calls_per_pump_route(self):
        self.assertIn("/api/calibration/flow/", self.html)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_dashboard_overhaul.TestPumpRuntimeAndFlow -v`
Expected: FAIL.

- [ ] **Step 3: Implement the runtime selector**

In `#settings-pumps`, replace the existing `pulseDurationMs` preset list (`index.html:4111-4128`) with `2s / 5s / 10s / 15s / 30s`. Add a manual numeric input bounded `100..30000` whose change handler writes `Math.min(30000, value)`. Show the equivalent volume beside it: `≈ {estimateVolumeMl(pumpRuntimeMs).toFixed(1)} mL` for the currently selected pump.

Pass `pumpRuntimeMs` into `toggleRelay` in place of the hard-coded `duration_ms`.

- [ ] **Step 4: Implement the flow calculator panel**

Add a compact `<details>` panel inside `#settings-pumps` titled `คำนวณอัตราการไหลของปั๊ม`. For each of A/B/C render three inputs — `collected_ml`, `test_duration_s` (default 10), `observed_prime_s` (default 2) — a `คำนวณ` button and a live result line. The button posts:

```js
await sendApiRequest(`/api/calibration/flow/${pump}`, { collected_ml, test_duration_s, observed_prime_s });
```

On success set `pumpFlowRates`; offline (`file://`) shows `โหมดออฟไลน์: ใช้ค่า Q = ... mL/s`.

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m unittest tests.test_dashboard_overhaul.TestPumpRuntimeAndFlow -v`
Expected: PASS (3 tests).

- [ ] **Step 6: Commit**

```bash
git add server/static/index.html tests/test_dashboard_overhaul.py
git commit -m "feat(control): 30s pump runtime selector and per-pump flow calculator"
```

---

### Task 9: Redesign the camera and saved-image display

**Files:**
- Modify: `server/static/index.html` (`getUnitLeafPhoto` 1560-1575; Analyze leaf card 3040-3070; `#settings-vision` group)
- Modify: `main.py` (add `latest_capture_at` to status)
- Test: `tests/test_dashboard_overhaul.py`

**Interfaces:**
- Consumes: `current_hardware_status["latest_image_url"]` (already populated at `main.py:157`).
- Produces: `function getSavedGallery(unitId) -> string[]` returning up to 8 manifest paths; `<VisionPanel />` rendering live capture first, gallery below.

**Why:** `latest_image_url` is served by the backend but never read by the frontend (grep count 0), so a fresh ESP32-CAM capture never appears. The gallery also shows only the single newest file.

- [ ] **Step 1: Write the failing test**

```python
class TestVisionPanel(unittest.TestCase):
    def setUp(self):
        self.html = (PROJECT_ROOT / "server" / "static" / "index.html").read_text(encoding="utf-8")
        self.main_py = (PROJECT_ROOT / "main.py").read_text(encoding="utf-8")

    def test_frontend_reads_latest_image_url(self):
        self.assertIn("latest_image_url", self.html)

    def test_gallery_helper_exists(self):
        self.assertIn("function getSavedGallery", self.html)

    def test_backend_timestamps_the_capture(self):
        self.assertIn("latest_capture_at", self.main_py)

    def test_image_error_falls_back_to_gallery(self):
        start = self.html.index("function getSavedGallery")
        self.assertIn("onError", self.html[start:start + 6000])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_dashboard_overhaul.TestVisionPanel -v`
Expected: FAIL (4 tests).

- [ ] **Step 3: Add the gallery helper**

```js
function getSavedGallery(unitId, limit = 8) {
  const manifest = window.IMAGES_MANIFEST || {};
  const list = manifest[unitId] || [];
  return list.slice(-limit).reverse().map((entry) => {
    const name = typeof entry === 'string' ? entry : (entry.path || entry.url);
    const clean = name.includes('/') ? name.split('/').pop() : name;
    return window.__AEGIS_ASSET_RESOLVER__(`images_real/${unitId}/${clean}`);
  });
}
```

- [ ] **Step 4: Add the capture timestamp to the backend**

In `main.py`, inside the `/predict` success path next to line 157, also set `current_hardware_status["latest_capture_at"] = datetime.now().isoformat()`. Initialise `"latest_capture_at": None` in the status dict at `main.py:71`.

- [ ] **Step 5: Build the vision panel**

Inside `#settings-vision`, render a two-column panel. Left: the live frame from `latest_image_url` with a `?t=` cache-buster, a `LIVE • ESP32-S3 CAM` badge, and `onError` that hides the live column and shows the gallery instead (no broken-image icon). Right: a 3-column thumbnail grid from `getSavedGallery(selectedUnit)`, each thumbnail opening the larger view on click, with the capture timestamp from `latest_capture_at` when present. Replace the Analyze leaf card's single `<img>` (`index.html:3044`) with the newest gallery item so both surfaces agree.

- [ ] **Step 6: Run tests to verify they pass**

Run: `python -m unittest tests.test_dashboard_overhaul.TestVisionPanel -v`
Expected: PASS (4 tests).

- [ ] **Step 7: Commit**

```bash
git add server/static/index.html main.py tests/test_dashboard_overhaul.py
git commit -m "feat(vision): live ESP32-CAM frame with saved-image gallery"
```

---

## Phase 4 — Chart interaction

### Task 10: Make the pointer select the point under the cursor

**Files:**
- Modify: `server/static/index.html:2493-2501` (`handlePointerScrub`), `2458-2482` (EC series and `activeEcPt`), `2745-2749` (tooltip offset)
- Test: `tests/test_dashboard_overhaul.py`

**Interfaces:**
- Produces: `function pointIndexFromPointer(ratio: number, count: number, width = 560, inset = 20) -> number` returning a clamped index; `handlePointerScrub(e)` applies it to the active series.

**Why:** spline points are drawn between x=20 and x=540 in a 560-wide viewBox, but the pointer handler maps the raw element ratio straight to an index over 0–560. At the left edge the tooltip therefore sits 3.6 % of the width right of the cursor; at the right edge it sits 3.6 % left. Separately, the EC chart plots `r2Readings` (a filtered array) while `activeEcPt` indexes the unfiltered `unitReadings`, so on tank units the crosshair lands on the wrong sample.

- [ ] **Step 1: Write the failing test**

```python
class TestChartPointerMapping(unittest.TestCase):
    def setUp(self):
        self.html = (PROJECT_ROOT / "server" / "static" / "index.html").read_text(encoding="utf-8")

    def test_pointer_helper_accounts_for_viewbox_inset(self):
        self.assertIn("function pointIndexFromPointer", self.html)

    def test_ec_chart_uses_the_series_it_draws(self):
        self.assertIn("ptsEcR2", self.html)
        start = self.html.index("const activeEcPt")
        body = self.html[start:start + 900]
        self.assertIn("__masterIdx", body)

    def test_mapping_clamps_at_both_edges(self):
        self.assertIn("Math.max(0, Math.min(count - 1", self.html)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_dashboard_overhaul.TestChartPointerMapping -v`
Expected: FAIL (3 tests).

- [ ] **Step 3: Add the mapping helper**

```js
// Spline points span [inset, width - inset]; invert that, not the raw ratio.
function pointIndexFromPointer(ratio, count, width = 560, inset = 20) {
  if (!count || count < 1) return 0;
  const vbX = Math.max(0, Math.min(1, ratio)) * width;
  const t = (vbX - inset) / (width - 2 * inset);
  return Math.max(0, Math.min(count - 1, Math.round(t * (count - 1))));
}
```

Use it in `handlePointerScrub`, passing the length of the series the active chart draws.

- [ ] **Step 4: Fix the EC master-index mapping**

Build the Round 2 series carrying its master index:

```js
const r2Series = useMemo(() => {
  return unitReadings
    .map((r, i) => ({ ...r, __masterIdx: i }))
    .filter((r) => r.solution_round === 'รอบ 2');
}, [unitReadings]);
```

Plot `ptsEcR2` from `r2Series`. In `activeEcPt`, resolve the point whose `reading.__masterIdx === activeIdx`; when the active index is not in Round 2, fall back to the nearest `__masterIdx`.

- [ ] **Step 5: Remove the tooltip's percentage offset**

Set the tooltip container `left` from the point's own viewBox x expressed against the same inset box, so it tracks the rendered node:

```jsx
left: `calc(${(activePhPt.x / 560) * 100}% )`,
```

The helper in Step 3 already guarantees the node sits under the cursor; this line must not add a second compensation.

- [ ] **Step 6: Run tests to verify they pass**

Run: `python -m unittest tests.test_dashboard_overhaul.TestChartPointerMapping -v`
Expected: PASS (3 tests).

- [ ] **Step 7: Commit**

```bash
git add server/static/index.html tests/test_dashboard_overhaul.py
git commit -m "fix(charts): align pointer, crosshair and tooltip with plotted points"
```

---

### Task 11: Repair the 10 stale structural assertions

**Files:**
- Modify: `tests/test_figma_r1_r2_r3_reviewer.py:192-215, 218-235, 247-259, 261-270`
- Modify: `tests/test_figma_r2_independent_stress.py:250-256, 292-301, 331-345`
- Modify: `tests/test_figma_r3_independent_audit.py:250-256, 356-370`
- Test: the same files

**Interfaces:**
- Consumes: the shipped backdrop at `server/static/back.jpg`.
- Produces: a green suite (0 failures).

**Why:** 10 tests still assert `space_bg.jpg`, `home-space-nebula`, `url("${spaceBg}")`, and the exact `createStarLayer(..., '#93c5fd', ...)` colour strings. Task 5 and the earlier backdrop work invalidated them.

- [ ] **Step 1: Confirm the baseline**

Run: `python -m unittest discover -s tests -p "test_*.py" 2>&1 | grep -E "^(Ran|FAILED|OK)"`
Expected: `Ran 170 tests`, `FAILED (failures=10)`.

- [ ] **Step 2: Update the backdrop assertions**

Replace every `"images_real/space_bg.jpg"` expectation with `"back.jpg"`, and every `url("${spaceBg}")` with `url("${homeBack}")`.

- [ ] **Step 3: Update the nebula assertions**

Replace `.home-space-nebula` with `.home-backdrop__bloom` and `home-space-nebula` with `home-backdrop__bloom` in all three files.

- [ ] **Step 4: Update the star-colour assertions**

In `test_r3_star_particle_density_and_twinkling` and `test_r3_reduced_star_particles_density`, change the expected colour tokens to the shipped ones: `#9dbdf0`, `#dbe4ff`, `#ffffff`. Keep the 280/150/60 counts (unchanged).

- [ ] **Step 5: Run the full suite**

Run: `python -m unittest discover -s tests -p "test_*.py" 2>&1 | grep -E "^(Ran|FAILED|OK)"`
Expected: `Ran 000 tests`, `OK` with zero failures.

- [ ] **Step 6: Commit**

```bash
git add tests/test_figma_r1_r2_r3_reviewer.py tests/test_figma_r2_independent_stress.py tests/test_figma_r3_independent_audit.py
git commit -m "test: align structural assertions with shipped backdrop and star layer"
```

---

## Self-Review

**1. Spec coverage**

| Request | Task |
|---|---|
| Home text too dense → title + buttons | 5 |
| Remove All Sample page | 6 |
| Remove "Control" labelling | 6 |
| Control page hard to use, type too small | 7 |
| Runtime selector ≤30 s for pumps and dosing | 8, 1–3 |
| Per-pump flow calculation | 4, 8 |
| Grouped settings index | 7 |
| Redesign saved-image + ESP32-S3 CAM display | 9 |
| Chart hover misaligned with line | 10 |
| Settings buttons drive real ESP32-S3 | 1, 2, 3 |

**2. Step scan** — every step names a file, a symbol, or a command with an expected result. No "handle edge cases" lines. Implementation bodies appear only where the signature and test leave a choice (the pointer inversion, the master-index mapping, the calibration formula).

**3. Type consistency** — `manualTriggerRelay(int, unsigned long)` unchanged in signature; `updateManualOverrides(unsigned long)` introduced once and consumed only in Task 2; `calibrate_pump(pump_key, collected_ml, test_duration_s, observed_prime_s)` matches the route call; `pointIndexFromPointer(ratio, count, width, inset)` used only in Task 10.

**4. Review Focus** — five lines, each mapped to a test: 30 s boundary (Tasks 1–3), mid-cycle button (Task 2), chart edges (Task 10), missing camera image (Task 9), empty readings (Task 10 clamps on `count < 1`).

**5. Proportion** — 11 tasks against a 10-item request; code blocks are signatures, test assertions and two short algorithms, not transcripts.

---

## Execution order note

Tasks 1–4 must land before Task 8 (the flow calculator calls the route Task 4 adds). Tasks 5–6 touch disjoint DOM ranges from 7–10 and may be reordered. Task 11 must run last, after every `index.html` edit, or it will chase a moving file.
