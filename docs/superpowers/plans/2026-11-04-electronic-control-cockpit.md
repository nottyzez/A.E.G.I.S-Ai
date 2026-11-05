# Electronic Control Cockpit & 8-Phase Preservation Overhaul Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Overhaul `ElectronicControlTabView` into a compact Cockpit with an interactive fluidic chamber/relay SVG schematic, full 8-phase (Phase 0–7) preservation sync across firmware/backend/UI, segmented sub-tabs to eliminate long scrolling, 2-group relay cards, per-pump calibrated dosing with quick volume chips, and an integrated ESP32-CAM live/gallery studio.

**Architecture:** Three coordinated layers. Layer 1 synchronizes the 8-phase closed-loop contract (`Phase 0: Pre-Return` through `Phase 7: Probe Preservation Soak`) across `firmware/esp32_main/esp32_main.ino` and `main.py`. Layer 2 introduces `<InteractiveChamberSchematic />` and upgrades `ElectronicControlTabView` in `server/static/index.html` to a Cockpit + CSS-persisted Segmented Sub-Tab layout (`pumps | vision | simulation | pinout`). Layer 3 binds per-pump flow rates (`pumpFlowRates[key]`) into `calcPumpMs(mlVal, pumpKey)`, adds quick volume chips (`0`, `2.5`, `5`, `10` mL), splits relays into 2 functional groups (`R1–R4 Fluidic Chamber` and `R5–R7 Peristaltic Dosing`), and upgrades `<VisionPanel />` with interactive preview selection.

**Tech Stack:** Python 3.12, FastAPI (`main.py`), Vanilla React 18 via Babel (`server/static/index.html`), Tailwind CSS CDN, ESP32-S3 Arduino (`firmware/esp32_main/esp32_main.ino`), Python `unittest`.

**Spec:** `docs/superpowers/specs/2026-11-04-electronic-control-cockpit-design.md`

## Global Constraints

- All Thai plant terminology must exclusively use **ผักบุ้ง (Water Spinach)**.
- Do not change GPIO pin assignments in `firmware/esp32_main/config.example.h` (GPIO 1, 2, 4 sensors; GPIO 5–11 relays).
- Manual and calculated pump runtime must never exceed **30 000 ms** (`Math.min(30000, ...)`).
- Keep all four `<section>` anchors (`#settings-schedule`, `#settings-pumps`, `#settings-vision`, `#settings-simulation`) and required test strings mounted in the DOM (using CSS `hidden` when a sub-tab is inactive) so `tests/test_dashboard_overhaul.py`, `tests/test_presentation_override.py`, and `scripts/verify_figma_implementation.py` pass without regression.
- No frontend build step is permitted; `server/static/index.html` remains a single self-contained file that works on both `http://` and `file://`.

## Review Focus

1. **Jumping to Phase 0 or Phase 7 on stage** — `handleJumpPhase(0, ...)` must activate Relay 2 (`GPIO 6`, 4 s Pre-Return) and `handleJumpPhase(7, ...)` must activate Relay 1 (`GPIO 5`, 3 s Preservation Soak) in UI, `main.py`, and `esp32_main.ino`. Owned by Tasks 1 & 2.
2. **Per-pump flow rate used in manual dosing** — calibrating Pump B to `0.75 mL/s` must change Pump B's `calcPumpMs(8.0, 'B')` duration while leaving Pump A's duration on `pumpFlowRates.A`. Owned by Task 3.
3. **Clicking a relay node in the SVG schematic** — clicking `data-schematic-relay="R1"` in `<InteractiveChamberSchematic />` must invoke `onToggleRelay('R1')` and reflect active glow state. Owned by Task 2.
4. **Switching sub-tabs preserves form state and DOM anchors** — switching `controlSubTab` between `'pumps'`, `'vision'`, `'simulation'`, and `'pinout'` must toggle visibility via CSS classes without unmounting `#settings-pumps`, `#settings-vision`, or `#settings-simulation`. Owned by Task 3.
5. **Selecting a saved thumbnail in VisionPanel** — clicking any gallery thumbnail in `<VisionPanel />` must promote that image into the main preview frame with its filename/timestamp label. Owned by Task 4.

---

### Task 1: Synchronize 8-Phase (Phase 0–7) Preservation Contract in Backend & Firmware

**Files:**
- Modify: `main.py:45-53` (`PHASE_LABELS`) and `main.py:465-485` (`JUMP_PHASE` handling)
- Modify: `firmware/esp32_main/esp32_main.ino:210-226` (`JUMP_PHASE` switch statement)
- Test: `tests/test_electronic_control_cockpit.py`

**Interfaces:**
- Consumes: `ActuatorController::manualTriggerRelay(int relayIndex, unsigned long durationMs)` in `firmware/esp32_main/actuator_controller.h`.
- Produces:
  - `main.PHASE_LABELS`: keys `0..7` mapping `0: "0. Pre-Return (4s)"`, `1: "1. Sample Inflow (6s)"`, `2: "2. Settling & Measure (5s)"`, `3: "3. Sample Return (7s)"`, `4: "4. Peristaltic Dosing"`, `5: "5. Probe Rinse (5s)"`, `6: "6. Drain Waste (6s)"`, `7: "7. Probe Preservation Soak (3s)"`.
  - `esp32_main.ino` `JUMP_PHASE` switch cases `0..7`:
    - `case 0`: `actuators.manualTriggerRelay(2, dur)` (R2 Pre-Return)
    - `case 1`: `actuators.manualTriggerRelay(1, dur)` (R1 Sample Inflow)
    - `case 2`: sensor read + vision (no relay)
    - `case 3`: `actuators.manualTriggerRelay(2, dur)` (R2 Sample Return)
    - `case 4`: `actuators.manualTriggerRelay(5, dur); actuators.manualTriggerRelay(6, dur); actuators.manualTriggerRelay(7, dur);` (R5–R7 Peristaltic Dosing)
    - `case 5`: `actuators.manualTriggerRelay(3, dur)` (R3 Probe Rinse)
    - `case 6`: `actuators.manualTriggerRelay(4, dur)` (R4 Drain Waste)
    - `case 7`: `actuators.manualTriggerRelay(1, dur)` (R1 Probe Preservation Soak)

- [ ] **Step 1: Write the failing test in `tests/test_electronic_control_cockpit.py`**

```python
import unittest
from pathlib import Path
import main

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIRMWARE_INO = PROJECT_ROOT / "firmware" / "esp32_main" / "esp32_main.ino"


class TestEightPhaseContract(unittest.TestCase):
    def test_backend_phase_labels_cover_0_to_7(self):
        for phase_id in range(0, 8):
            self.assertIn(phase_id, main.PHASE_LABELS)
        self.assertIn("Pre-Return", main.PHASE_LABELS[0])
        self.assertIn("Preservation", main.PHASE_LABELS[7])

    def test_backend_jump_phase_accepts_phase_0_and_7(self):
        res0 = main.post_dashboard_command({"command": "JUMP_PHASE", "phase_id": 0, "duration_ms": 4000})
        self.assertEqual(res0["status"], "ok")
        self.assertEqual(main.current_hardware_status["phase_id"], 0)

        res7 = main.post_dashboard_command({"command": "JUMP_PHASE", "phase_id": 7, "duration_ms": 3000})
        self.assertEqual(res7["status"], "ok")
        self.assertEqual(main.current_hardware_status["phase_id"], 7)

    def test_firmware_jump_phase_handles_cases_0_through_7(self):
        ino_src = FIRMWARE_INO.read_text(encoding="utf-8")
        start = ino_src.index('strcmp(cmd, "JUMP_PHASE")')
        block = ino_src[start:start + 1400]
        for c in range(0, 8):
            self.assertIn(f"case {c}:", block)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests/test_electronic_control_cockpit.py -v`
Expected: FAIL (`Pre-Return` not in `PHASE_LABELS[0]`, `case 0:` and `case 7:` missing in `esp32_main.ino`).

- [ ] **Step 3: Update `main.py` and `firmware/esp32_main/esp32_main.ino`**

In `main.py`, update `PHASE_LABELS` to include `0..7` and update `JUMP_PHASE` in `post_dashboard_command` so `phase_id = int(payload.get("phase_id", 1))` maps `0..7` onto `PHASE_LABELS.get(phase_id, f"Phase {phase_id}")` and sets `active_relays` per the 8-phase map (`0: [2], 1: [1], 2: [], 3: [2], 4: [5, 6, 7], 5: [3], 6: [4], 7: [1]`).
In `firmware/esp32_main/esp32_main.ino`, update the `switch (phase)` block inside `strcmp(cmd, "JUMP_PHASE") == 0` to handle `case 0:` through `case 7:`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests/test_electronic_control_cockpit.py -v`
Expected: PASS (3 tests).

---

### Task 2: Add Interactive Fluidic Chamber & Relay Schematic + 8-Phase Stepper Cockpit

**Files:**
- Modify: `server/static/index.html` (add `function InteractiveChamberSchematic` before `ElectronicControlTabView`, update `closedLoopPhases` and `phaseRelayMap` inside `ElectronicControlTabView`)
- Test: `tests/test_electronic_control_cockpit.py`

**Interfaces:**
- Consumes: `relays`, `activePhase`, `toggleRelay(id)`, `handleJumpPhase(step, title)`.
- Produces:
  - `function InteractiveChamberSchematic({ relays, activePhase, onToggleRelay, onSelectPhase })` rendering an interactive SVG schematic with clickable nodes `data-schematic-relay="R1"` .. `"R7"`, chamber water level indicator (`STANDBY_PRESERVED` in Phase 7, draining in Phase 0/3/6, filling in Phase 1/5), and animated flow paths.
  - `closedLoopPhases` array with 8 items (`step: 0` through `step: 7`), including `0. Pre-Return (4s)` and `7. Probe Preservation Soak (3s)`.

- [ ] **Step 1: Add failing tests for `<InteractiveChamberSchematic />` and 8-phase stepper**

```python
class TestInteractiveCockpitAndEightPhasesUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (PROJECT_ROOT / "server" / "static" / "index.html").read_text(encoding="utf-8")

    def test_interactive_chamber_schematic_component_exists(self):
        self.assertIn("function InteractiveChamberSchematic", self.html)
        for r_id in ("R1", "R2", "R3", "R4", "R5", "R6", "R7"):
            self.assertIn(f'data-schematic-relay="{r_id}"', self.html)

    def test_eight_phases_0_through_7_rendered_in_control_view(self):
        self.assertIn("0. Pre-Return", self.html)
        self.assertIn("7. Probe Preservation Soak", self.html)
        self.assertIn("STANDBY_PRESERVED", self.html)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests/test_electronic_control_cockpit.py -v`
Expected: FAIL (`InteractiveChamberSchematic` and `0. Pre-Return` not found).

- [ ] **Step 3: Implement `InteractiveChamberSchematic` and 8-Phase Stepper in `server/static/index.html`**

Create `function InteractiveChamberSchematic({ relays, activePhase, onToggleRelay })` displaying:
- Main Hydroponic Reservoir (23.3 L) + Water Spinach canopy + ESP32-S3 CAM node
- Isolated Measurement Chamber with pH (`GPIO 1`), EC (`GPIO 2`), Temp (`GPIO 4`) probes and dynamic water fill height/color based on `activePhase` (`0..7`)
- Clickable SVG relay pills `data-schematic-relay="R1"`..`"R7"` wired to `onClick={() => onToggleRelay('R1')}` with active glow & countdown badge
- Update `closedLoopPhases` to 8 steps (`0..7`) and `phaseRelayMap` (`{ 0: ['R2'], 1: ['R1'], 2: [], 3: ['R2'], 4: ['R5', 'R6', 'R7'], 5: ['R3'], 6: ['R4'], 7: ['R1'] }`).

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests/test_electronic_control_cockpit.py -v`
Expected: PASS.

---

### Task 3: Segmented Sub-Tab Workspace, 2-Group Relay Cards & Per-Pump Calibrated Dosing

**Files:**
- Modify: `server/static/index.html` (`ElectronicControlTabView` state `controlSubTab`, `calcPumpMs(mlVal, pumpKey)`, Quick Volume presets `0 / 2.5 / 5 / 10 mL`, 2-group relay cards `Fluidic Chamber R1–R4` and `Peristaltic Dosing R5–R7`)
- Test: `tests/test_electronic_control_cockpit.py`

**Interfaces:**
- Consumes: `pumpFlowRates` (`{ A, B, C }`), `calibration.priming_delay_s`.
- Produces:
  - `const [controlSubTab, setControlSubTab] = useState('pumps')` with 4 mode buttons (`data-control-tab="pumps"`, `"vision"`, `"simulation"`, `"pinout"`).
  - `const calcPumpMs = (mlVal, pumpKey = 'A') => ...` using `pumpFlowRates[pumpKey] || calibration.pump_flow_rate_ml_s || 1.5`.
  - Quick Volume buttons (`[0, 2.5, 5, 10]`) per stock channel (`data-quick-dose={`${st.key}-${v}`}`).
  - 2-group relay layout separating `Fluidic Chamber Relays (R1–R4)` and `Peristaltic Nutrient Pumps (R5–R7)`.

- [ ] **Step 1: Add failing tests for Segmented Sub-Tabs, 2-Group Relays, and Per-Pump `calcPumpMs`**

```python
class TestSegmentedControlAndPerPumpDosing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (PROJECT_ROOT / "server" / "static" / "index.html").read_text(encoding="utf-8")

    def test_segmented_sub_tabs_exist(self):
        self.assertIn("controlSubTab", self.html)
        for tab in ("pumps", "vision", "simulation", "pinout"):
            self.assertIn(f'data-control-tab="{tab}"', self.html)

    def test_calc_pump_ms_uses_per_pump_flow_rate(self):
        start = self.html.index("const calcPumpMs")
        block = self.html[start:start + 500]
        self.assertIn("pumpFlowRates[pumpKey]", block)

    def test_quick_volume_buttons_and_two_relay_groups_exist(self):
        self.assertIn("Fluidic Chamber Relays (R1–R4)", self.html)
        self.assertIn("Peristaltic Nutrient Pumps (R5–R7)", self.html)
        self.assertIn("data-quick-dose=", self.html)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests/test_electronic_control_cockpit.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement Segmented Sub-Tabs, Per-Pump `calcPumpMs`, Quick Dose Chips, and 2-Group Relay Grid**

- Update `calcPumpMs = (mlVal, pumpKey = 'A')` to read `pumpFlowRates[pumpKey]`.
- Update `handleExecuteManualDose` to pass `'A'`, `'B'`, `'C'` to `calcPumpMs`.
- Add the segmented sub-tab bar (`1. ปั๊ม & โดสปุ๋ย (R1–R7)` | `2. กล้อง ESP32-CAM & คลังภาพ` | `3. จำลองสถานการณ์ & Log` | `4. สเปก Pinout & สูตรวัด`) and toggle section visibility with CSS (`hidden` vs `block`) so all `#settings-*` sections stay in the DOM.
- Group relays into `Fluidic Chamber Relays (R1–R4)` and `Peristaltic Nutrient Pumps (R5–R7)` compact 2-column cards.
- Add quick volume buttons (`0`, `2.5`, `5`, `10` mL) on each Stock A/B/C card alongside its live `Q = {pumpFlowRates[st.key]} mL/s` badge.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests/test_electronic_control_cockpit.py -v`
Expected: PASS.

---

### Task 4: Upgrade `VisionPanel` into an Interactive ESP32-S3 CAM Studio

**Files:**
- Modify: `server/static/index.html` (`function VisionPanel`)
- Test: `tests/test_electronic_control_cockpit.py`

**Interfaces:**
- Consumes: `selectedUnit`, `getSavedGallery(unitId)`, `camStatusText`, `onTriggerCapture`.
- Produces: `<VisionPanel selectedUnit={selectedUnit} camStatusText={camStatusText} onTriggerCapture={handleTriggerCamCapture} />` with interactive thumbnail selection (`selectedPreviewUrl`), live/gallery source badge, and integrated capture button.

- [ ] **Step 1: Add failing test for interactive `VisionPanel` studio**

```python
class TestInteractiveVisionStudio(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (PROJECT_ROOT / "server" / "static" / "index.html").read_text(encoding="utf-8")

    def test_vision_panel_supports_thumbnail_preview_selection_and_capture(self):
        start = self.html.index("function VisionPanel")
        block = self.html[start:start + 4500]
        self.assertIn("selectedPreview", block)
        self.assertIn("onTriggerCapture", block)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests/test_electronic_control_cockpit.py -v`
Expected: FAIL.

- [ ] **Step 3: Update `VisionPanel` in `server/static/index.html`**

Enhance `VisionPanel` to accept `{ selectedUnit, camStatusText, onTriggerCapture }`, maintain `const [selectedPreview, setSelectedPreview] = useState(null)`, allow clicking any saved gallery thumbnail to inspect it in the primary frame (or clicking `"LIVE STREAM"` to return to `latest_image_url`), and include a direct `📸 สั่งถ่ายภาพสด (ESP32-CAM)` trigger button and status bar right inside the studio header.

- [ ] **Step 4: Run all test suites and verification scripts**

Run:
```powershell
python -m unittest tests/test_electronic_control_cockpit.py tests/test_dashboard_overhaul.py tests/test_presentation_override.py tests/test_chamber_fsm_preservation.py -v
python scripts/verify_figma_implementation.py
```
Expected: All unit tests PASS, `verify_figma_implementation.py` reports `26/26 Passed`.
