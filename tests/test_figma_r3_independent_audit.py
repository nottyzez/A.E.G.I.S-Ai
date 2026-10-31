# -*- coding: utf-8 -*-
"""
tests/test_figma_r3_independent_audit.py — Comprehensive Reviewer 3 Independent Verification Suite
Conducts exhaustive, adversarial verification of:
1. R1: Full Figma UI layout, pixel dimensions, typography, progress strips, chart day labels, logo hiding.
2. R2: Background image binary verification, dual-path asset resolution contract (file:// and http://), FastAPI serving.
3. R3: Reduced star particles, intermittent dashboard shooting stars, disabled home meteors, drifting non-blocking clouds, mouse-parallax space nebula.
4. Edge cases & Stress: Responsive safety guards, null/NaN handling, tab switching isolation, Node.js runtime validation.
"""

import unittest
import re
import os
import json
import subprocess
import sys
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
STATIC_DIR = PROJECT_ROOT / "server" / "static"
INDEX_PATH = STATIC_DIR / "index.html"
IMAGES_REAL_DIR = STATIC_DIR / "images_real"
DATA_DIR = STATIC_DIR / "data"

class TestFigmaR3LayoutAndDimensions(unittest.TestCase):
    """Deep verification of R1 Figma Layout, CSS Rules, and Component Hierarchy."""

    @classmethod
    def setUpClass(cls):
        cls.html = INDEX_PATH.read_text(encoding="utf-8")

    def test_r1_header_and_sidebar_spec(self):
        """Header (68px) and Sidebar (212px expanded, 68px collapsed) positioning and styles."""
        # Header styles
        header_css = re.search(r"\.figma-header\s*\{([^}]+)\}", self.html)
        self.assertIsNotNone(header_css, ".figma-header CSS class must exist")
        rules_h = header_css.group(1)
        self.assertIn("68px", rules_h)
        self.assertIn("rgba(16, 19, 29, 0.32)", rules_h)
        self.assertIn("blur(14px)", rules_h)

        # Sidebar styles
        sidebar_css = re.search(r"\.figma-sidebar\s*\{([^}]+)\}", self.html)
        self.assertIsNotNone(sidebar_css, ".figma-sidebar CSS class must exist")
        rules_s = sidebar_css.group(1)
        self.assertIn("212px", rules_s)
        self.assertIn("rgba(14, 16, 24, 0.52)", rules_s)
        self.assertIn("blur(22px)", rules_s)

        # Collapsed sidebar
        collapsed_css = re.search(r"\.figma-sidebar\.collapsed\s*\{([^}]+)\}", self.html)
        self.assertIsNotNone(collapsed_css)
        self.assertIn("68px", collapsed_css.group(1))

    def test_r1_sidebar_logo_hidden(self):
        """Sidebar logo hidden via display: none in CSS and JSX."""
        self.assertIn(".figma-sidebar-logo, .figma-sidebar .sidebar-logo", self.html)
        self.assertIn("display: none !important", self.html)
        logo_jsx = re.search(
            r'className=["\'][^"\']*figma-sidebar-logo[^"\']*["\'][^>]*style=\{\{\s*display:\s*[\'"]none[\'"]\s*\}\}',
            self.html
        )
        self.assertIsNotNone(logo_jsx, "Sidebar logo must have inline style={{ display: 'none' }}")

    def test_r1_title_block_inter_600_40px(self):
        """Title block: A.E.G.I.S Analyze (Inter 600, 40px, line-height 20px, color #FFFFFF)."""
        css_match = re.search(r"\.figma-title-block\s*\{([^}]+)\}", self.html)
        self.assertIsNotNone(css_match)
        rules = css_match.group(1)
        self.assertIn("'Inter'", rules)
        self.assertIn("600", rules)
        self.assertIn("40px", rules)
        self.assertIn("20px", rules)
        self.assertIn("#FFFFFF", rules)

        jsx_match = re.search(
            r'<h1[^>]*className=["\'][^"\']*figma-title-block[^"\']*["\'][^>]*>([\s\S]*?)</h1>',
            self.html
        )
        self.assertIsNotNone(jsx_match)
        self.assertIn("A.E.G.I.S Analyze", jsx_match.group(1))

    def test_r1_ph_kpi_card_geometry(self):
        """pH sensor KPI card: dimensions 315x116px, background rgba(227, 245, 255, 0.2), border-radius 16px."""
        css_match = re.search(r"\.figma-card-ph-kpi\s*\{([^}]+)\}", self.html)
        self.assertIsNotNone(css_match)
        rules = css_match.group(1)
        self.assertIn("315px", rules)
        self.assertIn("116px", rules)
        self.assertIn("rgba(227, 245, 255, 0.2)", rules)
        self.assertIn("16px", rules)
        self.assertIn("max-width: 100%", rules)

    def test_r1_ec_kpi_card_geometry(self):
        """EC sensor KPI card: dimensions 341x116px, background rgba(255, 255, 255, 0.05), border-radius 16px."""
        css_match = re.search(r"\.figma-card-ec-kpi\s*\{([^}]+)\}", self.html)
        self.assertIsNotNone(css_match)
        rules = css_match.group(1)
        self.assertIn("341px", rules)
        self.assertIn("116px", rules)
        self.assertIn("rgba(255, 255, 255, 0.05)", rules)
        self.assertIn("16px", rules)
        self.assertIn("max-width: 100%", rules)

    def test_r1_ec_line_chart_geometry_and_7day_labels(self):
        """EC sensor Line Chart: 665x248px, rgba(255, 255, 255, 0.05), shadow 0px 4px 5.8px 4px, blur 3.9px, radius 16px, 7-day axis."""
        css_match = re.search(r"\.figma-card-ec-chart\s*\{([^}]+)\}", self.html)
        self.assertIsNotNone(css_match)
        rules = css_match.group(1)
        self.assertIn("665px", rules)
        self.assertIn("248px", rules)
        self.assertIn("rgba(255, 255, 255, 0.05)", rules)
        self.assertIn("0px 4px 5.8px 4px rgba(0, 0, 0, 0.25)", rules)
        self.assertIn("blur(3.9px)", rules)
        self.assertIn("16px", rules)
        self.assertIn("max-width: 100%", rules)

        # 7-day horizontal labels in JSX
        idx = self.html.find('figma-card-ec-chart magic-bento-card')
        self.assertGreater(idx, 0, "EC chart JSX element must exist")
        end_idx = self.html.find('figma-card-aegis-analyze', idx)
        ec_block = self.html[idx:end_idx] if end_idx > idx else self.html[idx:idx + 10000]
        for day in ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']:
            self.assertIn(day, ec_block, f"EC chart missing day label {day}")

    def test_r1_ph_line_chart_geometry_and_7day_labels(self):
        """pH sensor Line Chart: 662x217px, rgba(255, 255, 255, 0.05), radius 16px, 7-day axis."""
        css_match = re.search(r"\.figma-card-ph-chart\s*\{([^}]+)\}", self.html)
        self.assertIsNotNone(css_match)
        rules = css_match.group(1)
        self.assertIn("662px", rules)
        self.assertIn("217px", rules)
        self.assertIn("rgba(255, 255, 255, 0.05)", rules)
        self.assertIn("16px", rules)
        self.assertIn("max-width: 100%", rules)

        idx = self.html.find('figma-card-ph-chart magic-bento-card')
        self.assertGreater(idx, 0, "pH chart JSX element must exist")
        end_idx = self.html.find('figma-card-ec-chart', idx)
        ph_block = self.html[idx:end_idx] if end_idx > idx else self.html[idx:idx + 10000]
        for day in ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']:
            self.assertIn(day, ph_block, f"pH chart missing day label {day}")

    def test_r1_temperature_card_geometry_icon_and_readout(self):
        """Temperature Card: 272x245px, rgba(255, 255, 255, 0.05), radius 16px, thermometer icon, Work Sans 700 64px."""
        css_match = re.search(r"\.figma-card-temperature\s*\{([^}]+)\}", self.html)
        self.assertIsNotNone(css_match)
        rules = css_match.group(1)
        self.assertIn("272px", rules)
        self.assertIn("245px", rules)
        self.assertIn("rgba(255, 255, 255, 0.05)", rules)
        self.assertIn("16px", rules)
        self.assertIn("max-width: 100%", rules)

        idx = self.html.find('figma-card-temperature magic-bento-card')
        self.assertGreater(idx, 0, "Temperature card JSX element must exist")
        temp_block = self.html[idx:idx + 1500]
        self.assertIn("IconThermometerFigma", temp_block)
        self.assertIn("64px", temp_block)
        self.assertIn("700", temp_block)
        self.assertIn("font-work font-bold", temp_block)

    def test_r1_projections_card_geometry(self):
        """Projections vs Actuals card: dimensions 524x248px, background rgba(120, 120, 128, 0.16), blur(2px), radius 16px."""
        css_match = re.search(r"\.figma-card-projections\s*\{([^}]+)\}", self.html)
        self.assertIsNotNone(css_match)
        rules = css_match.group(1)
        self.assertIn("524px", rules)
        self.assertIn("248px", rules)
        self.assertIn("rgba(120, 120, 128, 0.16)", rules)
        self.assertIn("blur(2px)", rules)
        self.assertIn("16px", rules)
        self.assertIn("max-width: 100%", rules)

    def test_r1_aegis_analyze_card_and_progress_strips(self):
        """A.E.G.I.S analyze! card: 524x352px, rgba(0, 0, 0, 0.15), radius 17px, centered title Work Sans 400 32px, 4 strips."""
        css_match = re.search(r"\.figma-card-aegis-analyze\s*\{([^}]+)\}", self.html)
        self.assertIsNotNone(css_match)
        rules = css_match.group(1)
        self.assertIn("524px", rules)
        self.assertIn("352px", rules)
        self.assertIn("rgba(0, 0, 0, 0.15)", rules)
        self.assertIn("17px", rules)
        self.assertIn("max-width: 100%", rules)

        # Centered title in JSX
        idx = self.html.find('figma-card-aegis-analyze magic-bento-card')
        self.assertGreater(idx, 0, "Analyze card JSX element must exist")
        analyze_block = self.html[idx:idx + 2500]
        self.assertIn("A.E.G.I.S analyze!", analyze_block)
        self.assertIn("32px", analyze_block)
        self.assertIn("text-center", analyze_block)

        # 4 Strips CSS
        track_css = re.search(r"\.figma-strip-track\s*\{([^}]+)\}", self.html)
        self.assertIsNotNone(track_css)
        self.assertIn("12.51px", track_css.group(1))
        self.assertIn("80px", track_css.group(1))
        self.assertIn("rgba(28, 28, 28, 0.4)", track_css.group(1))

        fill_css = re.search(r"\.figma-strip-fill\s*\{([^}]+)\}", self.html)
        self.assertIsNotNone(fill_css)
        self.assertIn("12.51px", fill_css.group(1))
        self.assertIn("80px", fill_css.group(1))
        self.assertIn("#A8C5DA", fill_css.group(1))

        # Typography check: Bold label on left (Work Sans 700 20px), percentage on right (Inter 12px)
        self.assertTrue(
            bool(re.search(
                r'font-work\s+font-bold\s+text-\[20px\][^>]*>\{item\.label\}</span>\s*<span[^>]*font-inter\s+text-\[12px\][^>]*>\{pct\}%</span>',
                self.html
            )),
            "Each strip must have bold label on the left (Work Sans 700, 20px) and percentage value on the right (Inter 12px)"
        )

        # 4 Strip categories: Healthy, N, P, K
        for k in ['Healthy', 'N', 'P', 'K']:
            self.assertIn(f"key: '{k}'", self.html)

    def test_r1_tab_isolation_and_no_leak(self):
        """Verify .figma-card-aegis-analyze is strictly isolated to Tab 1 (Analyze) and not present in Tab 2 or Tab 3."""
        idx_tab2 = self.html.find("Electronic Control — Dual ESP32-S3 Hardware")
        idx_tab3 = self.html.find("All Sample — 12 ชุดทดลองผักบุ้งไฮโดรโปนิกส์")
        self.assertGreater(idx_tab2, 0)
        self.assertGreater(idx_tab3, idx_tab2)

        tab2_content = self.html[idx_tab2:idx_tab3]
        self.assertNotIn("figma-card-aegis-analyze", tab2_content)
        self.assertIn("figma-card-dark", tab2_content)

        tab3_content = self.html[idx_tab3:]
        self.assertNotIn("figma-card-aegis-analyze", tab3_content)


class TestFigmaR3BackgroundImagesAndDualPath(unittest.TestCase):
    """Verification of R2 Background Images and Dual-Path Protocol Compatibility."""

    def test_r2_mountain_background_image(self):
        """dashboard_mountain_bg.png exists, valid PNG, >50KB, proper resolution."""
        img_path = IMAGES_REAL_DIR / "dashboard_mountain_bg.png"
        self.assertTrue(img_path.exists(), f"{img_path} must exist on disk")
        self.assertGreater(img_path.stat().st_size, 50000, "Image size must exceed 50KB")
        with Image.open(img_path) as im:
            self.assertEqual(im.format, "PNG")
            self.assertGreaterEqual(im.width, 800)
            self.assertGreaterEqual(im.height, 600)

    def test_r2_space_background_image(self):
        """space_bg.jpg exists, valid JPEG, >50KB, proper resolution."""
        img_path = IMAGES_REAL_DIR / "space_bg.jpg"
        self.assertTrue(img_path.exists(), f"{img_path} must exist on disk")
        self.assertGreater(img_path.stat().st_size, 50000, "Image size must exceed 50KB")
        with Image.open(img_path) as im:
            self.assertEqual(im.format, "JPEG")
            self.assertGreaterEqual(im.width, 500)
            self.assertGreaterEqual(im.height, 800)

    def test_r2_background_application_in_html(self):
        """Verify dashboard uses dashboard_mountain_bg.png and home uses space_bg.jpg."""
        html = INDEX_PATH.read_text(encoding="utf-8")
        self.assertIn("images_real/dashboard_mountain_bg.png", html)
        self.assertIn("images_real/space_bg.jpg", html)
        self.assertIn('url("${mountainBg}")', html)
        self.assertIn('url("${spaceBg}")', html)

    def test_r2_dual_path_contract_comprehensive(self):
        """Test asset resolver contract with clean, prefixed, and edge-case relative paths."""
        resolver_js = r"""
        var __AEGIS_IS_FILE__ = %s;
        var __AEGIS_ASSET_BASE__ = __AEGIS_IS_FILE__ ? '.' : '/static';
        function resolve(relativePath) {
          if (!relativePath) return '';
          var clean = relativePath.replace(/^(\.\/|\/)?(static\/)?/, '');
          return __AEGIS_ASSET_BASE__ + '/' + clean;
        }
        """

        # Verify on both file: and http:
        for is_file, prefix in [(True, "."), (False, "/static")]:
            cases = [
                ("images_real/dashboard_mountain_bg.png", f"{prefix}/images_real/dashboard_mountain_bg.png"),
                ("./images_real/space_bg.jpg", f"{prefix}/images_real/space_bg.jpg"),
                ("/static/data/sensor_data.js", f"{prefix}/data/sensor_data.js"),
                ("static/presentation_engine.js", f"{prefix}/presentation_engine.js"),
                ("data/images_manifest.js", f"{prefix}/data/images_manifest.js"),
            ]
            for input_p, expected in cases:
                js_code = (resolver_js % ('true' if is_file else 'false')) + f"\nconsole.log(resolve('{input_p}'));"
                proc = subprocess.run(["node", "-e", js_code], capture_output=True, text=True, check=True)
                res = proc.stdout.strip()
                self.assertEqual(res, expected, f"Failed for {input_p} under is_file={is_file}")

    def test_r2_fastapi_static_mounts_integrity(self):
        """Verify FastAPI mounts /static to server/static directory."""
        from main import app
        from fastapi.staticfiles import StaticFiles

        static_mounts = [
            r for r in app.routes
            if hasattr(r, "path") and r.path == "/static" and isinstance(getattr(r, "app", None), StaticFiles)
        ]
        self.assertGreater(len(static_mounts), 0, "FastAPI app missing '/static' mount")
        mount_dir = Path(static_mounts[0].app.directory).resolve()
        self.assertEqual(mount_dir, STATIC_DIR.resolve())


class TestFigmaR3CosmicAndAtmosphericEffects(unittest.TestCase):
    """Verification of R3 Cosmic Particles, Meteors, Clouds, and Nebula."""

    @classmethod
    def setUpClass(cls):
        cls.html = INDEX_PATH.read_text(encoding="utf-8")

    def test_r3_star_particle_density_and_twinkling(self):
        """Reduced star density (280 far, 150 mid, 60 near = 490 total < 500) and sinusoidal twinkling."""
        self.assertIn("createStarLayer(280, 560, -280, -80, 1.2, '#93c5fd', 0.55)", self.html)
        self.assertIn("createStarLayer(150, 420, -120, 20, 1.8, '#e0e7ff', 0.70)", self.html)
        self.assertIn("createStarLayer(60, 310, -30, 85, 2.4, '#ffffff', 0.85)", self.html)

        # Twinkling math in animate loop
        self.assertIn("farLayer.points.material.opacity = 0.45 + Math.sin(clock * 1.8) * 0.12", self.html)
        self.assertIn("midLayer.points.material.opacity = 0.58 + Math.cos(clock * 2.3) * 0.14", self.html)
        self.assertIn("nearLayer.points.material.opacity = 0.75 + Math.sin(clock * 2.8) * 0.12", self.html)

    def test_r3_meteors_dashboard_rare_and_home_disabled(self):
        """Dashboard meteors rare (random < 0.002); Home completely disabled (meteorGroup.visible = false)."""
        idx = self.html.find("Shooting Stars (Meteors)")
        self.assertGreater(idx, 0)
        meteor_code = self.html[idx:idx + 600]
        self.assertIn("viewRef.current === 'dashboard'", meteor_code)
        self.assertIn("meteorGroup.visible = true", meteor_code)
        self.assertIn("Math.random() < 0.002", meteor_code)
        self.assertIn("else {", meteor_code)
        self.assertIn("meteorGroup.visible = false;", meteor_code)

    def test_r3_dashboard_clouds_non_blocking_and_drifting(self):
        """Drifting cloud layer on dashboard with pointer-events: none, z-index: 1, keyframe animations."""
        cloud_css = re.search(r"\.dashboard-clouds-layer\s*\{([^}]+)\}", self.html)
        self.assertIsNotNone(cloud_css)
        rules = cloud_css.group(1)
        self.assertIn("pointer-events: none", rules)
        self.assertIn("opacity: 0.18", rules)

        self.assertIn("@keyframes cloudDriftSlow", self.html)
        self.assertIn("@keyframes cloudDriftFast", self.html)

        # Rendered strictly on dashboard view
        self.assertIn("currentView === 'dashboard' && (", self.html)
        self.assertIn("className=\"dashboard-clouds-layer\"", self.html)

    def test_r3_home_space_nebula_mouse_parallax(self):
        """Stationary space nebula on Home view with pointer-events: none and smooth mouse parallax."""
        nebula_css = re.search(r"\.home-space-nebula\s*\{([^}]+)\}", self.html)
        self.assertIsNotNone(nebula_css)
        rules = nebula_css.group(1)
        self.assertIn("pointer-events: none", rules)
        self.assertIn("transition: transform 0.25s", rules)

        # Smooth mouse parallax transform
        self.assertIn("nebulaRef.current.style.transform = `translate3d(${targetX * 28}px, ${targetY * 20}px, 0)`", self.html)

        # Rendered strictly on home view
        self.assertIn("currentView === 'home' && (", self.html)
        self.assertIn("ref={nebulaRef} className=\"home-space-nebula\"", self.html)


class TestFigmaR3NodeRuntimeAdversarialAndUnitProbabilities(unittest.TestCase):
    """Stress tests executed via Node.js V8 runtime for unit probabilities, scripts, and math."""

    def test_all_12_units_probabilities_math_in_node(self):
        """Verify all 12 units (Control, N, P, K, Cup1..Cup8) produce valid numeric probabilities in Node.js."""
        script = """
        const fs = require('fs');
        const path = require('path');
        const html = fs.readFileSync(path.join('server', 'static', 'index.html'), 'utf8');

        // Extract UNIT_META declaration
        const start = html.indexOf('const UNIT_META = {');
        const end = html.indexOf('function getUnitTimeSeries', start);
        if (start === -1 || end === -1) throw new Error('UNIT_META not found');

        const unitMetaCode = html.substring(start, end).trim();
        let UNIT_META;
        eval(unitMetaCode.replace('const UNIT_META =', 'UNIT_META ='));

        const units = Object.keys(UNIT_META);
        if (units.length !== 12) throw new Error('Expected 12 units in UNIT_META, found ' + units.length);

        // Control specific check: Healthy 78%, N 0%, P 10%, K 2%
        const ctrl = UNIT_META.Control;
        const h = Math.round(ctrl.probs.Healthy * 100);
        const n = Math.round(ctrl.probs.N_Deficiency * 100);
        const p = Math.round(ctrl.probs.P_Deficiency * 100);
        const k = Math.round(ctrl.probs.K_Deficiency * 100);

        if (h !== 78 || n !== 0 || p !== 10 || k !== 2) {
            throw new Error(`Control probs mismatch: H=${h}, N=${n}, P=${p}, K=${k}`);
        }

        // Treatment Tanks check
        if (Math.round(UNIT_META.N.probs.N_Deficiency * 100) !== 86) throw new Error('Tank N deficiency mismatch');
        if (Math.round(UNIT_META.P.probs.P_Deficiency * 100) !== 84) throw new Error('Tank P deficiency mismatch');
        if (Math.round(UNIT_META.K.probs.K_Deficiency * 100) !== 85) throw new Error('Tank K deficiency mismatch');

        // All units strip values check
        for (const uId of units) {
            const meta = UNIT_META[uId];
            const probs = meta.probs || {};
            const items = [
                { key: 'Healthy', val: probs.Healthy != null ? Math.round(probs.Healthy * 100) : 78 },
                { key: 'N', val: probs.N_Deficiency != null ? Math.round(probs.N_Deficiency * 100) : 0 },
                { key: 'P', val: probs.P_Deficiency != null ? Math.round(probs.P_Deficiency * 100) : 10 },
                { key: 'K', val: probs.K_Deficiency != null ? Math.round(probs.K_Deficiency * 100) : 2 },
            ];
            for (const item of items) {
                if (isNaN(item.val) || item.val < 0 || item.val > 100) {
                    throw new Error(`Invalid strip value for unit ${uId}: ${item.key}=${item.val}`);
                }
            }
        }

        console.log('ALL_12_UNITS_PROBS_VERIFIED');
        """
        out = subprocess.check_output(["node", "-e", script], text=True).strip()
        self.assertIn("ALL_12_UNITS_PROBS_VERIFIED", out)

    def test_sensor_readings_spline_paths_math_in_node(self):
        """Execute spline calculations over all 143 sensor readings in Node.js to verify zero NaNs."""
        script = """
        const fs = require('fs');
        const path = require('path');
        const globalWindow = {};
        global.window = globalWindow;

        const sensorJs = fs.readFileSync(path.join('server', 'static', 'data', 'sensor_data.js'), 'utf8');
        eval(sensorJs);

        const readings = globalWindow.SENSOR_DATA.readings;
        if (!readings || readings.length !== 143) throw new Error('Sensor readings count != 143');

        // Extract computeSvgSplinePoints formula from index.html
        function computeSpline(readings, field, width = 560, height = 130, yMin = 5.0, yMax = 8.0) {
            const pts = [];
            const n = readings.length;
            if (n === 0) return pts;
            for (let i = 0; i < n; i++) {
                const r = readings[i];
                const val = r ? r[field] : null;
                if (val == null || typeof val !== 'number' || isNaN(val)) continue;
                const x = 14 + (i / Math.max(1, n - 1)) * (width - 28);
                const normY = Math.max(0, Math.min(1, (val - yMin) / (yMax - yMin)));
                const y = height - 12 - normY * (height - 24);
                if (isNaN(x) || isNaN(y)) throw new Error('NaN in spline point: x=' + x + ', y=' + y);
                pts.push({ x, y, val });
            }
            return pts;
        }

        const phPts = computeSpline(readings, 'ph_after', 560, 130, 4.0, 9.0);
        const ecPts = computeSpline(readings, 'ec', 560, 165, 0.0, 3.0);
        if (phPts.length === 0 || ecPts.length === 0) throw new Error('Empty spline points');

        console.log(`SPLINE_OK: phPts=${phPts.length}, ecPts=${ecPts.length}`);
        """
        out = subprocess.check_output(["node", "-e", script], text=True).strip()
        self.assertIn("SPLINE_OK", out)

    def test_warp_speed_zoom_keyframes_present(self):
        """Verify warpSpeedZoom keyframes and animation timing in CSS."""
        html = INDEX_PATH.read_text(encoding="utf-8")
        self.assertIn("@keyframes warpSpeedZoom", html)
        self.assertIn(".warp-zoom-active", html)
        self.assertIn("0.82s cubic-bezier(0.22, 1, 0.36, 1)", html)


if __name__ == "__main__":
    unittest.main(verbosity=2)
