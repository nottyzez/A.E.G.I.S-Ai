# Electronic Control Cockpit & 8-Phase Preservation Sync — Design Spec

**Date:** 2026-11-04 (revised)
**Supersedes:** the earlier Antigravity draft of the same file
**Scope:** Overhaul `ElectronicControlTabView` in `server/static/index.html`, and synchronize `main.py` + `firmware/esp32_main/esp32_main.ino` with the firmware's real 8-phase `CyclePhase` FSM.

---

## 0. Why this revision exists

The first draft of this spec moved the UI to an 8-phase model but left three defects that would surface on stage. Each is confirmed against the code, not assumed:

**D1 — Two incompatible phase models.**
`main.py:45-53` `PHASE_LABELS` describes a 6-step *AI pipeline* (`1. Telemetry Sampling … 6. Mixing & Verification`). `actuator_controller.h:10-21` `CyclePhase` describes an 8-step *fluidic cycle* (`PHASE_0_PRE_RETURN … PHASE_7_PROBE_PRESERVATION`). The labels are shifted by up to two positions — the UI's "5. Peristaltic Dosing" is the firmware's `PHASE_5_PROBE_RINSE`. Meanwhile `index.html:3881-3888` `closedLoopPhases` is a *third* variant (6 steps, merging Rinse+Drain into one). Jumping to a phase today is therefore ambiguous: the number means three different things depending on which layer reads it.

**D2 — `JUMP_PHASE` is a label, not a command.**
`main.py:466-481` writes `current_hardware_status["phase"]` and returns. It never populates `extra_fields` with relay work, so `current_command` (`main.py:571-578`) carries no relay payload. The ESP32 receives a `JUMP_PHASE` with a `phase_id` and, on the real FSM, `setPhase()` (`actuator_controller.h:95-99`) only mutates three fields — **it does not energize anything**. The UI compensates by painting `relays[].active = true` client-side (`index.html:3661-3671`), which is why the display looks correct while no valve opens. On stage the schematic animates and nothing happens.

**D3 — `phase_id: 0` is already taken.**
`main.py:57-59` initialises `"phase_id": 0` and `main.py:567-568` writes `phase_id = 0` on STOP; both mean **STANDBY**. Firmware agrees: `PHASE_IDLE` renders as `"STANDBY_PRESERVED"` (`actuator_controller.h:171`). Reusing `0` for `Phase 0: Pre-Return` makes STOP and Pre-Return indistinguishable in `/api/status`, `/api/mc/status`, and any resumed session.

**D4 (found during review) — the firmware `JUMP_PHASE` would dose for the wrong duration.**
`esp32_main.ino:210-226` maps dashboard phase N onto `manualTriggerRelay(pin, dur)` using the *old* 6-phase meaning (`case 4: relay 2`, i.e. Sample Return). Once D1 is fixed that same `case 4` must become Peristaltic Dosing (`R5,R6,R7`). Worse, `manualTriggerRelay` (`actuator_controller.h:110-127`) starts a fresh window on every call and `clearManualOverrides()` is only reached via `STOP` (`esp32_main.ino:227-229`). Jumping 4 → 5 → 6 with a 7 s runtime leaves `R5,R6,R7` energized for 21 s, because nothing in the intervening phases releases them.

---

## 1. Intent

During a live stage demonstration the presenter must be able to: trigger any of the eight real fluidic phases and see the **physical** relay follow, read the chamber state, and dose Stock A/B/C using per-pump calibrated rates — without scrolling a wall of cards.

---

## 2. Goals

1. **One phase model, everywhere.** The firmware's `CyclePhase` becomes the single source of truth for phase numbering across firmware, `main.py`, and the UI.

   | Wire value (`phase_id`) | Firmware enum | Meaning | Relays |
   |---|---|---|---|
   | `0` | `PHASE_IDLE` | **STANDBY** (unchanged sentinel) | — |
   | `1` | `PHASE_0_PRE_RETURN` | Pre-Return 4 s | R2 |
   | `2` | `PHASE_1_SAMPLING_IN` | Sample Inflow 6 s | R1 |
   | `3` | `PHASE_2_MEASURING` | Settle & Measure | — |
   | `4` | `PHASE_3_SAMPLING_RETURN` | Sample Return 7 s | R2 |
   | `5` | `PHASE_4_DOSING` | Peristaltic Dosing | R5, R6, R7 |
   | `6` | `PHASE_5_PROBE_RINSE` | Probe Rinse 5 s | R3 |
   | `7` | `PHASE_6_DRAIN_WASTE` | Drain Waste 6 s | R4 |
   | `8` | `PHASE_7_PROBE_PRESERVATION` | Preservation Soak 3 s | R1 |

   `0 = STANDBY` is preserved; the eight cycle phases are `1..8`. This keeps STOP unambiguous (D3) and matches the enum's own ordinal values.

2. **A phase jump must reach the hardware.** `JUMP_PHASE` gains a relay plan. Because the FSM's `setPhase()` energizes nothing, the server sends the relay work as an explicit `MANUAL_RELAY`-style override set that the firmware already understands, and sends `CANCEL_OVERRIDE` first so the previous phase's relays are released before the new ones open (D4).

3. **Cockpit layout.** An always-visible top section — schedule banner, `InteractiveChamberSchematic` SVG, 8-phase stepper — over a four-tab workspace (`pumps | vision | simulation | pinout`) that hides inactive tabs with CSS so form state and every `#settings-*` anchor survive tab switches.

4. **Per-pump dosing.** `calcPumpMs(mlVal, pumpKey)` uses `pumpFlowRates[pumpKey]`; quick-volume chips `0 / 2.5 / 5 / 10 mL` per stock channel; relays split into `Fluidic Chamber Relays (R1–R4)` and `Peristaltic Nutrient Pumps (R5–R7)`.

5. **Vision studio.** `VisionPanel` gets a live capture trigger, a status bar, and click-to-preview on saved thumbnails.

## 3. Non-Goals & Anti-Goals

- **Do not** renumber the firmware's `CyclePhase` enum. Its C++ integer values are load-bearing for the FSM and `getPhaseName()`.
- **Do not** change GPIO assignments in `firmware/esp32_main/config.example.h` (sensors GPIO 1, 2, 4; relays GPIO 5–11).
- **Do not** remove the four `#settings-*` `<section>` anchors or any string asserted by `tests/test_dashboard_overhaul.py`, `tests/test_presentation_override.py`, `tests/test_chamber_fsm_preservation.py`, or `scripts/verify_figma_implementation.py`.
- **Do not** introduce a frontend build step; `index.html` stays a single file working on both `http://` and `file://`.
- **Do not** let any relay window exceed `30000 ms`.

---

## 4. Approaches considered

**A (selected) — Reuse the existing override machinery for phase jumps.**
`JUMP_PHASE` expands server-side into `CANCEL_OVERRIDE` + one `MANUAL_RELAY` per relay in the phase plan, each for the requested duration, and queues them together. The firmware's existing `manualTriggerRelay()` / `updateManualOverrides()` pair already caps at 30 s and self-releases; no new FSM path is needed. *Pro:* one code path, already covered by `test_chamber_fsm_preservation.py`. *Con:* a jump is a burst of up to three queued commands — acceptable because `/api/command` already returns one command per poll and the ESP32 polls continuously.

**B — Teach `setPhase()` to energize relays.**
Would make the FSM self-contained but duplicates relay ownership between `setPhase()` and the override table, and `clearManualOverrides()` would stop being the single release point. Rejected: the FSM de-energizes relays itself as it leaves a phase (documented in CLAUDE.md), so two owners would fight.

**C — Keep client-side highlight only.**
Status quo. Rejected: D2.

---

## 5. Design

### 5.1 Phase contract (`main.py`)

`PHASE_LABELS` becomes the 9-entry table in §2.1, indexed `0..8`, with `0: "STANDBY"`. `PHASE_RELAY_MAP = {0: [], 1: ["R2"], 2: ["R1"], 3: [], 4: ["R2"], 5: ["R5","R6","R7"], 6: ["R3"], 7: ["R4"], 8: ["R1"]}`.

`JUMP_PHASE` handler changes: clamp `phase_id` to `0..8` (was `1..6`), set `active_relays` from `PHASE_RELAY_MAP` instead of inheriting the previous override's list (`main.py:478` — currently copies stale relays, a latent bug), and emit the relay plan as `extra_fields`.

### 5.2 Phase jump reaches the hardware (`esp32_main.ino`)

Replace the `switch (phase)` block at `esp32_main.ino:210-226` with: `actuators.clearManualOverrides()` first, then a `switch` over the **new** `phase_id` values `1..8` calling `manualTriggerRelay` with the §2.1 relay list, `case 0` and `default` leaving every relay off. The existing `MAX_SAFETY_DOSING_MS` clamp inside `manualTriggerRelay` keeps the 30 s ceiling.

### 5.3 Cockpit UI (`index.html`)

- `function InteractiveChamberSchematic({ relays, activePhase, onToggleRelay })` — reservoir (23.3 L) + water spinach canopy + CAM node, an isolated measurement chamber with pH/EC/Temp probe markers and a water level driven by `activePhase` (`STANDBY_PRESERVED` at `0`), and seven clickable relay nodes carrying `data-schematic-relay="R1".."R7"`.
- `closedLoopPhases` becomes 8 entries, `step: 1..8`, using the §2.1 names. `phaseRelayMap` becomes `{1:['R2'],2:['R1'],3:[],4:['R2'],5:['R5','R6','R7'],6:['R3'],7:['R4'],8:['R1']}`.
- `handleJumpPhase` keeps painting the client-side highlight (instant feedback) but the server is now authoritative.
- Sub-tabs: `controlSubTab` state with four buttons `data-control-tab="pumps|vision|simulation|pinout"`; inactive panels get CSS `hidden`.

### 5.4 Per-pump dosing

`calcPumpMs(mlVal, pumpKey = 'A')` reads `pumpFlowRates[pumpKey] || calibration.pump_flow_rate_ml_s || 1.5`, clamped to 30000 ms. `handleExecuteManualDose` passes `'A'|'B'|'C'`. Quick-volume chips `[0, 2.5, 5, 10]` per channel with `data-quick-dose="{key}-{value}"`.

### 5.5 Vision studio

`VisionPanel({ selectedUnit, camStatusText, onTriggerCapture })` holds `selectedPreview` state; clicking a gallery thumbnail promotes it into the main frame, clicking "LIVE" returns to `latest_image_url`.

---

## 6. Error handling & limits

| Condition | Behavior |
|---|---|
| `phase_id` outside `0..8` | Clamped server-side; firmware `default:` leaves relays off |
| Jump while a manual override is active | `clearManualOverrides()` runs before the new relays open |
| Requested duration > 30000 ms | Clamped in `manualTriggerRelay`, and again by `calcPumpMs` client-side |
| `presentation/` absent (archived) | `/slides` not mounted — already guarded in `tests/test_minecraft_integration.py` |
| Relay node clicked while a phase is animating | Manual toggle wins; the phase highlight re-derives from `relays` state |

## 7. Testing

New file `tests/test_electronic_control_cockpit.py` covering, per task:

1. Backend phase table covers `0..8`, `0` is `STANDBY`, `8` mentions Preservation.
2. `JUMP_PHASE` sets `active_relays` from `PHASE_RELAY_MAP` and clears a stale list.
3. Firmware `JUMP_PHASE` block calls `clearManualOverrides()` and handles `case 0..8`.
4. `InteractiveChamberSchematic` exists with all seven `data-schematic-relay` nodes.
5. `closedLoopPhases` has 8 steps and `phaseRelayMap` matches §5.3.
6. Sub-tabs exist with all four `data-control-tab` values and inactive panels are `hidden`.
7. `calcPumpMs` reads `pumpFlowRates[pumpKey]`.
8. `VisionPanel` exposes `selectedPreview` and `onTriggerCapture`.

All existing suites (`test_dashboard_overhaul`, `test_presentation_override`, `test_chamber_fsm_preservation`, `test_minecraft_integration`) and `scripts/verify_figma_implementation.py` (26/26) must stay green. `scripts/check_jsx.py` must compile after every `index.html` edit.

## 8. Known limits

- A phase jump is fire-and-forget: no confirmation that the ESP32 applied it. Acceptable — the override auto-reverts and `STOP` always clears.
- `Phase 5: Peristaltic Dosing` energizes all three pumps for the same window. The real per-pump ratio comes from `MANUAL_DOSE`, which already exists; the phase jump is a demonstration of the flow path, not a dose.
- The firmware must be re-flashed for §5.2 to take effect on real hardware.
