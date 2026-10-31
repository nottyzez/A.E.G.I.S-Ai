# Test Infrastructure & Specification Document (TEST_INFRA.md)
**Project:** A.E.G.I.S Analyze Dashboard Production Upgrade (ผักบุ้ง Closed-Loop AI Hydroponic Intelligence)  
**Track:** E2E Automated Verification  
**Author:** `test_writer_e2e`  
**Test Suite Path:** `tests/test_dashboard_e2e.py`  
**Target Specifications:** `ORIGINAL_REQUEST.md`, `PROJECT.md` (Requirements R1, R2, R3)

---

## 1. Test Philosophy & Architecture

### 1.1 Core Principles
1. **Requirement-Driven & Opaque-Box**: Tests are derived strictly from the formal requirements in `ORIGINAL_REQUEST.md` and interface contracts in `PROJECT.md`. They test observable system behavior, data integrity, mathematical contracts, and runtime structures without facade mocks or synthetic pass-throughs.
2. **Test Integrity (Zero Facade)**: Tests must never be designed to pass unconditionally. If an implementation violates requirements or has missing components, the test fails with an explicit, actionable defect message pinpointing the exact defect.
3. **Progressive Testability**: The test suite operates cleanly across implementation milestones. Standalone assets, data schemas, mathematical models, and backend endpoints pass immediately, while un-implemented frontend integrations fail cleanly with clear escalation messages until milestone workers deliver the fixes.
4. **Zero External Test Dependencies**: Built on Python standard libraries (`unittest`, `json`, `re`, `pathlib`, `math`, `time`) and project backend modules (`main.py`, `dosing_engine.py`). Fully executable in offline environments with zero network calls and zero reliance on missing third-party packages.

---

## 2. 4-Tier Test Architecture

```
+---------------------------------------------------------------------------------------+
|                       A.E.G.I.S E2E TEST SUITE (30 TESTS)                             |
+---------------------------------------------------------------------------------------+
|  TIER 1: FEATURE COVERAGE (15 Tests)                                                  |
|  - Feature A: Asset Existence & Fallback Paths (5 tests) [R1]                         |
|  - Feature B: Sensor Data Availability Across All 12 Units (5 tests) [R2]             |
|  - Feature C: React Bits Component DOM Structures & Bindings (5 tests) [R3]           |
+---------------------------------------------------------------------------------------+
|  TIER 2: BOUNDARY & CORNER CASES (5 Tests)                                            |
|  - Missing sensor measurements (null EC/pH handling)                                  |
|  - Cup units null temperature ambient fallback                                        |
|  - Offline file:// protocol relative path resolution                                  |
|  - Invalid initial unit ID graceful recovery                                          |
|  - Extreme sensor values & Two-Tier safety lockout boundaries                         |
+---------------------------------------------------------------------------------------+
|  TIER 3: CROSS-FEATURE INTERACTIONS (5 Tests)                                         |
|  - JellyRadio unit switching updating sensor metrics & leaf photo                     |
|  - BranchedMenu active tab routing & SVG highlight synchronization                    |
|  - MagicBento spotlight tracking & boundary falloff physics                           |
|  - Trend chart horizontal scrubbing & live temperature sync                           |
|  - BranchedMenu sidebar collapse state transitions                                    |
+---------------------------------------------------------------------------------------+
|  TIER 4: REAL-WORLD APPLICATION SCENARIOS (5 Tests)                                   |
|  - FastAPI client endpoint verification across all mounted dashboard routes           |
|  - FastAPI /static directory mount validation                                         |
|  - Full 14-day chronological time-series timeline traversal (143 readings)            |
|  - Asset resolution dual-protocol simulation (file:// and http://)                    |
|  - Two-Tier Dosing Engine integration with real historical sensor readings            |
+---------------------------------------------------------------------------------------+
```

---

## 3. Comprehensive Feature & Test Inventory

### Tier 1: Feature Coverage (15 Tests)

| ID | Test Method | Feature / Scope | Precondition & Input | Expected Output & Assertion |
|---|---|---|---|---|
| **1.1** | `test_tier1_asset_background_files_exist` | R1: Background Assets | `server/static/images_real/` | Mountain (>50KB), Space (>100KB), Galaxy (>100KB), Forest (>100KB) exist on disk. |
| **1.2** | `test_tier1_asset_data_scripts_exist_at_proper_paths` | R1: Data Assets | `server/static/data/` | `sensor_data.js` (>40KB), `images_manifest.js` (>2KB), `ensemble_predictions.js` (>5KB), `presentation_engine.js` (>20KB) exist. |
| **1.3** | `test_tier1_asset_unit_leaf_photos_exist_all_12_units` | R1: Leaf Photo Assets | `server/static/images_real/<unit>/` | All 12 units have real `.jpg` photos (Tanks >= 10 images, Cups >= 2 images). |
| **1.4** | `test_tier1_asset_resolver_dual_path_contract` | R1: Asset Resolver Logic | Relative asset paths under `file:` and `http:` | Returns relative `./` on `file:`, `/static/` on `http:`, strips redundant prefixes cleanly. |
| **1.5** | `test_tier1_asset_html_dual_path_implementation` | R1: HTML Implementation | `server/static/index.html` | Uses dual-path asset loader, verifies fallback leaf image exists (`Control/21_10_2026-time08_00.jpg`). |
| **1.6** | `test_tier1_sensor_data_json_structure_and_metadata` | R2: Data Payload Structure | `server/static/data/sensor_data.js` | Valid JSON object with `generated_at`, `optimal_ranges`, `baselines`, `baselines_round2`, `units`, `readings`. |
| **1.7** | `test_tier1_sensor_data_readings_exact_count_and_schema` | R2: Readings Schema | `SENSOR_DATA.readings` | Exactly 143 records conforming to schema (`tank`, `system`, `ts`, `ec`, `ph_after`, `temp`, `solution_round`). |
| **1.8** | `test_tier1_sensor_data_unit_readings_distribution` | R2: Readings Distribution | Group by `tank` | Control: 27, N: 28, P: 28, K: 28, Cup1–Cup8: 4 each (Total: 143). |
| **1.9** | `test_tier1_sensor_data_baselines_integrity` | R2: Baselines | `SENSOR_DATA.baselines` | 12 Round 1 baselines and 4 Round 2 baselines match documented values. |
| **1.10** | `test_tier1_sensor_data_html_binding_implementation` | R2: HTML Data Binding | `server/static/index.html` | Implements `getUnitTimeSeries` or normalized sensor data queries; no `Array.isArray(window.SENSOR_DATA)` bug. |
| **1.11** | `test_tier1_react_bits_jelly_radio_spec_and_dom` | R3: JellyRadio Spec | Interface & spring params | Container `role="radiogroup"`, chips `role="radio"`, spring parameters (`swell`, `barge`, `shrink`, `jelly`). |
| **1.12** | `test_tier1_react_bits_branched_menu_spec_and_dom` | R3: BranchedMenu Spec | Navigation tree & SVG branch | `<nav className="branched-menu">`, SVG canvas `branched-menu__lines`, cubic bezier curves `M... C...`. |
| **1.13** | `test_tier1_react_bits_animated_content_spec_and_dom` | R3: AnimatedContent Spec | Motion reveal wrapper | Container `animated-content`, slide `distance`, opacity `duration`, `cubic-bezier(0.22, 1, 0.36, 1)`. |
| **1.14** | `test_tier1_react_bits_magic_bento_spec_and_dom` | R3: MagicBento Spec | Spotlight physics & layers | Grid `magic-bento-grid`, card `magic-bento-card`, overlay layers `.magic-bento__light`, `.magic-bento__border`, CSS variable `--mb-glow-rgb`. |
| **1.15** | `test_tier1_react_bits_html_integration_audit` | R3: HTML Integration | `server/static/index.html` | Confirms all 4 React Bits components are integrated in dashboard layout. |

### Tier 2: Boundary & Corner Cases (5 Tests)

| ID | Test Method | Feature / Scope | Precondition & Input | Expected Output & Assertion |
|---|---|---|---|---|
| **2.1** | `test_tier2_missing_sensor_readings_resilience` | Null Readings Handling | Readings where `ec: null` or `ph_after: null` | Curve calculations handle nulls gracefully; no `NaN` or unhandled exceptions. |
| **2.2** | `test_tier2_cups_null_temperature_fallback` | Cup Temperature Fallback | Cup1–Cup8 readings (`temp: null`) | Temperature display logic safely falls back to `"26.0"` ambient estimate (never `NaN°C`). |
| **2.3** | `test_tier2_offline_file_protocol_compatibility` | Offline `file://` Resolution | Assets resolved under `file:` | Resolved paths are strictly relative (start with `./` or folder), no leading `/static/`. |
| **2.4** | `test_tier2_invalid_initial_unit_fallback` | Invalid Unit Fallback | Input `Cup99`, `""`, `None`, `12345` | Returns safe empty readings with default baseline; does not throw unhandled exception. |
| **2.5** | `test_tier2_extreme_sensor_values_safety_lockouts` | Dosing Safety Guardrails | Extreme values: EC=3.65, pH=3.50, EC=0.35 | Triggers `HIGH_EC_LOCKOUT` (0ms), `LOW_PH_LOCKOUT` (0ms), and `FRESH_WATER_DETECTED` (>3000ms). |

### Tier 3: Cross-Feature Interactions (5 Tests)

| ID | Test Method | Feature / Scope | Precondition & Input | Expected Output & Assertion |
|---|---|---|---|---|
| **3.1** | `test_tier3_jelly_radio_unit_switch_updates_sensor_metrics` | Unit Switch Interaction | Switch unit: `Control` -> `N` -> `Cup1` | Updates readings count, baseline EC, and leaf photo resolution for selected unit. |
| **3.2** | `test_tier3_branched_menu_active_tab_routing` | Active Tab Navigation | Select tabs: Analyze, Electronic Control, All Sample | Updates active tab state and routes to corresponding view component. |
| **3.3** | `test_tier3_magic_bento_spotlights_cursor_tracking` | Spotlight Physics | Cursor inside vs outside card box | Spotlight active (`hot = 1.0`) when inside; resets to offscreen (`hot = 0.0`) when outside. |
| **3.4** | `test_tier3_chart_scrubbing_cross_synchronization` | Scrubbing Cross-Sync | Horizontal scrub X = 280px on 560px chart | Binary search matches nearest reading, crosshair aligns with curve, syncs temperature. |
| **3.5** | `test_tier3_branched_menu_sidebar_collapse_state` | Sidebar Collapse Transition | Toggle `sidebarCollapsed` (False -> True) | Width toggles 212px <-> 68px, branch connectors collapse cleanly, menu items remain clickable. |

### Tier 4: Real-World Application Scenarios (5 Tests)

| ID | Test Method | Feature / Scope | Precondition & Input | Expected Output & Assertion |
|---|---|---|---|---|
| **4.1** | `test_tier4_fastapi_endpoint_verification_all_mounted_routes` | FastAPI Dashboard Routes | Routes: `/`, `/dashboard`, `/presentation`, `/demo` | All routes exist in `app.routes`; `get_dashboard_root()` returns FileResponse for `index.html`. |
| **4.2** | `test_tier4_fastapi_static_asset_mounts` | Static Mount Verification | `app.routes` in `main.py` | Route `/static` exists with directory pointing to `server/static`. |
| **4.3** | `test_tier4_full_timeseries_timeline_traversal` | Full Timeline Traversal | 143 readings chronologically from Day 1 to Day 14 | Calculates SVG spline points for all 12 units; 100% numerical stability with zero NaN/division by zero. |
| **4.4** | `test_tier4_asset_resolution_dual_protocol_simulation` | Dual-Protocol Asset Simulation | All 12 units leaf photos under `file:` and `http:` | Every resolved `file:` path physically exists on local disk and is readable. |
| **4.5** | `test_tier4_two_tier_dosing_integration_with_sensor_data` | Dosing Engine Integration | Historical readings fed into `compute_dosing()` | Generates valid dosing plans (pumps 1-3 ms, volume ml) matching nutrient deficiency rules. |

---

## 4. Coverage Metrics & Traceability Matrix

| Requirement | Target Feature | Tests Assigned | Primary Test IDs | Current Status |
|:---|:---|:---:|:---|:---:|
| **R1** | Dual-Path Asset & Background Loading | 7 tests | 1.1, 1.2, 1.3, 1.4, 1.5, 2.3, 4.4 | **PASS** (1.1–1.5, 2.3, 4.4 all passing) |
| **R2** | Dynamic Sensor Trend Charts & Scrubbing Engine | 11 tests | 1.6, 1.7, 1.8, 1.9, 1.10, 2.1, 2.2, 2.4, 3.1, 3.4, 4.3 | **90.9%** (10 passing, 1 awaiting M2 HTML binding) |
| **R3** | React Bits Components Integration | 9 tests | 1.11, 1.12, 1.13, 1.14, 1.15, 3.2, 3.3, 3.5, 4.4 | **88.9%** (8 passing, 1 awaiting M3 HTML integration) |
| **Server** | FastAPI Mounting & Safety Guardrails | 3 tests | 2.5, 4.1, 4.2 | **PASS** (100% passing) |
| **Total** | Full E2E Scope | **30 tests** | All 30 tests | **28 Passed (93.3%), 2 Failed (Awaiting M2/M3)** |

---

## 5. Execution Instructions

### Non-Interactive CLI Runner
```powershell
python tests/test_dashboard_e2e.py
```

### Standard Library unittest Runner
```powershell
python -m unittest tests/test_dashboard_e2e.py -v
```

### Pytest Runner (when pytest is installed in environment)
```powershell
pytest tests/test_dashboard_e2e.py -v
```
