# Project: A.E.G.I.S Analyze Dashboard Production Upgrade

## Architecture
- **Runtime Environment**: In-browser React 18 + ReactDOM 18 (UMD CDN), Babel Standalone runtime transpilation, Tailwind CSS CDN, Three.js r128.
- **Backend Server**: FastAPI (`main.py`) serving static assets from `server/static` via `/static` mount.
- **Client Protocol Support**: Dual-path runtime support for both `file://` protocol (local filesystem) and `http://` (FastAPI web server).
- **Data Architecture**: Structured JSON payload in `window.SENSOR_DATA` (`server/static/data/sensor_data.js`) with 143 time-series readings across 12 experimental units (Control, N, P, K, Cup1–Cup8).
- **UI & Micro-Interactions**: Figma SnowUI dark-glass design system enhanced with four self-contained React Bits components: `<JellyRadio />`, `<BranchedMenu />`, `<AnimatedContent />`, `<MagicBento />`.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Universal Asset Resolver | `__AEGIS_ASSET_RESOLVER__` dynamically handles relative (`.`) vs web (`/static`) paths | M1 | Survey 1 (R1) |
| 2 | Synchronous Script Bootstrapper | Protocol-aware `<head>` loader for sensor, manifest, and engine data scripts | M1 | Survey 1 (R1) |
| 3 | Dual-Path Backgrounds | `CosmicThreeBackground` loads `dashboard_mountain_bg.jpg` and `space_bg.jpg` on both protocols | M1 | Survey 1 (R1) |
| 4 | Leaf Photo Path & Fallback Fix | Corrects `getUnitLeafPhoto` directory prefixing and fallback to verified existing image | M1 | Survey 1 (R1) |
| 5 | Multi-Mount Server Routes | Adds `/images_real` and `/data` static mounts in `main.py` for defense-in-depth | M1 | Survey 1 (R1) |
| 6 | Sensor Data Normalizer | Parses `window.SENSOR_DATA.readings`, filtering by `r.tank === unitId` with field mappings | M2 | Survey 2 (R2) |
| 7 | Dynamic PH Trend Chart | Smooth cubic bezier SVG plotting pH time-series, optimal range band, and scrub tooltip | M2 | Survey 2 (R2) |
| 8 | Dynamic EC Trend Chart | Dual-spline SVG plotting Round 1 vs Round 2, baseline delta, and crosshair tracking | M2 | Survey 2 (R2) |
| 9 | Dynamic Projections vs Actuals | Time-series bar visualization comparing actual EC uptake against target baseline | M2 | Survey 2 (R2) |
| 10 | Live Temperature Synchronization | Real-time temperature readout & sparkline synced with scrubbed timestamp | M2 | Survey 2 (R2) |
| 11 | `<JellyRadio />` Component | Spring physics segmented radio control with neighbor barge push for unit selection | M3 | Survey 3 (R3) |
| 12 | `<BranchedMenu />` Component | Organic SVG curved branch tree navigation for sidebar tabs | M3 | Survey 3 (R3) |
| 13 | `<AnimatedContent />` Component | Motion reveal wrapper with slide, blur, and opacity transitions for views and tabs | M3 | Survey 3 (R3) |
| 14 | `<MagicBento />` Component | Interactive cursor spotlight, border glow, and subtle 3D tilt for telemetry cards | M3 | Survey 3 (R3) |
| 15 | E2E Testing Suite (Tiers 1–4) | Systematic automated verification covering assets, trend charts, and React Bits | E2E Track | ORIGINAL_REQUEST |
| 16 | Final Integration & Verification | 100% test pass on both `file://` and `main.py` with zero console errors | M4 | ORIGINAL_REQUEST |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Dual-Path Asset and Background Loading System | Features 1–5 (R1) | none | DONE |
| M2 | Dynamic Sensor Trend Charts & Scrubbing Engine | Features 6–10 (R2) | M1 | DONE |
| M3 | React Bits Components Integration | Features 11–14 (R3) | M1 | DONE |
| M4 | Final Milestone: Full E2E Test Pass & Verification | Features 15–16 | M2, M3, E2E Track | DONE |

## Interface Contracts
### Asset Resolver ↔ Dashboard Components
- Function: `window.__AEGIS_ASSET_RESOLVER__(relativePath: string): string`
  - Input: e.g. `'images_real/dashboard_mountain_bg.jpg'`, `'data/sensor_data.js'`
  - Output on `file://`: `'./images_real/dashboard_mountain_bg.jpg'`
  - Output on HTTP: `'/static/images_real/dashboard_mountain_bg.jpg'`

### Sensor Data Engine ↔ Trend Chart Components
- Function: `getUnitTimeSeries(unitId: string)`
  - Output: `{ unitReadings: Array<Reading>, baseline: number, baselineR2: number, optimal: object }`
  - Reading Schema: `{ ts: string, ec: number|null, ph_after: number|null, ph_before: number|null, temp: number|null, notes: string|null, quality_flag: array }`

### React Bits ↔ Dashboard Shell
- `<JellyRadio items={units} value={selectedUnit} onChange={(u) => setSelectedUnit(u)} />`
- `<BranchedMenu items={navTree} active={activeTab} onSelect={(tab) => setActiveTab(tab)} collapsed={sidebarCollapsed} />`
- `<AnimatedContent distance={20} duration={0.45}>{children}</AnimatedContent>`
- `<MagicBento glowColor="198, 199, 248">{cards}</MagicBento>`

## Code Layout
- `server/static/index.html` — Main dashboard single-page application (React 18 + Babel)
- `main.py` — FastAPI application server
- `server/static/data/sensor_data.js` — Sensor time-series dataset (`window.SENSOR_DATA`)
- `server/static/data/images_manifest.js` — Leaf photos manifest (`window.IMAGES_MANIFEST`)
- `server/static/images_real/` — Background images and unit leaf photos
- `tests/test_dashboard_e2e.py` — Automated verification suite for dashboard features
