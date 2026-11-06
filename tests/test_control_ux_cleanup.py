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
        self.assertGreaterEqual(
            home_body.count("<SpecularButton"),
            2,
            "Both primary Home CTAs (ENTER A.E.G.I.S ANALYZE and READ SYSTEM SPEC) must use <SpecularButton>",
        )
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
        analyze_end = self.html.index("function ElectronicControlTabView", analyze_start)
        self.assertIn("<AnimatedContent", self.html[analyze_start:analyze_end])

        vision_start = self.html.index("function VisionPanel")
        vision_end = self.html.index("function HomeView", vision_start)
        vision_body = self.html[vision_start:vision_end]
        self.assertIn("<DepthCarousel", vision_body)
        self.assertIn('tiltDirection="right"', vision_body)
        self.assertIn("<RubberSegment", vision_body)

    def test_0c_animated_content_is_real_react_bits_gsap_scrolltrigger_component(self):
        ac_start = self.html.index("const AnimatedContent =")
        ac_end = self.html.index("const MagicBento =", ac_start)
        ac_def = self.html[ac_start:ac_end]
        for token in ("ScrollTrigger.create", "gsap.timeline", "WIPES", "stagger"):
            self.assertIn(token, ac_def, f"AnimatedContent must use {token}")

    def test_0d_analyze_view_uses_count_up_animated_content_and_magic_bento(self):
        analyze_start = self.html.index("function AnalyzeTabView")
        analyze_end = self.html.index("function ElectronicControlTabView", analyze_start)
        analyze_body = self.html[analyze_start:analyze_end]
        self.assertIn("<AnimatedContent", analyze_body)
        self.assertIn("<MagicBento", analyze_body)
        self.assertGreaterEqual(
            analyze_body.count("<CountUp"),
            4,
            "AnalyzeTabView must use <CountUp /> for Temperature, PH sensor, EC sensor, and NPK % readouts",
        )

    def test_0e_control_uses_the_whole_react_bits_suite(self):
        for count, token, why in (
            (4, "<MagicBento", "every Bento section"),
            (3, "<SloshGauge", "water volume/flow rate and Stock A/B/C"),
            (2, "<RubberSegment", "the 4 sub-tabs and the AI deficiency category"),
            (5, "<CountUp", "dosing volumes, pump runtime, simulation readouts"),
            (3, "<SpecularButton", "primary CTAs"),
        ):
            self.assertGreaterEqual(
                self.control_body.count(token), count,
                f"ElectronicControlTabView must use {token} in {why} (at least {count})",
            )
        self.assertNotIn("interactive={false}", self.control_body)

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
        # GPIO 6 is Diaphragm 2 (sample return) and GPIO 7 is Diaphragm 3 (probe
        # rinse) — see firmware/esp32_main/config.example.h. The spec listed an
        # air-agitator label for R2, which is not an actuator this rig has.
        for thai_name in (
            "ดูดน้ำเข้ากระบอกตวง",
            "สูบน้ำตัวอย่างวนคืนถังปลูก",
            "ปั๊มน้ำดีล้างและแช่หัววัด",
            "โซลินอยด์วาล์วปล่อยน้ำทิ้ง",
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

    def test_5_every_bento_card_can_light_up(self):
        """A .magic-bento-card without a __light child renders no cursor spotlight."""
        missing = []
        for m in re.finditer(r'className="[^"]*\bmagic-bento-card\b[^"]*"', self.html):
            if "magic-bento__light" not in self.html[m.end():m.end() + 600]:
                missing.append(self.html[:m.start()].count("\n") + 1)
        self.assertEqual(missing, [], f"magic-bento-card lines without a __light child: {missing}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
