# Home & Dashboard 11 React Bits Components + Electronic Control UX/UI Cleanup Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate 11 React Bits components into `server/static/index.html` — `<GradientASCII />` + `<Particles />` (Home background), `<TechText />` (`"A.E.G.I.S"` wordmark), `<Crosshair />` (Home HUD targeting reticle), `<SpecularButton />` (primary CTA buttons), `<CountUp />` (numeric readouts), `<DepthCarousel />` (3D leaf gallery in `VisionPanel`), `<MagicBento />` (every Bento card in `ElectronicControlTabView`), `<SloshGauge />` (water volume, flow rate, and fertilizer volume tanks in `#settings-pumps`), `<RubberSegment />` (category switchers), and `<AnimatedContent />` (staggered entrance animations across all 4 views: Home, Analyze, Model Architecture, Electronic Control) — while decluttering `ElectronicControlTabView` (`หน้าควบคุมวงจร`) into a compact top status/phase bar plus a 4-tab segmented view with Thai-first labels and separated `R1–R4` vs. `R5–R7` relay groups.

**Architecture:** We keep `server/static/index.html` as a self-contained React 18 + Tailwind CSS single-page app. All 11 React Bits components (`GradientASCII`, `Particles`, `TechText`, `Crosshair`, `SpecularButton`, `CountUp`, `DepthCarousel`, `MagicBento`, `SloshGauge`, `RubberSegment`, `AnimatedContent`) are embedded in IIFE modules (`const ComponentName = (() => { ... })();`) to prevent identifier collisions (`VERTEX`, `FRAGMENT`, `SHAPES`, `INTRO_SECONDS`, `clamp`, `clamp01`, `wrap`, `smoothstep`, `noise`, `compile`, `link`, `H`, `STEP`, `FONT`) and provide zero-dependency browser shims (`animate`, `cubicBezier`, `useInView`, `useMotionValue`, `useTransform`, `useReducedMotion`, `motion.div`, `gsap`, `ScrollTrigger`, and inline SVGs). In `ElectronicControlTabView`, inactive sub-tabs (`pumps`, `vision`, `simulation`, `pinout`) toggle visibility via CSS (`block` vs `hidden`) rather than unmounting, guaranteeing 100% DOM presence for existing test suites.

**Tech Stack:** React 18 (Babel standalone JSX in `server/static/index.html`), WebGL2 (`GradientASCII`, `Particles`, `SpecularButton`), 2D Canvas (`TechText`, `Crosshair`), 3D CSS Perspective (`DepthCarousel`), `CountUp`, `MagicBento`, `SloshGauge`, `RubberSegment` & `AnimatedContent` (React Bits), Tailwind CSS, Python `unittest`.

**Spec:** `docs/superpowers/specs/2026-11-05-control-ux-ui-copy-cleanup-design.md`

## Component Source Code Locations (For Subagents / Other Agents)

All 11 React Bits component full JS + CSS sources provided by the user are stored in `C:\Users\Admin\.gemini\antigravity\brain\3db8a5a7-963d-4d8f-a985-fe689ed088ef\.system_generated\logs\transcript_full.jsonl` at the following exact line numbers (read with `StartLine` = `EndLine`):

| Component | Line in `transcript_full.jsonl` | Step Index |
|---|---|---|
| `<Particles />` + `<GradientASCII />` | Line `5345` | `5142` |
| `<CountUp />` | Line `5359` | `5156` |
| `<TechText />` | Line `5371` | `5168` |
| `<DepthCarousel />` | Line `5379` | `5176` |
| `<SpecularButton />` | Line `5391` | `5188` |
| `<MagicBento />` | Line `5399` | `5196` |
| `<SloshGauge />` | Line `5409` | `5206` |
| `<RubberSegment />` | Line `5415` | `5212` |
| `<Crosshair />` + `<AnimatedContent />` | Line `5421` | `5218` |

## Global Constraints

- Zero `text-[10px]` or `text-[11px]` utility classes inside `ElectronicControlTabView` (`test_no_body_copy_below_twelve_pixels`).
- Never use the forbidden substring `"Control (สมบูรณ์)"` or `"quickUnits"` in `server/static/index.html` (`TestAllSampleRemoval` in `tests/test_dashboard_overhaul.py`).
- All Thai plant references must use `ผักบุ้ง` (Water Spinach).
- On the Home page (`currentView === 'home'`), remove the old `home-backdrop` (`back.jpg`) and hide the Three.js starfield canvas, rendering the `<GradientASCII />` + `<Particles />` combo with the exact user-specified props.
- In `HomeView`, render `<Crosshair containerRef={homeContainerRef} color="#ffffff" targetEffect="lock" thickness={1} opacity={0.85} smoothing={0.35} showCoordinates />`, `<TechText text="A.E.G.I.S" ... />`, and `<SpecularButton />` for the primary CTA buttons (`ENTER A.E.G.I.S ANALYZE`, `READ SYSTEM SPEC +`).
- Wrap content sections across **every page/view in `server/static/index.html`** (`HomeView`, `AnalyzeTabView`, `ModelArchitectureTabView`, `ElectronicControlTabView`) with `<AnimatedContent distance={100} direction="vertical" duration={0.8} ease="power3.out" blur={0} stagger={0.08} threshold={0.1}>`.
- Use `<SpecularButton />` selectively on primary action buttons in `ElectronicControlTabView` (`▶ รันอัตโนมัติครบ 6 ขั้นตอน`, `💧 สั่งฉีดปุ๋ยตามสูตรทันที`, `📸 สั่งถ่ายภาพใหม่`) so active WebGL2 contexts remain well within the browser limit (<= 6 per view).
- Integrate `<CountUp />` for key numeric readouts across `AnalyzeTabView` (Temperature, pH, EC KPIs) and `ElectronicControlTabView` (dosing volumes/durations and simulated sensor metrics).
- Integrate `<DepthCarousel />` inside `VisionPanel` (`#settings-vision`) to display the saved experimental ผักบุ้ง leaf photos in a 3D depth stack (`depth={220}`, `spread={90}`, `tilt={22}`, `tiltDirection="right"`, `perspective={1400}`, `visibleCards={4}`, `falloff={0.2}`, `blur={6}`, `autoplay`, `loop`).
- Upgrade `<MagicBento />` to the full React Bits implementation (`enableBorderGlow={true}`, `enableSpotlight={true}`, `spotlightRadius={300}`, `clickEffect={true}`, `enableStars`, `enableTilt`, `enableMagnetism`) and wrap every Bento card in `ElectronicControlTabView` (`#settings-schedule`, `#settings-pumps`, `#settings-vision`, `#settings-simulation`, `#settings-pinout`) in `<MagicBento />` while keeping `<MagicBentoCard />` compatible for `AnalyzeTabView`.
- Integrate `<SloshGauge />` inside `#settings-pumps` (`ElectronicControlTabView`) to interactively adjust **water volume / pump runtime (`pumpRuntimeMs`)**, **water flow rate (`calibration.pump_flow_rate_ml_s` / `pumpFlowRates`)**, and **Stock A/B/C dosing volumes (`stockAmounts`)**.
- Integrate `<RubberSegment />` (`stretch={100}`, `squash={3}`, `speed={1}`, `glide={75}`, `draggable`) for **category selection** across `ElectronicControlTabView` (the 4 sub-tabs `pumps` / `vision` / `simulation` / `pinout` and the AI deficiency category in `#settings-simulation`), `VisionPanel` (leaf photo category filter), and `AnalyzeTabView` (experimental unit category selector).
- Preserve all four section anchor IDs (`id="settings-schedule"`, `id="settings-pumps"`, `id="settings-vision"`, `id="settings-simulation"`) plus `id="settings-pinout"` inside `ElectronicControlTabView`.
- Preserve all strings asserted by `tests/test_presentation_override.py` and `tests/test_dashboard_overhaul.py`.

---

### Task 1: Add TDD Verification Suite for All 11 React Bits Components & Control UX/UI Cleanup

**Files:**
- Create: `tests/test_control_ux_cleanup.py`
- Test: `tests/test_control_ux_cleanup.py`

**Interfaces:**
- Consumes: `server/static/index.html`
- Produces: `TestControlUxUiCleanup` unittest suite verifying the 11 React Bits components (`GradientASCII`, `Particles`, `TechText`, `Crosshair`, `SpecularButton`, `CountUp`, `DepthCarousel`, `MagicBento`, `SloshGauge`, `RubberSegment`, `AnimatedContent`), the 4 sub-tabs, grouped `R1–R4` vs `R5–R7` relay cards, Thai-first action labels, and collapsible flow calibration drawer.

- [ ] **Step 1: Write the failing test in `tests/test_control_ux_cleanup.py`**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TDD verification for 11 React Bits components & Control UX/UI Cleanup."""

import re
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INDEX_HTML = PROJECT_ROOT / "server" / "static" / "index.html"


class TestControlUxUiCleanup(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = INDEX_HTML.read_text(encoding="utf-8")
        start = cls.html.index("function ElectronicControlTabView")
        end = cls.html.index("function App()", start)
        cls.control_body = cls.html[start:end]

    def test_0_home_uses_gradient_ascii_particles_tech_text_crosshair_and_specular_button(self):
        self.assertIn(".gradient-ascii-container", self.html)
        self.assertIn(".particles-container", self.html)
        self.assertIn(".tech-text-canvas", self.html)
        self.assertIn(".specular-button__light", self.html)
        self.assertIn("const GradientASCII =", self.html)
        self.assertIn("const Particles =", self.html)
        self.assertIn("const TechText =", self.html)
        self.assertIn("const Crosshair =", self.html)
        self.assertIn("const SpecularButton =", self.html)
        self.assertIn("const AnimatedContent =", self.html)
        self.assertIn('<GradientASCII', self.html)
        self.assertIn('characters=" 01"', self.html)
        self.assertIn('<Particles', self.html)
        self.assertIn('particleCount={1680}', self.html)
        self.assertIn('shape="sparkle"', self.html)
        home_start = self.html.index("function HomeView")
        home_end = self.html.index("function AnalyzeTabView", home_start)
        home_body = self.html[home_start:home_end]
        self.assertIn('<TechText', home_body)
        self.assertIn('text="A.E.G.I.S"', home_body)
        self.assertIn('reveal="letter"', home_body)
        self.assertIn('<Crosshair', home_body)
        self.assertIn('targetEffect="lock"', home_body)
        self.assertIn('showCoordinates', home_body)
        self.assertIn('<SpecularButton', home_body)
        self.assertIn('<AnimatedContent', home_body)
        cosmic_start = self.html.index("function CosmicThreeBackground")
        cosmic_end = self.html.index("function getSavedGallery", cosmic_start)
        cosmic_body = self.html[cosmic_start:cosmic_end]
        self.assertNotIn('<div className="home-backdrop">', cosmic_body)

    def test_0b_all_views_use_animated_content_and_react_bits_suite(self):
        self.assertIn("const CountUp =", self.html)
        self.assertIn("const DepthCarousel =", self.html)
        self.assertIn("const MagicBento =", self.html)
        self.assertIn("const SloshGauge =", self.html)
        self.assertIn("const RubberSegment =", self.html)
        self.assertIn(".depth-carousel__stage", self.html)
        self.assertIn(".magic-bento__star-layer", self.html)
        self.assertIn(".slosh-gauge__liquid", self.html)
        self.assertIn(".rubber-segment__thumb", self.html)
        self.assertIn("<CountUp", self.html)
        self.assertIn("replayOnHover", self.html)
        self.assertIn("<CountUp", self.control_body)
        self.assertIn("<SpecularButton", self.control_body)
        self.assertIn("<MagicBento", self.control_body)
        self.assertIn("enableStars", self.control_body)
        self.assertIn("enableTilt", self.control_body)
        self.assertIn("enableMagnetism", self.control_body)
        self.assertIn("<SloshGauge", self.control_body)
        self.assertIn("viscosity={0.15}", self.control_body)
        self.assertIn("<RubberSegment", self.control_body)
        self.assertIn("stretch={100}", self.control_body)
        self.assertIn("<AnimatedContent", self.control_body)

        analyze_start = self.html.index("function AnalyzeTabView")
        analyze_end = self.html.index("function ModelArchitectureTabView", analyze_start)
        self.assertIn("<AnimatedContent", self.html[analyze_start:analyze_end])

        model_start = self.html.index("function ModelArchitectureTabView")
        model_end = self.html.index("function ElectronicControlTabView", model_start)
        self.assertIn("<AnimatedContent", self.html[model_start:model_end])

        vision_start = self.html.index("function VisionPanel")
        vision_end = self.html.index("function HomeView", vision_start)
        vision_body = self.html[vision_start:vision_end]
        self.assertIn("<DepthCarousel", vision_body)
        self.assertIn('tiltDirection="right"', vision_body)
        self.assertIn("<RubberSegment", vision_body)

    def test_1_segmented_subtabs_exist_with_pumps_default(self):
        self.assertIn("const [controlSubTab, setControlSubTab] = useState('pumps')", self.control_body)
        for label in (
            "1. สั่งปั๊ม & โดสปุ๋ย",
            "2. กล้อง & ภาพใบผักบุ้ง",
            "3. จำลองค่า & ประวัติคำสั่ง",
            "4. ผังพินบอร์ด (GPIO)",
        ):
            self.assertIn(label, self.control_body)

    def test_2_relays_grouped_into_chamber_and_dosing_sets(self):
        self.assertIn("ชุดกระบอกตวงวัดน้ำ & ล้างหัววัด (R1–R4)", self.control_body)
        self.assertIn("ชุดปั๊มโดสปุ๋ย A / B / C (R5–R7)", self.control_body)
        for thai_name in (
            "ดูดน้ำเข้ากระบอกตวง",
            "ปั๊มลมกวนน้ำในกระบอก",
            "โซลินอยด์วาล์วปล่อยน้ำทิ้ง",
            "ปั๊มน้ำดีล้างและแช่หัววัด",
            "ปั๊มปุ๋ย A (เร่งใบ N)",
            "ปั๊มปุ๋ย B (โครงสร้าง P)",
            "ปั๊มปุ๋ย C (โพแทสเซียม K)",
        ):
            self.assertIn(thai_name, self.html)

    def test_3_clean_thai_action_buttons_and_collapsible_calibration(self):
        self.assertIn("สั่งฉีดปุ๋ยตามสูตรทันที", self.control_body)
        self.assertIn("ตั้งค่าเทียบอัตราการไหลของปั๊ม", self.control_body)
        self.assertIn("<details", self.control_body)

    def test_4_no_font_below_12px_in_electronic_control(self):
        sizes = [int(m) for m in re.findall(r"text-\[(\d+)px\]", self.control_body)]
        undersized = [s for s in sizes if s < 12]
        self.assertEqual(undersized, [], f"Found undersized font classes: {undersized}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `C:\Users\Admin\miniconda3\envs\ai-env312\python.exe -m unittest tests/test_control_ux_cleanup.py -v`
Expected: FAIL on the new assertions.

---

### Task 2: Integrate All 11 React Bits Components (`MagicBento`, `SloshGauge`, `RubberSegment`, `CountUp`, `TechText`, `Crosshair`, `SpecularButton`, `DepthCarousel`, `AnimatedContent`, `GradientASCII`, `Particles`) & Apply Across Views

**Files:**
- Modify: `server/static/index.html` (CSS styles around line 795, React Bits Component Suite around line 1425, `CosmicThreeBackground` around lines 1990-2045, `VisionPanel` around line 2061, `HomeView` around line 2293, `AnalyzeTabView`, and `ModelArchitectureTabView`)
- Test: `tests/test_control_ux_cleanup.py`, `tests/test_dashboard_overhaul.py`

**Interfaces:**
- Consumes: React `useState`, `useEffect`, `useLayoutEffect`, `useRef`, `useMemo`, `useCallback`, `useId`
- Produces:
  - CSS classes for all 11 React Bits components.
  - IIFE-scoped `MagicBento`, `SloshGauge`, `RubberSegment`, `CountUp`, `TechText`, `Crosshair`, `SpecularButton`, `DepthCarousel`, `AnimatedContent`, `GradientASCII`, and `Particles`.
  - Updated `CosmicThreeBackground` rendering `<GradientASCII />` + `<Particles />` when `isHome` is true.
  - Updated `HomeView` rendering `<Crosshair />`, `<TechText text="A.E.G.I.S" ... />`, `<SpecularButton />` CTAs, and `<AnimatedContent />`.
  - Updated `VisionPanel` rendering `<RubberSegment />` and `<DepthCarousel />`.
  - Updated `AnalyzeTabView` and `ModelArchitectureTabView` with `<AnimatedContent />`, `<CountUp />`, and `<RubberSegment />`.

- [ ] **Step 1: Add CSS and all 11 IIFE-scoped React Bits components to `server/static/index.html` and wire `HomeView`, `VisionPanel`, `AnalyzeTabView`, and `ModelArchitectureTabView`**

- [ ] **Step 2: Run `test_0_home_uses_gradient_ascii_particles_tech_text_crosshair_and_specular_button`, `TestHomeSimplification`, and `TestVisionPanel`**

Run: `C:\Users\Admin\miniconda3\envs\ai-env312\python.exe -m unittest tests.test_control_ux_cleanup.TestControlUxUiCleanup.test_0_home_uses_gradient_ascii_particles_tech_text_crosshair_and_specular_button tests.test_dashboard_overhaul.TestHomeSimplification tests.test_dashboard_overhaul.TestVisionPanel -v`
Expected: PASS.

---

### Task 3: Update `RELAY_CHANNELS` & `CHAMBER_PHASES` Copy to Clean Thai-First Metadata

**Files:**
- Modify: `server/static/index.html` (`CHAMBER_PHASES` and `RELAY_CHANNELS`)
- Test: `tests/test_control_ux_cleanup.py`, `tests/test_presentation_override.py`

- [ ] **Step 1: Update `CHAMBER_PHASES` and `RELAY_CHANNELS` in `server/static/index.html`**

- [ ] **Step 2: Verify existing hardware pinout tests still pass**

Run: `C:\Users\Admin\miniconda3\envs\ai-env312\python.exe -m unittest tests/test_presentation_override.py -v`
Expected: PASS.

---

### Task 4: Refactor `ElectronicControlTabView` with `<MagicBento />`, `<RubberSegment />`, `<SloshGauge />`, `<CountUp />`, `<SpecularButton />`, and `<AnimatedContent />`

**Files:**
- Modify: `server/static/index.html` (`ElectronicControlTabView`)
- Test: `tests/test_control_ux_cleanup.py`, `tests/test_dashboard_overhaul.py`, `tests/test_presentation_override.py`

- [ ] **Step 1: Refactor `ElectronicControlTabView` JSX in `server/static/index.html`**

Wrap sections in `<AnimatedContent />`, wrap all Bento cards in `<MagicBento />`, render `<RubberSegment />` for the 4 sub-tab categories and AI deficiency category selection, integrate interactive `<SloshGauge />` liquid tanks for water volume/flow rate and Stock A/B/C dosing volumes, implement the compact `#settings-schedule` bar, the split `R1–R4` / `R5–R7` relay groups, the clean dosing deck with `<CountUp />` readouts, `<SpecularButton />` primary CTAs, collapsible `<details>` calibration drawer, and CSS visibility toggling (`block` / `hidden`) across the 4 sub-tabs.

- [ ] **Step 2: Run all 3 test suites to verify everything passes**

Run: `C:\Users\Admin\miniconda3\envs\ai-env312\python.exe -m unittest tests/test_control_ux_cleanup.py tests/test_dashboard_overhaul.py tests/test_presentation_override.py -v`
Expected: PASS (all tests in all 3 suites pass with 0 errors).

- [ ] **Step 3: Commit changes**

```bash
git add server/static/index.html tests/test_control_ux_cleanup.py docs/superpowers/specs/2026-11-05-control-ux-ui-copy-cleanup-design.md docs/superpowers/plans/2026-11-05-control-ux-ui-copy-cleanup.md
git commit -m "feat(ui): integrate 11 React Bits components and declutter Electronic Control"
```
