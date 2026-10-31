# Next-Gen 3D Presentation Dashboards (Dual-Mode) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build two distinct, presentation-ready 3D web dashboards (`presentation_3d_hud.html` and `presentation_3d_bento.html`) in `server/static/` inspired by the Settigation dark-mode aesthetic, connecting a Three.js digital twin to physical pump actuation and FastAPI telemetry without modifying any existing dashboard files.

**Architecture:** Standalone HTML5 + Tailwind CSS CDN + Three.js r128 + Lucide Icons + Native ES6. A shared client-side engine provides 3D procedural kale plant rendering, nutrient fluid dynamics, 1000ms `/api/status` polling, `/api/command` actuation (Relays 1–7), and an autonomous client-side simulation fallback.

**Tech Stack:** Three.js r128, OrbitControls, Tailwind CSS, Lucide Icons, JetBrains Mono & Plus Jakarta Sans fonts, FastAPI backend (`main.py`).

**Spec:** `docs/superpowers/specs/2026-10-25-3d-presentation-dashboards-design.md`

## Global Constraints
- Zero modification to existing files (`server/static/dashboard.html`, `server/static/presentation_controller.html`, etc.).
- Hardware Relay mapping strictly adheres to firmware: Relays 1–4 = Fluidics, Relays 5–7 = Fertilizer Peristaltic Pumps N-P-K.
- Stepper strictly mirrors physical 6-Phase sequence (Sampling In -> Measuring & AI -> Sample Return -> Dosing NPK -> Probe Rinse -> Drain Waste).
- Standalone execution: Zero npm build step; must run out of `main.py` at `/static/...` or direct double-click in browser with offline demo simulation.

## Review Focus
1. **Offline / Disconnected ESP32**: Dashboard must not freeze, crash, or show an empty black screen when ESP32 or backend is offline; client-side demo simulation must engage smoothly.
2. **Relay Pinout Safety**: Clicking Pump N (Relay 5) must never send `relay: 1` (Inflow pump).
3. **Showcase Mode Lock**: Previewing deficiency symptoms in 3D must not be reverted on the next 1000ms polling tick until the user clicks "Resume Live Sync".
4. **Mobile & Projection Responsiveness**: The Bento Grid and floating HUD must scale cleanly on 1080p projectors and laptops without overflow or clipping.
5. **Camera Image Cache Busting**: Manual photo capture must bust the browser image cache (`latest_capture.jpg?t=...`).

---

### Task 1: Create Shared 3D Plant & Simulation Engine
**Files:**
- Create: `server/static/presentation_engine.js`

**Interfaces:**
- Produces:
  - `class HydroponicTwin3D(canvasElement, options)`: Manages Three.js scene, procedural kale plant with deficiency shaders, nutrient fluid mesh with bubbling particles, camera orbit presets (`topdown`, `tank`, `isometric`), and deficiency transitions (`setDeficiency(cls)`).
  - `class PresentationStateController(options)`: Handles 1000ms polling of `GET /api/status`, command dispatch to `POST /api/command`, camera dispatch to `POST /api/cam_command`, mode switching (`live` vs `demo`), and client-side simulation loop.

- [ ] **Step 1: Implement `HydroponicTwin3D` in `server/static/presentation_engine.js`**
  - Setup Scene, PerspectiveCamera, WebGLRenderer with antialias and alpha.
  - Create procedural kale plant: stem, branching petioles, 8 curled ruffled leaves with custom vertex/fragment or Phong material tints (Normal green, N yellow, P purple, K leaf margin chlorosis).
  - Create translucent acrylic reservoir with animated wave vertex shader and rising air bubbles.
  - Add OrbitControls with smooth damping and camera view helper methods.

- [ ] **Step 2: Implement `PresentationStateController` in `server/static/presentation_engine.js`**
  - Implement polling logic with timeout and error handling.
  - Implement client-side simulation state machine with synthetic EC (1.85 ± 0.05 mS/cm), pH (6.20 ± 0.04), Temp (26.5 ± 0.2°C).
  - Implement command dispatchers: `sendRelayCommand(relayId, durationMs)`, `startCycle()`, `emergencyStop()`, `capturePhoto()`.
  - Implement symptom showcase lock with `lockShowcase(symptomClass)` and `resumeLiveSync()`.

- [ ] **Step 3: Verify syntax and exports**
  - Run Node check: `node -c server/static/presentation_engine.js`

---

### Task 2: Build `server/static/presentation_3d_hud.html` (Immersive 3D HUD View)
**Files:**
- Create: `server/static/presentation_3d_hud.html`

**Interfaces:**
- Consumes: `HydroponicTwin3D`, `PresentationStateController` from `presentation_engine.js`.
- Produces: Complete HTML5 web application mounted at `/static/presentation_3d_hud.html`.

- [ ] **Step 1: Structure HTML and Settigation Glassmorphism Styling**
  - Dark obsidian background (`#060a08`), full-screen fixed canvas (`#webgl-canvas`).
  - Google Fonts (`Plus Jakarta Sans`, `Kanit`, `JetBrains Mono`), Lucide icons, Tailwind CSS CDN.
  - Glass card utility classes (`bg-emerald-950/40 backdrop-blur-xl border border-emerald-500/20`).
  - Animated CSS border beam gradients.

- [ ] **Step 2: Build Floating Top Header & 6-Phase Stepper**
  - Brand identity: A.E.G.I.S. AI Smart Hydroponics Digital Twin.
  - Live Connection Status pill (pulsing dot, latency) + Live/Demo mode toggle button.
  - Horizontal 6-Phase physical stepper with active glow states.
  - Red Emergency Stop button (`STOP`).

- [ ] **Step 3: Build Left Floating Bento Card (Telemetry HUD)**
  - Circular SVG animated gauge meters for EC, pH, and Water Temp.
  - Two-Tier AI diagnostic status badge with stage indicator.
  - Camera orbit view preset buttons (`Top-Down`, `Tank`, `Reset`).

- [ ] **Step 4: Build Right Floating Bento Card (Vision & Two-Tier AI)**
  - Live ESP32-CAM preview with capture photo trigger button and timestamp.
  - AI symptom breakdown and Two-Tier NPK Dosing recommendation (Pump 1/2/3 ms & ml).

- [ ] **Step 5: Build Bottom Floating Dock (Actuation Station)**
  - Tactile matrix buttons for Relays 1–7 with live active pulsing ring.
  - Pulse duration selectors (500ms, 1000ms, 2000ms, 5000ms).
  - Prominent "START FULL AI CYCLE" button.

- [ ] **Step 6: Integrate with `presentation_engine.js` and verify rendering**
  - Bind telemetry polling and UI updates.
  - Test offline demo simulation behavior.

---

### Task 3: Build `server/static/presentation_3d_bento.html` (Settigation Bento Grid View)
**Files:**
- Create: `server/static/presentation_3d_bento.html`

**Interfaces:**
- Consumes: `HydroponicTwin3D`, `PresentationStateController` from `presentation_engine.js`.
- Produces: Complete HTML5 web application mounted at `/static/presentation_3d_bento.html`.

- [ ] **Step 1: Layout 12-Column Settigation Bento Grid**
  - Dark mode obsidian layout with modular responsive grid cards.
  - Bento card headers with glowing pill badges and monospace coordinate tags.

- [ ] **Step 2: Build Tile A (Col 1-8, Row 1-2): Hero 3D Digital Twin Viewer**
  - Dedicated rounded container embedding `HydroponicTwin3D`.
  - Top bar with view rotation presets and wireframe toggle.
  - Bottom floating symptom selector buttons (`Healthy`, `-N Nitrogen`, `-P Phosphorus`, `-K Potassium`) with Showcase Lock indicator and "Resume Live" button.

- [ ] **Step 3: Build Tile B (Col 9-12, Row 1): AI Diagnostic & Vision Feed**
  - High-res camera image card with instant capture action button.
  - Two-tier classification badge and late-fusion confidence meter.

- [ ] **Step 4: Build Tile C (Col 9-12, Row 2): Hydroponic Sensor Array**
  - Metric tiles for EC, pH, Temp with live min/max markers and target delta indicator.

- [ ] **Step 5: Build Tile D (Col 1-7, Row 3): Hardware Actuation Switchboard**
  - Complete 7-relay manual test console (Inflow, Return, Rinse, Drain, Pump N, Pump P, Pump K).
  - Dosing calibration parameters preview (Flow rate ml/s, Priming delay).
  - Start Full AI Cycle trigger and Emergency Stop.

- [ ] **Step 6: Build Tile E (Col 8-12, Row 3): Live Event Stream & Monospace Terminal**
  - Real-time auto-scrolling log capturing hardware polling, dispatched relay pulses, and AI diagnosis logs.

---

### Task 4: Verification, Non-Interference Check, and Final Delivery
**Files:**
- Verify: `server/static/dashboard.html` (must be byte-identical to original)
- Verify: `server/static/presentation_controller.html` (must be byte-identical to original)
- Verify: `server/static/presentation_3d_hud.html` (HTTP 200 via test request)
- Verify: `server/static/presentation_3d_bento.html` (HTTP 200 via test request)

- [ ] **Step 1: Verify git status confirms existing files are untouched**
- [ ] **Step 2: Test both pages in browser or sandbox**
- [ ] **Step 3: Deliver direct clickable links and presentation guide to the user**
