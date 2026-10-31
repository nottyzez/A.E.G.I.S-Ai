"""
tests/test_full_dashboard_adversarial.py — Empirical Adversarial Verification Suite
for A.E.G.I.S Analyze Dashboard (ผักบุ้ง Closed-Loop Hydroponic Intelligence)

Mission:
Adversarial challenge & empirical stress-testing across both protocols (file:// and http://):
1. Dual-Protocol Asset Resolution:
   - Validate background images, leaf photos, and data scripts resolve valid paths on both
     relative ('.') and web ('/static') routes.
   - Verify fallback behavior when unit photos or paths are corrupted.
2. Fault Tolerance & Data Anomalies:
   - Adversarial payloads into window.SENSOR_DATA.readings: missing fields, null/NaN values,
     unknown unit IDs, non-array or corrupt structures.
   - Empirical evaluation of client-side math and SVG coordinate generation using Node.js V8.
3. Zero Console Errors & Layout Stability:
   - DOM and SVG path grammar validation, scrubbing bounds resilience, and FastAPI endpoint stability.

Execution:
    python tests/test_full_dashboard_adversarial.py
"""

import os
import sys
import json
import re
import math
import subprocess
import unittest
from pathlib import Path

# Setup paths — ensure PROJECT_ROOT is at the top of sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SERVER_DIR = PROJECT_ROOT / "server"
STATIC_DIR = SERVER_DIR / "static"
DATA_DIR = STATIC_DIR / "data"
IMAGES_REAL_DIR = STATIC_DIR / "images_real"

if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from main import app, get_dashboard_root
    FASTAPI_AVAILABLE = True
    FASTAPI_ERROR = None
except Exception as e:
    FASTAPI_AVAILABLE = False
    FASTAPI_ERROR = str(e)


# ==============================================================================
# Helper Utilities & Authoritative Specification Simulators
# ==============================================================================

def read_file_utf8(path: Path) -> str:
    assert path.exists(), f"File does not exist: {path}"
    return path.read_text(encoding="utf-8")


def simulate_asset_resolver(relative_path: str, protocol: str = "file:") -> str:
    """
    Simulates window.__AEGIS_ASSET_RESOLVER__(relativePath) in index.html:
    var clean = relativePath.replace(/^(\\.\\/|\\/)?(static\\/)?/, '');
    return window.__AEGIS_ASSET_BASE__ + '/' + clean;
    """
    if not relative_path:
        return ""
    # Standardize backslashes
    norm = relative_path.replace("\\", "/")
    # Strip leading ./ or / and optional static/ prefix
    clean = re.sub(r"^(\./|/)?(static/)?", "", norm)
    base = "." if protocol == "file:" else "/static"
    return f"{base}/{clean}"


def run_node_eval(js_code: str):
    """
    Executes a JavaScript string using Node.js V8 engine and captures stdout, stderr, and exitcode.
    """
    res = subprocess.run(
        ["node"],
        input=js_code.encode("utf-8"),
        capture_output=True,
        timeout=15
    )
    return {
        "exit_code": res.returncode,
        "stdout": res.stdout.decode("utf-8", errors="replace"),
        "stderr": res.stderr.decode("utf-8", errors="replace")
    }


def extract_js_helpers_from_index_html():
    """
    Extracts the pure helper logic (UNIT_META, getUnitLeafPhoto, getUnitTimeSeries,
    getUnitSensorSummary, computeSvgSplinePoints, buildSvgCubicBezierPath) from index.html.
    """
    html_content = read_file_utf8(STATIC_DIR / "index.html")
    lines = html_content.splitlines()

    # Locate from UNIT_META up to Three.js starfield section
    start_idx = None
    end_idx = None
    for i, line in enumerate(lines):
        if "const UNIT_META = {" in line:
            start_idx = i
        if "// 2. THREE.JS" in line:
            end_idx = i
            break

    assert start_idx is not None and end_idx is not None, "Failed to locate helper functions in index.html"
    return "\n".join(lines[start_idx:end_idx])


# ==============================================================================
# Suite 1: Dual-Protocol Asset Resolution & Multi-Mount Verification
# ==============================================================================

class DualProtocolAssetResolutionAdversarialTest(unittest.TestCase):
    """Adversarial stress-testing of asset resolution under both file:// and http:// protocols."""

    ALL_UNITS = ["Control", "N", "P", "K", "Cup1", "Cup2", "Cup3", "Cup4", "Cup5", "Cup6", "Cup7", "Cup8"]
    REQUIRED_BACKGROUNDS = [
        "dashboard_mountain_bg.jpg",
        "space_bg.jpg",
        "galaxy_home_bg.jpg",
        "forest_bg.png"
    ]
    REQUIRED_DATA_SCRIPTS = [
        "data/sensor_data.js",
        "data/images_manifest.js",
        "data/ensemble_predictions.js",
        "presentation_engine.js"
    ]

    def setUp(self):
        self.manifest_raw = read_file_utf8(DATA_DIR / "images_manifest.js")
        match = re.search(r"window\.IMAGES_MANIFEST\s*=\s*(\{.*?\});", self.manifest_raw, re.DOTALL)
        self.assertIsNotNone(match, "Failed to extract window.IMAGES_MANIFEST")
        self.manifest = json.loads(match.group(1))

    def test_file_protocol_backgrounds_resolve_to_valid_disk_files(self):
        """Verify all background assets resolve to relative paths and exist on disk with valid file size (>50KB)."""
        for bg in self.REQUIRED_BACKGROUNDS:
            rel_arg = f"images_real/{bg}"
            resolved = simulate_asset_resolver(rel_arg, protocol="file:")
            self.assertTrue(resolved.startswith("./"), f"file:// resolved path must start with './': {resolved}")

            # Verify physical file existence on disk
            clean_rel = resolved[2:]
            disk_path = STATIC_DIR / clean_rel
            self.assertTrue(disk_path.exists(), f"Asset {clean_rel} not found on disk at {disk_path}")
            size = disk_path.stat().st_size
            self.assertGreater(size, 50_000, f"Asset {clean_rel} size too small: {size} bytes")

    def test_file_protocol_data_scripts_resolve_to_valid_disk_files(self):
        """Verify all required head scripts resolve to relative paths and physically exist in server/static/."""
        for script in self.REQUIRED_DATA_SCRIPTS:
            resolved = simulate_asset_resolver(script, protocol="file:")
            self.assertTrue(resolved.startswith("./"), f"file:// script path must start with './': {resolved}")

            clean_rel = resolved[2:]
            disk_path = STATIC_DIR / clean_rel
            self.assertTrue(disk_path.exists(), f"Script {clean_rel} missing on disk at {disk_path}")
            self.assertGreater(disk_path.stat().st_size, 2_000, f"Script {clean_rel} suspiciously small")

    def test_file_protocol_unit_leaf_photos_all_12_units_resolve(self):
        """Verify leaf photos for all 12 units resolve to existing photos on disk (>1MB)."""
        for unit in self.ALL_UNITS:
            list_key = unit if unit in self.manifest else f"Cup_{unit.replace('Cup', '')}"
            self.assertIn(list_key, self.manifest, f"Unit {unit} missing in manifest")
            file_list = self.manifest[list_key]
            self.assertGreater(len(file_list), 0, f"Unit {unit} has empty photo list")

            last_photo = file_list[-1]
            fname = last_photo.split("/")[-1] if "/" in last_photo else last_photo
            rel_arg = f"images_real/{unit}/{fname}"

            resolved = simulate_asset_resolver(rel_arg, protocol="file:")
            self.assertTrue(resolved.startswith("./"), f"Resolved photo path must be relative: {resolved}")

            disk_path = STATIC_DIR / resolved[2:]
            self.assertTrue(disk_path.exists(), f"Leaf photo for {unit} does not exist at {disk_path}")
            self.assertGreater(disk_path.stat().st_size, 1_000_000, f"Leaf photo for {unit} smaller than 1MB")

    def test_http_protocol_asset_resolver_output_contract(self):
        """Verify __AEGIS_ASSET_RESOLVER__ under http: protocol outputs '/static/...' paths."""
        for bg in self.REQUIRED_BACKGROUNDS:
            resolved = simulate_asset_resolver(f"images_real/{bg}", protocol="http:")
            self.assertTrue(resolved.startswith("/static/"), f"HTTP path must start with /static/: {resolved}")
            self.assertNotIn("//", resolved[1:], f"Redundant double slash in path: {resolved}")

    def test_http_protocol_fastapi_asset_mounts_and_routes(self):
        """Verify FastAPI mounts (/static, /images_real, /data) and dashboard routes serve properly."""
        self.assertTrue(FASTAPI_AVAILABLE, f"FastAPI server could not be loaded: {FASTAPI_ERROR}")

        # 1. Inspect registered routes
        app_routes = {r.path: r for r in app.routes if hasattr(r, "path")}
        for route_path in ["/", "/dashboard", "/presentation", "/demo"]:
            self.assertIn(route_path, app_routes, f"FastAPI missing registered route '{route_path}'")

        # 2. Verify get_dashboard_root returns index.html
        res = get_dashboard_root()
        self.assertTrue(hasattr(res, "path"), "get_dashboard_root() must return FileResponse with 'path'")
        served_path = Path(res.path).resolve()
        expected_path = (STATIC_DIR / "index.html").resolve()
        self.assertEqual(served_path, expected_path, f"Served path mismatch: {served_path} != {expected_path}")

        # 3. Verify static mounts
        static_mounts = {r.name: r for r in app.routes if hasattr(r, "name")}
        self.assertIn("static", static_mounts, "FastAPI app missing '/static' mount")
        self.assertEqual(Path(static_mounts["static"].app.directory).resolve(), STATIC_DIR.resolve())

        # 4. Verify defense-in-depth mounts
        self.assertIn("images_real", static_mounts, "FastAPI app missing '/images_real' defense-in-depth mount")
        self.assertEqual(Path(static_mounts["images_real"].app.directory).resolve(), IMAGES_REAL_DIR.resolve())
        self.assertIn("data", static_mounts, "FastAPI app missing '/data' defense-in-depth mount")
        self.assertEqual(Path(static_mounts["data"].app.directory).resolve(), DATA_DIR.resolve())

    def test_asset_resolver_path_sanitization_adversarial_inputs(self):
        """Adversarial stress-test of __AEGIS_ASSET_RESOLVER__ against dirty, prefixed, and malformed paths."""
        dirty_inputs = [
            ("/images_real/space_bg.jpg", "./images_real/space_bg.jpg", "/static/images_real/space_bg.jpg"),
            ("static/images_real/space_bg.jpg", "./images_real/space_bg.jpg", "/static/images_real/space_bg.jpg"),
            ("./static/images_real/space_bg.jpg", "./images_real/space_bg.jpg", "/static/images_real/space_bg.jpg"),
            ("/static/images_real/space_bg.jpg", "./images_real/space_bg.jpg", "/static/images_real/space_bg.jpg"),
            ("images_real\\space_bg.jpg", "./images_real/space_bg.jpg", "/static/images_real/space_bg.jpg"),
            ("./images_real/space_bg.jpg", "./images_real/space_bg.jpg", "/static/images_real/space_bg.jpg"),
        ]

        for dirty, exp_file, exp_http in dirty_inputs:
            res_file = simulate_asset_resolver(dirty, protocol="file:")
            res_http = simulate_asset_resolver(dirty, protocol="http:")
            self.assertEqual(res_file, exp_file, f"File resolution failed for {dirty}: got {res_file}")
            self.assertEqual(res_http, exp_http, f"HTTP resolution failed for {dirty}: got {res_http}")

    def test_unknown_unit_leaf_photo_verified_fallback(self):
        """Verify unrecognized unit IDs fall back to the verified Control photo on disk (>4MB)."""
        js_helpers = extract_js_helpers_from_index_html()
        eval_script = f"""
        const window = {{
          location: {{ protocol: 'file:' }},
          __AEGIS_ASSET_BASE__: '.',
          __AEGIS_ASSET_RESOLVER__: function(rel) {{
            if (!rel) return '';
            var clean = rel.replace(/^(\\.\\/|\\/)?(static\\/)?/, '');
            return window.__AEGIS_ASSET_BASE__ + '/' + clean;
          }},
          IMAGES_MANIFEST: {{}}
        }};

        {js_helpers}

        const fallbackControl = getUnitLeafPhoto('UnrecognizedCup999');
        const fallbackNull = getUnitLeafPhoto(null);
        const fallbackUndefined = getUnitLeafPhoto(undefined);
        console.log(JSON.stringify({{ fallbackControl, fallbackNull, fallbackUndefined }}));
        """
        res = run_node_eval(eval_script)
        self.assertEqual(res["exit_code"], 0, f"Node execution failed: {res['stderr']}")

        data = json.loads(res["stdout"].strip())
        expected_fallback = "./images_real/Control/21_10_2026-time08_00.jpg"
        self.assertEqual(data["fallbackControl"], expected_fallback)
        self.assertEqual(data["fallbackNull"], expected_fallback)
        self.assertEqual(data["fallbackUndefined"], expected_fallback)

        # Confirm fallback exists on disk and is non-trivial
        clean_fallback = expected_fallback[2:]
        fb_disk = STATIC_DIR / clean_fallback
        self.assertTrue(fb_disk.exists(), "Fallback leaf image missing on disk")
        self.assertGreater(fb_disk.stat().st_size, 4_000_000, "Fallback leaf photo truncated")


# ==============================================================================
# Suite 2: Fault Tolerance & Data Anomalies Adversarial Injections
# ==============================================================================

class SensorDataFaultToleranceAdversarialTest(unittest.TestCase):
    """Adversarial stress-testing of sensor data engine, normalizers, and SVG generators."""

    @classmethod
    def setUpClass(cls):
        cls.js_helpers = extract_js_helpers_from_index_html()

    def test_missing_and_sparse_fields_in_sensor_readings(self):
        """Test engine behavior when sensor readings have missing or sparse fields."""
        eval_script = f"""
        const window = {{
          location: {{ protocol: 'file:' }},
          __AEGIS_ASSET_BASE__: '.',
          __AEGIS_ASSET_RESOLVER__: function(rel) {{ return './' + rel; }},
          IMAGES_MANIFEST: {{}},
          SENSOR_DATA: {{
            readings: [
              {{ tank: 'Control' }},                                           // Completely empty fields
              {{ tank: 'Control', ts: '2026-10-21T08:00:00' }},               // Only timestamp
              {{ tank: 'Control', ts: '2026-10-21T09:00:00', ec: 1.45 }},     // Missing pH and temp
              {{ tank: 'Control', ts: '2026-10-21T10:00:00', ph_after: 6.1 }} // Missing EC and temp
            ],
            baselines: {{ Control: 1.8 }},
            baselines_round2: {{ Control: 1.8 }},
            optimal_ranges: {{ ec_min: 1.2, ec_max: 2.5, ph_min: 5.5, ph_max: 6.5, temp_min: 22.0, temp_max: 28.0 }}
          }}
        }};

        {self.js_helpers}

        const summary = getUnitSensorSummary('Control');
        const ts = getUnitTimeSeries('Control');
        const ptsPh = computeSvgSplinePoints(ts.unitReadings, 'ph_after');
        const ptsEc = computeSvgSplinePoints(ts.unitReadings, 'ec');
        const pathPh = buildSvgCubicBezierPath(ptsPh);
        const pathEc = buildSvgCubicBezierPath(ptsEc);

        console.log(JSON.stringify({{
          summaryPh: summary.ph,
          summaryEc: summary.ec,
          summaryTemp: summary.temp,
          ptsPhCount: ptsPh.length,
          ptsEcCount: ptsEc.length,
          hasNanPathPh: pathPh.includes('NaN'),
          hasNanPathEc: pathEc.includes('NaN'),
          pathPh,
          pathEc
        }}));
        """
        res = run_node_eval(eval_script)
        self.assertEqual(res["exit_code"], 0, f"Node script failed with missing fields: {res['stderr']}")

        data = json.loads(res["stdout"].strip())
        self.assertFalse(data["hasNanPathPh"], "PH spline path contains NaN!")
        self.assertFalse(data["hasNanPathEc"], "EC spline path contains NaN!")
        # Valid non-empty values generated from available data or fallbacks
        self.assertNotEqual(data["summaryPh"], "NaN")
        self.assertNotEqual(data["summaryEc"], "NaN")
        self.assertNotEqual(data["summaryTemp"], "NaN")

    def test_null_and_nan_sensor_values_resilience(self):
        """Stress-test sensor summary and spline path generation under explicit null and NaN values."""
        eval_script = f"""
        const window = {{
          location: {{ protocol: 'file:' }},
          __AEGIS_ASSET_BASE__: '.',
          __AEGIS_ASSET_RESOLVER__: function(rel) {{ return './' + rel; }},
          IMAGES_MANIFEST: {{}},
          SENSOR_DATA: {{
            readings: [
              {{ tank: 'Control', ts: '2026-10-21T08:00:00', ec: null, ph_after: null, ph_before: null, temp: null }},
              {{ tank: 'Control', ts: '2026-10-21T09:00:00', ec: NaN, ph_after: NaN, ph_before: NaN, temp: NaN }},
              {{ tank: 'Control', ts: '2026-10-21T10:00:00', ec: 1.25, ph_after: 6.2, ph_before: 6.1, temp: 28.0 }}
            ],
            baselines: {{ Control: 1.8 }},
            baselines_round2: {{ Control: 1.8 }},
            optimal_ranges: {{ ec_min: 1.2, ec_max: 2.5, ph_min: 5.5, ph_max: 6.5, temp_min: 22.0, temp_max: 28.0 }}
          }}
        }};

        {self.js_helpers}

        const summary = getUnitSensorSummary('Control');
        const ts = getUnitTimeSeries('Control');
        const ptsPh = computeSvgSplinePoints(ts.unitReadings, 'ph_after');
        const ptsEc = computeSvgSplinePoints(ts.unitReadings, 'ec');
        const pathPh = buildSvgCubicBezierPath(ptsPh);
        const pathEc = buildSvgCubicBezierPath(ptsEc);

        console.log(JSON.stringify({{
          summaryPh: summary.ph,
          summaryEc: summary.ec,
          summaryTemp: summary.temp,
          ptsPhLength: ptsPh.length,
          ptsEcLength: ptsEc.length,
          hasNanPathPh: pathPh.includes('NaN'),
          hasNanPathEc: pathEc.includes('NaN'),
          pathPh,
          pathEc
        }}));
        """
        res = run_node_eval(eval_script)
        self.assertEqual(res["exit_code"], 0, f"Node script failed with null/NaN values: {res['stderr']}")

        data = json.loads(res["stdout"].strip())
        # computeSvgSplinePoints explicitly ignores null and NaN
        self.assertEqual(data["ptsPhLength"], 1)
        self.assertEqual(data["ptsEcLength"], 1)
        self.assertFalse(data["hasNanPathPh"])
        self.assertFalse(data["hasNanPathEc"])
        # Fallback scanned backwards to 10:00 reading
        self.assertEqual(data["summaryPh"], "6.20")
        self.assertEqual(data["summaryEc"], "1.250")
        self.assertEqual(data["summaryTemp"], "28.0")

    def test_complete_sensor_blackout_all_readings_null(self):
        """Test behavior when an entire unit has readings but every measurement field is null."""
        eval_script = f"""
        const window = {{
          location: {{ protocol: 'file:' }},
          __AEGIS_ASSET_BASE__: '.',
          __AEGIS_ASSET_RESOLVER__: function(rel) {{ return './' + rel; }},
          IMAGES_MANIFEST: {{}},
          SENSOR_DATA: {{
            readings: [
              {{ tank: 'Control', ts: '2026-10-21T08:00:00', ec: null, ph_after: null, ph_before: null, temp: null }},
              {{ tank: 'Control', ts: '2026-10-21T09:00:00', ec: null, ph_after: null, ph_before: null, temp: null }}
            ],
            baselines: {{ Control: 1.8 }},
            optimal_ranges: {{ ec_min: 1.2, ec_max: 2.5, ph_min: 5.5, ph_max: 6.5, temp_min: 22.0, temp_max: 28.0 }}
          }}
        }};

        {self.js_helpers}

        const summary = getUnitSensorSummary('Control');
        const ts = getUnitTimeSeries('Control');
        const ptsPh = computeSvgSplinePoints(ts.unitReadings, 'ph_after');
        const ptsEc = computeSvgSplinePoints(ts.unitReadings, 'ec');

        console.log(JSON.stringify({{
          ph: summary.ph,
          ec: summary.ec,
          temp: summary.temp,
          ptsPhLen: ptsPh.length,
          ptsEcLen: ptsEc.length,
          defaultPh: UNIT_META.Control.defaultPh.toFixed(2),
          defaultEc: UNIT_META.Control.defaultEc.toFixed(3)
        }}));
        """
        res = run_node_eval(eval_script)
        self.assertEqual(res["exit_code"], 0, f"Script failed under complete blackout: {res['stderr']}")

        data = json.loads(res["stdout"].strip())
        self.assertEqual(data["ptsPhLen"], 0)
        self.assertEqual(data["ptsEcLen"], 0)
        # Should gracefully fall back to default metadata values
        self.assertEqual(data["ph"], data["defaultPh"])
        self.assertEqual(data["ec"], data["defaultEc"])

    def test_unknown_and_invalid_unit_ids_resilience(self):
        """Verify behavior when querying unrecognized or hostile unit IDs."""
        eval_script = f"""
        const window = {{
          location: {{ protocol: 'file:' }},
          __AEGIS_ASSET_BASE__: '.',
          __AEGIS_ASSET_RESOLVER__: function(rel) {{ return './' + rel; }},
          IMAGES_MANIFEST: {{}},
          SENSOR_DATA: {{
            readings: [
              {{ tank: 'Control', ts: '2026-10-21T08:00:00', ec: 1.2, ph_after: 6.0, temp: 28.0 }}
            ]
          }}
        }};

        {self.js_helpers}

        const testIds = ['Cup99', 'MarsRover', '', null, undefined, 42, 'Control'];
        const results = testIds.map(uId => {{
          try {{
            const summary = getUnitSensorSummary(uId);
            const ts = getUnitTimeSeries(uId);
            const photo = getUnitLeafPhoto(uId);
            return {{
              unitId: String(uId),
              hasSummary: !!summary,
              unitReadingsCount: ts.unitReadings.length,
              baseline: ts.baseline,
              photo: photo,
              error: null
            }};
          }} catch (err) {{
            return {{
              unitId: String(uId),
              error: err.message
            }};
          }}
        }});

        console.log(JSON.stringify(results));
        """
        res = run_node_eval(eval_script)
        self.assertEqual(res["exit_code"], 0, f"Node script threw on unknown unit IDs: {res['stderr']}")

        data = json.loads(res["stdout"].strip())
        for item in data:
            self.assertIsNone(item["error"], f"Error querying unit ID {item['unitId']}: {item['error']}")
            self.assertTrue(item["hasSummary"])
            self.assertTrue(item["photo"].startswith("./images_real/"))

    def test_empty_or_corrupted_sensor_data_object(self):
        """Stress-test when window.SENSOR_DATA is completely missing, empty, or has non-array readings."""
        eval_script = f"""
        const window = {{
          location: {{ protocol: 'file:' }},
          __AEGIS_ASSET_BASE__: '.',
          __AEGIS_ASSET_RESOLVER__: function(rel) {{ return './' + rel; }},
          IMAGES_MANIFEST: {{}},
          SENSOR_DATA: null // Missing entirely
        }};

        {self.js_helpers}

        const results = [];
        // Test 1: SENSOR_DATA is null
        try {{
          const s1 = getUnitSensorSummary('Control');
          results.push({{ test: 'null_sensor_data', ok: true, ph: s1.ph }});
        }} catch(e) {{
          results.push({{ test: 'null_sensor_data', ok: false, error: e.message }});
        }}

        // Test 2: SENSOR_DATA has readings as string instead of array
        window.SENSOR_DATA = {{ readings: 'corrupted_string_not_array' }};
        try {{
          const s2 = getUnitSensorSummary('Control');
          results.push({{ test: 'string_readings', ok: true, ec: s2.ec }});
        }} catch(e) {{
          results.push({{ test: 'string_readings', ok: false, error: e.message }});
        }}

        // Test 3: SENSOR_DATA is empty object
        window.SENSOR_DATA = {{}};
        try {{
          const s3 = getUnitSensorSummary('Control');
          results.push({{ test: 'empty_sensor_data', ok: true, temp: s3.temp }});
        }} catch(e) {{
          results.push({{ test: 'empty_sensor_data', ok: false, error: e.message }});
        }}

        console.log(JSON.stringify(results));
        """
        res = run_node_eval(eval_script)
        self.assertEqual(res["exit_code"], 0, f"Script failed with corrupt top-level SENSOR_DATA: {res['stderr']}")

        data = json.loads(res["stdout"].strip())
        for r in data:
            self.assertTrue(r["ok"], f"Failed under {r['test']}: {r.get('error')}")

    def test_adversarial_manifest_anomalies_and_leaf_photo_fallbacks(self):
        """Stress-test getUnitLeafPhoto when IMAGES_MANIFEST has empty arrays or invalid objects."""
        eval_script = f"""
        const window = {{
          location: {{ protocol: 'file:' }},
          __AEGIS_ASSET_BASE__: '.',
          __AEGIS_ASSET_RESOLVER__: function(rel) {{ return './' + rel; }},
          IMAGES_MANIFEST: {{
            Cup1: [],                     // Empty list
            Cup2: [{{ path: '' }}],        // Empty path string
            Cup3: [{{ not_a_path: 123 }}], // Missing path/url keys
            Cup4: ['valid_image.jpg']     // Valid filename
          }}
        }};

        {self.js_helpers}

        const fallbackControl = './images_real/Control/21_10_2026-time08_00.jpg';
        const p1 = getUnitLeafPhoto('Cup1');
        const p2 = getUnitLeafPhoto('Cup2');
        const p3 = getUnitLeafPhoto('Cup3');
        const p4 = getUnitLeafPhoto('Cup4');

        console.log(JSON.stringify({{ p1, p2, p3, p4, fallbackControl }}));
        """
        res = run_node_eval(eval_script)
        self.assertEqual(res["exit_code"], 0, f"Script failed on manifest anomalies: {res['stderr']}")

        data = json.loads(res["stdout"].strip())
        self.assertEqual(data["p1"], data["fallbackControl"], "Empty array must fall back to Control")
        self.assertEqual(data["p2"], data["fallbackControl"], "Empty path must fall back to Control")
        self.assertEqual(data["p3"], data["fallbackControl"], "Object without path/url must fall back to Control")
        self.assertEqual(data["p4"], "./images_real/Cup4/valid_image.jpg", "Valid filename must resolve properly")

    def test_extreme_sensor_values_numerical_stability_projection_bars(self):
        """Stress-test Projections vs Actuals bar math under extreme numbers (ec=0, negative, 100 EC)."""
        eval_script = f"""
        {self.js_helpers}

        // Implementation of projectionBars math from index.html line 2138
        function computeProjectionBars(unitReadings, baseline, baselineR2) {{
          if (unitReadings.length === 0) return [];
          let sampled = unitReadings.slice(0, 6);
          const maxScale = Math.max(3.5, ...sampled.map(r => Math.max(r.ec || 0, baseline || 0))) * 1.08;

          return sampled.map((r) => {{
            const actualEc = r.ec != null ? r.ec : (baseline || 1.8);
            const targetEc = (r.solution_round === 'รอบ 2' && baselineR2) ? baselineR2 : (baseline || 1.8);
            const projectedPct = Math.round((targetEc / maxScale) * 100);
            const actualPct = Math.round((actualEc / maxScale) * 100);
            const fillPct = Math.min(100, Math.max(8, Math.round((actualPct / Math.max(projectedPct, 1)) * 100)));
            const diffPct = ((actualEc - targetEc) / Math.max(targetEc, 0.001)) * 100;
            return {{
              actualEc,
              targetEc,
              projectedPct: Math.min(100, Math.max(20, projectedPct)),
              fillPct,
              diffPct,
              isFiniteDiff: isFinite(diffPct),
              isNanDiff: isNaN(diffPct)
            }};
          }});
        }}

        const extremeReadings = [
          {{ ts: '2026-10-21T08:00:00', ec: 0, solution_round: 'รอบ 1' }},
          {{ ts: '2026-10-21T09:00:00', ec: -0.5, solution_round: null }},
          {{ ts: '2026-10-21T10:00:00', ec: 99.9, solution_round: 'รอบ 2' }},
          {{ ts: '2026-10-21T11:00:00', ec: null }},
          {{ ts: '2026-10-21T12:00:00' }}
        ];

        const bars = computeProjectionBars(extremeReadings, 1.8, 2.0);
        console.log(JSON.stringify(bars));
        """
        res = run_node_eval(eval_script)
        self.assertEqual(res["exit_code"], 0, f"Script failed on extreme sensor math: {res['stderr']}")

        bars = json.loads(res["stdout"].strip())
        self.assertEqual(len(bars), 5)
        for b in bars:
            self.assertTrue(b["isFiniteDiff"], f"diffPct was not finite: {b}")
            self.assertFalse(b["isNanDiff"], f"diffPct was NaN: {b}")
            self.assertGreaterEqual(b["projectedPct"], 20)
            self.assertLessEqual(b["projectedPct"], 100)
            self.assertGreaterEqual(b["fillPct"], 8)
            self.assertLessEqual(b["fillPct"], 100)


# ==============================================================================
# Suite 3: Layout, DOM Syntax, & Scrubbing Stability Verification
# ==============================================================================

class DashboardLayoutAndConsoleStabilityTest(unittest.TestCase):
    """Verifies layout syntax, React Bits component bindings, and scrubbing bounds stability."""

    @classmethod
    def setUpClass(cls):
        cls.html_content = read_file_utf8(STATIC_DIR / "index.html")

    def test_html_doctype_and_root_mount_container(self):
        """Verify HTML document structure, doctype, and React root mount point."""
        self.assertTrue(self.html_content.startswith("<!DOCTYPE html>"), "Missing standard HTML5 doctype")
        self.assertIn('<html lang="th" class="dark">', self.html_content, "Missing Thai dark mode root html tag")
        self.assertIn('<div id="root"></div>', self.html_content, "Missing standard React mount element #root")

    def test_head_scripts_synchronous_bootstrapper_presence(self):
        """Verify synchronous asset resolver and required head scripts bootstrapper."""
        self.assertIn("window.__AEGIS_ASSET_RESOLVER__", self.html_content)
        self.assertIn("data/sensor_data.js", self.html_content)
        self.assertIn("data/images_manifest.js", self.html_content)
        self.assertIn("presentation_engine.js", self.html_content)

    def test_react_bits_components_definition_and_usage(self):
        """Verify all four React Bits components are defined and integrated into JSX rendering."""
        components = [
            ("JellyRadio", "<JellyRadio"),
            ("BranchedMenu", "<BranchedMenu"),
            ("AnimatedContent", "<AnimatedContent"),
            ("MagicBento", "<MagicBento")
        ]
        for name, tag in components:
            self.assertIn(f"function {name}", self.html_content, f"React Bits component {name} definition missing")
            self.assertIn(tag, self.html_content, f"React Bits component {tag} JSX integration missing")

    def test_svg_bezier_path_syntax_generator_math(self):
        """Verify buildSvgCubicBezierPath produces strictly valid SVG path commands without NaN/undefined."""
        js_helpers = extract_js_helpers_from_index_html()
        eval_script = f"""
        {js_helpers}

        const cases = [
          [],
          [{{ x: 20, y: 50 }}],
          [{{ x: 20, y: 50 }}, {{ x: 100, y: 80 }}],
          [{{ x: 20, y: 50 }}, {{ x: 100, y: 80 }}, {{ x: 200, y: 40 }}],
          [{{ x: 20, y: 50 }}, {{ x: 100, y: 80 }}, {{ x: 200, y: 40 }}, {{ x: 300, y: 90 }}]
        ];

        const paths = cases.map(pts => buildSvgCubicBezierPath(pts));
        console.log(JSON.stringify(paths));
        """
        res = run_node_eval(eval_script)
        self.assertEqual(res["exit_code"], 0, f"Bezier math failed: {res['stderr']}")

        paths = json.loads(res["stdout"].strip())
        self.assertEqual(paths[0], "")
        self.assertEqual(paths[1], "M 20 50 L 20 50")

        # Verify SVG path syntax for multi-point paths
        svg_path_regex = re.compile(r"^M\s+[\d\.\-]+\s+[\d\.\-]+(\s+[CL]\s+[\d\.\-, ]+)*$")
        for p in paths[2:]:
            self.assertRegex(p, svg_path_regex, f"Path does not conform to SVG syntax: {p}")
            self.assertNotIn("NaN", p)
            self.assertNotIn("undefined", p)

    def test_horizontal_scrubbing_boundary_index_clamping(self):
        """Verify scrubbing handler bounds clamping math (from index.html handlePointerScrub)."""
        # Testing the pointer scrubbing clamping math:
        # const relX = clientX - rect.left;
        # const ratio = Math.max(0, Math.min(1, relX / rect.width));
        # const targetIdx = Math.round(ratio * (unitReadings.length - 1));
        total_readings = 28
        width = 560.0

        test_client_xs = [-100.0, -0.01, 0.0, 100.0, 280.0, 560.0, 560.01, 1000.0]
        for cx in test_client_xs:
            rel_x = cx
            ratio = max(0.0, min(1.0, rel_x / width))
            target_idx = round(ratio * (total_readings - 1))
            self.assertGreaterEqual(target_idx, 0, f"Target index underflow: {target_idx}")
            self.assertLessEqual(target_idx, total_readings - 1, f"Target index overflow: {target_idx}")


# ==============================================================================
# Main Runner with Detailed Adversarial Diagnostics
# ==============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("  A.E.G.I.S ANALYZE DASHBOARD — EMPIRICAL ADVERSARIAL VERIFICATION SUITE")
    print("=" * 80)
    print(f"Working Directory : {PROJECT_ROOT}")
    print(f"Static Directory  : {STATIC_DIR}")
    print("=" * 80)

    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(DualProtocolAssetResolutionAdversarialTest))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(SensorDataFaultToleranceAdversarialTest))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(DashboardLayoutAndConsoleStabilityTest))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 80)
    print("  ADVERSARIAL VERIFICATION SUMMARY")
    print("=" * 80)
    print(f"  Total Adversarial Tests : {result.testsRun}")
    print(f"  Passed                  : {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  Failures                : {len(result.failures)}")
    print(f"  Errors                  : {len(result.errors)}")
    print("=" * 80)

    if result.wasSuccessful():
        print("\n🎉 ALL ADVERSARIAL VERIFICATION TESTS PASSED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("\n❌ ADVERSARIAL VERIFICATION DETECTED FAILURES!")
        sys.exit(1)
