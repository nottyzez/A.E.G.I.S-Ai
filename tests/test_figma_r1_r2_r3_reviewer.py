# -*- coding: utf-8 -*-
"""
tests/test_figma_r1_r2_r3_reviewer.py — Adversarial Verification Suite for Reviewer 1
Validates:
1. R1: Full Figma Card Geometry, Typography, Progress Strips, Sidebar Logo Hiding, and Tab Isolation.
2. R2: Asset Integrity, Binary File Format, Dual-Protocol Resolution, and FastAPI Serving.
3. R3: Star Particle Density, Meteor Suppression, Drifting Clouds Non-Blocking Behavior, and Nebula Parallax.
"""

import unittest
import re
import os
import json
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = PROJECT_ROOT / "server" / "static"
INDEX_PATH = STATIC_DIR / "index.html"
IMAGES_REAL_DIR = STATIC_DIR / "images_real"

class FigmaR1ComponentAndTypographyTest(unittest.TestCase):
    """Deep verification of R1 Figma Layout, Dimensions, and Typography requirements."""

    @classmethod
    def setUpClass(cls):
        cls.html = INDEX_PATH.read_text(encoding="utf-8")

    def test_r1_figma_title_block_typography(self):
        """Verify Title Block: Inter 600, 40px, line-height 20px, color #FFFFFF."""
        # CSS rule verification
        css_match = re.search(r"\.figma-title-block\s*\{([^}]+)\}", self.html)
        self.assertIsNotNone(css_match, ".figma-title-block CSS class must exist")
        rules = css_match.group(1)
        self.assertIn("40px", rules)
        self.assertIn("20px", rules)
        self.assertIn("#FFFFFF", rules)

        # JSX tag verification
        jsx_match = re.search(r'<h1[^>]*className=["\'][^"\']*figma-title-block[^"\']*["\'][^>]*>([\s\S]*?)</h1>', self.html)
        self.assertIsNotNone(jsx_match, "<h1> with .figma-title-block must be present")
        self.assertIn("A.E.G.I.S Analyze", jsx_match.group(1))

    def test_r1_ph_kpi_card_geometry_and_styling(self):
        """Verify pH sensor KPI card: 315x116px, background rgba(227, 245, 255, 0.2), border-radius 16px."""
        css_match = re.search(r"\.figma-card-ph-kpi\s*\{([^}]+)\}", self.html)
        self.assertIsNotNone(css_match)
        rules = css_match.group(1)
        self.assertIn("315px", rules)
        self.assertIn("116px", rules)
        self.assertIn("rgba(227, 245, 255, 0.2)", rules)
        self.assertIn("16px", rules)
        self.assertIn("max-width: 100%", rules, "Must include max-width for responsive safety")

    def test_r1_ec_kpi_card_geometry_and_styling(self):
        """Verify EC sensor KPI card: 341x116px, background rgba(255, 255, 255, 0.05), border-radius 16px."""
        css_match = re.search(r"\.figma-card-ec-kpi\s*\{([^}]+)\}", self.html)
        self.assertIsNotNone(css_match)
        rules = css_match.group(1)
        self.assertIn("341px", rules)
        self.assertIn("116px", rules)
        self.assertIn("rgba(255, 255, 255, 0.05)", rules)
        self.assertIn("16px", rules)
        self.assertIn("max-width: 100%", rules, "Must include max-width for responsive safety")

    def test_r1_ec_line_chart_geometry_and_styling(self):
        """Verify EC sensor Line Chart: 665x248px, rgba(255, 255, 255, 0.05), shadow 0px 4px 5.8px 4px, blur 3.9px, radius 16px, 7-day axis."""
        css_match = re.search(r"\.figma-card-ec-chart\s*\{([^}]+)\}", self.html)
        self.assertIsNotNone(css_match)
        rules = css_match.group(1)
        self.assertIn("665px", rules)
        self.assertIn("248px", rules)
        self.assertIn("rgba(255, 255, 255, 0.05)", rules)
        self.assertIn("0px 4px 5.8px 4px rgba(0, 0, 0, 0.25)", rules)
        self.assertIn("blur(3.9px)", rules)
        self.assertIn("16px", rules)

        # 7-day labels in EC card
        ec_chart_jsx = re.search(r'<div[^>]*className=["\'][^"\']*figma-card-ec-chart[^"\']*["\'][\s\S]*?\{(\[[^\]]*Sun[^\]]*Sat[^\]]*\])\.map', self.html)
        self.assertIsNotNone(ec_chart_jsx, "EC chart must render 7-day labels")
        for day in ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']:
            self.assertIn(day, ec_chart_jsx.group(1))

    def test_r1_ph_line_chart_geometry_and_styling(self):
        """Verify pH sensor Line Chart: 662x217px, rgba(255, 255, 255, 0.05), radius 16px, 7-day axis."""
        css_match = re.search(r"\.figma-card-ph-chart\s*\{([^}]+)\}", self.html)
        self.assertIsNotNone(css_match)
        rules = css_match.group(1)
        self.assertIn("662px", rules)
        self.assertIn("217px", rules)
        self.assertIn("rgba(255, 255, 255, 0.05)", rules)
        self.assertIn("16px", rules)

        # 7-day labels in pH card
        ph_chart_jsx = re.search(r'<div[^>]*className=["\'][^"\']*figma-card-ph-chart[^"\']*["\'][\s\S]*?\{(\[[^\]]*Sun[^\]]*Sat[^\]]*\])\.map', self.html)
        self.assertIsNotNone(ph_chart_jsx, "pH chart must render 7-day labels")
        for day in ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']:
            self.assertIn(day, ph_chart_jsx.group(1))

    def test_r1_temperature_card_geometry_icon_and_readout(self):
        """Verify Temperature Card: 272x245px, rgba(255, 255, 255, 0.05), radius 16px, thermometer icon, Work Sans 700 64px."""
        css_match = re.search(r"\.figma-card-temperature\s*\{([^}]+)\}", self.html)
        self.assertIsNotNone(css_match)
        rules = css_match.group(1)
        self.assertIn("272px", rules)
        self.assertIn("245px", rules)
        self.assertIn("rgba(255, 255, 255, 0.05)", rules)
        self.assertIn("16px", rules)

        temp_card_jsx = re.search(r'figma-card-temperature[\s\S]*?(<IconThermometerFigma[\s\S]*?\{activeTemp\}°C[\s\S]*?)<\/div>', self.html)
        self.assertIsNotNone(temp_card_jsx, "Temperature card must contain IconThermometerFigma and activeTemp readout")
        self.assertIn("64px", temp_card_jsx.group(1))
        self.assertIn("font-work font-bold", temp_card_jsx.group(1))

    def test_r1_projections_card_geometry_and_styling(self):
        """Verify Projections vs Actuals card: 524x248px, background rgba(120, 120, 128, 0.16), blur(2px), radius 16px."""
        css_match = re.search(r"\.figma-card-projections\s*\{([^}]+)\}", self.html)
        self.assertIsNotNone(css_match)
        rules = css_match.group(1)
        self.assertIn("524px", rules)
        self.assertIn("248px", rules)
        self.assertIn("rgba(120, 120, 128, 0.16)", rules)
        self.assertIn("blur(2px)", rules)
        self.assertIn("16px", rules)

    def test_r1_aegis_analyze_card_and_progress_strips_typography(self):
        """Verify A.E.G.I.S analyze! card: 524x352px, rgba(0,0,0,0.15), radius 17px, centered title Work Sans 400 32px, 4 strips."""
        css_match = re.search(r"\.figma-card-aegis-analyze\s*\{([^}]+)\}", self.html)
        self.assertIsNotNone(css_match)
        rules = css_match.group(1)
        self.assertIn("524px", rules)
        self.assertIn("352px", rules)
        self.assertIn("rgba(0, 0, 0, 0.15)", rules)
        self.assertIn("17px", rules)

        # Centered Title Work Sans 400 32px
        title_match = re.search(r'<h2[^>]*style=\{\{[^}]*fontSize:\s*[\'"]32px[\'"][^}]*\}\}[^>]*>\s*A\.E\.G\.I\.S analyze!\s*</h2>', self.html)
        self.assertIsNotNone(title_match, "Centered title Work Sans 32px must exist")

        # Strip track and fill CSS
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

        # Progress strip layout: Bold label on left (Work Sans 700 20px), percentage value on right (Inter 12px)
        strip_jsx = re.search(
            r'font-work\s+font-bold\s+text-\[20px\][^>]*>\{item\.label\}</span>\s*<span[^>]*font-inter\s+text-\[12px\][^>]*>\{pct\}%</span>',
            self.html
        )
        self.assertIsNotNone(strip_jsx, "Progress strip must position bold label (Work Sans 700 20px) on left and percentage (Inter 12px) on right")

        # Default values 78%, 0%, 10%, 2%
        for val in ['78', '0', '10', '2']:
            self.assertTrue(re.search(rf':\s*{val}\b', self.html), f"Default value {val}% must exist in fallback list")

    def test_r1_sidebar_logo_hidden(self):
        """Verify sidebar logo is hidden with display: none in both CSS and inline styles."""
        self.assertIn(".figma-sidebar-logo, .figma-sidebar .sidebar-logo", self.html)
        self.assertIn("display: none !important", self.html)
        self.assertTrue(re.search(r'figma-sidebar-logo[^>]*style=\{\{\s*display:\s*[\'"]none[\'"]', self.html))

    def test_r1_card_isolation_no_leak_to_tab2(self):
        """Verify .figma-card-aegis-analyze is not inadvertently applied to Tab 2 Hardware Dosing Deck."""
        idx_tab2 = self.html.find("Peristaltic Fertilizer Dosing Deck")
        self.assertGreater(idx_tab2, 0, "Tab 2 Dosing Deck marker must exist")
        tab2_slice = self.html[idx_tab2:idx_tab2 + 400]
        self.assertNotIn("figma-card-aegis-analyze", tab2_slice, "Tab 2 must not use figma-card-aegis-analyze")
        self.assertIn("figma-card-dark", tab2_slice, "Tab 2 must use figma-card-dark")


class FigmaR2AssetsAndDualPathTest(unittest.TestCase):
    """Verification of R2 Background Image Assets, Disk Files, and Dual-Protocol Resolution."""

    def test_r2_dashboard_mountain_image_validity(self):
        """Verify server/static/images_real/dashboard_mountain_bg.png exists, valid PNG > 50KB."""
        path = IMAGES_REAL_DIR / "dashboard_mountain_bg.png"
        self.assertTrue(path.exists(), f"{path} must exist")
        self.assertGreater(path.stat().st_size, 50000, "Image must be > 50KB")
        with Image.open(path) as img:
            self.assertEqual(img.format, "PNG")
            self.assertGreaterEqual(img.width, 800)
            self.assertGreaterEqual(img.height, 600)

    def test_r2_space_image_validity(self):
        """Verify server/static/images_real/space_bg.jpg exists, valid JPEG > 50KB."""
        path = IMAGES_REAL_DIR / "space_bg.jpg"
        self.assertTrue(path.exists(), f"{path} must exist")
        self.assertGreater(path.stat().st_size, 50000, "Image must be > 50KB")
        with Image.open(path) as img:
            self.assertEqual(img.format, "JPEG")
            self.assertGreaterEqual(img.width, 500)
            self.assertGreaterEqual(img.height, 800)

    def test_r2_dual_path_resolver_contract(self):
        """Verify window.__AEGIS_ASSET_RESOLVER__ properly produces relative paths on file: and /static/ on http:."""
        html = INDEX_PATH.read_text(encoding="utf-8")
        self.assertIn("window.__AEGIS_IS_FILE__ = window.location.protocol === 'file:'", html)
        self.assertIn("window.__AEGIS_ASSET_BASE__ = window.__AEGIS_IS_FILE__ ? '.' : '/static'", html)
        self.assertIn("dashboard_mountain_bg.png", html)
        self.assertIn("space_bg.jpg", html)


class FigmaR3CosmicAndAtmosphericEffectsTest(unittest.TestCase):
    """Verification of R3 Reduced Star Density, Meteors, Drifting Clouds, and Nebula Parallax."""

    @classmethod
    def setUpClass(cls):
        cls.html = INDEX_PATH.read_text(encoding="utf-8")

    def test_r3_reduced_star_particles_density(self):
        """Verify 3 star layers have reduced count: 280 far, 150 mid, 60 near (490 total, < 500)."""
        far_match = re.search(r"createStarLayer\((\d+)[^)]*#93c5fd", self.html)
        mid_match = re.search(r"createStarLayer\((\d+)[^)]*#e0e7ff", self.html)
        near_match = re.search(r"createStarLayer\((\d+)[^)]*#ffffff", self.html)

        self.assertIsNotNone(far_match)
        self.assertIsNotNone(mid_match)
        self.assertIsNotNone(near_match)

        far_count = int(far_match.group(1))
        mid_count = int(mid_match.group(1))
        near_count = int(near_match.group(1))
        total_stars = far_count + mid_count + near_count

        self.assertEqual(far_count, 280)
        self.assertEqual(mid_count, 150)
        self.assertEqual(near_count, 60)
        self.assertEqual(total_stars, 490)
        self.assertLess(total_stars, 600, "Star particle density must be reduced from 1200+ down to subtle twinkle (<600)")

    def test_r3_shooting_stars_meteors_dashboard_rare_and_home_disabled(self):
        """Verify meteors: rare on Dashboard (random < 0.002), completely hidden on Home (meteorGroup.visible = false)."""
        dash_meteor = re.search(r"if\s*\(\s*viewRef\.current\s*===\s*[\'\"`]dashboard[\'\"`]\s*\)\s*\{[\s\S]*?meteorGroup\.visible\s*=\s*true[\s\S]*?Math\.random\(\)\s*<\s*0\.002", self.html)
        self.assertIsNotNone(dash_meteor, "Dashboard must show rare meteors at long intervals (0.002)")

        home_meteor = re.search(r"else\s*\{[\s\S]*?meteorGroup\.visible\s*=\s*false", self.html)
        self.assertIsNotNone(home_meteor, "Home view must completely disable meteors (meteorGroup.visible = false)")

    def test_r3_drifting_clouds_non_blocking_interactions(self):
        """Verify drifting background clouds have pointer-events: none and keyframe animations."""
        cloud_css = re.search(r"\.dashboard-clouds-layer\s*\{([^}]+)\}", self.html)
        self.assertIsNotNone(cloud_css)
        self.assertIn("pointer-events: none", cloud_css.group(1))

        # Check keyframe animations
        self.assertIn("@keyframes cloudDriftSlow", self.html)
        self.assertIn("@keyframes cloudDriftFast", self.html)

        # Check JSX rendering under dashboard view
        cloud_jsx = re.search(r'currentView\s*===\s*[\'"]dashboard[\'"]\s*&&\s*\(\s*<div\s+className=["\']dashboard-clouds-layer["\']', self.html)
        self.assertIsNotNone(cloud_jsx, "Dashboard drifting clouds must be rendered when currentView === 'dashboard'")

    def test_r3_home_space_nebula_mouse_parallax(self):
        """Verify stationary space nebula on Home view with pointer-events: none and smooth mouse parallax."""
        nebula_css = re.search(r"\.home-space-nebula\s*\{([^}]+)\}", self.html)
        self.assertIsNotNone(nebula_css)
        self.assertIn("pointer-events: none", nebula_css.group(1))

        # Check JSX rendering under home view
        nebula_jsx = re.search(r'currentView\s*===\s*[\'"]home[\'"]\s*&&\s*\(\s*<div\s+ref=\{nebulaRef\}\s+className=["\']home-space-nebula["\']', self.html)
        self.assertIsNotNone(nebula_jsx, "Home space nebula must be rendered when currentView === 'home'")

        # Check parallax transform update
        self.assertIn("nebulaRef.current.style.transform = `translate3d(${targetX * 28}px, ${targetY * 20}px, 0)`", self.html)


if __name__ == "__main__":
    unittest.main(verbosity=2)
