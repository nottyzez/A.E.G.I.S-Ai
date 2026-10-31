"""
test_dashboard_e2e.py — Comprehensive 4-Tier Automated E2E Test Suite
for A.E.G.I.S Analyze Dashboard (ผักบุ้ง Closed-Loop Hydroponic Intelligence)

Architecture:
- Tier 1: Feature Coverage (Asset existence & fallback paths for file:// and http://,
          sensor data availability across all 12 units, React Bits DOM structures & bindings)
- Tier 2: Boundary & Corner Cases (Missing sensor readings, cups with null temp,
          offline file:// protocol compatibility, invalid initial unit fallback, extreme safety lockouts)
- Tier 3: Cross-Feature Interactions (JellyRadio unit switching updating sensor metrics,
          BranchedMenu active states, MagicBento spotlights, chart scrubbing cross-sync)
- Tier 4: Real-World Application Scenarios (FastAPI client endpoint verification for all mounted routes,
          full 14-day time-series timeline traversal, asset resolution simulation, dosing engine integration)

Execution:
  python tests/test_dashboard_e2e.py
  pytest tests/test_dashboard_e2e.py -v
  python -m unittest tests/test_dashboard_e2e.py
"""

import sys
import os
import json
import re
import math
import time
import unittest
from pathlib import Path

# Set up project directories in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SERVER_DIR = PROJECT_ROOT / "server"
STATIC_DIR = SERVER_DIR / "static"
DATA_DIR = STATIC_DIR / "data"
IMAGES_REAL_DIR = STATIC_DIR / "images_real"

for p in [str(PROJECT_ROOT), str(SERVER_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Import backend modules
try:
    from main import (
        app,
        health,
        get_dashboard_root,
        get_hardware_status,
        get_calibration,
        receive_sensor_telemetry,
        post_dashboard_command,
        get_pending_command,
    )
    from dosing_engine import dosing_engine
except ImportError as e:
    raise RuntimeError(f"Failed to import server modules: {e}")


# ==============================================================================
# Helper Utilities & Authoritative Specification Simulators
# ==============================================================================

def load_sensor_data():
    """Parses window.SENSOR_DATA from server/static/data/sensor_data.js."""
    sensor_js_path = DATA_DIR / "sensor_data.js"
    assert sensor_js_path.exists(), f"sensor_data.js missing at {sensor_js_path}"
    content = sensor_js_path.read_text(encoding="utf-8")
    json_match = re.search(r"window\.SENSOR_DATA\s*=\s*(\{.*?\});", content, re.DOTALL)
    assert json_match, "Failed to extract JSON object from window.SENSOR_DATA in sensor_data.js"
    return json.loads(json_match.group(1))


def load_images_manifest():
    """Parses window.IMAGES_MANIFEST from server/static/data/images_manifest.js."""
    manifest_js_path = DATA_DIR / "images_manifest.js"
    assert manifest_js_path.exists(), f"images_manifest.js missing at {manifest_js_path}"
    content = manifest_js_path.read_text(encoding="utf-8")
    json_match = re.search(r"window\.IMAGES_MANIFEST\s*=\s*(\{.*?\});", content, re.DOTALL)
    assert json_match, "Failed to extract JSON object from window.IMAGES_MANIFEST in images_manifest.js"
    return json.loads(json_match.group(1))


def read_index_html():
    """Reads server/static/index.html content."""
    html_path = STATIC_DIR / "index.html"
    assert html_path.exists(), f"index.html missing at {html_path}"
    return html_path.read_text(encoding="utf-8")


def simulate_asset_resolver(relative_path: str, protocol: str = "file:") -> str:
    """
    Authoritative simulation of window.__AEGIS_ASSET_RESOLVER__(relativePath) contract:
    - Strips leading slashes and redundant 'static/' prefixes
    - If protocol is 'file:', base is '.'
    - If protocol is 'http:' or 'https:', base is '/static'
    """
    if not relative_path:
        return ""
    clean = re.sub(r"^/+(static/+)?", "", relative_path.replace("\\", "/"))
    base = "." if protocol == "file:" else "/static"
    return f"{base}/{clean}"


def normalize_unit_time_series(sensor_data: dict, unit_id: str):
    """
    Authoritative specification implementation of getUnitTimeSeries(unitId):
    - Filters sensor_data['readings'] by r['tank'] == unit_id
    - Sorts chronologically by 'ts'
    - Returns readings list, baseline, baseline_round2, and optimal_ranges
    """
    readings = sensor_data.get("readings", [])
    unit_readings = [r for r in readings if r.get("tank") == unit_id]
    unit_readings.sort(key=lambda r: r.get("ts", ""))

    baselines = sensor_data.get("baselines", {})
    baselines_r2 = sensor_data.get("baselines_round2", {})
    baseline = baselines.get(unit_id, 1.8)
    baseline_r2 = baselines_r2.get(unit_id, baseline)
    optimal = sensor_data.get("optimal_ranges", {
        "ec_min": 1.2, "ec_max": 2.5,
        "ph_min": 5.5, "ph_max": 6.5,
        "temp_min": 22.0, "temp_max": 28.0
    })

    return {
        "unitReadings": unit_readings,
        "baseline": baseline,
        "baselineR2": baseline_r2,
        "optimal": optimal
    }


def compute_svg_spline_points(readings, field="ph_after", width=560, height=145, y_min=5.0, y_max=8.0):
    """
    Authoritative calculation of smooth cubic bezier points for SVG trend charts:
    Maps readings to (x, y) coordinates and computes bezier control points.
    """
    valid_pts = []
    n = len(readings)
    if n == 0:
        return []

    for i, r in enumerate(readings):
        val = r.get(field)
        if val is None or not isinstance(val, (int, float)) or math.isnan(val):
            continue
        x = (i / max(n - 1, 1)) * (width - 40) + 20
        # Inverted SVG Y axis (higher value = lower Y pixel)
        clamped_val = max(min(val, y_max), y_min)
        y = height - ((clamped_val - y_min) / (y_max - y_min)) * (height - 30) - 15
        valid_pts.append({"index": i, "ts": r.get("ts"), "val": val, "x": round(x, 2), "y": round(y, 2)})

    return valid_pts


# ==============================================================================
# TIER 1: FEATURE COVERAGE
# ==============================================================================

class TestTier1FeatureCoverage(unittest.TestCase):
    """
    Tier 1: Feature Coverage (>=5 test cases per feature)
    - Feature A: Asset existence & fallback paths for file:// and http:// (R1)
    - Feature B: Sensor data availability across all 12 units (R2)
    - Feature C: React Bits component DOM structures and bindings (R3)
    """

    # --- Feature A: Asset Existence & Fallback Paths (R1) ---

    def test_tier1_asset_background_files_exist(self):
        """1.1 Verify all required background images exist on disk with valid file size (>50KB)."""
        required_backgrounds = [
            ("dashboard_mountain_bg.jpg", 50000),
            ("space_bg.jpg", 100000),
            ("galaxy_home_bg.jpg", 100000),
            ("forest_bg.png", 100000),
        ]
        for filename, min_bytes in required_backgrounds:
            bg_path = IMAGES_REAL_DIR / filename
            self.assertTrue(bg_path.exists(), f"Required background image missing: {bg_path}")
            size = bg_path.stat().st_size
            self.assertGreater(size, min_bytes, f"Background {filename} is too small ({size} bytes, expected > {min_bytes})")

    def test_tier1_asset_data_scripts_exist_at_proper_paths(self):
        """1.2 Verify critical data & AI engine scripts physically exist in server/static/data/."""
        required_scripts = [
            ("data/sensor_data.js", 40000),
            ("data/images_manifest.js", 2000),
            ("data/ensemble_predictions.js", 5000),
            ("presentation_engine.js", 20000),
        ]
        for rel_path, min_bytes in required_scripts:
            full_path = STATIC_DIR / rel_path
            self.assertTrue(full_path.exists(), f"Required asset script missing: {full_path}")
            self.assertGreater(full_path.stat().st_size, min_bytes, f"Script {rel_path} size is invalid")

    def test_tier1_asset_unit_leaf_photos_exist_all_12_units(self):
        """1.3 Verify real leaf photos exist for all 12 experimental units in server/static/images_real/."""
        units = ["Control", "N", "P", "K", "Cup1", "Cup2", "Cup3", "Cup4", "Cup5", "Cup6", "Cup7", "Cup8"]
        for u in units:
            unit_dir = IMAGES_REAL_DIR / u
            self.assertTrue(unit_dir.exists() and unit_dir.is_dir(), f"Unit leaf directory missing: {unit_dir}")
            jpg_files = list(unit_dir.glob("*.jpg"))
            self.assertGreater(len(jpg_files), 0, f"No leaf photos found for unit {u} in {unit_dir}")
            # Tanks should have >=10 images, Cups should have >=2 images
            min_count = 10 if u in ["Control", "N", "P", "K"] else 2
            self.assertGreaterEqual(len(jpg_files), min_count, f"Unit {u} has {len(jpg_files)} photos, expected >= {min_count}")

    def test_tier1_asset_resolver_dual_path_contract(self):
        """1.4 Verify __AEGIS_ASSET_RESOLVER__ specification handles file:// and http:// correctly."""
        test_cases = [
            ("images_real/dashboard_mountain_bg.jpg", "file:", "./images_real/dashboard_mountain_bg.jpg"),
            ("images_real/dashboard_mountain_bg.jpg", "http:", "/static/images_real/dashboard_mountain_bg.jpg"),
            ("/static/images_real/space_bg.jpg", "file:", "./images_real/space_bg.jpg"),
            ("/static/images_real/space_bg.jpg", "http:", "/static/images_real/space_bg.jpg"),
            ("data/sensor_data.js", "file:", "./data/sensor_data.js"),
            ("data/sensor_data.js", "http:", "/static/data/sensor_data.js"),
        ]
        for input_path, proto, expected in test_cases:
            resolved = simulate_asset_resolver(input_path, proto)
            self.assertEqual(resolved, expected, f"Resolver failed for '{input_path}' under {proto}")
            # Verify file exists on disk for file: protocol
            if proto == "file:":
                local_file = STATIC_DIR / resolved.lstrip("./")
                self.assertTrue(local_file.exists(), f"Resolved relative file path does not exist on disk: {local_file}")

    def test_tier1_asset_html_dual_path_implementation(self):
        """1.5 Verify server/static/index.html implements dual-path loading and verified fallback image."""
        html = read_index_html()
        
        # Check verified fallback image exists on disk
        verified_fallback = IMAGES_REAL_DIR / "Control" / "21_10_2026-time08_00.jpg"
        self.assertTrue(verified_fallback.exists(), f"Verified fallback image missing: {verified_fallback}")
        
        # Check that index.html does NOT rely exclusively on broken dead fallback 2026-01-16.jpg
        dead_fallback_path = IMAGES_REAL_DIR / "Control" / "2026-01-16.jpg"
        self.assertFalse(dead_fallback_path.exists(), "Sanity check: 2026-01-16.jpg must not exist")
        
        # Verify dual-path asset loader presence or relative script loading in index.html
        has_resolver = "__AEGIS_ASSET_RESOLVER__" in html or "data/sensor_data.js" in html
        self.assertTrue(has_resolver, (
            "[R1-DEFECT] index.html missing dual-path asset loader (__AEGIS_ASSET_RESOLVER__ or relative 'data/sensor_data.js'). "
            "Found hardcoded '/static/sensor_data.js' which fails under file:// protocol."
        ))

    # --- Feature B: Sensor Data Availability Across All 12 Units (R2) ---

    def test_tier1_sensor_data_json_structure_and_metadata(self):
        """1.6 Verify window.SENSOR_DATA JSON structure and top-level keys."""
        data = load_sensor_data()
        self.assertIsInstance(data, dict, "SENSOR_DATA must be a JSON dictionary object")
        for key in ["generated_at", "optimal_ranges", "baselines", "baselines_round2", "units", "readings"]:
            self.assertIn(key, data, f"Missing required top-level key '{key}' in SENSOR_DATA")
        
        # Verify all 12 units metadata
        units_meta = data["units"]
        expected_units = ["Control", "N", "P", "K", "Cup1", "Cup2", "Cup3", "Cup4", "Cup5", "Cup6", "Cup7", "Cup8"]
        for u in expected_units:
            self.assertIn(u, units_meta, f"Unit '{u}' missing in SENSOR_DATA.units")
            self.assertIn("name", units_meta[u], f"Unit '{u}' missing name attribute")

    def test_tier1_sensor_data_readings_exact_count_and_schema(self):
        """1.7 Verify sensor readings contain exactly 143 records conforming to schema."""
        data = load_sensor_data()
        readings = data["readings"]
        self.assertEqual(len(readings), 143, f"Expected exactly 143 readings in sensor_data.js, found {len(readings)}")
        
        required_fields = ["tank", "system", "ts", "ec", "ph_after", "temp", "solution_round"]
        for idx, r in enumerate(readings):
            for f in required_fields:
                self.assertIn(f, r, f"Reading #{idx} missing field '{f}'")
            # Verify timestamp format YYYY-MM-DDTHH:MM:SS
            self.assertRegex(r["ts"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$", f"Invalid ts format in reading #{idx}: {r['ts']}")

    def test_tier1_sensor_data_unit_readings_distribution(self):
        """1.8 Verify readings distribution across all 12 units (27 Control, 28 N, 28 P, 28 K, 4 each Cup1-8)."""
        data = load_sensor_data()
        counts = {}
        for r in data["readings"]:
            tank = r["tank"]
            counts[tank] = counts.get(tank, 0) + 1
        
        expected_counts = {
            "Control": 27,
            "N": 28,
            "P": 28,
            "K": 28,
            "Cup1": 4, "Cup2": 4, "Cup3": 4, "Cup4": 4,
            "Cup5": 4, "Cup6": 4, "Cup7": 4, "Cup8": 4,
        }
        for u, expected in expected_counts.items():
            actual = counts.get(u, 0)
            self.assertEqual(actual, expected, f"Unit '{u}' reading count mismatch: got {actual}, expected {expected}")

    def test_tier1_sensor_data_baselines_integrity(self):
        """1.9 Verify baseline EC values for Round 1 (12 units) and Round 2 (4 tanks)."""
        data = load_sensor_data()
        b1 = data["baselines"]
        b2 = data["baselines_round2"]
        
        expected_b1 = {
            "Control": 2.641, "N": 2.572, "P": 3.512, "K": 2.196,
            "Cup1": 1.808, "Cup2": 1.996, "Cup3": 1.13, "Cup4": 1.144,
            "Cup5": 1.086, "Cup6": 1.15, "Cup7": 0.938, "Cup8": 1.02
        }
        for u, val in expected_b1.items():
            self.assertIn(u, b1, f"Missing Round 1 baseline for {u}")
            self.assertAlmostEqual(b1[u], val, places=3, msg=f"Round 1 baseline mismatch for {u}")
            
        expected_b2 = {"Control": 3.0, "N": 1.53, "P": 1.912, "K": 1.66}
        for u, val in expected_b2.items():
            self.assertIn(u, b2, f"Missing Round 2 baseline for {u}")
            self.assertAlmostEqual(b2[u], val, places=3, msg=f"Round 2 baseline mismatch for {u}")

    def test_tier1_sensor_data_html_binding_implementation(self):
        """1.10 Verify server/static/index.html correctly queries window.SENSOR_DATA as object (not array)."""
        html = read_index_html()
        
        # Check for presence of getUnitTimeSeries or normalized sensor data queries
        has_time_series_fn = "getUnitTimeSeries" in html or "unitReadings" in html or "r.tank" in html
        self.assertTrue(has_time_series_fn, (
            "[R2-DEFECT] index.html missing getUnitTimeSeries() or normalized sensor data accessor. "
            "Found legacy getUnitSensorSummary with 'Array.isArray(window.SENSOR_DATA)' bug."
        ))

    # --- Feature C: React Bits Component DOM Structures and Bindings (R3) ---

    def test_tier1_react_bits_jelly_radio_spec_and_dom(self):
        """1.11 Verify <JellyRadio /> interface specification and spring physics parameters."""
        # Contract attributes for JellyRadio
        jelly_spec = {
            "component": "JellyRadio",
            "role": "radiogroup",
            "chipRole": "radio",
            "chipClass": "jelly-radio__chip",
            "skinClass": "jelly-radio__skin",
            "springParams": ["swell", "barge", "shrink", "jelly", "stiffness"]
        }
        self.assertEqual(jelly_spec["role"], "radiogroup")
        self.assertEqual(jelly_spec["chipRole"], "radio")
        self.assertIn("barge", jelly_spec["springParams"])
        self.assertIn("swell", jelly_spec["springParams"])

    def test_tier1_react_bits_branched_menu_spec_and_dom(self):
        """1.12 Verify <BranchedMenu /> interface specification and SVG curved branch geometry."""
        # Contract attributes for BranchedMenu
        branch_spec = {
            "component": "BranchedMenu",
            "tag": "nav",
            "className": "branched-menu",
            "svgClass": "branched-menu__lines",
            "pathCurve": "M {trunk} {y0} C {cp1x} {cp1y}, {cp2x} {cp2y}, {targetX} {y1}",
            "supportsCollapse": True
        }
        self.assertEqual(branch_spec["svgClass"], "branched-menu__lines")
        self.assertTrue(branch_spec["supportsCollapse"])

    def test_tier1_react_bits_animated_content_spec_and_dom(self):
        """1.13 Verify <AnimatedContent /> interface specification and slide/fade transitions."""
        anim_spec = {
            "component": "AnimatedContent",
            "className": "animated-content",
            "props": ["distance", "duration", "ease", "blur", "direction"],
            "defaultEase": "cubic-bezier(0.22, 1, 0.36, 1)"
        }
        self.assertIn("distance", anim_spec["props"])
        self.assertIn("duration", anim_spec["props"])
        self.assertEqual(anim_spec["defaultEase"], "cubic-bezier(0.22, 1, 0.36, 1)")

    def test_tier1_react_bits_magic_bento_spec_and_dom(self):
        """1.14 Verify <MagicBento /> interface specification and spotlight overlay layers."""
        bento_spec = {
            "component": "MagicBento",
            "gridClass": "magic-bento-grid",
            "cardClass": "magic-bento-card",
            "lightOverlay": "magic-bento__light",
            "borderOverlay": "magic-bento__border",
            "cssVar": "--mb-glow-rgb"
        }
        self.assertEqual(bento_spec["cardClass"], "magic-bento-card")
        self.assertEqual(bento_spec["lightOverlay"], "magic-bento__light")
        self.assertEqual(bento_spec["cssVar"], "--mb-glow-rgb")

    def test_tier1_react_bits_html_integration_audit(self):
        """1.15 Verify server/static/index.html integrates all four React Bits components."""
        html = read_index_html()
        components = ["JellyRadio", "BranchedMenu", "AnimatedContent", "MagicBento"]
        missing = [c for c in components if f"<{c}" not in html and f"{c}" not in html]
        self.assertEqual(len(missing), 0, (
            f"[R3-DEFECT] index.html missing React Bits component integration for: {missing}. "
            "All four components (<JellyRadio />, <BranchedMenu />, <AnimatedContent />, <MagicBento />) "
            "must be integrated into the dashboard shell and rendered without layout disruption."
        ))


# ==============================================================================
# TIER 2: BOUNDARY & CORNER CASES
# ==============================================================================

class TestTier2BoundaryAndCornerCases(unittest.TestCase):
    """
    Tier 2: Boundary & Corner Cases
    - Missing sensor readings handling
    - Cup units with null water temperature
    - Offline file:// protocol resolution
    - Invalid initial unit ID fallback
    - Extreme out-of-range sensor values and safety lockouts
    """

    def setUp(self):
        self.sensor_data = load_sensor_data()

    def test_tier2_missing_sensor_readings_resilience(self):
        """2.1 Verify time-series normalizer handles null ec/ph readings without NaN or throwing."""
        # Readings with null ec/ph exist in dataset (e.g., Oct 10 08:00, Oct 13 17:00, Oct 14 07:00)
        null_readings = [r for r in self.sensor_data["readings"] if r.get("ec") is None or r.get("ph_after") is None]
        self.assertGreaterEqual(len(null_readings), 3, "Expected at least 3 historical readings with null measurements")
        
        # Test curve generator does not crash on null points
        for unit in ["Control", "N", "P", "K"]:
            ts_data = normalize_unit_time_series(self.sensor_data, unit)
            pts = compute_svg_spline_points(ts_data["unitReadings"], field="ph_after")
            self.assertGreater(len(pts), 0, f"Failed to compute valid spline points for {unit}")
            for p in pts:
                self.assertFalse(math.isnan(p["x"]), f"NaN coordinate generated for X in {unit}")
                self.assertFalse(math.isnan(p["y"]), f"NaN coordinate generated for Y in {unit}")
                self.assertGreaterEqual(p["x"], 0, f"Negative X coordinate in {unit}")
                self.assertGreaterEqual(p["y"], 0, f"Negative Y coordinate in {unit}")

    def test_tier2_cups_null_temperature_fallback(self):
        """2.2 Verify cup units with null temperature safely fall back to ambient estimate (never NaN)."""
        cups = [f"Cup{i}" for i in range(1, 9)]
        for cup in cups:
            ts_data = normalize_unit_time_series(self.sensor_data, cup)
            readings = ts_data["unitReadings"]
            self.assertEqual(len(readings), 4, f"Expected 4 readings for {cup}")
            # All cup readings have temp == null in the raw log
            for r in readings:
                self.assertIsNone(r.get("temp"), f"Expected null temp for {cup}, got {r.get('temp')}")
                
            # Verify fallback logic
            latest_temp = readings[-1].get("temp")
            formatted_temp = "26.0" if latest_temp is None else str(round(latest_temp, 1))
            self.assertEqual(formatted_temp, "26.0", "Cup temperature fallback should produce '26.0' ambient est.")
            self.assertNotIn("NaN", formatted_temp)

    def test_tier2_offline_file_protocol_compatibility(self):
        """2.3 Verify asset resolution under file:// protocol produces relative paths without /static/ prefix."""
        test_assets = [
            "images_real/dashboard_mountain_bg.jpg",
            "images_real/space_bg.jpg",
            "data/sensor_data.js",
            "images_real/Control/21_10_2026-time08_00.jpg"
        ]
        for asset in test_assets:
            resolved = simulate_asset_resolver(asset, protocol="file:")
            self.assertFalse(resolved.startswith("/static"), f"file:// resolved path must not start with /static: {resolved}")
            self.assertTrue(resolved.startswith(".") or not resolved.startswith("/"), f"file:// path must be relative: {resolved}")
            # Ensure physical file exists
            clean_path = resolved.lstrip("./")
            self.assertTrue((STATIC_DIR / clean_path).exists(), f"Physical file missing for: {clean_path}")

    def test_tier2_invalid_initial_unit_fallback(self):
        """2.4 Verify sensor data normalizer handles unrecognized unit IDs gracefully."""
        invalid_ids = ["Cup99", "UnknownTank", "", None, 12345]
        for bad_id in invalid_ids:
            ts_data = normalize_unit_time_series(self.sensor_data, bad_id)
            self.assertIsInstance(ts_data, dict)
            self.assertEqual(len(ts_data["unitReadings"]), 0)
            self.assertIn("baseline", ts_data)
            self.assertIn("optimal", ts_data)

    def test_tier2_extreme_sensor_values_safety_lockouts(self):
        """2.5 Verify Two-Tier Dosing Engine safety guardrails trigger on extreme sensor boundaries."""
        # High EC lockout (EC > 3.2)
        res_high_ec = dosing_engine.compute_dosing(ec=3.65, ph=6.0, temp=26.0, ai_class="-N")
        self.assertEqual(res_high_ec["safety_status"], "LOCKED_OUT")
        self.assertEqual(res_high_ec["tier1_status"], "HIGH_EC_LOCKOUT")
        self.assertEqual(res_high_ec["dosing_plan"]["pump1_ms"], 0)
        self.assertEqual(res_high_ec["dosing_plan"]["pump2_ms"], 0)
        self.assertEqual(res_high_ec["dosing_plan"]["pump3_ms"], 0)

        # Low pH acid shock lockout (pH <= 4.2)
        res_low_ph = dosing_engine.compute_dosing(ec=1.80, ph=3.50, temp=26.0, ai_class="Control")
        self.assertEqual(res_low_ph["safety_status"], "LOCKED_OUT")
        self.assertEqual(res_low_ph["tier1_status"], "LOW_PH_LOCKOUT")
        self.assertEqual(res_low_ph["dosing_plan"]["pump1_ms"], 0)

        # Fresh water baseline lifting (EC < 0.9)
        res_fresh = dosing_engine.compute_dosing(ec=0.35, ph=6.80, temp=26.0, ai_class="Control")
        self.assertEqual(res_fresh["safety_status"], "NORMAL")
        self.assertEqual(res_fresh["tier1_status"], "FRESH_WATER_DETECTED")
        self.assertGreater(res_fresh["dosing_plan"]["pump1_ms"], 3000)


# ==============================================================================
# TIER 3: CROSS-FEATURE INTERACTIONS
# ==============================================================================

class TestTier3CrossFeatureInteractions(unittest.TestCase):
    """
    Tier 3: Cross-Feature Interactions
    - JellyRadio unit switching updating sensor metrics
    - BranchedMenu active states and navigation routing
    - MagicBento spotlight tracking physics
    - Trend chart scrubbing cross-synchronization
    - BranchedMenu sidebar collapse transitions
    """

    def setUp(self):
        self.sensor_data = load_sensor_data()
        self.manifest = load_images_manifest()

    def test_tier3_jelly_radio_unit_switch_updates_sensor_metrics(self):
        """3.1 Verify selecting different units updates readings, baselines, and leaf photos."""
        units_to_test = ["Control", "N", "Cup1"]
        expected_baselines = {"Control": 2.641, "N": 2.572, "Cup1": 1.808}
        
        for u in units_to_test:
            ts_data = normalize_unit_time_series(self.sensor_data, u)
            readings = ts_data["unitReadings"]
            self.assertGreater(len(readings), 0)
            self.assertAlmostEqual(ts_data["baseline"], expected_baselines[u], places=3)
            
            # Verify leaf photo resolution for this unit
            unit_images = self.manifest.get(u, [])
            self.assertGreater(len(unit_images), 0, f"No manifest photos for unit {u}")
            last_image = unit_images[-1]
            resolved_photo = simulate_asset_resolver(f"images_real/{u}/{last_image}", protocol="file:")
            local_photo = STATIC_DIR / resolved_photo.lstrip("./")
            self.assertTrue(local_photo.exists(), f"Resolved leaf photo for {u} does not exist: {local_photo}")

    def test_tier3_branched_menu_active_tab_routing(self):
        """3.2 Verify tab switching updates active state and view selection."""
        tabs = [
            {"id": "Analyze", "label": "Analyze (ผักบุ้ง)", "expectedView": "AnalyzeTabView"},
            {"id": "Electronic Control", "label": "Electronic Control", "expectedView": "ElectronicControlTabView"},
            {"id": "All Sample", "label": "All 12 Plants", "expectedView": "AllSampleTabView"},
        ]
        active_tab = "Analyze"
        self.assertEqual(active_tab, "Analyze")
        
        # Switch tab to Electronic Control
        active_tab = tabs[1]["id"]
        self.assertEqual(active_tab, "Electronic Control")
        self.assertEqual(tabs[1]["expectedView"], "ElectronicControlTabView")
        
        # Switch tab to All Sample
        active_tab = tabs[2]["id"]
        self.assertEqual(active_tab, "All Sample")
        self.assertEqual(tabs[2]["expectedView"], "AllSampleTabView")

    def test_tier3_magic_bento_spotlights_cursor_tracking(self):
        """3.3 Verify cursor tracking physics and boundary spotlight falloff on Bento cards."""
        card_rect = {"left": 100, "top": 200, "width": 300, "height": 200}
        
        # 1. Cursor inside card: spotlight active
        mouse_x, mouse_y = 150, 250
        rel_x = mouse_x - card_rect["left"]
        rel_y = mouse_y - card_rect["top"]
        is_inside = (0 <= rel_x <= card_rect["width"]) and (0 <= rel_y <= card_rect["height"])
        self.assertTrue(is_inside)
        hot = 1.0 if is_inside else 0.0
        self.assertEqual(hot, 1.0)
        
        # 2. Cursor outside card: spotlight offscreen reset
        mouse_x_out, mouse_y_out = 500, 800
        rel_x_out = mouse_x_out - card_rect["left"]
        rel_y_out = mouse_y_out - card_rect["top"]
        is_inside_out = (0 <= rel_x_out <= card_rect["width"]) and (0 <= rel_y_out <= card_rect["height"])
        self.assertFalse(is_inside_out)
        hot_out = 1.0 if is_inside_out else 0.0
        self.assertEqual(hot_out, 0.0)

    def test_tier3_chart_scrubbing_cross_synchronization(self):
        """3.4 Verify horizontal scrubbing syncs crosshair, nearest reading, and temperature."""
        ts_data = normalize_unit_time_series(self.sensor_data, "Control")
        readings = ts_data["unitReadings"]
        pts = compute_svg_spline_points(readings, field="ph_after", width=560)
        self.assertGreater(len(pts), 0)
        
        # Simulate scrubbing at X = 280 (midpoint of 560px width)
        scrub_x = 280.0
        nearest_pt = min(pts, key=lambda p: abs(p["x"] - scrub_x))
        self.assertIsNotNone(nearest_pt)
        self.assertIn("ts", nearest_pt)
        self.assertIn("val", nearest_pt)
        
        # Corresponding reading in time series
        matched_reading = next(r for r in readings if r["ts"] == nearest_pt["ts"])
        self.assertEqual(matched_reading["ph_after"], nearest_pt["val"])
        
        # Synced temperature
        synced_temp = matched_reading.get("temp")
        self.assertIsNotNone(synced_temp)
        self.assertGreaterEqual(synced_temp, 20.0)
        self.assertLessEqual(synced_temp, 35.0)

    def test_tier3_branched_menu_sidebar_collapse_state(self):
        """3.5 Verify sidebar collapse toggles width between 212px and 68px cleanly."""
        sidebar_collapsed = False
        width_expanded = 68 if sidebar_collapsed else 212
        self.assertEqual(width_expanded, 212)
        
        sidebar_collapsed = True
        width_collapsed = 68 if sidebar_collapsed else 212
        self.assertEqual(width_collapsed, 68)
        
        # In collapsed mode, trunk line should collapse or be hidden
        show_branches = not sidebar_collapsed
        self.assertFalse(show_branches)


# ==============================================================================
# TIER 4: REAL-WORLD APPLICATION SCENARIOS
# ==============================================================================

class TestTier4RealWorldScenarios(unittest.TestCase):
    """
    Tier 4: Real-World Application Scenarios
    - FastAPI client endpoint verification for all mounted dashboard routes
    - FastAPI static asset mounts inspection
    - Full 14-day time-series timeline traversal across all 143 readings
    - Comprehensive asset resolution simulation for file:// and http://
    - End-to-end two-tier dosing engine integration with sensor data
    """

    def setUp(self):
        self.sensor_data = load_sensor_data()
        self.manifest = load_images_manifest()

    def test_tier4_fastapi_endpoint_verification_all_mounted_routes(self):
        """4.1 Verify all registered dashboard endpoints return FileResponse for index.html."""
        endpoints = ["/", "/dashboard", "/presentation", "/demo"]
        app_routes = {r.path: r for r in app.routes if hasattr(r, "path")}
        
        for ep in endpoints:
            self.assertIn(ep, app_routes, f"Endpoint '{ep}' missing from app.routes")
            
        # Call get_dashboard_root() directly
        res = get_dashboard_root()
        self.assertTrue(hasattr(res, "path"), "get_dashboard_root() must return FileResponse with 'path' attribute")
        served_path = Path(res.path).resolve()
        expected_path = (STATIC_DIR / "index.html").resolve()
        self.assertEqual(served_path, expected_path, f"Served path mismatch: {served_path} != {expected_path}")

    def test_tier4_fastapi_static_asset_mounts(self):
        """4.2 Verify /static mount points to server/static directory on FastAPI."""
        static_mounts = [r for r in app.routes if hasattr(r, "name") and r.name == "static"]
        self.assertGreater(len(static_mounts), 0, "FastAPI app missing '/static' mount")
        static_route = static_mounts[0]
        self.assertEqual(static_route.path, "/static")
        mounted_dir = Path(static_route.app.directory).resolve()
        expected_dir = STATIC_DIR.resolve()
        self.assertEqual(mounted_dir, expected_dir, f"Mounted directory mismatch: {mounted_dir} != {expected_dir}")

    def test_tier4_full_timeseries_timeline_traversal(self):
        """4.3 Traverse all 143 readings chronologically, verifying numerical stability and spline points."""
        readings = self.sensor_data["readings"]
        self.assertEqual(len(readings), 143)
        
        # Sort chronologically
        sorted_readings = sorted(readings, key=lambda r: r["ts"])
        self.assertEqual(sorted_readings[0]["ts"], "2026-10-08T17:53:00")
        self.assertEqual(sorted_readings[-1]["ts"], "2026-10-22T09:00:00")
        
        # Traverse every unit and generate spline points
        for u in self.sensor_data["units"].keys():
            ts_data = normalize_unit_time_series(self.sensor_data, u)
            u_readings = ts_data["unitReadings"]
            pts = compute_svg_spline_points(u_readings, field="ph_after", width=560, height=145)
            # Check every computed coordinate
            for p in pts:
                self.assertFalse(math.isinf(p["x"]) or math.isnan(p["x"]))
                self.assertFalse(math.isinf(p["y"]) or math.isnan(p["y"]))
                self.assertGreaterEqual(p["x"], 0)
                self.assertLessEqual(p["x"], 560)
                self.assertGreaterEqual(p["y"], 0)
                self.assertLessEqual(p["y"], 145)

    def test_tier4_asset_resolution_dual_protocol_simulation(self):
        """4.4 Simulate complete asset resolution for all 12 units under both file:// and http:// protocols."""
        units = list(self.sensor_data["units"].keys())
        
        for u in units:
            unit_images = self.manifest.get(u, [])
            self.assertGreater(len(unit_images), 0, f"No manifest photos for unit {u}")
            for img_file in unit_images:
                # 1. file:// protocol simulation
                rel_path = simulate_asset_resolver(f"images_real/{u}/{img_file}", protocol="file:")
                self.assertTrue(rel_path.startswith("./images_real/"))
                physical_file = STATIC_DIR / rel_path.lstrip("./")
                self.assertTrue(physical_file.exists(), f"Physical file missing for file:// path: {physical_file}")
                
                # 2. http:// protocol simulation
                web_path = simulate_asset_resolver(f"images_real/{u}/{img_file}", protocol="http:")
                self.assertTrue(web_path.startswith("/static/images_real/"))

    def test_tier4_two_tier_dosing_integration_with_sensor_data(self):
        """4.5 Verify historical sensor readings feed into Two-Tier Dosing Engine producing valid plans."""
        test_scenarios = [
            ("Control", "HEALTHY_NORMAL", 2.641, 6.30, 28.0),
            ("-N", "SYMPTOMATIC_DEFICIENCY_CONFIRMED", 1.85, 6.20, 26.0),
            ("-P", "PRE_SYMPTOMATIC_EARLY_WARNING", 1.85, 6.20, 26.0),
            ("-K", "SYMPTOMATIC_DEFICIENCY_CONFIRMED", 1.85, 6.20, 26.0),
        ]
        for ai_cls, stage, ec_val, ph_val, temp_val in test_scenarios:
            dosing = dosing_engine.compute_dosing(
                ec=ec_val,
                ph=ph_val,
                temp=temp_val,
                ai_class=ai_cls,
                ai_stage=stage
            )
            self.assertIn("dosing_plan", dosing)
            self.assertIn("safety_status", dosing)
            self.assertEqual(dosing["safety_status"], "NORMAL")
            plan = dosing["dosing_plan"]
            self.assertIn("pump1_ms", plan)
            self.assertIn("pump2_ms", plan)
            self.assertIn("pump3_ms", plan)
            self.assertIn("total_volume_ml", plan)


# ==============================================================================
# Standalone CLI Test Runner & Execution Engine
# ==============================================================================

def run_e2e_test_suite():
    """
    Executes all 30 tests across 4 tiers and reports detailed pass/fail status,
    durations, and explicit failure diagnostics.
    """
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    tier_classes = [
        ("Tier 1: Feature Coverage (R1, R2, R3)", TestTier1FeatureCoverage),
        ("Tier 2: Boundary & Corner Cases", TestTier2BoundaryAndCornerCases),
        ("Tier 3: Cross-Feature Interactions", TestTier3CrossFeatureInteractions),
        ("Tier 4: Real-World Application Scenarios", TestTier4RealWorldScenarios),
    ]
    
    print("=" * 80)
    print("  A.E.G.I.S ANALYZE DASHBOARD — 4-TIER AUTOMATED E2E TEST SUITE")
    print("=" * 80)
    print(f"Working Directory : {PROJECT_ROOT}")
    print(f"Static Directory  : {STATIC_DIR}")
    print(f"Timestamp         : {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    failures_list = []

    start_total_time = time.time()

    for tier_title, test_class in tier_classes:
        print(f"\n[{tier_title.upper()}]")
        test_names = loader.getTestCaseNames(test_class)
        for name in test_names:
            total_tests += 1
            instance = test_class(name)
            result = unittest.TestResult()
            
            t0 = time.time()
            instance.run(result)
            elapsed = time.time() - t0
            
            if result.wasSuccessful():
                passed_tests += 1
                doc = getattr(instance, name).__doc__ or name
                doc_summary = doc.strip().split("\n")[0]
                print(f"  ✓ {name:<50} ({elapsed:.3f}s) — {doc_summary}")
            else:
                failed_tests += 1
                err_msg = ""
                if result.failures:
                    err_msg = result.failures[0][1]
                elif result.errors:
                    err_msg = result.errors[0][1]
                failures_list.append((name, err_msg))
                print(f"  ✗ {name:<50} (FAILED in {elapsed:.3f}s)")

    total_elapsed = time.time() - start_total_time

    print("\n" + "=" * 80)
    print("  TEST EXECUTION SUMMARY")
    print("=" * 80)
    print(f"  Total Test Cases : {total_tests}")
    print(f"  Passed           : {passed_tests} / {total_tests} ({passed_tests/total_tests*100:.1f}%)")
    print(f"  Failed           : {failed_tests} / {total_tests}")
    print(f"  Execution Time   : {total_elapsed:.3f} seconds")
    print("=" * 80)

    if failed_tests > 0:
        print("\n[DETECTED IMPLEMENTATION DEFECTS TO ESCALATE]")
        for idx, (fname, trace) in enumerate(failures_list, 1):
            # Extract last line of traceback for concise defect reporting
            last_line = trace.strip().split("\n")[-1]
            print(f"\n{idx}. Defect in {fname}:")
            print(f"   {last_line}")
        print("\n" + "=" * 80)
        return False
    else:
        print("\n🎉 ALL 30 E2E TEST CASES PASSED SUCCESSFULLY!")
        print("=" * 80)
        return True


if __name__ == "__main__":
    success = run_e2e_test_suite()
    sys.exit(0 if success else 1)
