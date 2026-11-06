# Complete All 11 React Bits Components & Electronic Control UX/UI Cleanup Plan (Gap-Closing Edition)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the integration of all **11 React Bits components** in `server/static/index.html` — fixing every partial/stubbed component left by the previous pass (`MotionShim`, `GsapShim`, `<AnimatedContent />`, `<MagicBento />`, interactive `<SloshGauge />` for water volume & flow rate, `<RubberSegment />` for category switchers, `<CountUp />` across `AnalyzeTabView` & `ElectronicControlTabView`, `<SpecularButton />` on remaining primary CTAs, and Thai-first relay titles).

**Architecture:** `server/static/index.html` (currently 10,535 lines) already contains the CSS and IIFE definitions for `GradientASCII`, `Particles`, `CountUp`, `TechText`, `DepthCarousel`, `SpecularButton`, `SloshGauge`, `RubberSegment`, and `Crosshair` (lines 1317–6165), but has **7 specific incomplete areas** where components were either stubbed or not wired into the views. This plan closes all 7 gaps with strict TDD tests in `tests/test_control_ux_cleanup.py`.

**Tech Stack:** React 18 (Babel standalone JSX in `server/static/index.html`), WebGL2, 2D Canvas, CSS 3D Perspective, Tailwind CSS, Python `unittest`.

**Spec:** `docs/superpowers/specs/2026-11-05-control-ux-ui-copy-cleanup-design.md`

---

## Audit of Exact Gaps in `server/static/index.html` (What Was Left Incomplete)

| # | Component / Area | Current State in `server/static/index.html` | Required Fix |
|---|---|---|---|
| **1** | **`MotionShim` & `GsapShim`** (lines 1191–1315) | `MotionShim.animate` ignores cubic-bezier array eases (`[0.23, 1, 0.32, 1]`) and spring physics (`type: 'spring'`), and `getVelocity()` returns `0`. `GsapShim` only has `gsap.to` (missing `gsap.set`, `gsap.context`, `gsap.timeline`, `gsap.registerPlugin`, `ScrollTrigger.create`). | Upgrade `MotionShim` to support cubic-bezier arrays, spring physics (`bounce`, `velocity`), and real velocity tracking in `useMotionValue`. Upgrade `GsapShim` with `gsap.set`, `gsap.context`, `gsap.timeline`, `gsap.registerPlugin`, and `ScrollTrigger.create`. |
| **2** | **`<AnimatedContent />`** (lines 6565–6637) | Still uses the old CSS-transition stub (`distance = 20`, `duration = 0.45`) instead of the React Bits GSAP + `ScrollTrigger` component. | Replace lines 6565–6637 with the genuine React Bits `<AnimatedContent />` component (`WIPES`, `gsap.context`, `gsap.timeline`, `ScrollTrigger.create`, `distance = 100`, `duration = 0.8`, `ease = 'power3.out'`, `stagger = 0.08`, `threshold = 0.1`) and wrap the content sections of `HomeView`, `AnalyzeTabView`, and each sub-tab section of `ElectronicControlTabView`. |
| **3** | **`<MagicBento />`** (lines 6641–6797 & `ElectronicControlTabView`) | Lines 6641–6733 are still the old simple wrapper, and `#settings-schedule` (line 9470), `#settings-vision` (line 9865), `#settings-simulation` (lines 9961, 10090), and `#settings-pinout` (line 10145) do NOT use `<MagicBento />`! | Upgrade `<MagicBento />` to support `.magic-bento__stars` 2D canvas star particles, spring tilt (`enableTilt`), magnetism (`enableMagnetism`), spotlight border glow (`enableBorderGlow`, `enableSpotlight`, `spotlightRadius={300}`), and click wave (`clickEffect={true}`), and wrap **every** Bento card in `ElectronicControlTabView` (`#settings-schedule`, `#settings-pumps`, `#settings-vision`, `#settings-simulation`, `#settings-pinout`) in `<MagicBento enableBorderGlow={true} enableSpotlight={true} spotlightRadius={300} clickEffect={true} enableStars enableTilt enableMagnetism>`. |
| **4** | **`<SloshGauge />`** (lines 9605–9765 in `#settings-pumps`) | Rendered with `interactive={false}` and `showValue={false}` (lines 9717–9731) and no `onChange`! Missing water volume & water flow rate `<SloshGauge />` controllers (`"อันนี้เอาไว้ปรับ volume อัตราการไหลของน้ำ"`). | Add 2 interactive `<SloshGauge interactive showValue viscosity={0.15} tilt={0.45} splash={0.42} />` tanks in the left column of `#settings-pumps` to adjust **Water Volume / Pump Runtime (`pumpRuntimeMs`)** and **Water Flow Rate (`calibration.pump_flow_rate_ml_s` & `pumpFlowRates`)**, and change all 3 Stock A/B/C `<SloshGauge />` tanks (lines 9717–9731) to `interactive={true}` `showValue={true}` with `onChange` updating `stockAmounts`. |
| **5** | **`<RubberSegment />`** (lines 9435–9458 & `#settings-simulation`) | Only used once in `VisionPanel`. The 4 main sub-tabs of `ElectronicControlTabView` (lines 9435–9458) are plain `<button>`s, and `#settings-simulation` has no `<RubberSegment />` category selector (`"เอาไปใช้กับการเลือกหมวดหมู่"`). | Replace the 4 sub-tab `<button>`s at lines 9435–9458 with `<RubberSegment items={SUB_TABS.map(t => ({ value: t.id, label: t.label }))} value={controlSubTab} onChange={setControlSubTab} stretch={100} squash={3} speed={1} glide={75} draggable />`, and add `<RubberSegment />` in `#settings-simulation` for selecting the AI deficiency category (`Control`, `-N`, `-P`, `-K`). |
| **6** | **`<CountUp />`** (`AnalyzeTabView` lines 8122, 8196, 8224, 8604 & `#settings-simulation` lines 10000–10063) | Only used on Stock A/B/C mL in `#settings-pumps`. Missing in `AnalyzeTabView` (Temperature, PH sensor, EC sensor, Healthy/N/P/K %) and in `#settings-simulation` (`simEc`, `simPh`, `simTemp`, ratios, total mL, pump ms) (`"เอาไปใส่ในส่วนของตัวเลข"`). | Wrap numeric readouts in `AnalyzeTabView` (`activeTemp`, `unitSummary.ph`, `unitSummary.ec`, and the 4 NPK `%` values) and in `ElectronicControlTabView` (`pumpRuntimeMs / 1000`, `simEc`, `simPh`, `simTemp`, `r1_pct`/`r2_pct`/`r3_pct`, `total_volume_ml`, `pump1_ms`/`pump2_ms`/`pump3_ms`) with `<CountUp easing="expo" replayOnHover />`. |
| **7** | **`<SpecularButton />` & Relay Thai Copy** (lines 7780, 8848–8855, 9662, 9880, 9893) | `READ SYSTEM SPEC +` on Home and `▶ สั่งรันครบ 6 ขั้นตอนทันที` / `📸 โหมดส่งภาพจริง` in `#settings-vision` are plain `<button>`s. Relay cards at line 9662 show English `{r.name}` as primary title, and `R2` role is missing `"ปั๊มลมกวนน้ำในกระบอก"`. | Upgrade those CTA buttons to `<SpecularButton />`. In `relays` state (lines 8848–8854), include `"ปั๊มลมกวนน้ำในกระบอก"` in `R2`, and at line 9662 display `{r.role}` as the visible primary title with `<span className="sr-only">{r.name}</span>` so hardware strings remain in DOM for tests. |

---

### Task 1: Tighten TDD Verification Suite in `tests/test_control_ux_cleanup.py` to Catch All 7 Gaps

**Files:**
- Modify: `tests/test_control_ux_cleanup.py`
- Test: `tests/test_control_ux_cleanup.py`

- [ ] **Step 1: Replace `tests/test_control_ux_cleanup.py` with strict assertions covering all 11 React Bits components and their exact placements**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Strict TDD verification for all 11 React Bits components & Control UX/UI Cleanup."""

import re
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INDEX_HTML = PROJECT_ROOT / "server" / "static" / "index.html"


class TestControlUxUiCleanup(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = INDEX_HTML.read_text(encoding="utf-8")
        home_start = cls.html.index("function HomeView")
        home_end = cls.html.index("function AnalyzeTabView", home_start)
        cls.home_body = cls.html[home_start:home_end]

        analyze_start = home_end
        analyze_end = cls.html.index("function computeLocalTwoFactorDosing", analyze_start)
        cls.analyze_body = cls.html[analyze_start:analyze_end]

        control_start = cls.html.index("function ElectronicControlTabView")
        control_end = cls.html.index("function App()", control_start)
        cls.control_body = cls.html[control_start:control_end]

        vision_start = cls.html.index("function VisionPanel")
        vision_end = cls.html.index("function HomeView", vision_start)
        cls.vision_body = cls.html[vision_start:vision_end]

    def test_0_home_uses_gradient_ascii_particles_tech_text_crosshair_and_two_specular_buttons(self):
        self.assertIn("<GradientASCII", self.home_body)
        self.assertIn("characters=\" 01\"", self.home_body)
        self.assertIn("<Particles", self.home_body)
        self.assertIn("particleCount={1680}", self.home_body)
        self.assertIn("shape=\"sparkle\"", self.home_body)
        self.assertIn("<TechText", self.home_body)
        self.assertIn("text=\"A.E.G.I.S\"", self.home_body)
        self.assertIn("reveal=\"letter\"", self.home_body)
        self.assertIn("<Crosshair", self.home_body)
        self.assertIn("targetEffect=\"lock\"", self.home_body)
        self.assertIn("showCoordinates", self.home_body)
        self.assertIn("<AnimatedContent", self.home_body)
        self.assertGreaterEqual(
            self.home_body.count("<SpecularButton"),
            2,
            "Both primary Home CTAs (ENTER A.E.G.I.S ANALYZE and READ SYSTEM SPEC) must use <SpecularButton>",
        )

    def test_0b_animated_content_is_real_react_bits_gsap_scrolltrigger_component(self):
        ac_start = self.html.index("const AnimatedContent =")
        ac_end = self.html.index("const MagicBento =", ac_start)
        ac_def = self.html[ac_start:ac_end]
        self.assertIn("ScrollTrigger.create", ac_def)
        self.assertIn("gsap.timeline", ac_def)
        self.assertIn("WIPES", ac_def)
        self.assertIn("stagger", ac_def)

    def test_0c_analyze_view_uses_count_up_animated_content_and_magic_bento(self):
        self.assertIn("<AnimatedContent", self.analyze_body)
        self.assertIn("<MagicBento", self.analyze_body)
        self.assertGreaterEqual(
            self.analyze_body.count("<CountUp"),
            4,
            "AnalyzeTabView must use <CountUp /> for Temperature, PH sensor, EC sensor, and NPK % readouts",
        )

    def test_0d_electronic_control_uses_all_react_bits_components_completely(self):
        # 1. MagicBento must wrap cards across all sections in ElectronicControlTabView (at least 4 MagicBento grids)
        self.assertGreaterEqual(
            self.control_body.count("<MagicBento"),
            4,
            "Every Bento section in ElectronicControlTabView (#settings-schedule, #settings-pumps, #settings-vision, #settings-simulation, #settings-pinout) must use <MagicBento>",
        )
        self.assertIn("enableStars", self.control_body)
        self.assertIn("enableTilt", self.control_body)
        self.assertIn("enableMagnetism", self.control_body)

        # 2. SloshGauge must be interactive (interactive + onChange) for water volume, flow rate, and Stock A/B/C
        self.assertNotIn("interactive={false}", self.control_body)
        self.assertGreaterEqual(
            self.control_body.count("<SloshGauge"),
            3,
            "ElectronicControlTabView must render interactive <SloshGauge /> tanks for water volume/flow rate and Stock A/B/C",
        )
        self.assertIn("viscosity={0.15}", self.control_body)

        # 3. RubberSegment must be used for the 4 main sub-tabs AND simulation category selection
        self.assertGreaterEqual(
            self.control_body.count("<RubberSegment"),
            2,
            "ElectronicControlTabView must use <RubberSegment /> for the 4 main sub-tabs and AI deficiency category selection",
        )
        self.assertIn("stretch={100}", self.control_body)

        # 4. CountUp must be used for dosing volumes AND simulation readouts
        self.assertGreaterEqual(
            self.control_body.count("<CountUp"),
            5,
            "ElectronicControlTabView must use <CountUp /> across dosing volumes, pump runtime, and simulation readouts",
        )

        # 5. SpecularButton must be used for primary action CTAs in ElectronicControlTabView
        self.assertGreaterEqual(
            self.control_body.count("<SpecularButton"),
            3,
            "ElectronicControlTabView must use <SpecularButton /> for primary CTAs (Full Cycle, Manual Dose, Camera Capture)",
        )

        # 6. VisionPanel uses DepthCarousel and RubberSegment
        self.assertIn("<DepthCarousel", self.vision_body)
        self.assertIn('tiltDirection="right"', self.vision_body)
        self.assertIn("<RubberSegment", self.vision_body)

    def test_1_segmented_subtabs_exist_with_pumps_default(self):
        self.assertIn("const [controlSubTab, setControlSubTab] = useState('pumps')", self.control_body)
        for label in (
            "1. สั่งปั๊ม & โดสปุ๋ย",
            "2. กล้อง & ภาพใบผักบุ้ง",
            "3. จำลองค่า & ประวัติคำสั่ง",
            "4. ผังพินบอร์ด (GPIO)",
        ):
            self.assertIn(label, self.control_body)

    def test_2_relays_grouped_into_chamber_and_dosing_sets_with_thai_titles(self):
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
        self.assertIn('<span className="sr-only">{r.name}</span>', self.control_body)

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

- [ ] **Step 2: Run `tests/test_control_ux_cleanup.py` to confirm it fails on the 7 incomplete gaps**

Run: `C:\Users\Admin\miniconda3\envs\ai-env312\python.exe -m unittest tests/test_control_ux_cleanup.py -v`
Expected: FAIL on `test_0`, `test_0b`, `test_0c`, `test_0d`, and `test_2`.

---

### Task 2: Upgrade `MotionShim`, `GsapShim`, `<AnimatedContent />`, and `<MagicBento />` in `server/static/index.html`

**Files:**
- Modify: `server/static/index.html` (lines 1191–1315 for `MotionShim` and `GsapShim`; lines 6563–6797 for `AnimatedContent` and `MagicBento`)
- Test: `tests/test_control_ux_cleanup.py`

- [ ] **Step 1: Upgrade `MotionShim` and `GsapShim` (lines 1191–1315 of `server/static/index.html`)**

Update `MotionShim` so:
- `useMotionValue` tracks velocity (`lastVal`, `lastTime`, `vel`) inside `set(v)` and returns `vel` from `getVelocity()`.
- `animate(fromOrMv, to, opts)` supports:
  - Cubic-bezier array `opts.ease` (`Array.isArray(opts.ease)` -> `cubicBezier(...opts.ease)`),
  - Spring animation when `opts.type === 'spring'` (damped harmonic oscillator using `opts.duration`, `opts.bounce`, `opts.velocity`),
  - Returning a Promise-like `{ stop, then }` object.
Update `GsapShim` so it exports `{ gsap, ScrollTrigger }`:
- `gsap.registerPlugin = () => {}`
- `gsap.set(targets, vars)` applies `visibility`, `opacity`, `x`, `y`, `scale`, `rotation`, `filter`, `maskImage`, `webkitMaskImage`, or `clearProps` to an element or array of elements.
- `gsap.context(fn, scope)` executes `fn()` and returns `{ revert: () => {} }`.
- `gsap.timeline({ paused, onStart, onComplete })` provides `.fromTo(targets, fromVars, toVars, delaySec)` with `stagger` support (`toVars.stagger?.each`), `.play()`, and `.reverse()`.
- `ScrollTrigger.create({ trigger, start, once, onEnter, onLeaveBack, animation, scrub })` uses `IntersectionObserver` (threshold `0.1`) to call `onEnter()` / `animation?.play()` as soon as `trigger` enters the viewport (or immediately on mount if already visible).

- [ ] **Step 2: Replace `AnimatedContent` (lines 6565–6637) with the genuine React Bits `<AnimatedContent />` component**

Use the exact React Bits `AnimatedContent` implementation (with `WIPES`, `gsap.context`, `gsap.set`, `gsap.timeline`, `tl.fromTo`, `ScrollTrigger.create`, `distance = 100`, `direction = 'vertical'`, `duration = 0.8`, `ease = 'power3.out'`, `blur = 0`, `stagger = 0.08`, `threshold = 0.1`, `trigger = 'scroll'`).

- [ ] **Step 3: Upgrade `MagicBento` (lines 6641–6797) to include `.magic-bento__stars` particle canvas, spring tilt, magnetism, and click wave**

In `MagicBento` (lines 6641–6733), add:
- Automatic `.magic-bento__stars` 2D canvas particle spawner inside each `.magic-bento-card` when `enableStars` is true, drawing rising glowing specks near the pointer (`particleCount = 24`).
- Click wave ring (`--mb-wx`, `--mb-wy`, `--mb-wr`, `--mb-wa`) when `clickEffect` is true.
- Support for `enableBorderGlow`, `enableSpotlight`, `spotlightRadius`, `enableStars`, `enableTilt`, and `enableMagnetism`.

---

### Task 3: Wire `<SpecularButton />` on `HomeView` and `<CountUp />` on `AnalyzeTabView`

**Files:**
- Modify: `server/static/index.html` (`HomeView` around line 7780, `AnalyzeTabView` around lines 8120–8615)
- Test: `tests/test_control_ux_cleanup.py`

- [ ] **Step 1: Upgrade `READ SYSTEM SPEC +` in `HomeView` (line 7780) to `<SpecularButton />`**

Replace the plain `<button onClick={() => setShowModal(true)} ...>READ SYSTEM SPEC +</button>` at line 7780 with:
```jsx
<SpecularButton
  size="lg"
  radius={18}
  tint="#0a1120"
  tintOpacity={0.45}
  textColor="#f5f5f5"
  lineColor="#88deec"
  baseColor="#334155"
  intensity={0.9}
  idleIntensity={0.3}
  shineSize={10}
  shineFade={34}
  thickness={1.2}
  glow={0.9}
  followMouse
  proximity={250}
  className="font-display tracking-[0.2em] uppercase"
  onClick={() => setShowModal(true)}
>
  READ SYSTEM SPEC +
</SpecularButton>
```

- [ ] **Step 2: Wire `<CountUp />` to the 4 KPI / probability readouts in `AnalyzeTabView` (lines 8122, 8196, 8224, 8604)**

1. **Temperature card (line 8122):**
   Replace `{activeTemp}°C` with:
   `<CountUp to={parseFloat(activeTemp) || 0} decimals={1} duration={0.8} suffix="°C" easing="expo" replayOnHover />`
2. **PH sensor KPI card (line 8196):**
   Replace `{unitSummary.ph}` with:
   `<CountUp to={parseFloat(unitSummary.ph) || 0} decimals={2} duration={0.8} easing="expo" replayOnHover />`
3. **EC sensor KPI card (line 8224):**
   Replace `{unitSummary.ec}` with:
   `<CountUp to={parseFloat(unitSummary.ec) || 0} decimals={3} duration={0.8} easing="expo" replayOnHover />`
4. **4 NPK Class Progress Strips (`Healthy`, `N`, `P`, `K` at line 8604):**
   Replace `{pct}%` with:
   `<CountUp to={pct} decimals={0} duration={0.7} suffix="%" easing="expo" replayOnHover />`

---

### Task 4: Complete `<RubberSegment />`, Interactive `<SloshGauge />`, `<MagicBento />`, `<CountUp />`, `<SpecularButton />`, and Thai Relay Titles in `ElectronicControlTabView`

**Files:**
- Modify: `server/static/index.html` (`ElectronicControlTabView`, lines 8847–10250)
- Test: `tests/test_control_ux_cleanup.py`, `tests/test_dashboard_overhaul.py`, `tests/test_presentation_override.py`

- [ ] **Step 1: Add `"ปั๊มลมกวนน้ำในกระบอก"` to `relays` metadata (lines 8848–8855) and show Thai role as primary title at line 9662**

In `relays` initial state (lines 8848–8854):
- `R1`: `role: 'ดูดน้ำเข้ากระบอกตวง (สูบน้ำจากถังปลูกเข้ากระบอกวัด)'`
- `R2`: `role: 'ปั๊มลมกวนน้ำในกระบอก / สูบน้ำตัวอย่างวนคืนถังปลูก'`
- `R3`: `role: 'ปั๊มน้ำดีล้างและแช่หัววัด'`
- `R4`: `role: 'โซลินอยด์วาล์วปล่อยน้ำทิ้ง'`
- `R5`: `role: 'ปั๊มปุ๋ย A (เร่งใบ N)'`
- `R6`: `role: 'ปั๊มปุ๋ย B (โครงสร้าง P)'`
- `R7`: `role: 'ปั๊มปุ๋ย C (โพแทสเซียม K)'`

And at line 9662 (inside `renderRelayCard`), replace:
```jsx
<span className="font-inter font-semibold text-sm text-white">
  {r.name}
</span>
```
with:
```jsx
<span className="font-inter font-semibold text-sm text-white" title={r.name}>
  {r.role}
</span>
<span className="sr-only">{r.name}</span>
```

- [ ] **Step 2: Replace the 4 sub-tab `<button>`s (lines 9435–9458) with `<RubberSegment />`**

Replace `<nav aria-label="หมวดการควบคุม" ...>` (lines 9435–9458) with:
```jsx
<div className="mb-6">
  <RubberSegment
    items={SUB_TABS.map((tab) => ({ value: tab.id, label: tab.label }))}
    value={controlSubTab}
    onChange={(val) => setControlSubTab(val)}
    trackColor="#18181b"
    thumbColor="#C6C7F8"
    textColor="#fafafa"
    activeTextColor="#090d16"
    size="lg"
    radius={14}
    inset={4}
    equalSlots
    stretch={100}
    squash={3}
    speed={1}
    glide={75}
    draggable
    aria-label="หมวดการควบคุม"
  />
</div>
```

- [ ] **Step 3: Wrap `#settings-schedule`, `#settings-vision`, `#settings-simulation`, and `#settings-pinout` cards in `<MagicBento />`**

Wrap the `.figma-card-dark` cards inside `#settings-schedule` (line 9470), `#settings-vision` (line 9865), `#settings-simulation` (line 9959), and `#settings-pinout` (line 10145) with:
```jsx
<MagicBento
  glowColor="198, 199, 248"
  spotlightRadius={300}
  enableBorderGlow={true}
  enableSpotlight={true}
  clickEffect={true}
  enableStars
  enableTilt
  enableMagnetism
>
```
and add the `magic-bento-card` class to each `.figma-card-dark` card inside them so every Bento card in `ElectronicControlTabView` has full spotlight, border glow, 3D tilt, magnetism, and star particles.

- [ ] **Step 4: Make `<SloshGauge />` interactive for Water Volume (`pumpRuntimeMs`), Water Flow Rate (`pumpFlowRates`), and Stock A/B/C Volumes (`stockAmounts`) in `#settings-pumps`**

1. Inside the Manual Pump Runtime & Water Flow box (lines 9620–9652), add two interactive `<SloshGauge />` liquid tanks side-by-side:
   - **Tank 1 (ปริมาตรน้ำเดินปั๊ม / Water Volume):**
     ```jsx
     <SloshGauge
       value={Math.round((pumpRuntimeMs / 30000) * 100)}
       onChange={(lvl) => setPumpRuntimeMs(Math.max(300, Math.round((lvl / 100) * 30000)))}
       interactive
       showValue
       liquidColor="#38bdf8"
       glassColor="#27272a"
       width={68}
       height={120}
       radius={16}
       ticks={4}
       viscosity={0.15}
       tilt={0.45}
       splash={0.42}
       unit="%"
       ariaLabel="ปรับปริมาตรน้ำเดินปั๊ม"
     />
     ```
   - **Tank 2 (อัตราการไหลของน้ำ / Water Flow Rate `Q` mL/s):**
     ```jsx
     <SloshGauge
       value={Math.round(((calibration.pump_flow_rate_ml_s || 1.0) / 3.0) * 100)}
       onChange={(lvl) => {
         const q = +Math.max(0.2, (lvl / 100) * 3.0).toFixed(2);
         setCalibration((prev) => ({ ...prev, pump_flow_rate_ml_s: q }));
         setPumpFlowRates({ A: q, B: q, C: q });
       }}
       interactive
       showValue
       liquidColor="#22d3ee"
       glassColor="#27272a"
       width={68}
       height={120}
       radius={16}
       ticks={4}
       viscosity={0.15}
       tilt={0.45}
       splash={0.42}
       unit="%"
       ariaLabel="ปรับอัตราการไหลของน้ำ"
     />
     ```
2. On all 3 Stock A / B / C `<SloshGauge />` tanks (lines 9717–9731), change `showValue={false}` `interactive={false}` to:
   ```jsx
   <SloshGauge
     value={Math.min(100, Math.round((stockAmounts[st.key] / 25) * 100))}
     onChange={(lvl) =>
       setStockAmounts((prev) => ({
         ...prev,
         [st.key]: +((lvl / 100) * 25).toFixed(1),
       }))
     }
     interactive
     showValue
     liquidColor={st.color}
     glassColor="#27272a"
     width={56}
     height={108}
     radius={14}
     ticks={3}
     viscosity={0.15}
     tilt={0.45}
     splash={0.42}
     unit="%"
     ariaLabel={st.title}
   />
   ```
   and wrap `(pumpRuntimeMs / 1000).toFixed(1)` at line 9626 with `<CountUp to={+(pumpRuntimeMs / 1000).toFixed(1)} decimals={1} duration={0.5} suffix="s" easing="expo" replayOnHover />`.

- [ ] **Step 5: Upgrade `#settings-vision` CTAs to `<SpecularButton />` and add `<RubberSegment />` + `<CountUp />` to `#settings-simulation`**

1. In `#settings-vision` (lines 9879–9896), replace the `▶ สั่งรันครบ 6 ขั้นตอนทันที (START_CYCLE)` button and the `📸 โหมดส่งภาพจริง (ESP32-CAM → AI)` button with `<SpecularButton size="md" radius={12} followMouse proximity={220} ...>`.
2. In `#settings-simulation` (right below the 5 scenario preset buttons at line 9994), add a `<RubberSegment />` category selector for `simClass`:
   ```jsx
   <div className="mb-4">
     <div className="text-xs text-white/60 mb-1.5">เลือกหมวดหมู่อาการขาดธาตุอาหาร (AI Category):</div>
     <RubberSegment
       items={[
         { value: 'Control', label: 'Control (ปกติ)' },
         { value: 'N_Deficiency', label: 'ขาดไนโตรเจน (-N)' },
         { value: 'P_Deficiency', label: 'ขาดฟอสฟอรัส (-P)' },
         { value: 'K_Deficiency', label: 'ขาดโพแทสเซียม (-K)' },
       ]}
       value={simClass}
       onChange={(val) => setSimClass(val)}
       trackColor="#27272a"
       thumbColor="#C6C7F8"
       textColor="#fafafa"
       activeTextColor="#18181b"
       size="md"
       radius={10}
       inset={3}
       equalSlots
       stretch={100}
       squash={3}
       speed={1}
       glide={75}
       draggable
       aria-label="หมวดหมู่อาการขาดธาตุอาหาร"
     />
   </div>
   ```
3. In `#settings-simulation` (lines 10000, 10016, 10032, 10052, 10058), replace `{simEc.toFixed(2)} mS/cm`, `{simPh.toFixed(2)}`, `{simTemp.toFixed(1)} °C`, and `{simDosingResult.volumes_ml.total_volume_ml.toFixed(2)} mL` with `<CountUp easing="expo" replayOnHover ... />`.

- [ ] **Step 6: Run all 3 verification test suites**

Run: `C:\Users\Admin\miniconda3\envs\ai-env312\python.exe -m unittest tests/test_control_ux_cleanup.py tests/test_dashboard_overhaul.py tests/test_presentation_override.py -v`
Expected: PASS (100% pass across all 3 test files).
