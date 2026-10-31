# Non-Destructive Presentation Override & Electronic Control Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the `Electronic Control` tab (`ElectronicControlTabView`) and FastAPI backend (`main.py`) with a Hybrid Priority Override Engine so the presenter can manually control relays `R1–R7`, peristaltic dosing (`Stock A/B/C`), `ESP32-S3 CAM` capture, 6-step Closed-Loop phases (`Phase 1–6`), and live AI/sensor scenarios during a presentation while keeping the background scheduled automation system active (`AUTO SCHEDULE: ACTIVE`) with auto-revert and `Hold/Queue` collision protection.

**Architecture:** We extend `main.py` with non-destructive override state (`schedule`, `override`, `command_log`), enhanced `/api/command` (`MANUAL_RELAY`, `JUMP_PHASE`, `MANUAL_DOSE`, `START_CYCLE`, `CANCEL_OVERRIDE`, `RESUME_AUTO`), `/api/schedule`, and `/api/override/simulate` backed by `TwoTierDosingEngine`. In `server/static/index.html`, `ElectronicControlTabView` implements the 4-Pillar Presentation Command Deck with optimistic local state + dual-path (`http://` and `file://`) execution and cross-tab scenario synchronization.

**Tech Stack:** Python 3, FastAPI, React 18 (Babel standalone in `server/static/index.html`), Tailwind CSS, `TwoTierDosingEngine` (`server/dosing_engine.py`).

**Spec:** [`docs/superpowers/specs/2026-10-31-presentation-override-control-design.md`](file:///d:/Code%20มหาปลัย/docs/superpowers/specs/2026-10-31-presentation-override-control-design.md)

## Global Constraints

- Preserve all 198 existing verification assertions (`scripts/verify_figma_implementation.py`, `tests/test_dashboard_e2e.py`).
- Keep the comment `{/* Peristaltic Fertilizer Dosing Deck (5 Cols) */}` in `server/static/index.html` and never add `figma-card-aegis-analyze` outside `AnalyzeTabView`.
- Support both `http://localhost:8000/dashboard` (`python main.py`) and direct `file://` opening via dual-path fallback.
- Use **ผักบุ้ง (Water Spinach)** exclusively in all Thai plant descriptions.

## Review Focus

- Scheduled countdown hitting `00:00` while a manual presentation override is active must set `schedule.queued_during_override = True` (`AUTO CYCLE QUEUED`) rather than interrupting the active demo or turning off `schedule.enabled`.
- Cancelling an override (`CANCEL_OVERRIDE`) must immediately clear active manual relays and return to `AUTO SCHEDULE: ACTIVE` without disabling the schedule timer.
- Extreme simulated sensor values (`ec >= 3.2` or `ph <= 4.2`) in `/api/override/simulate` and the frontend simulator must trigger `LOCKED_OUT` (`HIGH_EC_LOCKOUT` / `LOW_PH_LOCKOUT`) with `0 ms` pump durations.
- Manual dosing (`Stock A / B / C`) with `0 mL` for a channel must compute `0 ms` for that pump (priming delay `t_prime` is only added when `V_i > 0`).
- Offline `file://` mode must gracefully catch `fetch()` failures and execute the identical local override/simulation state machine without throwing unhandled promise rejections.

---

### Task 1: Backend Priority Override Queue, Schedule Coexistence, & Simulation API (`main.py`)

**Files:**
- Modify: `main.py:42-70`, `main.py:362-475`
- Test: `tests/test_presentation_override.py`

**Interfaces:**
- Consumes: `dosing_engine.compute_dosing(ec, ph, temp, ai_class, ai_confidence, ai_stage)` from `server/dosing_engine.py`
- Produces:
  - `POST /api/command` accepting `command`, `relay`, `duration_ms`, `phase_id`, `dosing_ms`, `preserve_schedule`
  - `POST /api/schedule` accepting `interval_sec`, `remaining_sec`, `action` (`"SET_INTERVAL" | "SIMULATE_COLLISION" | "RESUME_QUEUED"`)
  - `POST /api/override/simulate` accepting `ec`, `ph`, `temp`, `ai_class`, `ai_confidence`, `ai_stage`, `apply_to_status`
  - `GET /api/status` returning `schedule`, `override`, and `command_log` fields inside `current_hardware_status`

- [x] **Step 1: Write the failing test in `tests/test_presentation_override.py`**
- [x] **Step 2: Run test to verify it fails**
- [x] **Step 3: Implement non-destructive override queue, schedule coexistence, and `/api/override/simulate` in `main.py`**
- [x] **Step 4: Run test to verify it passes**

---

### Task 2: Frontend 4-Pillar Presentation Override Control Deck (`server/static/index.html`)

**Files:**
- Modify: `server/static/index.html:3145-3337`, `server/static/index.html:3434-3715`
- Test: `tests/test_presentation_override.py`

**Interfaces:**
- Consumes: `POST /api/command`, `POST /api/cam_command`, `POST /api/schedule`, `POST /api/override/simulate`, `POST /api/calibration`, `GET /api/status` (with local offline fallback when `fetch` fails or on `file://`)
- Produces:
  - `ElectronicControlTabView({ selectedUnit, setSelectedUnit, unitSummary, onTriggerDose, liveOverrideScenario, setLiveOverrideScenario })`
  - Dual-State Schedule & Override Banner (`AUTO SCHEDULE: ACTIVE`, countdown timer, `Test 15s` collision demo, `Resume Auto Now`, `Stop Override Only`)
  - Interactive 6-Phase Closed-Loop Stepper (`Phase 1–6` jump + `START_CYCLE` full cycle override)
  - Direct Hardware Relay Matrix (`R1–R7` with `2s / 5s / 10s / 30s` auto-revert pulse timers) & `ESP32-S3 CAM` instant capture button
  - Precision Peristaltic Dosing Override (`Stock A/B/C` mL sliders + `ms` priming calculator) & Live AI Scenario Simulator (`Healthy`, `-N`, `-P`, `-K`, `High EC Lockout`)
  - Live Command & Coexistence Telemetry Log

- [x] **Step 1: Add frontend DOM & simulation verification tests to `tests/test_presentation_override.py`**
- [x] **Step 2: Implement upgraded `ElectronicControlTabView` and shared override state in `server/static/index.html`**
- [x] **Step 3: Run `tests/test_presentation_override.py`, `scripts/verify_figma_implementation.py`, and `tests/test_dashboard_e2e.py` to verify 100% pass rate**
