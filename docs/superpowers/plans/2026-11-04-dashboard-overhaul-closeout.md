# Dashboard Overhaul Close-out Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `feature/dashboard-overhaul` green on a clean checkout, finish the per-pump flow calibration so calibrating a pump actually changes its dose, separate the unrelated working-tree work off the branch, and merge into `main`.

**Architecture:** Three phases. Phase 1 makes the suite honest — four tests assert on a 362 MB photo dataset that `.gitignore:60` excludes, so they pass only on a machine that already has the photos. Phase 2 completes per-pump calibration: the rates are stored, returned and displayed today, but `compute_dosing` still divides every pump by the single global `pump_flow_rate`, so pressing calibrate changes nothing. Phase 3 moves the Minecraft and poster work off this branch, commits the close-out files, and fast-forwards `main`.

**Tech Stack:** Python 3.12, `unittest` (not pytest), FastAPI, vanilla React 18 via Babel standalone (no build step), esbuild via `scripts/check_jsx.py`.

**Spec:** `docs/superpowers/plans/2026-11-03-dashboard-overhaul.md` (the 11-task plan this branch implements) and `docs/superpowers/specs/2026-10-31-presentation-override-control-design.md`. Read both before starting.

---

## Global Constraints

- All Thai plant terminology is **ผักบุ้ง (Water Spinach)**. Never ผักกาด.
- Manual pump runtime may never exceed **30 000 ms**. The ceiling is currently duplicated in 10 places: `firmware/esp32_main/config.example.h:61`, `server/dosing_engine.py:24`, `main.py:501`, and seven in `server/static/index.html` (3328, 3470, 3578, 3641, 4046, 4063, 4066). Do not add an eleventh; reuse an existing constant where one is in scope.
- `server/static/index.html` stays one self-contained file. No build step.
- Every fetch goes through `sendApiRequest` and short-circuits on `window.location.protocol === 'file:'`. Assets go through `window.__AEGIS_ASSET_RESOLVER__`.
- `scripts/verify_figma_implementation.py` must report **26/26 Passed** after every task touching `index.html`.
- `python scripts/check_jsx.py` must report `OK: JSX compiles (…)` after every `index.html` edit. Structural tests pass on JSX Babel rejects at page load.
- **Never** commit `firmware/*/config.h` (gitignored, holds the WiFi password). Constants go in `config.example.h`.
- Test command is `python -m unittest discover -s tests -p "test_*.py"`. There is no pytest config; `tests/test_demo_system.py` contains pytest-style module functions and is **not** collected by `unittest` — it contributes 0 to the count and is out of scope here.

## Review Focus

Inputs and states most likely to bite a person using this software, each with a test in the task that owns the code.

1. **A clean clone with no photo dataset** — `git clone && python -m unittest discover` must not fail because the local, gitignored 362 MB `server/static/images_real/` photos are absent. Owned by Task 1.
2. **Calibrating one pump, then dosing** — after raising pump A from 1.5 to 5.0 mL/s, the plan's `pump1_ms` must fall to about a third while `pump2_ms`/`pump3_ms` stay put. Owned by Tasks 2, 3, 4.
3. **A pump calibrated far slower than the others** — the 30 000 ms ceiling must bind on the *slowest* pump, not on a single global rate, so the total-volume cap cannot let one pump overrun. Owned by Task 2.
4. **The dashboard reloaded after a calibration** — the UI must show the calibrated per-pump rates fetched from the server, not the hardcoded `1.5` defaults. Owned by Tasks 2 and 4.
5. **Dosing with three different rates at once** — `MANUAL_DOSE` from the Control page must compute each pump's runtime from that pump's own rate. Owned by Task 3.

---

## File Structure

| File | Responsibility | Change |
|---|---|---|
| `tests/test_dashboard_e2e.py` | 4-tier E2E suite over shipped assets and handler contracts | add dataset guard, skip 3 tests |
| `tests/test_full_dashboard_adversarial.py` | adversarial asset-resolution suite | add dataset guard, skip 1 test |
| `server/dosing_engine.py` | two-tier dosing math; owns `pump_flow_rates` | per-pump rates in `compute_dosing`, expose in `get_calibration` |
| `main.py` | FastAPI; `MANUAL_DOSE` payload → ms | per-pump rate in `calc_ms` |
| `server/static/index.html` | the whole dashboard | per-pump rates in `calcMs` / `calcPumpMs`, hydrate from calibration |
| `tests/test_dashboard_overhaul.py` | structural + handler tests for this branch | new tests for the three pieces above |
| `.gitignore` | ignore rules | add `.npmrc`, `presentation/` |

---

## Task 1: Skip the dataset-dependent tests on a clean clone

Four tests assert on `server/static/images_real/<unit>/*.jpg`, which `.gitignore:60` excludes (`server/static/images_real/*`). They fail identically on `main` and on this branch, so this is not a regression — but it means "199 tests OK" is only reproducible on a machine that already has the photos.

**Files:**
- Modify: `tests/test_dashboard_e2e.py:35` (add guard), `:196`, `:513`, `:680`
- Modify: `tests/test_full_dashboard_adversarial.py:36` (add guard), `:168`

**Interfaces:**
- Produces: module-level `DATASET_PRESENT: bool` in both files. Nothing else consumes it.

- [ ] **Step 1: Write the guard test**

In `tests/test_dashboard_e2e.py`, after `IMAGES_REAL_DIR = STATIC_DIR / "images_real"` (line 35), add:

```python
# The 12-unit photo set is gitignored (362 MB; .gitignore:60), so a clean clone has
# the unit folders but not the photos. Tests that assert on those files skip instead
# of failing; TANKS_NEED is the same floor test 1.3 enforces.
TANKS_NEED = {"Control": 10, "N": 10, "P": 10, "K": 10}
DATASET_PRESENT = all(
    len(list((IMAGES_REAL_DIR / u).glob("*.jpg"))) >= n for u, n in TANKS_NEED.items()
)
```

In `tests/test_full_dashboard_adversarial.py`, after `IMAGES_REAL_DIR = STATIC_DIR / "images_real"` (line 36), add the same block plus, inside `DualProtocolAssetResolutionAdversarialTest`:

```python
def test_dataset_guard_matches_disk(self):
    """DATASET_PRESENT must reflect the disk, so the skips below cannot go stale."""
    on_disk = all(
        len(list((IMAGES_REAL_DIR / u).glob("*.jpg"))) >= 10
        for u in ("Control", "N", "P", "K")
    )
    self.assertEqual(DATASET_PRESENT, on_disk)
```

- [ ] **Step 2: Run the guard test to verify it passes**

Run: `python -m unittest tests.test_full_dashboard_adversarial.DualProtocolAssetResolutionAdversarialTest.test_dataset_guard_matches_disk -v`
Expected: `ok` (the photos are on disk here, so both sides are `True`).

- [ ] **Step 3: Decorate the four dataset tests**

Add `@unittest.skipUnless(DATASET_PRESENT, "12-unit photo dataset not present (gitignored)")` directly above each of these `def` lines:

- `tests/test_dashboard_e2e.py:196` `test_tier1_asset_unit_leaf_photos_exist_all_12_units`
- `tests/test_dashboard_e2e.py:513` `test_tier3_jelly_radio_unit_switch_updates_sensor_metrics`
- `tests/test_dashboard_e2e.py:680` `test_tier4_asset_resolution_dual_protocol_simulation`
- `tests/test_full_dashboard_adversarial.py:168` `test_file_protocol_unit_leaf_photos_all_12_units_resolve`

`unittest` is already imported in both files.

- [ ] **Step 4: Verify the suite is green here, and green without the photos**

With photos (this machine), from the branch tip with only Task 1 applied:
`python -m unittest discover -s tests -p "test_*.py"` → `OK` (the four still run, since `DATASET_PRESENT` is `True`).

Without photos, simulate a clean clone by hiding the units:
```bash
mv "server/static/images_real/N" /tmp/N_hidden
python -m unittest discover -s tests -p "test_*.py"
mv /tmp/N_hidden "server/static/images_real/N"
```
Expected without photos: same total, `OK (skipped=4)`. Restoring the folder must return the run to plain `OK`. Do not pin a count here — the tree still holds Task 5's 16 pending tests at this point.

- [ ] **Step 5: Commit**

```bash
git add tests/test_dashboard_e2e.py tests/test_full_dashboard_adversarial.py
git commit -m "test: skip the gitignored photo-dataset assertions on a clean clone"
```

---

## Task 2: `compute_dosing` charges each pump at its own rate

`calibrate_pump` writes `self.pump_flow_rates[key]`, but `compute_dosing` divides all three volumes by `self.pump_flow_rate` (lines 246–248) and caps the total with it (line 234). Calibrating changes no dose.

**Files:**
- Modify: `server/dosing_engine.py:68-75` (`get_calibration`), `:234` (cap), `:246-248` (runtimes)
- Test: `tests/test_dashboard_overhaul.py` (class `TestPerPumpFlowCalibration`)

**Interfaces:**
- Consumes: `self.pump_flow_rates` — `Dict[str, float]` keyed `"A"`, `"B"`, `"C"`, already maintained by `calibrate_pump` and `__init__`.
- Produces: `get_calibration()` gains a `"pump_flow_rates"` key (`Dict[str, float]`, values rounded to 2 dp). Task 4 reads it from `/api/calibration`. `compute_dosing`'s return dict is unchanged in shape.

- [ ] **Step 1: Write the failing test**

In `tests/test_dashboard_overhaul.py`, add to `TestPerPumpFlowCalibration`:

```python
def test_a_calibrated_pump_changes_its_own_runtime(self):
    from dosing_engine import TwoTierDosingEngine
    eng = TwoTierDosingEngine()
    eng.calibrate_pump("A", collected_ml=40.0, test_duration_s=10.0, observed_prime_s=2.0)  # Q = 5.0
    eng.calibrate_pump("B", collected_ml=16.0, test_duration_s=10.0, observed_prime_s=2.0)  # Q = 2.0
    res = eng.compute_dosing(ec=1.20, ph=6.50, temp=26.0, ai_class="Control")

    plan, vols = res["dosing_plan"], res["volumes_ml"]
    prime = res["priming_delay_ms"]
    self.assertEqual(plan["pump1_ms"], round(prime + vols["pump1_ml"] / 5.0 * 1000))
    self.assertEqual(plan["pump2_ms"], round(prime + vols["pump2_ml"] / 2.0 * 1000))
    self.assertEqual(plan["pump3_ms"], round(prime + vols["pump3_ml"] / 1.5 * 1000))

def test_the_ceiling_binds_on_the_slowest_pump(self):
    from dosing_engine import TwoTierDosingEngine, MAX_PUMP_DURATION_MS
    eng = TwoTierDosingEngine()
    eng.calibrate_pump("A", collected_ml=2.0, test_duration_s=10.0, observed_prime_s=2.0)  # Q = 0.25
    res = eng.compute_dosing(ec=0.40, ph=6.50, temp=26.0, ai_class="-N")
    self.assertLessEqual(max(res["dosing_plan"][k] for k in ("pump1_ms", "pump2_ms", "pump3_ms")),
                         MAX_PUMP_DURATION_MS)

def test_calibration_exposes_every_pump_rate(self):
    from dosing_engine import TwoTierDosingEngine
    eng = TwoTierDosingEngine()
    eng.calibrate_pump("C", collected_ml=8.0, test_duration_s=10.0, observed_prime_s=2.0)
    cal = eng.get_calibration()
    self.assertAlmostEqual(cal["pump_flow_rates"]["A"], 1.5, places=2)
    self.assertAlmostEqual(cal["pump_flow_rates"]["C"], 1.0, places=2)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m unittest tests.test_dashboard_overhaul.TestPerPumpFlowCalibration -v`
Expected: `test_a_calibrated_pump_changes_its_own_runtime` FAILs (`pump1_ms` is computed with 1.5, not 5.0); `test_calibration_exposes_every_pump_rate` FAILs with `KeyError: 'pump_flow_rates'`. `test_the_ceiling_binds_on_the_slowest_pump` may already pass — it is a regression guard, not a driver.

- [ ] **Step 3: Use each pump's own rate**

In `server/dosing_engine.py`, add to `get_calibration()`'s returned dict:

```python
"pump_flow_rates": {k: round(v, 2) for k, v in self.pump_flow_rates.items()},
```

In `compute_dosing`, replace the total-volume cap at line 234. The binding constraint is the pump that needs the longest run for its share, so solve for the volume the *slowest* pump allows:

```python
rates = self.pump_flow_rates
ratios = {"A": r1, "B": r2, "C": r3}
budget_s = (MAX_PUMP_DURATION_MS - self.priming_delay_s * 1000) / 1000.0
max_allowable_vol = budget_s * min(rates[k] / ratios[k] for k in rates if ratios[k] > 0)
v_total = max(3.0, min(v_total, max_allowable_vol))
```

With three equal ratios and three equal rates this reduces to the old `budget_s * rate * 3.0`, so the existing behaviour is preserved when nothing has been calibrated.

Replace lines 246–248 with a lookup on the same `rates` dict:

```python
t1 = int(round(prime_ms + (v1 / rates["A"]) * 1000)) if v1 > 0 else 0
t2 = int(round(prime_ms + (v2 / rates["B"]) * 1000)) if v2 > 0 else 0
t3 = int(round(prime_ms + (v3 / rates["C"]) * 1000)) if v3 > 0 else 0
```

Leave the returned `"flow_rate_ml_s": round(self.pump_flow_rate, 2)` as is — `tests/test_demo_system.py:141` reads it, and it names the global rate, which still exists.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m unittest tests.test_dashboard_overhaul.TestPerPumpFlowCalibration -v`
Expected: 6 tests, `OK`.

Then the whole suite: `python -m unittest discover -s tests -p "test_*.py"`
Expected: `OK`, with the module's own count up by 3. Default (uncalibrated) rates are all 1.5, so no existing dosing assertion moves.

- [ ] **Step 5: Commit**

```bash
git add server/dosing_engine.py tests/test_dashboard_overhaul.py
git commit -m "fix(dosing): charge each pump at its own calibrated flow rate"
```

---

## Task 3: `MANUAL_DOSE` computes each pump's runtime from its own rate

`main.py:456` reads one `flow_rate` from `get_calibration()` and `calc_ms` (line 501) applies it to all three volumes, so a per-pump calibration is ignored on the manual path too.

**Files:**
- Modify: `main.py:455-457`, `:495-505`
- Test: `tests/test_dashboard_overhaul.py`

**Interfaces:**
- Consumes: `get_calibration()["pump_flow_rates"]` from Task 2.
- Produces: nothing new; `post_dashboard_command`'s `dosing_ms` keys and types are unchanged.

- [ ] **Step 1: Write the failing test**

Append a class to `tests/test_dashboard_overhaul.py`:

```python
class TestManualDoseUsesPerPumpRates(unittest.TestCase):
    def setUp(self):
        import main
        self.main = main
        self.saved = dict(main.dosing_engine.pump_flow_rates)

    def tearDown(self):
        self.main.dosing_engine.pump_flow_rates.clear()
        self.main.dosing_engine.pump_flow_rates.update(self.saved)

    def test_each_pump_gets_its_own_runtime(self):
        self.main.dosing_engine.pump_flow_rates.update({"A": 5.0, "B": 1.0, "C": 1.5})
        res = self.main.post_dashboard_command({
            "command": "MANUAL_DOSE",
            "volumes_ml": {"A": 5.0, "B": 5.0, "C": 5.0},
        })
        prime = self.main.dosing_engine.get_calibration()["priming_delay_s"] * 1000
        plan = res["queued_command"]["dosing_ms"]
        self.assertEqual(plan["pump1_ms"], round(prime + 5.0 / 5.0 * 1000))
        self.assertEqual(plan["pump2_ms"], round(prime + 5.0 / 1.0 * 1000))
        self.assertEqual(plan["pump3_ms"], round(prime + 5.0 / 1.5 * 1000))
```

`dosing_ms` reaches the caller through `extra_fields` (`main.py:537`) into the `current_command` dict returned as `res["queued_command"]` (`main.py:583-588`).

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m unittest tests.test_dashboard_overhaul.TestManualDoseUsesPerPumpRates -v`
Expected: FAIL — all three values are computed with 1.5, so `pump1_ms` is 5333 instead of 3000 and `pump2_ms` is 5333 instead of 7000.

- [ ] **Step 3: Key `calc_ms` by pump**

At `main.py:455-457`, keep `glass`/flow reads as they are and add the per-pump map:

```python
cal = dosing_engine.get_calibration()
flow_rate = max(0.1, float(cal.get("pump_flow_rate_ml_s", 1.5)))
rates = {k: max(0.1, float(v)) for k, v in (cal.get("pump_flow_rates") or {}).items()}
rates.setdefault("A", flow_rate); rates.setdefault("B", flow_rate); rates.setdefault("C", flow_rate)
prime_ms = int(float(cal.get("priming_delay_s", 2.0)) * 1000)
```

Change `calc_ms` to take the pump key, keeping the `30000` literal that already lives there:

```python
def calc_ms(v_ml: float, pump_key: str) -> int:
    if v_ml <= 0.0:
        return 0
    return min(30000, int(round(prime_ms + (v_ml / rates[pump_key]) * 1000.0)))
```

Update the three call sites to `calc_ms(vol_a, "A")`, `calc_ms(vol_b, "B")`, `calc_ms(vol_c, "C")`.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m unittest tests.test_dashboard_overhaul.TestManualDoseUsesPerPumpRates tests.test_dashboard_overhaul.TestServerRuntimeCeiling -v`
Expected: `OK`, 2 tests. The existing ceiling test must still pass — the `min(30000, …)` is retained.

- [ ] **Step 5: Commit**

```bash
git add main.py tests/test_dashboard_overhaul.py
git commit -m "fix(server): MANUAL_DOSE uses each pump's calibrated flow rate"
```

---

## Task 4: The dashboard previews with per-pump rates

Two UI paths still use the global rate: `calcMs` inside `computeLocalTwoFactorDosing` (`index.html:3328`), and `calcPumpMs` (`:3463`), which prices Stock A/B/C. The `pumpFlowRates` state starts at `{A:1.5, B:1.5, C:1.5}` and is never loaded from the server, so a reload wipes what was calibrated.

**Files:**
- Modify: `server/static/index.html:3273-3279` (`computeLocalTwoFactorDosing` locals), `:3326-3328` (`calcMs`), `:3347-3349` (call sites), `:3380` (initial state), `:3463-3471` (`calcPumpMs`), `:3725-3727`, `:4145` (call sites)
- Test: `tests/test_dashboard_overhaul.py`

**Interfaces:**
- Consumes: `get_calibration()["pump_flow_rates"]` (Task 2) over `GET /api/calibration`.
- Produces: `calcMs(v, pumpKey)` and `calcPumpMs(mlVal, pumpKey)` — both take a `'A' | 'B' | 'C'` second argument.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_dashboard_overhaul.py`:

```python
class TestLocalPreviewUsesPerPumpRates(unittest.TestCase):
    def setUp(self):
        from pathlib import Path
        self.html = (Path(__file__).resolve().parent.parent
                     / "server" / "static" / "index.html").read_text(encoding="utf-8")

    def test_calc_ms_is_keyed_by_pump(self):
        self.assertIn("const calcMs = (v, pumpKey) =>", self.html)
        for n, key in ((1, "A"), (2, "B"), (3, "C")):
            self.assertIn(f"calcMs(v{n}, '{key}')", self.html)

    def test_calc_pump_ms_is_keyed_by_pump(self):
        self.assertIn("const calcPumpMs = (mlVal, pumpKey) =>", self.html)

    def test_local_preview_reads_the_per_pump_map(self):
        self.assertIn("calibration.pump_flow_rates", self.html)

    def test_rates_are_hydrated_from_the_server(self):
        self.assertIn("api/calibration'", self.html)
        self.assertIn("setPumpFlowRates((prev) => ({ ...prev, ...data.pump_flow_rates }))", self.html)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m unittest tests.test_dashboard_overhaul.TestLocalPreviewUsesPerPumpRates -v`
Expected: 4 FAILs — the current signatures are `(v)` and `(mlVal)`, `pump_flow_rates` appears nowhere, and no `/api/calibration` GET is fetched.

- [ ] **Step 3: Thread the pump key through both helpers**

In `computeLocalTwoFactorDosing`, replace the single `flowRate` local (line 3276) with a per-pump lookup that keeps the global rate as the fallback, so a server that predates this change still works:

```js
const globalRate = Math.max(0.1, (calibration && calibration.pump_flow_rate_ml_s) || 1.5);
const rateFor = (pumpKey) => Math.max(0.1, (calibration && calibration.pump_flow_rates || {})[pumpKey] || globalRate);
```

Change `calcMs` (line 3328) to:

```js
const calcMs = (v, pumpKey) => (v <= 0 ? 0 : Math.min(30000, Math.round(primeDelayS * 1000 + (v / rateFor(pumpKey)) * 1000)));
```

and its three call sites at 3347–3349 to `calcMs(v1, 'A')`, `calcMs(v2, 'B')`, `calcMs(v3, 'C')`.

Change `calcPumpMs` (line 3463) to read the pump:

```js
const calcPumpMs = (mlVal, pumpKey) => {
  const v = parseFloat(mlVal) || 0;
  if (v <= 0) return 0;
  const primeMs = (calibration.priming_delay_s || 2.0) * 1000;
  const q = Math.max(0.1, pumpFlowRates[pumpKey] || calibration.pump_flow_rate_ml_s || 1.5);
  return Math.min(30000, Math.round(primeMs + (v / q) * 1000));
};
```

Update the call sites: `:3725-3727` → `calcPumpMs(stockAmounts.A, 'A')`, `(stockAmounts.B, 'B')`, `(stockAmounts.C, 'C')`; `:4145` → `calcPumpMs(stockAmounts[st.key], st.key)`.

- [ ] **Step 4: Hydrate the rates from the server on load**

Leave line 3380's defaults. **There is no calibration GET today** — `setCalibration(` is never called, and `GET /api/calibration` (`main.py:751`) is never fetched by the UI. Add a `useEffect` that runs once on mount:

```js
useEffect(() => {
  if (window.location.protocol === 'file:') return;
  fetch('/api/calibration')
    .then((r) => (r.ok ? r.json() : null))
    .then((data) => {
      if (!data) return;
      setCalibration((prev) => ({ ...prev, ...data }));
      if (data.pump_flow_rates) setPumpFlowRates((prev) => ({ ...prev, ...data.pump_flow_rates }));
    })
    .catch(() => {});
}, []);
```

A raw `fetch` here, not `sendApiRequest` — the latter hardcodes `method: 'POST'` (`index.html:3442`) and `/api/calibration` is a GET. The `file:` short-circuit is kept explicitly for that reason.

- [ ] **Step 5: Run the tests and the structural checks**

```bash
python -m unittest tests.test_dashboard_overhaul -v
python scripts/check_jsx.py
python scripts/verify_figma_implementation.py
```
Expected: `OK`; `OK: JSX compiles (… lines …)`; `Verification Result: 26/26 Passed`.

- [ ] **Step 6: Commit**

```bash
git add server/static/index.html tests/test_dashboard_overhaul.py
git commit -m "fix(control): preview dosing with each pump's calibrated flow rate"
```

---

## Task 5: Move the unrelated working-tree work off this branch

The working tree holds two finished-but-unrelated bodies of work — the Minecraft backend (`main.py` +217 lines, `minecraft/`, `tests/test_minecraft_integration.py`, `docs/minecraft_presentation_backend_guide.md`) and further poster/blueprint edits. Both would otherwise ride into `main` through this merge. The dirty `main.py` also blocks `git switch main`.

`git switch -c` preserves local modifications when both branches point at the same commit, which is what makes this a clean move rather than a stash.

**Files:** none edited; git state only.

- [ ] **Step 1: Branch off without touching the working tree**

```bash
git switch -c wip/next-features
git status --porcelain | wc -l
```
Expected: the same count as before the switch — modifications followed the branch.

- [ ] **Step 2: Commit the Minecraft backend separately from the poster work**

```bash
git add main.py minecraft/ tests/test_minecraft_integration.py docs/minecraft_presentation_backend_guide.md
git commit -m "feat(mc): Minecraft digital-twin API, Lua suite and guide"
git add -A assets/blueprints docs/poster_content_companion.md POSTER_QR_DOWNLOAD.md scripts/generate_poster_blueprints.py tests/test_poster_blueprints.py REFERENCES.md
git commit -m "feat(poster): extend blueprint set and companion guide"
```
Expected: `git status --porcelain` now shows only untracked run artifacts (`presentation/`, `.npmrc`), handled in Task 6.

Do **not** `git add .` — `server/static/images_real/` is gitignored and `presentation/` is 363 MB.

- [ ] **Step 3: Verify the dashboard branch is untouched**

```bash
git switch feature/dashboard-overhaul
git status --porcelain
git log --oneline -1 feature/dashboard-overhaul
```
Expected: only the Task 6 leftovers listed; HEAD unchanged at this branch's tip.

- [ ] **Step 4: Confirm the Minecraft work is safe on the other branch**

```bash
git log --oneline -2 wip/next-features
git show --stat --oneline wip/next-features | head -20
```
Expected: two commits, and the file list matches what Step 2 staged.

---

## Task 6: Track the close-out files

Five files this branch's work depends on are still untracked. `scripts/check_jsx.py` is the one that matters most — `CLAUDE.md` mandates running it after every `index.html` edit, and a clean clone cannot.

**Files:**
- Modify: `.gitignore`
- Add: `scripts/check_jsx.py`, `CLAUDE.md`, `docs/superpowers/plans/2026-11-03-dashboard-overhaul.md`, `docs/chamber_operation_guide.md`

- [ ] **Step 1: Confirm each file is meant to be tracked**

```bash
git check-ignore -v scripts/check_jsx.py CLAUDE.md \
  docs/superpowers/plans/2026-11-03-dashboard-overhaul.md docs/chamber_operation_guide.md
```
Expected: no output for any of them (not ignored). If a path prints a rule, stop — do not force-add.

`CLAUDE.md` may hold no secrets: `grep -niE "password|token|secret|sk-" CLAUDE.md` must print nothing before it is committed.

- [ ] **Step 2: Ignore the two run artifacts**

Append to `.gitignore`, under the existing Node section:

```
# Machine-local npm cache pointer (absolute path per checkout)
.npmrc
# Rendered presentation rasters (363 MB); regenerate with scripts/generate_poster_blueprints.py
presentation/
```

- [ ] **Step 3: Verify the ignore rules bite**

```bash
git status --porcelain | grep -E "npmrc|presentation/" ; echo "exit=$?"
```
Expected: no matches (grep exit 1).

- [ ] **Step 4: Commit**

```bash
git add .gitignore scripts/check_jsx.py CLAUDE.md \
  docs/superpowers/plans/2026-11-03-dashboard-overhaul.md docs/chamber_operation_guide.md
git commit -m "chore: track the JSX checker, project guide and overhaul plan"
```

- [ ] **Step 5: Verify a clean clone has everything the docs name**

```bash
git ls-files --error-unmatch scripts/check_jsx.py CLAUDE.md server/static/back.jpg \
  tests/test_chamber_fsm_preservation.py scripts/verify_figma_implementation.py
```
Expected: every path prints. This is the same `back.jpg`/`config.h` failure shape `CLAUDE.md` warns about.

---

## Task 7: Merge into `main`

`feature/dashboard-overhaul` is 22 commits ahead of `main` and `main` is a direct ancestor, so this is a fast-forward. `origin/main` is an ancestor of `main`, so the push fast-forwards too.

**Files:** none.

- [ ] **Step 1: Full verification at the branch tip**

```bash
python -m unittest discover -s tests -p "test_*.py"
python scripts/verify_figma_implementation.py
python scripts/check_jsx.py
python scripts/check_firmware_config.py
```
Expected: `Ran 203 tests` … `OK` | `26/26 Passed` | `OK: JSX compiles (…)` | `OK: no identifier used by tracked firmware is undefined`.

Why 203 and not the 210 the tree showed at the start: 194 is the branch's own tracked count (measured in a clean `HEAD` worktree), +1 Task 1, +3 Task 2, +1 Task 3, +4 Task 4. The 16 that disappear are Task 5's move — 11 in `tests/test_minecraft_integration.py` and 5 in the dirty `tests/test_poster_blueprints.py`. Re-run the command after each task and trust the printed number over this one; it is a checkpoint, not a contract.

If any of these disagree with the numbers above, stop and report rather than merging.

- [ ] **Step 2: Fast-forward `main`**

```bash
git switch main
git merge --ff-only feature/dashboard-overhaul
git log --oneline -1
```

- [ ] **Step 3: Verify the merged tree in a clean checkout**

```bash
git worktree add /tmp/aegis-merged main --detach
cd /tmp/aegis-merged && python -m unittest discover -s tests -p "test_*.py"
cd - && git worktree remove /tmp/aegis-merged --force
```
Expected: `OK (skipped=4)` or `OK` — never a failure. The four skips appear only if the photos are absent from that worktree.

- [ ] **Step 4: Push — ask the user first**

`git push origin main` is outward-facing and rewrites the shared branch. **Confirm with the user before running it.** Expected when approved: `main -> main` fast-forward, no force.

- [ ] **Step 5: Record the close-out**

Update `CLAUDE.md`'s "Current work (2026-11-04)" section: the branch is merged, the merge commit, the new test count, and that `wip/next-features` now carries the Minecraft and poster work. Then commit:

```bash
git add CLAUDE.md
git commit -m "docs: record the dashboard-overhaul merge"
```

---

## Self-Review

**Spec coverage.** The 11 tasks of `2026-11-03-dashboard-overhaul.md` are already implemented and committed (`84e9320..78042c7`). This plan carries the four things that plan left open or that block a merge: the per-pump calibration it explicitly deferred ("Keep the existing global `pump_flow_rate` untouched"), the gitignored-dataset failures it never encountered (its runs had the photos), the untracked `check_jsx.py`, and the unrelated work in the tree.

**Step scan.** Every step names a file, a signature, or a command with an expected result. Task 3's Step 1 flags one genuine ambiguity — whether `dosing_ms` is nested — with the instruction to read the return rather than guess.

**Type consistency.** `pump_flow_rates` is `Dict[str, float]` keyed `"A"|"B"|"C"` throughout: produced in `dosing_engine.py`, read by `main.py`'s `rates[pump_key]`, exposed as `calibration.pump_flow_rates` in JS, and passed as `'A'|'B'|'C'` to `calcMs`/`calcPumpMs`. The key type matches `calibrate_pump`'s existing `key = str(pump_key).upper()`.

**Review Focus.** All five lines have a test: (1) Task 1 Step 4, (2) Task 2 Step 1 and Task 3 Step 1, (3) Task 2 `test_the_ceiling_binds_on_the_slowest_pump`, (4) Task 2 `test_calibration_exposes_every_pump_rate` plus Task 4 Step 4, (5) Task 3 Step 1.

**Proportion.** Five short code blocks against a 40 KB source plan. The rest is commands and assertions.

**Corrections made during self-review:** Task 3's `dosing_ms` lookup is now pinned to `res["queued_command"]["dosing_ms"]` (verified against `main.py:537` and `:583`), not left for the implementer to discover. Task 4 Step 4 states outright that no calibration GET exists today — `setCalibration` is never called — rather than suggesting a search that would come back empty. Task 4 gained a fourth test so hydration from the server is pinned, not just described. The three suite-count checkpoints were re-derived from measured numbers (clean `HEAD` worktree = 194; dirty tree = 210; the Minecraft and poster modules = 11 + 5 of that 210).
