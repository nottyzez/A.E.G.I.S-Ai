# A.E.G.I.S. Non-Destructive Presentation Override & Electronic Control Design Spec

**Date:** 2026-10-31  
**Target Files:**
- [`server/static/index.html`](file:///d:/Code%20มหาปลัย/server/static/index.html) (`ElectronicControlTabView` and shared Dashboard state)
- [`main.py`](file:///d:/Code%20มหาปลัย/main.py) (Priority Override Queue, Schedule Coexistence, & Simulation Endpoints)
- [`server/dosing_engine.py`](file:///d:/Code%20มหาปลัย/server/dosing_engine.py) (`TwoTierDosingEngine` integration)

---

## 1. Intent & Why
During live academic presentations and committee demonstrations of the **A.E.G.I.S. Closed-Loop AI Hydroponic Nutrient Management System** for **ผักบุ้ง (Water Spinach)**, the presenter needs full, immediate manual control over every hardware and AI subsystem from the **`Electronic Control`** tab **without turning off or resetting the background scheduled automation system**.

---

## 2. Goals, Non-Goals, & Anti-Goals
- **Goals:**
  1. **Non-Destructive Presentation Override:** Keep the background scheduled automation (`AUTO SCHEDULE: ACTIVE`) running at all times while allowing instant manual command injection.
  2. **Auto-Revert & Collision Prevention (`Hold/Queue`):** Every manual hardware or phase command runs for a bounded duration (e.g., configurable pulse `2s / 5s / 10s` or single-phase step) and automatically reverts to the background schedule upon completion. If the scheduled timer reaches `00:00` during an active manual demo, the scheduled cycle enters **`QUEUED (ชะลอรอจบการสาธิต)`** and executes automatically once the override finishes.
  3. **Full 4-Pillar Presentation Command Deck:**
     - **Dual-State Schedule & Override Banner:** Live countdown for the scheduled cycle (`Interval: 15m / 30m / 1h / 4h`, plus a demo fast-forward test button), active override countdown badge, **"คืนค่าตารางอัตโนมัติทันที (Resume Auto Now)"**, and **"หยุดเฉพาะคำสั่งสาธิต (Cancel Override Only)"**.
     - **Direct Hardware Command Deck (`R1–R7`, Pumps A/B/C, ESP32-CAM):** Individual relay pulse/toggle with selectable duration (`2s`, `5s`, `10s`, `Manual Hold`), Stock A/B/C precision dosing by `mL` or `ms` (showing Priming Delay compensation `t_prime + V/Q`), and instant `ESP32-S3 CAM` capture trigger (`POST /api/cam_command`).
     - **Interactive 6-Phase Closed-Loop Stepper (`Phase 1–6`):** Jump to or execute any of the 6 closed-loop phases (`1. Shunt Intake` → `2. Stabilization` → `3. AI Leaf Scan` → `4. Dynamic Dosing` → `5. Purge & Return` → `6. Main Mixing`) or trigger a full cycle (`START_CYCLE`) while keeping the background schedule active.
     - **Live AI & Sensor Scenario Simulator (Presentation Stage Mode):** Interactive sliders and presets (`Healthy Control`, `Early/Confirmed -N`, `-P`, `-K`, `High EC Lockout`, `Low pH Lockout`) for `EC`, `pH`, and `Water Temp` that compute real-time Two-Factor Dosing via [`TwoTierDosingEngine`](file:///d:/Code%20มหาปลัย/server/dosing_engine.py#L27-L90), allow immediate one-click dosing execution, and optionally sync live to the `Analyze` tab.
  4. **Live Command Activity Log:** Real-time telemetry feed showing sent commands (`POST /api/command`, `POST /api/cam_command`, `POST /api/override/simulate`), response latency, and schedule coexistence status.
- **Non-Goals:**
  - Modifying the physical wiring or GPIO pin assignments of the ESP32-S3 firmware.
- **Anti-Goals (Failure Conditions):**
  - Turning off `AUTO SCHEDULE` when the user clicks a manual relay, pump, or phase button.
  - Letting a scheduled cycle interrupt the presenter mid-demonstration.
  - Breaking any of the existing 198 automated Figma/Dashboard verification checks or breaking offline `file://` preview mode.

---

## 3. Constraints
- Must preserve 100% compatibility with existing `scripts/verify_figma_implementation.py` and `tests/test_dashboard_e2e.py` assertions.
- Must work seamlessly both when served via `python main.py` (`http://localhost:8000/dashboard`) and when opened directly via `file://` (Dual-Path Hybrid Engine).
- All Thai plant terminology must exclusively use **ผักบุ้ง (Water Spinach)**.

---

## 4. Approaches Considered
1. **Approach 1 (Selected): Hybrid Priority Override Engine (FastAPI Backend + Optimistic Frontend State Machine)**
   - Extends [`main.py`](file:///d:/Code%20มหาปลัย/main.py) with non-destructive override state (`override_state`, `/api/override/simulate`, `/api/schedule`, enhanced `/api/command` with `duration_ms`, `mode="PRESENTATION_OVERRIDE"`, and `phase_id`) while running a synchronized local timer & Two-Factor Dosing calculator in [`index.html`](file:///d:/Code%20มหาปลัย/server/static/index.html).
   - *Trade-off:* Slightly more code across backend and frontend, but guarantees zero-latency stage responsiveness, real hardware control when `main.py` is running, and 100% offline reliability if opened via `file://`.
2. **Approach 2: Server-Only State Machine**
   - *Rejected:* Fails when opened via `file://` and introduces 1s polling lag on countdown timers.
3. **Approach 3: Frontend-Only Timer**
   - *Rejected:* Backend [`main.py`](file:///d:/Code%20มหาปลัย/main.py) would remain unaware of simulated scenarios, phase jumps, and schedule `Hold/Queue` state.

---

## 5. Architecture & Implementation Details
### 5.1 Backend (`main.py`)
- Enhance `system_status` with:
  - `schedule`: `{ "enabled": True, "interval_sec": 1800, "remaining_sec": 1420, "queued_during_override": False, "last_auto_run": ... }`
  - `override`: `{ "active": False, "source": None, "label": None, "remaining_ms": 0, "expires_at": 0, "active_relays": [] }`
  - `command_log`: Recent 15 commands with timestamps, mode (`OVERRIDE` vs `AUTO_SCHEDULE`), and target hardware.
- Update `POST /api/command`:
  - Accepts `{ "command": "START_CYCLE" | "MANUAL_RELAY" | "JUMP_PHASE" | "MANUAL_DOSE" | "CANCEL_OVERRIDE" | "RESUME_AUTO" | "STOP", "relay": 1..7, "duration_ms": 5000, "phase_id": 1..6, "dosing_ms": { "pump1_ms": ..., "pump2_ms": ..., "pump3_ms": ... }, "preserve_schedule": True }`.
  - Sets `system_status["override"]` with an auto-expiration timestamp (`expires_at`) without setting `schedule.enabled = False`.
- Add `POST /api/override/simulate`:
  - Accepts `{ "ec": float, "ph": float, "temp": float, "ai_class": str, "ai_confidence": float, "ai_stage": str, "apply_to_status": bool }`.
  - Runs `dosing_engine.compute_dosing(...)`, updates `system_status` so both `Electronic Control` and `Analyze` tabs reflect the live demonstration scenario, and returns the full Two-Factor calculation breakdown.

### 5.2 Frontend (`ElectronicControlTabView` in `server/static/index.html`)
- **Top Coexistence Bar (`Dual-State Schedule & Override Banner`):**
  - Left: Green pulsing badge `AUTO SCHEDULE: ACTIVE (ตารางเวลาอัตโนมัติทำงานอยู่)` + countdown timer `MM:SS` + interval selector (`15m`, `30m`, `60m`, and `Test 15s` for demonstrating the `Hold/Queue` collision protection live on stage!).
  - Right: Dynamic Override Status Pill (`STANDBY — ซิงก์ตามตารางเวลา` vs `PRESENTATION OVERRIDE ACTIVE — เหลือเวลา XXs` vs `AUTO CYCLE QUEUED — รอจบการสาธิต`) + buttons for **`คืนค่าตารางอัตโนมัติทันที (Resume Auto)`** and **`หยุดเฉพาะคำสั่งสาธิต (Stop Override Only)`**.
- **Section 1: 6-Phase Closed-Loop Stepper & Live Override:**
  - Interactive cards for `Phase 1` through `Phase 6` + `สั่งรันครบ 6 ขั้นตอนทันที (Run Full Cycle Override)` and `ข้ามไปสาธิตเฟสที่เลือก (Jump to Phase)`.
- **Section 2: Direct Hardware Relay Matrix (`R1–R7`) & ESP32-CAM Trigger:**
  - Duration preset selector (`2 วินาที`, `5 วินาที`, `10 วินาที`, `เปิดค้างชั่วคราว 30s`) so clicking any relay `R1–R7` fires a real `POST /api/command` (`MANUAL_RELAY`) with a live countdown bar on the relay card and auto-reverts when done.
  - Dedicated `ESP32-S3 CAM — สั่งถ่ายภาพและวิเคราะห์ใบผักบุ้งทันที` button (`POST /api/cam_command`).
- **Section 3: Precision Peristaltic Dosing Override (`Stock A / B / C`) & Live AI Scenario Simulator:**
  - Sliders + quick presets for Stock A (`N-Ca`), Stock B (`P-K-Mg`), Stock C (`Fe-Micro`) in `mL` with real-time conversion to `ms` (`t_prime + V/Q`) and a **`สั่งโดสตามปริมาณที่ตั้งทันที (Inject Override Dose)`** button.
  - **Live Presentation Scenario Simulator:** Quick scenario buttons (`สมดุล (Healthy)`, `ขาดไนโตรเจน (-N)`, `ขาดฟอสฟอรัส (-P)`, `ขาดโพแทสเซียม (-K)`, `EC สูงเกินเกณฑ์ (Lockout)`) + `EC / pH / Temp` sliders that compute the exact Two-Factor dosing plan and let the presenter push the scenario to the whole Dashboard (`Analyze` + `Electronic Control`) in one click.
- **Section 4: Live Command & Coexistence Telemetry Log:**
  - Shows every manual override command injected, its auto-revert timer, and confirmation that the background schedule was preserved.
