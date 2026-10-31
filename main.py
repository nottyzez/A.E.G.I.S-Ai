"""
Smart Plant Care - FastAPI Server (Kale NPK Classifier — Symptom-Gated Ensemble)
Model: Symptom-Gated Multimodal Stacking Ensemble (Vision Ensemble + Sensor Ensemble)
Input:  Top-down ESP32-S3 CAM image (auto-cropped via 3-Layer Illumination-Invariant + Symptom-Inclusive Mask)
        + Hydroponic Sensor features (EC, pH, temp, ec_pct_change, day_idx)
Output: 4 classes (Control | -N | -P | -K) + 3-stage diagnosis:
        HEALTHY_NORMAL | PRE_SYMPTOMATIC_EARLY_WARNING | SYMPTOMATIC_DEFICIENCY_CONFIRMED
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import numpy as np
import base64
from datetime import datetime
from pathlib import Path
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add Ai มหาปลัย/model and server to sys.path
ROOT_DIR = Path(__file__).resolve().parent
MODEL_SCRIPT_DIR = ROOT_DIR / "Ai มหาปลัย" / "model"
SERVER_DIR = ROOT_DIR / "server"
for p in [str(MODEL_SCRIPT_DIR), str(SERVER_DIR), str(ROOT_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from dosing_engine import dosing_engine

app = FastAPI(title="Kale NPK Symptom-Gated Ensemble API & Presentation Controller", version="3.1.0")

# Mount static files for Dashboard
STATIC_DIR = ROOT_DIR / "server" / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    if (STATIC_DIR / "images_real").exists():
        app.mount("/images_real", StaticFiles(directory=str(STATIC_DIR / "images_real")), name="images_real")
    if (STATIC_DIR / "data").exists():
        app.mount("/data", StaticFiles(directory=str(STATIC_DIR / "data")), name="data")

# ── State Management for Single-Box Presentation Machine ─────────────────────
PHASE_LABELS = {
    0: "STANDBY",
    1: "1. Telemetry Sampling",
    2: "2. Leaf Vision Capture",
    3: "3. Symptom-Gated Fusion",
    4: "4. Safety Interlock Check",
    5: "5. Peristaltic Dosing",
    6: "6. Mixing & Verification",
}

current_command = {"command": "IDLE", "timestamp": datetime.now().isoformat()}
current_cam_command = {"command": "IDLE", "timestamp": datetime.now().isoformat()}
current_hardware_status = {
    "phase": "STANDBY",
    "phase_id": 0,
    "ec": 1.85,
    "ph": 6.20,
    "temp": 26.5,
    "last_update": datetime.now().isoformat(),
    "dosing_plan": {"pump1_ms": 0, "pump2_ms": 0, "pump3_ms": 0, "total_volume_ml": 0},
    "ratios": {"r1_pct": 33.3, "r2_pct": 33.3, "r3_pct": 33.3},
    "volumes_ml": {"pump1_ml": 0.0, "pump2_ml": 0.0, "pump3_ml": 0.0, "total_volume_ml": 0.0},
    "ai_reason": "ระบบพร้อมทำงานในโหมดสาธิต (Standby)",
    "tier1_status": "OPTIMAL",
    "deficiency_class": "Control",
    "stage": "HEALTHY_NORMAL",
    "latest_image_url": "/static/latest_capture.jpg",
    "latest_test_file": "None",
    "calibration": dosing_engine.get_calibration(),
    "refill_status": {
        "stage": "IDLE",
        "pre_dosing_ec": 0.0,
        "post_dosing_ec": 0.0,
        "circulation_remaining_sec": 0,
    },
    "schedule": {
        "enabled": True,
        "interval_sec": 1800,
        "remaining_sec": 1420,
        "queued_during_override": False,
        "last_auto_run": datetime.now().isoformat(),
    },
    "override": {
        "active": False,
        "mode": "STANDBY",
        "label": "ซิงก์ตามตารางเวลาอัตโนมัติปกติ",
        "duration_ms": 0,
        "expires_at": None,
        "active_relays": [],
    },
    "command_log": [],
}


def append_command_log(entry_type: str, detail: str, preserve_schedule: bool = True):
    log_item = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "type": entry_type,
        "detail": detail,
        "schedule_status": (
            "AUTO CYCLE QUEUED (Hold)"
            if current_hardware_status["schedule"].get("queued_during_override")
            else ("AUTO SCHEDULE ACTIVE" if preserve_schedule else "MANUAL")
        ),
    }
    logs = current_hardware_status.get("command_log", [])
    current_hardware_status["command_log"] = [log_item] + logs[:14]


def reset_presentation_override_state():
    current_hardware_status["phase"] = "STANDBY"
    current_hardware_status["phase_id"] = 0
    current_hardware_status["schedule"] = {
        "enabled": True,
        "interval_sec": 1800,
        "remaining_sec": 1420,
        "queued_during_override": False,
        "last_auto_run": datetime.now().isoformat(),
    }
    current_hardware_status["override"] = {
        "active": False,
        "mode": "STANDBY",
        "label": "ซิงก์ตามตารางเวลาอัตโนมัติปกติ",
        "duration_ms": 0,
        "expires_at": None,
        "active_relays": [],
    }
    current_hardware_status["command_log"] = []


# ── Dedicated Test Captures Storage ──────────────────────────────────────────
TEST_CAPTURES_DIR = ROOT_DIR / "test_captures"
TEST_CAPTURES_DIR.mkdir(parents=True, exist_ok=True)


def save_incoming_test_image(img_bytes: bytes) -> str:
    """
    บันทึกภาพถ่ายทดสอบลงในโฟลเดอร์ test_captures/ แยกไว้เฉพาะสำหรับตอนทดสอบ
    พร้อมอัปเดต latest_capture.jpg สำหรับแสดงผลบน Web Dashboard
    """
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"capture_{timestamp_str}.jpg"
    test_filepath = TEST_CAPTURES_DIR / filename
    try:
        with open(test_filepath, "wb") as f:
            f.write(img_bytes)
    except Exception as e:
        logger.warning(f"Failed to save to {test_filepath}: {e}")

    try:
        with open(STATIC_DIR / "latest_capture.jpg", "wb") as f:
            f.write(img_bytes)
        current_hardware_status["latest_image_url"] = f"/static/latest_capture.jpg?t={int(datetime.now().timestamp())}"
    except Exception as img_err:
        logger.warning(f"Failed to cache latest_capture.jpg: {img_err}")

    rel_path = f"test_captures/{filename}"
    current_hardware_status["latest_test_file"] = rel_path
    logger.info(f"[TEST CAPTURE STORED] Saved to: {rel_path} ({len(img_bytes)} bytes)")
    return rel_path


# ── โหลด Symptom-Gated Ensemble Predictor ────────────────────────────────────
try:
    from predict_ensemble import HydroponicEnsemblePredictor
    predictor = HydroponicEnsemblePredictor()
    CLASSES = predictor.classes
    logger.info(f"✅ Symptom-Gated Ensemble loaded | Classes: {CLASSES}")
    DEMO_MODE = False
except Exception as e:
    logger.warning(f"⚠️  Ensemble load failed ({e}) — DEMO mode")
    predictor = None
    CLASSES = ["Control", "-N", "-P", "-K"]
    DEMO_MODE = True


# ── Rule Engine ───────────────────────────────────────────────────────────────
# วินาทีที่ pump ทำงานต่อครั้ง — ปรับตาม flow rate ของ pump จริง
PUMP_RULES = {
    "Control":    {"water_sec": 0,  "N_sec": 0,  "P_sec": 0,  "K_sec": 0},
    "healthy":    {"water_sec": 0,  "N_sec": 0,  "P_sec": 0,  "K_sec": 0},
    "-N":         {"water_sec": 5,  "N_sec": 15, "P_sec": 0,  "K_sec": 0},
    "nitrogen":   {"water_sec": 5,  "N_sec": 15, "P_sec": 0,  "K_sec": 0},
    "-P":         {"water_sec": 5,  "N_sec": 0,  "P_sec": 15, "K_sec": 0},
    "phosphorus": {"water_sec": 5,  "N_sec": 0,  "P_sec": 15, "K_sec": 0},
    "-K":         {"water_sec": 5,  "N_sec": 0,  "P_sec": 0,  "K_sec": 15},
    "potassium":  {"water_sec": 5,  "N_sec": 0,  "P_sec": 0,  "K_sec": 15},
}
LEGACY_CLASS_MAP = {
    "Control": "healthy",
    "-N":      "nitrogen",
    "-P":      "phosphorus",
    "-K":      "potassium",
}
MOISTURE_THRESHOLD = 40.0   # % — รดน้ำเพิ่มถ้าต่ำกว่านี้
WATER_LOW_SEC = 10


def run_ensemble_prediction(
    image_bytes: bytes,
    ec: float,
    ph: float,
    temp: float,
    ec_pct_change: float = 0.0,
    day_idx: int = 7,
    moisture: float = 50.0,
) -> dict:
    """
    1. Auto-crops raw top-down ESP32-S3 CAM image using 3-Layer Illumination-Invariant
       + Symptom-Inclusive Auto-Cropper (extracts canopy + up to 4 individual plant holes).
    2. Runs Symptom-Gated Vision Ensemble + Sensor Ensemble + Meta-Learner.
    3. Returns 3-stage diagnosis + pump dosing commands.
    """
    if DEMO_MODE or predictor is None:
        probs = np.random.dirichlet(np.ones(4))
        idx = int(np.argmax(probs))
        cls = CLASSES[idx]
        legacy_cls = LEGACY_CLASS_MAP.get(cls, cls)
        cmd = dict(PUMP_RULES.get(cls, PUMP_RULES["Control"]))
        current_hardware_status["deficiency_class"] = cls
        current_hardware_status["confidence"] = round(float(probs[idx]), 3)
        current_hardware_status["stage"] = "DEMO_MODE"

        dosing_res = dosing_engine.compute_dosing(
            ec=ec, ph=ph, temp=temp, ai_class=cls, ai_confidence=probs[idx], ai_stage="DEMO_MODE"
        )
        current_hardware_status["dosing_plan"] = dosing_res["dosing_plan"]

        return {
            **cmd,
            "deficiency": legacy_cls,
            "ensemble_class": cls,
            "stage": "DEMO_MODE",
            "stage_th": "โหมดจำลอง (Demo Mode)",
            "confidence": round(float(probs[idx]), 3),
            "probabilities": {c: round(float(p), 3) for c, p in zip(CLASSES, probs)},
            "dosing_plan": dosing_res["dosing_plan"],
            "two_tier_dosing": dosing_res,
            "timestamp": datetime.now().isoformat(),
            "message": f"Demo: {cls} ({probs[idx]*100:.1f}%)",
        }

    import cv2
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    img_bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img_bgr is None:
        raise ValueError("Cannot decode uploaded image bytes")

    ens_res = predictor.predict_from_topdown_and_sensor(
        img_bgr=img_bgr,
        ec=ec,
        ph=ph,
        water_temp=temp,
    )
    cls = ens_res["final_class"]
    cmd = dict(PUMP_RULES.get(cls, PUMP_RULES["healthy"]))

    if moisture < MOISTURE_THRESHOLD:
        cmd["water_sec"] = max(cmd["water_sec"], WATER_LOW_SEC)

    current_hardware_status["deficiency_class"] = cls
    current_hardware_status["confidence"] = ens_res["final_confidence"]
    current_hardware_status["stage"] = ens_res["diagnostic_stage"]

    dosing_res = dosing_engine.compute_dosing(
        ec=ec,
        ph=ph,
        temp=temp,
        ai_class=cls,
        ai_confidence=ens_res["final_confidence"],
        ai_stage=ens_res["diagnostic_stage"]
    )
    current_hardware_status["dosing_plan"] = dosing_res["dosing_plan"]

    return {
        **cmd,
        "deficiency": cls,
        "class_th": ens_res["final_class_thai"],
        "stage": ens_res["diagnostic_stage"],
        "stage_th": ens_res["diagnostic_message_thai"],
        "confidence": ens_res["final_confidence"],
        "probabilities": ens_res["fusion_probabilities"],
        "visual_leaf_status": ens_res["visual_leaf_status"],
        "water_sensor_status": ens_res["water_sensor_status"],
        "dosing_plan": dosing_res["dosing_plan"],
        "two_tier_dosing": dosing_res,
        "timestamp": datetime.now().isoformat(),
        "message": ens_res["diagnostic_message_thai"],
    }


# ── Endpoints ─────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {
        "status": "ok",
        "demo_mode": DEMO_MODE,
        "classes": CLASSES,
        "auto_crop_enabled": True,
        "cropper_pipeline": "3-Layer Illumination-Invariant (CLAHE) + Symptom-Inclusive (ExG+HSV+CIELAB) + Multi-Hole Patch",
    }


@app.post("/predict")
async def predict(
    image:         UploadFile = File(...),
    soil_moisture: float = Form(50.0),
    soil_temp:     float = Form(28.0),
    air_temp:      float = Form(30.0),
    humidity:      float = Form(70.0),
    ph:            float = Form(6.5),
    ec:            float = Form(1.2),
    ec_pct_change: float = Form(0.0),
    day_idx:       int   = Form(7),
    light_lux:     float = Form(5000.0),
    raw_n:         float = Form(0.0),
    raw_p:         float = Form(0.0),
    device_id:     str   = Form("esp32-s3-cam-001"),
):
    """
    รับ multipart/form-data: ภาพมุมสูงจาก ESP32-S3 CAM + ค่าเซนเซอร์น้ำ
    ระบบจะทำการปรับแสงอัตโนมัติ (CLAHE) + ครอปใบพืชทั้งถังและแยกหลุมปลูก (Auto-Crop)
    ก่อนส่งเข้า Symptom-Gated Ensemble และคืนผลวินิจฉัย 3 ระดับพร้อมคำสั่งปั๊มปุ๋ย
    """
    logger.info(f"[{device_id}] EC={ec} mS/cm | pH={ph} | Temp={soil_temp}°C | Day={day_idx}")
    try:
        img_bytes = await image.read()
        saved_file = save_incoming_test_image(img_bytes)

        result = run_ensemble_prediction(
            image_bytes=img_bytes,
            ec=ec,
            ph=ph,
            temp=soil_temp,
            ec_pct_change=ec_pct_change,
            day_idx=day_idx,
            moisture=soil_moisture,
        )
        result["saved_test_file"] = saved_file
        logger.info(f"[{device_id}] → {result['ensemble_class']} ({result['stage']}) | Stored: {saved_file}")
        return result
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict_b64")
async def predict_b64(payload: dict):
    """
    รับ JSON + base64 image จาก ESP32-S3 CAM
    Body: {"image_b64":"...", "ec":1.2, "ph":6.5, "soil_temp":28.0, "ec_pct_change":-5.0, "day_idx":7}
    """
    try:
        img_bytes = base64.b64decode(payload["image_b64"])
        saved_file = save_incoming_test_image(img_bytes)

        result = run_ensemble_prediction(
            image_bytes=img_bytes,
            ec=float(payload.get("ec", 1.2)),
            ph=float(payload.get("ph", 6.5)),
            temp=float(payload.get("soil_temp", payload.get("temp", 28.0))),
            ec_pct_change=float(payload.get("ec_pct_change", 0.0)),
            day_idx=int(payload.get("day_idx", 7)),
            moisture=float(payload.get("soil_moisture", 50.0)),
        )
        result["saved_test_file"] = saved_file
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
@app.get("/presentation")
@app.get("/demo")
@app.get("/dashboard")
def get_dashboard_root():
    dash_file = STATIC_DIR / "index.html"
    if dash_file.exists():
        return FileResponse(str(dash_file))
    return {"message": "AEGIS Master Web Hub is running. Visit /docs for OpenAPI specs."}


# ── Presentation Machine & Telemetry Endpoints ───────────────────────────────
@app.post("/api/sensor")
def receive_sensor_telemetry(payload: dict):
    """
    รับข้อมูลเซนเซอร์จากแก้ววัด (ESP32-S3 Main): ec, ph, temp
    ประมวลผลผ่าน Two-Tier Dosing Engine และคืนค่า dosing_plan (ms) ให้ฮาร์ดแวร์สั่งปั๊มปุ๋ย 3 สูตร
    """
    ec = float(payload.get("ec", 1.8))
    ph = float(payload.get("ph", 6.2))
    temp = float(payload.get("temp", payload.get("soil_temp", 26.5)))
    device_id = payload.get("device_id", "esp32-s3-main")

    # Evaluate via Two-Tier Engine using latest Vision/Ensemble AI diagnosis
    ai_cls = current_hardware_status.get("deficiency_class", "Control")
    ai_conf = current_hardware_status.get("confidence", 0.95)
    ai_stage = current_hardware_status.get("stage", "HEALTHY_NORMAL")

    dosing_res = dosing_engine.compute_dosing(
        ec=ec,
        ph=ph,
        temp=temp,
        ai_class=ai_cls,
        ai_confidence=ai_conf,
        ai_stage=ai_stage
    )

    # Update in-memory hardware status
    current_hardware_status["ec"] = ec
    current_hardware_status["ph"] = ph
    current_hardware_status["temp"] = temp
    current_hardware_status["last_update"] = datetime.now().isoformat()
    current_hardware_status["dosing_plan"] = dosing_res["dosing_plan"]
    current_hardware_status["ratios"] = dosing_res.get("ratios", {"r1_pct": 33.3, "r2_pct": 33.3, "r3_pct": 33.3})
    current_hardware_status["volumes_ml"] = dosing_res.get("volumes_ml", {})
    current_hardware_status["ai_reason"] = dosing_res["ai_reason"]
    current_hardware_status["tier1_status"] = dosing_res["tier1_status"]

    logger.info(f"[{device_id}] EC={ec} | pH={ph} | Dosing: P1={dosing_res['dosing_plan']['pump1_ms']}ms, P2={dosing_res['dosing_plan']['pump2_ms']}ms, P3={dosing_res['dosing_plan']['pump3_ms']}ms")
    return dosing_res


@app.post("/api/command")
def post_dashboard_command(payload: dict):
    """
    แดชบอร์ดส่งคำสั่งควบคุมแบบไม่ปิดตารางเวลาอัตโนมัติ (Non-Destructive Presentation Override):
    START_CYCLE | MANUAL_RELAY | JUMP_PHASE | MANUAL_DOSE | CANCEL_OVERRIDE | RESUME_AUTO | STOP
    """
    global current_command
    cmd = payload.get("command", "IDLE")
    relay_num = int(payload.get("relay", 1))
    duration_ms = int(payload.get("duration_ms", 2000))
    preserve_schedule = bool(payload.get("preserve_schedule", True))

    # Ensure background schedule remains enabled during presentation override
    if preserve_schedule:
        current_hardware_status["schedule"]["enabled"] = True

    cal = dosing_engine.get_calibration()
    flow_rate = max(0.1, float(cal.get("pump_flow_rate_ml_s", 1.5)))
    prime_ms = int(float(cal.get("priming_delay_s", 2.0)) * 1000)

    extra_fields = {}

    if cmd == "MANUAL_RELAY":
        active_relays = list(current_hardware_status["override"].get("active_relays", []))
        if relay_num not in active_relays:
            active_relays.append(relay_num)
        current_hardware_status["override"] = {
            "active": True,
            "mode": "MANUAL_RELAY",
            "label": f"สั่งเปิดรีเลย์ R{relay_num} ชั่วคราว ({duration_ms / 1000:.1f}s) — ตารางเวลาอัตโนมัติยังทำงานอยู่",
            "duration_ms": duration_ms,
            "expires_at": datetime.now().isoformat(),
            "active_relays": active_relays,
        }
        append_command_log("MANUAL_RELAY", f"Relay R{relay_num} ON ({duration_ms} ms)", preserve_schedule)

    elif cmd == "JUMP_PHASE":
        phase_id = int(payload.get("phase_id", 1))
        phase_id = max(1, min(6, phase_id))
        phase_title = PHASE_LABELS.get(phase_id, f"Phase {phase_id}")
        current_hardware_status["phase_id"] = phase_id
        current_hardware_status["phase"] = phase_title
        current_hardware_status["override"] = {
            "active": True,
            "mode": "JUMP_PHASE",
            "label": f"สาธิตเฟส {phase_title} ({duration_ms / 1000:.1f}s) — ตารางเวลาอัตโนมัติยังทำงานอยู่",
            "duration_ms": duration_ms,
            "expires_at": datetime.now().isoformat(),
            "active_relays": current_hardware_status["override"].get("active_relays", []),
        }
        extra_fields["phase_id"] = phase_id
        append_command_log("JUMP_PHASE", f"ข้ามไปสาธิต {phase_title}", preserve_schedule)

    elif cmd == "MANUAL_DOSE":
        vols = payload.get("volumes_ml", {})
        vol_a = max(0.0, float(vols.get("A", vols.get("pump1_ml", 0.0))))
        vol_b = max(0.0, float(vols.get("B", vols.get("pump2_ml", 0.0))))
        vol_c = max(0.0, float(vols.get("C", vols.get("pump3_ml", 0.0))))

        def calc_ms(v_ml: float) -> int:
            if v_ml <= 0.0:
                return 0
            return min(25000, int(round(prime_ms + (v_ml / flow_rate) * 1000.0)))

        dosing_ms = {
            "pump1_ms": calc_ms(vol_a),
            "pump2_ms": calc_ms(vol_b),
            "pump3_ms": calc_ms(vol_c),
            "total_volume_ml": round(vol_a + vol_b + vol_c, 2),
        }
        max_ms = max(dosing_ms["pump1_ms"], dosing_ms["pump2_ms"], dosing_ms["pump3_ms"], 1000)
        active_pumps = []
        if dosing_ms["pump1_ms"] > 0:
            active_pumps.append(5)  # Relay 5: Peristaltic 1 (Stock A / High-N, GPIO 9)
        if dosing_ms["pump2_ms"] > 0:
            active_pumps.append(6)  # Relay 6: Peristaltic 2 (Stock B / High-P, GPIO 10)
        if dosing_ms["pump3_ms"] > 0:
            active_pumps.append(7)  # Relay 7: Peristaltic 3 (Stock C / High-K, GPIO 11)

        current_hardware_status["dosing_plan"] = dosing_ms
        current_hardware_status["volumes_ml"] = {
            "pump1_ml": round(vol_a, 2),
            "pump2_ml": round(vol_b, 2),
            "pump3_ml": round(vol_c, 2),
            "total_volume_ml": round(vol_a + vol_b + vol_c, 2),
        }
        current_hardware_status["phase_id"] = 5
        current_hardware_status["phase"] = PHASE_LABELS[5]
        current_hardware_status["override"] = {
            "active": True,
            "mode": "MANUAL_DOSE",
            "label": f"สั่งฉีดปุ๋ยผักบุ้ง A:{vol_a:.1f} B:{vol_b:.1f} C:{vol_c:.1f} mL",
            "duration_ms": max_ms,
            "expires_at": datetime.now().isoformat(),
            "active_relays": active_pumps,
        }
        duration_ms = max_ms
        extra_fields["dosing_ms"] = dosing_ms
        append_command_log(
            "MANUAL_DOSE",
            f"Dose A={vol_a:.1f}mL ({dosing_ms['pump1_ms']}ms), B={vol_b:.1f}mL ({dosing_ms['pump2_ms']}ms), C={vol_c:.1f}mL ({dosing_ms['pump3_ms']}ms)",
            preserve_schedule,
        )

    elif cmd == "START_CYCLE":
        current_hardware_status["phase_id"] = 1
        current_hardware_status["phase"] = PHASE_LABELS[1]
        current_hardware_status["override"] = {
            "active": True,
            "mode": "FULL_CYCLE_DEMO",
            "label": "สั่งรันรอบสาธิต Closed-Loop 6 ขั้นตอน (ไม่ปิดตารางเวลาอัตโนมัติ)",
            "duration_ms": duration_ms,
            "expires_at": datetime.now().isoformat(),
            "active_relays": [1],  # Relay 1: Diaphragm Pump 1 (Inflow / GPIO 5)
        }
        append_command_log("START_CYCLE", "เริ่มรันรอบสาธิต 6 ขั้นตอนทันที (Sample Inflow R1 / GPIO 5)", preserve_schedule)

    elif cmd in ("CANCEL_OVERRIDE", "RESUME_AUTO", "STOP"):
        was_queued = bool(current_hardware_status["schedule"].get("queued_during_override"))
        current_hardware_status["override"] = {
            "active": False,
            "mode": "STANDBY",
            "label": "ซิงก์ตามตารางเวลาอัตโนมัติปกติ",
            "duration_ms": 0,
            "expires_at": None,
            "active_relays": [],
        }
        current_hardware_status["schedule"]["enabled"] = True
        if was_queued and cmd == "RESUME_AUTO":
            current_hardware_status["schedule"]["queued_during_override"] = False
            current_hardware_status["schedule"]["remaining_sec"] = current_hardware_status["schedule"]["interval_sec"]
            current_hardware_status["schedule"]["last_auto_run"] = datetime.now().isoformat()
            current_hardware_status["phase_id"] = 1
            current_hardware_status["phase"] = PHASE_LABELS[1]
            append_command_log("RESUME_AUTO", "คืนค่าตารางอัตโนมัติ + รันรอบที่ค้างคิวไว้ทันที", True)
        else:
            current_hardware_status["schedule"]["queued_during_override"] = False
            current_hardware_status["phase_id"] = 0
            current_hardware_status["phase"] = "STANDBY"
            append_command_log(cmd, "หยุดคำสั่งสาธิตชั่วคราว คงตารางเวลาอัตโนมัติไว้ตามปกติ", True)

    current_command = {
        "command": cmd,
        "relay": relay_num,
        "duration_ms": duration_ms,
        "preserve_schedule": preserve_schedule,
        "timestamp": datetime.now().isoformat(),
        **extra_fields,
    }
    logger.info(f"[COMMAND QUEUED] {current_command}")
    return {
        "status": "ok",
        "queued_command": current_command,
        "schedule": current_hardware_status["schedule"],
        "override": current_hardware_status["override"],
    }


@app.get("/api/command")
def get_pending_command():
    """
    ESP32 โพลคำสั่งจากเซิร์ฟเวอร์ เมื่อดึงไปแล้วจะรีเซ็ตสถานะกลับเป็น IDLE
    """
    global current_command
    cmd_to_send = dict(current_command)
    if current_command["command"] != "IDLE":
        current_command = {"command": "IDLE", "timestamp": datetime.now().isoformat()}
    return cmd_to_send


@app.post("/api/schedule")
def post_schedule_control(payload: dict):
    """
    จัดการตารางเวลาอัตโนมัติและทดสอบระบบป้องกันการชนกันขณะนำเสนอ (Hold/Queue Collision Protection)
    """
    action = payload.get("action", "SET_INTERVAL")
    sched = current_hardware_status["schedule"]
    sched["enabled"] = True

    if action == "SET_INTERVAL":
        interval_sec = max(10, int(payload.get("interval_sec", 1800)))
        sched["interval_sec"] = interval_sec
        sched["remaining_sec"] = int(payload.get("remaining_sec", interval_sec))
        append_command_log("SCHEDULE", f"ตั้งรอบเวลาอัตโนมัติทุก {interval_sec} วินาที (ACTIVE)", True)
    elif action == "SIMULATE_COLLISION":
        if current_hardware_status["override"].get("active"):
            sched["remaining_sec"] = 0
            sched["queued_during_override"] = True
            append_command_log(
                "COLLISION_HOLD",
                "รอบอัตโนมัติครบกำหนดขณะกำลังสาธิต -> ชะลอไว้ในคิว (Hold/Queue) รอจบการสาธิต",
                True,
            )
        else:
            sched["remaining_sec"] = sched["interval_sec"]
            sched["last_auto_run"] = datetime.now().isoformat()
            current_hardware_status["phase_id"] = 1
            current_hardware_status["phase"] = PHASE_LABELS[1]
            append_command_log("AUTO_CYCLE", "เริ่มรอบทำงานอัตโนมัติตามตารางเวลา", True)
    elif action == "RESUME_QUEUED":
        sched["queued_during_override"] = False
        sched["remaining_sec"] = sched["interval_sec"]
        sched["last_auto_run"] = datetime.now().isoformat()
        current_hardware_status["override"]["active"] = False
        current_hardware_status["override"]["active_relays"] = []
        current_hardware_status["phase_id"] = 1
        current_hardware_status["phase"] = PHASE_LABELS[1]
        append_command_log("AUTO_RESUME", "รันรอบอัตโนมัติที่ชะลอไว้ทันทีหลังสาธิตเสร็จ", True)

    return {
        "status": "ok",
        "schedule": sched,
        "override": current_hardware_status["override"],
    }


@app.post("/api/override/simulate")
def post_override_simulate(payload: dict):
    """
    จำลองสถานการณ์ค่าเซนเซอร์และผลการวินิจฉัยใบผักบุ้งสดๆ ตอนนำเสนอ
    คำนวณผ่าน TwoTierDosingEngine จริงโดยไม่ปิดระบบตารางเวลาอัตโนมัติ
    """
    ec = float(payload.get("ec", 1.85))
    ph = float(payload.get("ph", 6.20))
    temp = float(payload.get("temp", 26.5))
    ai_class = str(payload.get("ai_class", "Control"))
    ai_confidence = float(payload.get("ai_confidence", 0.95))
    ai_stage = str(payload.get("ai_stage", "HEALTHY_NORMAL"))
    apply_to_status = bool(payload.get("apply_to_status", True))

    dosing_res = dosing_engine.compute_dosing(
        ec=ec,
        ph=ph,
        temp=temp,
        ai_class=ai_class,
        ai_confidence=ai_confidence,
        ai_stage=ai_stage,
    )

    if apply_to_status:
        current_hardware_status["ec"] = ec
        current_hardware_status["ph"] = ph
        current_hardware_status["temp"] = temp
        current_hardware_status["deficiency_class"] = ai_class
        current_hardware_status["stage"] = ai_stage
        current_hardware_status["dosing_plan"] = dosing_res["dosing_plan"]
        current_hardware_status["ratios"] = dosing_res.get("ratios", {"r1_pct": 33.3, "r2_pct": 33.3, "r3_pct": 33.3})
        current_hardware_status["volumes_ml"] = dosing_res.get("volumes_ml", {})
        current_hardware_status["ai_reason"] = dosing_res["ai_reason"]
        current_hardware_status["tier1_status"] = dosing_res["tier1_status"]
        current_hardware_status["last_update"] = datetime.now().isoformat()
        current_hardware_status["schedule"]["enabled"] = True
        append_command_log(
            "SIMULATE_SCENARIO",
            f"จำลองผักบุ้ง {ai_class} (EC {ec:.2f}, pH {ph:.2f}, Temp {temp:.1f}°C) -> {dosing_res['safety_status']}",
            True,
        )

    return dosing_res


@app.post("/api/cam_command")
def post_cam_command(payload: dict):
    """
    แดชบอร์ดส่งคำสั่งให้ ESP32-CAM ถ่ายภาพ: {"command": "CAPTURE"}
    """
    global current_cam_command
    cmd = payload.get("command", "CAPTURE")
    current_cam_command = {"command": cmd, "timestamp": datetime.now().isoformat()}
    current_hardware_status["schedule"]["enabled"] = True
    append_command_log("CAM_CAPTURE", f"สั่ง ESP32-S3 CAM ถ่ายภาพใบผักบุ้ง ({cmd})", True)
    logger.info(f"[CAM COMMAND QUEUED] {current_cam_command}")
    return {"status": "ok", "queued_command": current_cam_command}


@app.get("/api/cam_command")
def get_pending_cam_command():
    """
    ESP32-CAM โพลคำสั่งถ่ายภาพ
    """
    global current_cam_command
    cmd_to_send = dict(current_cam_command)
    if current_cam_command["command"] != "IDLE":
        current_cam_command = {"command": "IDLE", "timestamp": datetime.now().isoformat()}
    return cmd_to_send


@app.post("/api/status")
def update_hardware_status(payload: dict):
    """
    ESP32 อัปเดตสถานะ Phase ปัจจุบัน (1-6) และค่าเซนเซอร์
    """
    current_hardware_status["phase"] = payload.get("phase", current_hardware_status["phase"])
    current_hardware_status["phase_id"] = payload.get("phase_id", current_hardware_status["phase_id"])
    if "ec" in payload:
        current_hardware_status["ec"] = float(payload["ec"])
    if "ph" in payload:
        current_hardware_status["ph"] = float(payload["ph"])
    if "temp" in payload:
        current_hardware_status["temp"] = float(payload["temp"])
    current_hardware_status["last_update"] = datetime.now().isoformat()
    return {"status": "ok"}


@app.get("/api/status")
def get_hardware_status():
    """
    แดชบอร์ดโพลเพื่ออัปเดตหน้าจอแบบ Real-time
    """
    return current_hardware_status


@app.get("/api/calibration")
def get_calibration():
    """คืนค่าพารามิเตอร์ Calibration ปัจจุบัน (flow_rate, tank_volume, target_ec, priming_delay)"""
    return dosing_engine.get_calibration()


@app.post("/api/calibration")
def set_calibration(payload: dict):
    """อัปเดตค่าพารามิเตอร์ Calibration ผ่าน Dashboard"""
    updated = dosing_engine.update_calibration(
        target_ec=payload.get("target_ec"),
        tank_volume=payload.get("tank_volume_liters", payload.get("tank_volume")),
        pump_flow_rate_ml_s=payload.get("pump_flow_rate_ml_s", payload.get("flow_rate")),
        priming_delay_s=payload.get("priming_delay_s", payload.get("priming_delay")),
    )
    current_hardware_status["calibration"] = updated
    append_command_log("CALIBRATION", f"อัปเดต Target EC={updated['target_ec']} / Q={updated['pump_flow_rate_ml_s']} mL/s", True)
    logger.info(f"[CALIBRATION UPDATED] {updated}")
    return {"status": "ok", "calibration": updated}


@app.post("/api/calibration/calculate")
def calculate_calibration(payload: dict):
    """
    คำนวณ Flow Rate อัตโนมัติจากผลการทดสอบเปิดปั๊ม (Calibration Wizard):
    Q = collected_ml / (test_duration_s - observed_prime_s)
    """
    collected_ml = float(payload.get("collected_ml", 12.0))
    test_duration_s = float(payload.get("test_duration_s", 10.0))
    observed_prime_s = float(payload.get("observed_prime_s", 2.0))
    res = dosing_engine.calibrate_from_test_run(
        collected_ml=collected_ml,
        test_duration_s=test_duration_s,
        observed_prime_s=observed_prime_s,
    )
    current_hardware_status["calibration"] = dosing_engine.get_calibration()
    logger.info(f"[CALIBRATION WIZARD COMPLETED] {res}")
    return res


@app.get("/rules")
def get_rules():
    return {"pump_rules_sec": PUMP_RULES, "moisture_threshold": MOISTURE_THRESHOLD}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
