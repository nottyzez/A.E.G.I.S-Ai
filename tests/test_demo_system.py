"""
test_demo_system.py — Automated Test Suite for Single-Box Presentation Machine
Tests the Two-Tier Dosing Engine, REST API Command Queue, Hardware Status Reporting,
and Safety Guardrail Lockouts.
"""

import sys
import asyncio
from pathlib import Path

# Ensure project root & server are in path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "server"))

from main import (
    health,
    get_dashboard_root,
    receive_sensor_telemetry,
    post_dashboard_command,
    get_pending_command,
    update_hardware_status,
    get_hardware_status,
    post_cam_command,
    get_pending_cam_command,
    get_calibration,
    set_calibration,
    calculate_calibration,
)
from dosing_engine import dosing_engine


# ------------------------------------------------------------------------------
# 1. Server Health & Root Static Serving Tests
# ------------------------------------------------------------------------------
def test_server_health():
    res = health()
    assert res["status"] == "ok"
    assert "classes" in res


def test_presentation_dashboard_endpoint():
    res = get_dashboard_root()
    # Should return FileResponse
    assert hasattr(res, "path") or isinstance(res, dict)


# ------------------------------------------------------------------------------
# 2. Two-Factor Precision Dosing Engine Unit Tests
# ------------------------------------------------------------------------------
def test_dosing_fresh_water_tier1():
    """Fresh water (EC < 0.9) must trigger baseline lifting with equal 33.3% ratios."""
    res = dosing_engine.compute_dosing(
        ec=0.35,
        ph=6.80,
        temp=26.0,
        ai_class="Control",
        ai_stage="HEALTHY_NORMAL"
    )
    assert res["safety_status"] == "NORMAL"
    assert res["tier1_status"] == "FRESH_WATER_DETECTED"
    # All three fertilizer pumps must run to raise baseline EC
    plan = res["dosing_plan"]
    assert plan["pump1_ms"] > 3000
    assert plan["pump2_ms"] > 3000
    assert plan["pump3_ms"] > 3000
    assert plan["total_volume_ml"] > 0
    # Ratios must be equal 33.3%
    assert abs(res["ratios"]["r1_pct"] - 33.3) <= 0.1
    assert abs(res["ratios"]["r2_pct"] - 33.3) <= 0.1
    assert abs(res["ratios"]["r3_pct"] - 33.3) <= 0.1


def test_dosing_nitrogen_deficiency_tier2():
    """Deficiency -N with confirmed stage must allocate 55% share to Pump 1."""
    res = dosing_engine.compute_dosing(
        ec=1.85,
        ph=6.20,
        temp=26.0,
        ai_class="-N",
        ai_stage="SYMPTOMATIC_DEFICIENCY_CONFIRMED"
    )
    plan = res["dosing_plan"]
    assert res["safety_status"] == "NORMAL"
    assert res["ratios"]["r1_pct"] == 55.0
    assert res["ratios"]["r2_pct"] == 22.5
    assert res["ratios"]["r3_pct"] == 22.5
    assert plan["pump1_ms"] > plan["pump2_ms"]
    assert plan["pump1_ms"] > plan["pump3_ms"]
    assert "ไนโตรเจน" in res["tier2_reason"] or "-N" in res["tier2_reason"]


def test_dosing_phosphorus_deficiency_tier2():
    """Deficiency -P with Early Warning must allocate 45% share to Pump 2."""
    res = dosing_engine.compute_dosing(
        ec=1.85,
        ph=6.20,
        temp=26.0,
        ai_class="-P",
        ai_stage="PRE_SYMPTOMATIC_EARLY_WARNING"
    )
    plan = res["dosing_plan"]
    assert res["safety_status"] == "NORMAL"
    assert res["ratios"]["r2_pct"] == 45.0
    assert res["ratios"]["r1_pct"] == 27.5
    assert res["ratios"]["r3_pct"] == 27.5
    assert plan["pump2_ms"] > plan["pump1_ms"]
    assert plan["pump2_ms"] > plan["pump3_ms"]


def test_dosing_potassium_deficiency_tier2():
    """Deficiency -K with confirmed stage must allocate 55% share to Pump 3."""
    res = dosing_engine.compute_dosing(
        ec=1.85,
        ph=6.20,
        temp=26.0,
        ai_class="-K",
        ai_stage="SYMPTOMATIC_DEFICIENCY_CONFIRMED"
    )
    plan = res["dosing_plan"]
    assert res["safety_status"] == "NORMAL"
    assert res["ratios"]["r3_pct"] == 55.0
    assert res["ratios"]["r1_pct"] == 22.5
    assert res["ratios"]["r2_pct"] == 22.5
    assert plan["pump3_ms"] > plan["pump1_ms"]
    assert plan["pump3_ms"] > plan["pump2_ms"]


def test_priming_delay_compensation():
    """Verify that pump runtime includes priming offset delay (t_prime)."""
    res = dosing_engine.compute_dosing(
        ec=1.20,
        ph=6.50,
        temp=26.0,
        ai_class="Control"
    )
    prime_ms = res["priming_delay_ms"]
    assert prime_ms == 2000  # Default 2.0s
    vol1 = res["volumes_ml"]["pump1_ml"]
    expected_t1 = int(round(prime_ms + (vol1 / res["flow_rate_ml_s"]) * 1000))
    assert res["dosing_plan"]["pump1_ms"] == min(expected_t1, 25000)


def test_calibration_api_and_wizard():
    """Verify calibration get, update, and wizard flow rate calculation."""
    # 1. Update calibration via API
    set_res = set_calibration({
        "target_ec": 1.90,
        "tank_volume_liters": 25.0,
        "pump_flow_rate_ml_s": 1.6,
        "priming_delay_s": 2.5
    })
    assert set_res["status"] == "ok"
    assert set_res["calibration"]["target_ec"] == 1.90
    assert set_res["calibration"]["pump_flow_rate_ml_s"] == 1.6

    # 2. Get calibration
    get_res = get_calibration()
    assert get_res["tank_volume_liters"] == 25.0
    assert get_res["priming_delay_s"] == 2.5

    # 3. Calibration Wizard calculation: 12ml in 10s with 2s prime -> Q = 12 / 8 = 1.5 ml/s
    calc_res = calculate_calibration({
        "collected_ml": 12.0,
        "test_duration_s": 10.0,
        "observed_prime_s": 2.0
    })
    assert calc_res["status"] == "success"
    assert calc_res["calculated_flow_rate_ml_s"] == 1.5
    assert calc_res["priming_delay_s"] == 2.0

    # Reset back to default
    set_calibration({
        "target_ec": 1.85,
        "tank_volume_liters": 23.3,
        "pump_flow_rate_ml_s": 1.5,
        "priming_delay_s": 2.0
    })


def test_dosing_high_ec_hazard_lockout():
    """EC > 3.2 must trigger high EC lockout with 0ms across all pumps."""
    res = dosing_engine.compute_dosing(
        ec=3.65,
        ph=6.0,
        temp=26.0,
        ai_class="-N"
    )
    assert res["safety_status"] == "LOCKED_OUT"
    assert res["tier1_status"] == "HIGH_EC_LOCKOUT"
    plan = res["dosing_plan"]
    assert plan["pump1_ms"] == 0
    assert plan["pump2_ms"] == 0
    assert plan["pump3_ms"] == 0


def test_dosing_low_ph_acid_lockout():
    """pH <= 4.2 must trigger acid shock lockout with 0ms across all pumps."""
    res = dosing_engine.compute_dosing(
        ec=1.80,
        ph=3.50,
        temp=26.0,
        ai_class="Control"
    )
    assert res["safety_status"] == "LOCKED_OUT"
    assert res["tier1_status"] == "LOW_PH_LOCKOUT"
    plan = res["dosing_plan"]
    assert plan["pump1_ms"] == 0
    assert plan["pump2_ms"] == 0
    assert plan["pump3_ms"] == 0


# ------------------------------------------------------------------------------
# 3. REST API Command & Status Queue Integration Tests
# ------------------------------------------------------------------------------
def test_dashboard_command_queue_and_pop():
    # 1. Post START_CYCLE command from dashboard
    post_res = post_dashboard_command({"command": "START_CYCLE"})
    assert post_res["status"] == "ok"
    assert post_res["queued_command"]["command"] == "START_CYCLE"

    # 2. ESP32 polls and pops the command
    get_res = get_pending_command()
    assert get_res["command"] == "START_CYCLE"

    # 3. Subsequent poll must return IDLE (command popped)
    subsequent_res = get_pending_command()
    assert subsequent_res["command"] == "IDLE"


def test_esp32_status_update_and_query():
    # ESP32 updates status to Phase 1: SAMPLING_IN
    post_res = update_hardware_status({
        "phase": "1_SAMPLING_IN",
        "phase_id": 1,
        "ec": 1.72,
        "ph": 6.35,
        "temp": 26.8
    })
    assert post_res["status"] == "ok"

    # Dashboard polls status
    status = get_hardware_status()
    assert status["phase"] == "1_SAMPLING_IN"
    assert status["phase_id"] == 1
    assert status["ec"] == 1.72


def test_telemetry_sensor_evaluation():
    # ESP32 sends measurement cup telemetry
    data = receive_sensor_telemetry({
        "device_id": "esp32-s3-main",
        "ec": 0.45,
        "ph": 6.70,
        "temp": 26.2
    })
    assert "dosing_plan" in data
    assert data["tier1_status"] == "FRESH_WATER_DETECTED"
    assert data["dosing_plan"]["pump1_ms"] > 0


def test_camera_capture_command_queue():
    # Dashboard queues CAPTURE
    post_res = post_cam_command({"command": "CAPTURE"})
    assert post_res["status"] == "ok"
    assert post_res["queued_command"]["command"] == "CAPTURE"

    # ESP32-CAM polls command
    pop_res = get_pending_cam_command()
    assert pop_res["command"] == "CAPTURE"

    # Next poll should be IDLE
    pop_idle = get_pending_cam_command()
    assert pop_idle["command"] == "IDLE"


if __name__ == "__main__":
    print("Running Presentation Unit Tests...")
    test_server_health()
    print("  ✓ test_server_health passed")
    test_presentation_dashboard_endpoint()
    print("  ✓ test_presentation_dashboard_endpoint passed")
    test_dosing_fresh_water_tier1()
    print("  ✓ test_dosing_fresh_water_tier1 passed")
    test_dosing_nitrogen_deficiency_tier2()
    print("  ✓ test_dosing_nitrogen_deficiency_tier2 passed")
    test_dosing_phosphorus_deficiency_tier2()
    print("  ✓ test_dosing_phosphorus_deficiency_tier2 passed")
    test_dosing_potassium_deficiency_tier2()
    print("  ✓ test_dosing_potassium_deficiency_tier2 passed")
    test_dosing_high_ec_hazard_lockout()
    print("  ✓ test_dosing_high_ec_hazard_lockout passed")
    test_dosing_low_ph_acid_lockout()
    print("  ✓ test_dosing_low_ph_acid_lockout passed")
    test_dashboard_command_queue_and_pop()
    print("  ✓ test_dashboard_command_queue_and_pop passed")
    test_esp32_status_update_and_query()
    print("  ✓ test_esp32_status_update_and_query passed")
    test_telemetry_sensor_evaluation()
    print("  ✓ test_telemetry_sensor_evaluation passed")
    test_priming_delay_compensation()
    print("  ✓ test_priming_delay_compensation passed")
    test_calibration_api_and_wizard()
    print("  ✓ test_calibration_api_and_wizard passed")
    test_camera_capture_command_queue()
    print("  ✓ test_camera_capture_command_queue passed")
    print("\n🎉 ALL 14 TESTS PASSED SUCCESSFULLY!")
