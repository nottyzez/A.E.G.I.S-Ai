# UX/UI & Copy Cleanup Design Spec — `server/static/index.html` (11 React Bits Components + Electronic Control Decluttering)

**Date:** 2026-11-05  
**Target File:** `server/static/index.html`  
**Scope (Round 1 — 11 React Bits Components + Electronic Control Decluttering):**
1. **Home Page Background Replacement (`<GradientASCII />` + `<Particles />` Combo)**
2. **Home Hero `"A.E.G.I.S"` Wordmark (`<TechText />` Component from React Bits)**
3. **Home Interactive Targeting Reticle (`<Crosshair />` Component from React Bits)**
4. **Interactive Glass CTA Buttons (`<SpecularButton />` Component from React Bits)**
5. **Animated Numeric Readouts (`<CountUp />` Component from React Bits)**
6. **3D Leaf Image Gallery (`<DepthCarousel />` Component from React Bits)**
7. **Interactive Bento Cards (`<MagicBento />` Full React Bits Component across `หน้าควบคุมวงจร`)**
8. **Interactive Liquid Tank Gauge (`<SloshGauge />` Component from React Bits for Water Volume & Flow Rate Adjustment)**
9. **Rubber Physics Category Switcher (`<RubberSegment />` Component from React Bits for Category & Mode Selection)**
10. **Scroll & Mount Entrance Animations Across All Pages (`<AnimatedContent />` Component from React Bits)**
11. **Navigation + `หน้าควบคุมวงจร` (`ElectronicControlTabView`) UX/UI & Copy Decluttering**

---

## 1. Problem Statement & Goals

1. **Home Background Update:** Remove the static `back.jpg` image background (`home-backdrop`) on the Home page (`currentView === 'home'`) and replace it with a layered React Bits WebGL2 combination:
   - **Base Layer:** `<GradientASCII />` (`colors={["#88deec","#f6f8ff","#a5d8ff","#38bdf8"]}`, `shape="horizon"`, `characters=" 01"`, `cellSize={14}`, `density={0.41}`, `glyphOpacity={0.26}`, `gradientOpacity={0.22}`, `glow={1.5}`, `depthOfField={0.46}`, `softness={0.79}`, `scale={1.3}`, `flow={0.55}`, `speed={0.7}`, `variation={1}`, `scrambleRadius={0.12}`)
   - **Overlay Layer:** `<Particles />` (`particleColors={["#eab308","#3b82f6","#ffffff"]}`, `particleCount={1680}`, `particleSpread={5.5}`, `speed={0.02}`, `particleBaseSize={45}`, `glow={2}`, `twinkle={0.85}`, `moveParticlesOnHover`, `hoverEffect="repel"`, `shape="sparkle"`, `depthOfField={0.15}`, `connections`, `connectionDistance={85}`, `particleHoverFactor={0.45}`, `cameraDistance={22}`, `disableRotation`, `variation={4}`)
2. **Home Hero `"A.E.G.I.S"` Wordmark (`<TechText />`):** Render the `"A.E.G.I.S"` title on the Home page with `<TechText />` (`text="A.E.G.I.S"`, `fontWeight={600}`, `fontSize={150}`, `reveal="letter"`, `dashLength={4}`, `dashGap={2}`, `specks={15}`, `intro="none"`, `introDuration={2}`, `clickKick`, `guides={false}`).
3. **Home Interactive Targeting Reticle (`<Crosshair />`):** Add `<Crosshair />` (`containerRef={homeContainerRef}`, `color="#ffffff"`, `targetEffect="lock"`, `thickness={1}`, `opacity={0.85}`, `smoothing={0.35}`, `showCoordinates`) to `HomeView` so moving the pointer across the Home page draws crisp full-container HUD crosshair lines with X/Y edge coordinate badges, locks onto interactive buttons/targets with corner brackets and `W × H` dimensions, and emits click pulse rings.
4. **Interactive Specular Glass Buttons (`<SpecularButton />`):** Integrate `<SpecularButton />` (`size="lg"`, `radius={18}`, `tint="#ffffff"`, `tintOpacity={0.04}`, `textColor="#f5f5f5"`, `lineColor="#ffffff"`, `baseColor="#525252"`, `intensity={1}`, `idleIntensity={0.35}`, `shineSize={10}`, `shineFade={34}`, `thickness={1.2}`, `glow={1}`, `followMouse`, `proximity={250}`) for primary CTA buttons across Home and Electronic Control.
5. **Animated Number Readouts (`<CountUp />`):** Integrate `<CountUp />` for numeric displays ("ส่วนของตัวเลข") across the dashboard (`easing="expo"`, `replayOnHover`).
6. **3D Leaf Image Gallery (`<DepthCarousel />`):** Integrate `<DepthCarousel />` for the image gallery section ("ส่วนของรูปภาพ") inside `VisionPanel` (`#settings-vision`) (`depth={220}`, `spread={90}`, `tilt={22}`, `tiltDirection="right"`, `perspective={1400}`, `visibleCards={4}`, `falloff={0.2}`, `blur={6}`, `autoplay`, `loop`).
7. **Full React Bits `<MagicBento />` on Every Bento Card in `หน้าควบคุมวงจร`:** Apply the full React Bits `<MagicBento />` component (`enableBorderGlow={true}`, `enableSpotlight={true}`, `spotlightRadius={300}`, `clickEffect={true}`, `enableStars`, `enableTilt`, `enableMagnetism`) to every Bento card in `ElectronicControlTabView` (`หน้าควบคุมวงจร`).
8. **Interactive Liquid Tank Gauge (`<SloshGauge />`) for Water Volume & Flow Rate Adjustment:** Integrate `<SloshGauge />` (`interactive`, `showValue`, `liquidColor`, `glassColor="#27272a"`, `width={88}`, `height={180}`, `radius={20}`, `ticks={4}`, `viscosity={0.15}`, `tilt={0.45}`, `splash={0.42}`) to adjust **water volume and flow rate (`อันนี้เอาไว้ปรับ volume อัตราการไหลของน้ำ`)** inside `ElectronicControlTabView` (`#settings-pumps`).
9. **Rubber Physics Category Switcher (`<RubberSegment />`) for Category Selection:** Integrate `<RubberSegment />` (`trackColor="#27272a"`, `thumbColor="#fafafa"`, `textColor="#fafafa"`, `activeTextColor="#18181b"`, `size="md"`, `radius={10}`, `inset={3}`, `equalSlots`, `stretch={100}`, `squash={3}`, `speed={1}`, `glide={75}`, `draggable`) for **category selection (`เอาไปใช้กับการเลือกหมวดหมู่`)** across `ElectronicControlTabView`, `VisionPanel`, and `AnalyzeTabView`.
10. **Scroll & Mount Entrance Animations Across All Pages (`<AnimatedContent />`):** Integrate `<AnimatedContent />` (`distance={100}`, `direction="vertical"`, `duration={0.8}`, `ease="power3.out"`, `blur={0}`, `stagger={0.08}`, `threshold={0.1}`) across **every page/view in `server/static/index.html`** (`HomeView`, `AnalyzeTabView`, `ModelArchitectureTabView`, and `ElectronicControlTabView`) so sections and cards animate smoothly into place with staggered entrance physics.
11. **Electronic Control Decluttering & Strict Backward Compatibility:** Reorganize `ElectronicControlTabView` into a compact top status/phase bar + 4 segmented sub-tabs with grouped `R1–R4` and `R5–R7` relays and conversational Thai copy, while preserving all DOM IDs, English strings, and font-size constraints asserted by `tests/test_dashboard_overhaul.py` and `tests/test_presentation_override.py`.

---

## 2. Approved Design Decisions (from `/grill-me` & Component Additions)

### 2.1 Home Page (`<GradientASCII />` + `<Particles />` + `<TechText />` + `<Crosshair />` + `<SpecularButton />` + `<AnimatedContent />`)
- **Remove Old Backdrop:** In `CosmicThreeBackground`, remove `<div className="home-backdrop">` (`back.jpg`) and hide the Three.js starfield canvas when `isHome` (`currentView === 'home'`) is active.
- **Layer 1 (Base):** `<GradientASCII />` rendered inside `<div className="fixed inset-0 pointer-events-none" style={{ zIndex: 0 }}>`.
- **Layer 2 (Combo Overlay):** `<Particles />` rendered inside `<div className="fixed inset-0 pointer-events-none" style={{ zIndex: 1 }}>`.
- **Targeting Reticle (`<Crosshair />`):** Inside `HomeView`, bind `const homeContainerRef = useRef(null);` to the root `<div ref={homeContainerRef}>` of `HomeView` and render:
  ```jsx
  <Crosshair
    containerRef={homeContainerRef}
    color="#ffffff"
    targetEffect="lock"
    thickness={1}
    opacity={0.85}
    smoothing={0.35}
    showCoordinates
  />
  ```
- **Wordmark (`<TechText />`):** Render `<TechText text="A.E.G.I.S" fontWeight={600} fontSize={150} reveal="letter" dashLength={4} dashGap={2} specks={15} intro="none" introDuration={2} clickKick guides={false} />` in the hero center.
- **Hero CTAs (`<SpecularButton />`):** Wrap `ENTER A.E.G.I.S ANALYZE →` and `READ SYSTEM SPEC +` in `<SpecularButton />` (`data-crosshair-target` enabled automatically since `<SpecularButton />` renders a `<button>`).
- **Staggered Entrance (`<AnimatedContent />`):** Wrap the hero stack and expandable system specification sections in `HomeView` inside `<AnimatedContent distance={100} direction="vertical" duration={0.8} ease="power3.out" blur={0} stagger={0.08} threshold={0.1}>`.

### 2.2 All-Page Entrance Animation (`<AnimatedContent />`)
- **Zero-Dependency `gsap` + `ScrollTrigger` Shim:** Inside the `AnimatedContent` IIFE, we provide a self-contained browser implementation of `gsap.registerPlugin`, `gsap.context`, `gsap.set`, `gsap.to`, `gsap.timeline().fromTo()`, and `ScrollTrigger.create` using `IntersectionObserver` and `requestAnimationFrame` cubic-bezier/power3 easing (`1 - Math.pow(1 - t, 3)`).
- **Applied Across Every View in `server/static/index.html`:**
  1. **`HomeView` (`currentView === 'home'`):** Hero badge, `<TechText />` wordmark, subtitle, `<SpecularButton />` CTA row, and System Specification cards animate in with `<AnimatedContent distance={100} direction="vertical" duration={0.8} ease="power3.out" blur={0} stagger={0.08} threshold={0.1}>`.
  2. **`AnalyzeTabView` (`currentView === 'analyze'`):** Hero KPI Bento row, Digital Twin / Nutrient Radar row, and Telemetry Charts row each animate into view via `<AnimatedContent distance={100} direction="vertical" duration={0.8} ease="power3.out" blur={0} stagger={0.08} threshold={0.1}>`.
  3. **`ModelArchitectureTabView` (`currentView === 'model'`):** Architecture header, Dual-Pathway MobileNetV3 + Sensor Fusion pipeline cards, and performance metric sections animate in via `<AnimatedContent distance={100} direction="vertical" duration={0.8} ease="power3.out" blur={0} stagger={0.08} threshold={0.1}>`.
  4. **`ElectronicControlTabView` (`currentView === 'settings'`):** Top header, `#settings-schedule` bar, `<RubberSegment />` category bar, and each of the 4 sub-tab panels (`#settings-pumps`, `#settings-vision`, `#settings-simulation`, `#settings-pinout`) are wrapped in `<AnimatedContent distance={100} direction="vertical" duration={0.8} ease="power3.out" blur={0} stagger={0.08} threshold={0.1}>`.

### 2.3 Interactive Glass CTA Buttons (`<SpecularButton />`)
- Applied selectively to primary CTA buttons (max 2–4 visible per view to respect the browser WebGL2 context limit):
  - `HomeView`: `ENTER A.E.G.I.S ANALYZE →`, `READ SYSTEM SPEC +`
  - `ElectronicControlTabView`: `▶ รันอัตโนมัติครบ 6 ขั้นตอน`, `💧 สั่งฉีดปุ๋ยตามสูตรทันที`, `📸 สั่งถ่ายภาพใหม่`

### 2.4 Animated Numeric Readouts (`<CountUp />`)
- Applied to:
  - `AnalyzeTabView` Hero KPI Cards: Temperature (`°C`), pH Sensor, EC Sensor (`mS/cm`).
  - `ElectronicControlTabView` Numeric Readouts: Stock A / B / C volume readouts (`mL`), pump duration readouts (`วินาที`), total dosing volume (`mL`), simulated `EC`, `pH`, `Temp`, and Stock A/B/C ratio percentages (`%`).

### 2.5 3D Leaf Image Gallery (`<DepthCarousel />`)
- Applied inside `VisionPanel` (`#settings-vision` in `ElectronicControlTabView`) with `depth={220}`, `spread={90}`, `tilt={22}`, `tiltDirection="right"`, `perspective={1400}`, `visibleCards={4}`, `falloff={0.2}`, `blur={6}`, `autoplay`, `loop`.

### 2.6 Full React Bits `<MagicBento />` Across All Bento Cards in `หน้าควบคุมวงจร`
- Applied to every Bento card in `ElectronicControlTabView` (`#settings-schedule`, `#settings-pumps`, `#settings-vision`, `#settings-simulation`, `#settings-pinout`) with `enableBorderGlow={true}`, `enableSpotlight={true}`, `spotlightRadius={300}`, `clickEffect={true}`, `enableStars`, `enableTilt`, `enableMagnetism`.

### 2.7 Interactive Liquid Tank Gauge (`<SloshGauge />`) for Water Volume & Flow Rate Adjustment
- Applied inside `#settings-pumps`:
  1. **Tank 1 — ปริมาตรน้ำเดินปั๊ม (Water Volume / Runtime Level, `#38bdf8`):** Maps `0–100%` to `pumpRuntimeMs` (`300 ms – 30,000 ms`).
  2. **Tank 2 — อัตราการไหลของน้ำ (Water Flow Rate `Q`, `#22d3ee`):** Maps `0–100%` to `calibration.pump_flow_rate_ml_s` (`0.20 – 3.00 mL/s`).
  3. **Stock A / B / C Dosing Volume Tanks (`#eab308`, `#a855f7`, `#f97316`):** Interactive tanks mapped to `stockAmounts.A`, `stockAmounts.B`, `stockAmounts.C` (`0–25 mL` ↔ `0–100%`).

### 2.8 Rubber Physics Category Switcher (`<RubberSegment />`) for Category Selection
- Applied to:
  1. **Electronic Control 4 Sub-Tab Category Switcher (`controlSubTab`):** `1. สั่งปั๊ม & โดสปุ๋ย`, `2. กล้อง & ภาพใบผักบุ้ง`, `3. จำลองค่า & ประวัติคำสั่ง`, `4. ผังพินบอร์ด (GPIO)`
  2. **VisionPanel Leaf Category Filter (`#settings-vision`):** `ทั้งหมด (ALL)`, `สมบูรณ์ (Control)`, `ขาดไนโตรเจน (-N)`, `ขาดฟอสฟอรัส (-P)`, `ขาดโพแทสเซียม (-K)`
  3. **Scenario Simulator AI Deficiency Category (`#settings-simulation`):** `Control (ปกติ)`, `ขาด N (-N)`, `ขาด P (-P)`, `ขาด K (-K)`
  4. **AnalyzeTabView Experimental Unit Category Switcher:** `Control`, `-N`, `-P`, `-K`

### 2.9 Layout Architecture & Relay R1–R7 Grouping in `หน้าควบคุมวงจร`
- **Top Status & 6-Step Bar (`#settings-schedule`):** Compact 1-row Auto Schedule + Override status bar + 6-Step phase strip.
- **4 Segmented Sub-Tabs (`controlSubTab`):** Toggled via CSS `block` vs `hidden` so all DOM IDs remain mounted.
- **Relay R1–R7 Split into 2 Visual Groups:**
  1. **ชุดกระบอกตวงวัดน้ำ & ล้างหัววัด (`R1–R4`):** `ดูดน้ำเข้ากระบอกตวง`, `ปั๊มลมกวนน้ำในกระบอก`, `โซลินอยด์วาล์วปล่อยน้ำทิ้ง`, `ปั๊มน้ำดีล้างและแช่หัววัด`
  2. **ชุดปั๊มโดสปุ๋ย A / B / C (`R5–R7`):** `ปั๊มปุ๋ย A (เร่งใบ N)`, `ปั๊มปุ๋ย B (โครงสร้าง P)`, `ปั๊มปุ๋ย C (โพแทสเซียม K)`

---

## 3. Verification Criteria

1. `tests/test_dashboard_overhaul.py` passes 100%.
2. `tests/test_presentation_override.py` passes 100%.
3. `tests/test_control_ux_cleanup.py` verifies all 11 React Bits components (`GradientASCII`, `Particles`, `TechText`, `Crosshair`, `SpecularButton`, `CountUp`, `DepthCarousel`, `MagicBento`, `SloshGauge`, `RubberSegment`, `AnimatedContent`) plus the 4 sub-tabs, grouped `R1–R4` vs `R5–R7` relay cards, Thai-first action labels, and zero `<12px` fonts in `ElectronicControlTabView`.
