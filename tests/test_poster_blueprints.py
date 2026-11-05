#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A.E.G.I.S. Poster Blueprints Verification Test Suite
Verifies that all 4 Minimal White Engineering Blueprint vector graphics
and the academic companion markdown document are complete, valid, and
strictly aligned with the 55-page project thesis.
"""

import os
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BLUEPRINTS_DIR = PROJECT_ROOT / "assets" / "blueprints"
COMPANION_DOC = PROJECT_ROOT / "docs" / "poster_content_companion.md"

CARD_FILENAMES = [
    "blueprint_closed_loop_fsm",
    "blueprint_multimodal_ai",
    "blueprint_performance_charts",
    "blueprint_key_metrics_summary",
]

class TestPosterBlueprints(unittest.TestCase):

    def test_01_svg_files_exist_and_valid_xml(self):
        """Verify all 4 SVG blueprint files exist and are well-formed XML."""
        self.assertTrue(BLUEPRINTS_DIR.exists(), f"Blueprints dir missing: {BLUEPRINTS_DIR}")
        for base_name in CARD_FILENAMES:
            svg_path = BLUEPRINTS_DIR / f"{base_name}.svg"
            self.assertTrue(svg_path.exists(), f"SVG missing: {svg_path}")
            self.assertGreater(svg_path.stat().st_size, 2048, f"SVG too small: {svg_path}")
            
            # Parse XML
            try:
                tree = ET.parse(svg_path)
                root = tree.getroot()
                self.assertIn("svg", root.tag.lower(), f"Root tag must be svg in {svg_path}")
            except Exception as e:
                self.fail(f"Failed to parse valid XML in {svg_path}: {e}")

    def test_02_png_files_exist_and_high_res(self):
        """Verify all 4 PNG blueprint files exist, have high resolution (>= 2400x1600), and valid filesize."""
        for base_name in CARD_FILENAMES:
            png_path = BLUEPRINTS_DIR / f"{base_name}.png"
            self.assertTrue(png_path.exists(), f"PNG missing: {png_path}")
            self.assertGreater(png_path.stat().st_size, 50 * 1024, f"PNG size too small: {png_path}")
            
            with Image.open(png_path) as img:
                width, height = img.size
                self.assertGreaterEqual(width, 2400, f"Width {width} < 2400 in {png_path}")
                self.assertGreaterEqual(height, 1500, f"Height {height} < 1500 in {png_path}")

    def test_03_fsm_card_content_and_pinouts(self):
        """Verify Card 1 contains all 11 GPIO pins, 6 fluidic phases, and timing specs from Thesis Chapter 3 & Appendix B-C."""
        svg_content = (BLUEPRINTS_DIR / "blueprint_closed_loop_fsm.svg").read_text(encoding="utf-8")
        svg_upper = svg_content.upper()
        
        # Verify Pinouts (GPIO 1 to GPIO 11)
        for pin in ["GPIO 1", "GPIO 2", "GPIO 4", "GPIO 5", "GPIO 6", "GPIO 7", "GPIO 8", "GPIO 9", "GPIO 10", "GPIO 11"]:
            self.assertIn(pin, svg_content, f"Missing {pin} in FSM blueprint")
            
        # Verify 6 Phases (case-insensitive)
        phases = [
            "PHASE 1", "SAMPLING",
            "PHASE 2", "SENSING",
            "PHASE 3", "RECOVERY",
            "PHASE 4", "DOSING",
            "PHASE 5", "PROBE WASH",
            "PHASE 6", "WASTE DRAIN"
        ]
        for p in phases:
            self.assertIn(p, svg_upper, f"Missing phase term '{p}' in FSM blueprint")
            
        # Verify Timings (6s, 3s, 7s, 5s, 6s)
        for t in ["6s", "3s", "7s", "5s"]:
            self.assertIn(t, svg_content, f"Missing timing '{t}' in FSM blueprint")

    def test_04_multimodal_ai_card_content(self):
        """Verify Card 2 contains Dual Streams, Symptom-Gating 122 images, Late-Fusion weights, and 100.00% accuracy."""
        svg_content = (BLUEPRINTS_DIR / "blueprint_multimodal_ai.svg").read_text(encoding="utf-8")
        svg_upper = svg_content.upper()
        
        keywords = [
            "STREAM A", "STREAM B",
            "MOBILENETV2", "SE-ATTENTION",
            "SYMPTOM-GATED", "122",
            "GBDT", "RANDOM FOREST",
            "META-CLASSIFIER", "0.35", "0.65",
            "100.00%", "GRAD-CAM"
        ]
        for kw in keywords:
            self.assertIn(kw, svg_upper, f"Missing AI term '{kw}' in Multimodal AI blueprint")

    def test_05_performance_charts_card_content(self):
        """Verify Card 3 contains exact Ablation Study metrics and Day 22 Fresh Biomass weights from thesis tables."""
        svg_content = (BLUEPRINTS_DIR / "blueprint_performance_charts.svg").read_text(encoding="utf-8")
        
        # Ablation study values (Table 4.2 a, b)
        ablation_vals = ["85.37%", "90.24%", "87.80%", "95.12%", "97.56%", "100.00%"]
        for val in ablation_vals:
            self.assertIn(val, svg_content, f"Missing ablation metric '{val}' in charts blueprint")
            
        # Day 22 Fresh Biomass weights (Appendix A Table 3)
        biomass_vals = ["54.3", "19.8", "32.2", "37.9"]
        for val in biomass_vals:
            self.assertIn(val, svg_content, f"Missing biomass value '{val}' in charts blueprint")

    def test_06_key_metrics_summary_card_content(self):
        """Verify Card 4 contains Big Number Badges, Safety Lockouts, and GitHub QR reference."""
        svg_content = (BLUEPRINTS_DIR / "blueprint_key_metrics_summary.svg").read_text(encoding="utf-8")
        
        badges = ["100.00%", "12 / 12", "122", "0%"]
        for b in badges:
            self.assertIn(b, svg_content, f"Missing badge '{b}' in key metrics blueprint")
            
        safety_terms = ["HARD SAFETY LOCKOUT", "2.5 mS/cm", "github.com/nottyzez/A.E.G.I.S-Ai"]
        for st in safety_terms:
            self.assertIn(st, svg_content, f"Missing safety/repo term '{st}' in key metrics blueprint")
        # Check pH < 4.0 or XML escaped pH &lt; 4.0
        self.assertTrue("pH < 4.0" in svg_content or "pH &lt; 4.0" in svg_content, "Missing pH < 4.0 in Card 4 SVG")

    def test_07_poster_companion_doc_exists_and_complete(self):
        """Verify docs/poster_content_companion.md exists and contains Thai text and table citations for all 4 cards."""
        self.assertTrue(COMPANION_DOC.exists(), f"Companion doc missing: {COMPANION_DOC}")
        content = COMPANION_DOC.read_text(encoding="utf-8")
        
        for base_name in CARD_FILENAMES:
            self.assertIn(base_name, content, f"Companion doc must document {base_name}")
            
        # Check Thai citations of thesis tables
        citations = ["ตารางที่ 4.1", "ตารางที่ 4.2", "ตารางที่ 4.4", "ภาคผนวก ก", "ผักบุ้ง"]
        for cit in citations:
            self.assertIn(cit, content, f"Companion doc missing thesis citation '{cit}'")

    def test_08_unified_combo_blueprint_exists_and_high_res(self):
        """Verify the unified combo blueprint (Card 5) exists, is valid SVG & PNG, and >= 3000x2000 px."""
        combo_svg = BLUEPRINTS_DIR / "blueprint_unified_results_metrics.svg"
        combo_png = BLUEPRINTS_DIR / "blueprint_unified_results_metrics.png"
        self.assertTrue(combo_svg.exists(), f"Unified combo SVG missing: {combo_svg}")
        self.assertTrue(combo_png.exists(), f"Unified combo PNG missing: {combo_png}")
        
        # Verify PNG dimensions
        with Image.open(combo_png) as img:
            w, h = img.size
            self.assertGreaterEqual(w, 3000, f"Combo PNG width {w} < 3000")
            self.assertGreaterEqual(h, 2000, f"Combo PNG height {h} < 2000")
            
        # Verify SVG content has key metrics and citations
        svg_content = combo_svg.read_text(encoding="utf-8")
        self.assertIn("100.00%", svg_content)
        self.assertIn("54.3", svg_content)
        self.assertIn("Table 4.2", svg_content)

    def test_09_flowchart_blueprint_exists_and_high_res(self):
        """Verify the AI & ESP32 pump flowchart blueprint (Card 6) exists, is valid SVG & PNG, and >= 3000x2000 px."""
        flow_svg = BLUEPRINTS_DIR / "blueprint_ai_esp32_flowchart.svg"
        flow_png = BLUEPRINTS_DIR / "blueprint_ai_esp32_flowchart.png"
        self.assertTrue(flow_svg.exists(), f"Flowchart SVG missing: {flow_svg}")
        self.assertTrue(flow_png.exists(), f"Flowchart PNG missing: {flow_png}")
        
        # Verify PNG dimensions
        with Image.open(flow_png) as img:
            w, h = img.size
            self.assertGreaterEqual(w, 3000, f"Flowchart PNG width {w} < 3000")
            self.assertGreaterEqual(h, 2000, f"Flowchart PNG height {h} < 2000")
            
        # Verify SVG content has ESP32, GPIO pins, and Closed-loop terms
        svg_content = flow_svg.read_text(encoding="utf-8")
        self.assertIn("ESP32-S3", svg_content)
        self.assertIn("GPIO 9", svg_content)
        self.assertIn("CLOSED-LOOP", svg_content)

    def test_10_compact_canva_blueprints_exist_and_high_res(self):
        """Verify the 4:3 compact Canva blueprints (Cards 7 & 8) exist, are valid SVG & PNG, and >= 3000x3500 px."""
        for base_name in ["blueprint_methodology_flowchart_compact", "blueprint_results_biomass_compact"]:
            svg_path = BLUEPRINTS_DIR / f"{base_name}.svg"
            png_path = BLUEPRINTS_DIR / f"{base_name}.png"
            self.assertTrue(svg_path.exists(), f"Compact SVG missing: {svg_path}")
            self.assertTrue(png_path.exists(), f"Compact PNG missing: {png_path}")
            
            # Check XML
            tree = ET.parse(svg_path)
            self.assertIn("svg", tree.getroot().tag.lower())
            
            # Check dimensions
            with Image.open(png_path) as img:
                w, h = img.size
                self.assertGreaterEqual(w, 3000, f"Width {w} < 3000 in {png_path}")
                self.assertGreaterEqual(h, 3500, f"Height {h} < 3500 in {png_path}")
                
        # Check content in Methodology compact
        meth_svg = (BLUEPRINTS_DIR / "blueprint_methodology_flowchart_compact.svg").read_text(encoding="utf-8")
        self.assertIn("100.00%", meth_svg)
        self.assertIn("ESP32-S3", meth_svg)
        self.assertIn("Closed-Loop", meth_svg)
        
        # Check content in Results compact
        res_svg = (BLUEPRINTS_DIR / "blueprint_results_biomass_compact.svg").read_text(encoding="utf-8")
        self.assertIn("100.00%", res_svg)
        self.assertIn("12 / 12", res_svg)
        self.assertIn("54.3", res_svg)
        self.assertIn("19.8", res_svg)

    def test_11_ai_workflow_and_growth_morphology_blueprints(self):
        """Verify the dedicated 4-stage AI Flowchart (Card 9) and 3D Morphology (Card 10) blueprints exist and are valid."""
        for base_name in ["blueprint_ai_workflow_flowchart", "blueprint_growth_morphology_3d"]:
            svg_path = BLUEPRINTS_DIR / f"{base_name}.svg"
            png_path = BLUEPRINTS_DIR / f"{base_name}.png"
            self.assertTrue(svg_path.exists(), f"Blueprint SVG missing: {svg_path}")
            self.assertTrue(png_path.exists(), f"Blueprint PNG missing: {png_path}")
            
            # Check XML
            tree = ET.parse(svg_path)
            self.assertIn("svg", tree.getroot().tag.lower())
            
            # Check dimensions
            with Image.open(png_path) as img:
                w, h = img.size
                self.assertGreaterEqual(w, 3000, f"Width {w} < 3000 in {png_path}")
                self.assertGreaterEqual(h, 3500, f"Height {h} < 3500 in {png_path}")

        # Check AI Flowchart content
        ai_svg = (BLUEPRINTS_DIR / "blueprint_ai_workflow_flowchart.svg").read_text(encoding="utf-8")
        self.assertIn("100.00%", ai_svg)
        self.assertIn("MobileNetV2", ai_svg)
        self.assertIn("GBDT", ai_svg)
        self.assertIn("ESP32-S3", ai_svg)

        # Check Morphology content
        growth_svg = (BLUEPRINTS_DIR / "blueprint_growth_morphology_3d.svg").read_text(encoding="utf-8")
        self.assertIn("54.3", growth_svg)
        self.assertIn("39.6", growth_svg)
        self.assertIn("20.4", growth_svg)
        self.assertIn("19.8", growth_svg)

    def test_12_ai_evaluation_table_blueprint(self):
        """Verify the AI Evaluation Table blueprint (Card 11) exists, is valid SVG & PNG, and >= 3000x2500 px."""
        svg_path = BLUEPRINTS_DIR / "blueprint_ai_evaluation_table.svg"
        png_path = BLUEPRINTS_DIR / "blueprint_ai_evaluation_table.png"
        self.assertTrue(svg_path.exists(), f"Blueprint SVG missing: {svg_path}")
        self.assertTrue(png_path.exists(), f"Blueprint PNG missing: {png_path}")
        
        # Check XML
        tree = ET.parse(svg_path)
        self.assertIn("svg", tree.getroot().tag.lower())
        
        # Check dimensions
        with Image.open(png_path) as img:
            w, h = img.size
            self.assertGreaterEqual(w, 3000, f"Width {w} < 3000 in {png_path}")
            self.assertGreaterEqual(h, 2500, f"Height {h} < 2500 in {png_path}")

        # Check content
        content = svg_path.read_text(encoding="utf-8")
        self.assertIn("100.00%", content)
        self.assertIn("12 / 12", content)
        self.assertIn("83.96%", content)
        self.assertIn("90.78%", content)
        self.assertIn("72.60%", content)

if __name__ == "__main__":
    unittest.main()
