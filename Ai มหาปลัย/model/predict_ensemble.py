"""
predict_ensemble.py — Live ESP32-S3 CAM Top-Down Auto-Crop & Symptom-Gated Ensemble Predictor
for Hydroponic Water Spinach NPK Deficiency Detection.

Pipeline when ESP32-S3 CAM sends a top-down photo + sensor readings (EC, pH, temp):
  1. 3-Layer Illumination-Invariant & Symptom-Inclusive Auto-Cropper (`ml.crop_plants`):
     - Normalizes lighting via Gray-World White Balance + CLAHE on CIELAB L*.
     - Segments ALL plant tissue colors (Green + Yellow Chlorosis + Purple Anthocyanin + Brown Necrosis).
     - Wraps in Convex Hull + 14% safety margin + Minimum 56% Safe Tank ROI fallback.
     - Extracts:
         (a) Whole-Canopy Crop (224x224)
         (b) Up to 4 Individual Plant-Hole Sub-Patches (224x224 per hole)
  2. Stream A (Symptom-Gated Vision Ensemble: A1 MobileNetV2 + A2 SE-CNN + A3 44-D Foliar Expert):
     - Evaluates both the canopy crop and all individual plant-hole sub-patches.
     - Uses Symptom-Aware Max/Weighted Pooling so if even 1 plant hole shows early
       yellowing/purpling/scorch, it flags the visual symptom immediately.
  3. Stream B (Sensor Ensemble: B1 GradientBoosting + B2 RandomForest + B3 ExtraTrees):
     - Evaluates water EC, pH, temperature, EC ratio vs baseline, and pH deviation.
  4. Two-Stage Diagnostic Decision:
     - Stage 1 (Healthy): Both leaves and water are healthy -> `HEALTHY_NORMAL`
     - Stage 2 (Pre-Symptomatic Early Warning): Leaves are still visually green (`healthy`),
       but water sensor ensemble detects nutrient depletion/imbalance -> `PRE_SYMPTOMATIC_EARLY_WARNING`
     - Stage 3 (Confirmed Symptomatic Deficiency): Leaves show visual deficiency symptoms
       AND/OR both streams confirm deficiency -> `SYMPTOMATIC_DEFICIENCY_CONFIRMED`
"""

import os
import sys
import io
import json
import pickle
import warnings
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
KERAS_CACHE_DIR = ROOT_DIR / ".keras_cache"
KERAS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
(KERAS_CACHE_DIR / "mpl").mkdir(parents=True, exist_ok=True)
os.environ["KERAS_HOME"] = str(KERAS_CACHE_DIR)
os.environ["MPLCONFIGDIR"] = str(KERAS_CACHE_DIR / "mpl")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
warnings.filterwarnings("ignore")

try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
except Exception:
    pass

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import cv2
import numpy as np
import tensorflow as tf

from ml.crop_plants import extract_canopy_and_hole_patches, imread_unicode, imwrite_unicode

ENSEMBLE_DIR = ROOT_DIR / "Ai มหาปลัย" / "model" / "output_ensemble"
CLASSES = ["healthy", "nitrogen", "phosphorus", "potassium"]

THAI_CLASS_NAMES = {
    "healthy": "ปกติสมบูรณ์ (Healthy / Control)",
    "nitrogen": "ขาดธาตุไนโตรเจน (Nitrogen Deficiency -N)",
    "phosphorus": "ขาดธาตุฟอสฟอรัส (Phosphorus Deficiency -P)",
    "potassium": "ขาดธาตุโพแทสเซียม (Potassium Deficiency -K)",
}


def extract_foliar_features_single(img_rgb_float):
    """Extract the 44-D physiological foliar feature vector matching train_ensemble_model.py."""
    img_u8 = np.clip(img_rgb_float * 255.0, 0, 255).astype(np.uint8)
    r, g, b = img_rgb_float[:, :, 0], img_rgb_float[:, :, 1], img_rgb_float[:, :, 2]

    exg = 2.0 * g - r - b
    exr = 1.4 * r - g
    exgr = exg - exr
    ndi = (g - r) / (g + r + 1e-5)
    vari = (g - r) / (g + r - b + 1e-5)

    bgr_u8 = cv2.cvtColor(img_u8, cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(bgr_u8, cv2.COLOR_BGR2HSV).astype(np.float32)
    lab = cv2.cvtColor(bgr_u8, cv2.COLOR_BGR2LAB).astype(np.float32)
    chroma = np.hypot(lab[:, :, 1] - 128.0, lab[:, :, 2] - 128.0)

    leaf_mask = (exg > 0.03) | (chroma > 15.0)
    if np.sum(leaf_mask) < 100:
        leaf_mask = np.ones_like(exg, dtype=bool)

    mask_u8 = leaf_mask.astype(np.uint8) * 255
    eroded = cv2.erode(mask_u8, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (17, 17)), iterations=1)
    core_mask = eroded > 0
    margin_mask = (mask_u8 - eroded) > 0
    if np.sum(core_mask) < 50:
        core_mask = leaf_mask
    if np.sum(margin_mask) < 50:
        margin_mask = leaf_mask

    feats = []
    for idx_map in [exg, exr, exgr, ndi, vari]:
        vals = idx_map[leaf_mask]
        feats.extend([float(np.mean(vals)), float(np.std(vals))])

    for ch in range(3):
        l_vals = lab[:, :, ch][leaf_mask]
        h_vals = hsv[:, :, ch][leaf_mask]
        feats.extend([float(np.mean(l_vals)), float(np.std(l_vals))])
        feats.extend([float(np.mean(h_vals)), float(np.std(h_vals))])

    for ch in range(3):
        core_lab = float(np.mean(lab[:, :, ch][core_mask]))
        marg_lab = float(np.mean(lab[:, :, ch][margin_mask]))
        core_hsv = float(np.mean(hsv[:, :, ch][core_mask]))
        marg_hsv = float(np.mean(hsv[:, :, ch][margin_mask]))
        feats.extend([marg_lab - core_lab, marg_lab / (core_lab + 1e-4)])
        feats.extend([marg_hsv - core_hsv, marg_hsv / (core_hsv + 1e-4)])

    for ch in range(3):
        vals = lab[:, :, ch][leaf_mask]
        feats.extend([float(np.percentile(vals, 15)), float(np.percentile(vals, 85))])

    gray = cv2.cvtColor(bgr_u8, cv2.COLOR_BGR2GRAY).astype(np.float32)
    sobelx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    grad_mag = np.hypot(sobelx, sobely)[leaf_mask]
    lap_var = float(np.var(cv2.Laplacian(gray, cv2.CV_32F)[leaf_mask]))

    yellow_ratio = float(np.mean((hsv[:, :, 0][leaf_mask] >= 16) & (hsv[:, :, 0][leaf_mask] <= 36)))
    dark_purple_ratio = float(np.mean((lab[:, :, 0][leaf_mask] < 115) & (lab[:, :, 1][leaf_mask] > 125)))

    feats.extend([float(np.mean(grad_mag)), lap_var, yellow_ratio, dark_purple_ratio])
    return np.nan_to_num(np.array(feats, dtype=np.float32), nan=0.0, posinf=0.0, neginf=0.0)


class HydroponicEnsemblePredictor:
    """Singleton wrapper around the trained Symptom-Gated Hierarchical Multimodal Ensemble."""

    def __init__(self, model_dir=ENSEMBLE_DIR):
        self.model_dir = Path(model_dir)
        self.classes = CLASSES
        self.loaded = False
        self.a1 = None
        self.a2 = None
        self.a3 = None
        self.sensor_models = None
        self.scalers = None
        self._load()

    def _load(self):
        try:
            a1_path = self.model_dir / "member_a1_mobilenetv2.keras"
            a2_path = self.model_dir / "member_a2_se_cnn.keras"
            a3_path = self.model_dir / "vision_a3_foliar_expert.pkl"
            sen_path = self.model_dir / "sensor_ensemble_models.pkl"
            sc_path = self.model_dir / "scalers_and_encoder.pkl"

            if not (a1_path.exists() and a3_path.exists() and sen_path.exists() and sc_path.exists()):
                return

            self.a1 = tf.keras.models.load_model(str(a1_path))
            self.a2 = tf.keras.models.load_model(str(a2_path)) if a2_path.exists() else None
            with open(a3_path, "rb") as f:
                self.a3 = pickle.load(f)
            with open(sen_path, "rb") as f:
                self.sensor_models = pickle.load(f)
            with open(sc_path, "rb") as f:
                self.scalers = pickle.load(f)
            self.loaded = True
        except Exception as e:
            print(f"⚠️ Ensemble load warning: {e}")
            self.loaded = False

    def predict_vision_patch_batch(self, patches_rgb):
        """Run Stream A Vision Ensemble across [canopy_crop + hole_patches]."""
        X_img = np.array(patches_rgb, dtype=np.float32)
        X_fol = np.array([extract_foliar_features_single(p) for p in patches_rgb], dtype=np.float32)
        X_fol_s = self.scalers["fol_scaler"].transform(X_fol)

        w1, w2, w3 = self.scalers.get("vision_weights", (0.35, 0.15, 0.50))
        p_a1 = self.a1.predict(X_img, verbose=0)
        p_a2 = self.a2.predict(X_img, verbose=0) if self.a2 is not None else p_a1
        p_a3 = (
            0.45 * self.a3["et"].predict_proba(X_fol_s)
            + 0.35 * self.a3["rf"].predict_proba(X_fol_s)
            + 0.20 * self.a3["mlp"].predict_proba(X_fol_s)
        )
        p_patches = w1 * p_a1 + w2 * p_a2 + w3 * p_a3

        # Symptom-Aware Pooling across Canopy (index 0) and Individual Hole Patches (index 1..N):
        # If any individual plant hole has strong deficiency confidence (> 0.55), boost its weight
        canopy_prob = p_patches[0]
        if len(p_patches) == 1:
            return canopy_prob, p_patches

        hole_probs = p_patches[1:]
        max_def_per_hole = np.max(hole_probs[:, 1:], axis=1)  # max non-healthy prob per hole
        worst_hole_idx = int(np.argmax(max_def_per_hole))
        worst_hole_prob = hole_probs[worst_hole_idx]

        if max_def_per_hole[worst_hole_idx] > 0.58:
            # Localized early symptom detected in a specific plant hole!
            pooled_vision = 0.45 * canopy_prob + 0.35 * worst_hole_prob + 0.20 * np.mean(hole_probs, axis=0)
        else:
            pooled_vision = 0.55 * canopy_prob + 0.45 * np.mean(hole_probs, axis=0)

        pooled_vision = pooled_vision / np.sum(pooled_vision)
        return pooled_vision, p_patches

    def predict_from_topdown_and_sensor(
        self,
        img_bgr: np.ndarray,
        ec: float,
        ph: float,
        water_temp: float = 28.0,
        baseline_ec: float = 2.641,
        ph_before: float = None,
    ):
        """
        Full end-to-end ESP32-S3 CAM Top-Down Auto-Crop + Symptom-Gated Multimodal Inference.
        """
        # 1. Run 3-Layer Illumination-Invariant & Symptom-Inclusive Auto-Cropper
        crop_res = extract_canopy_and_hole_patches(img_bgr, max_hole_patches=4)
        all_patches = [crop_res["canopy_rgb"]] + crop_res["hole_patches_rgb"]

        if not self.loaded:
            self._load()

        # 2. Compute Stream A (Vision Ensemble)
        P_img, patch_probs = self.predict_vision_patch_batch(all_patches)
        vis_idx = int(np.argmax(P_img))
        visual_class = CLASSES[vis_idx]
        visual_conf = float(P_img[vis_idx])

        # 3. Compute Stream B (Sensor Ensemble)
        if ph_before is None:
            ph_before = ph
        ec_ratio = ec / baseline_ec if baseline_ec > 0 else 1.0
        ec_change_pct = ((ec - baseline_ec) / baseline_ec) * 100.0 if baseline_ec > 0 else 0.0
        ph_drift = ph_before - ph
        ph_opt_dev = abs(ph - 6.0)

        sen_vec = np.array([[ec, ph, water_temp, ec_ratio, ec_change_pct, ph_drift, ph_opt_dev]], dtype=np.float32)
        sen_scaled = self.scalers["sen_scaler"].transform(sen_vec)

        P_sen = (
            0.45 * self.sensor_models["b1_gb"].predict_proba(sen_scaled)[0]
            + 0.30 * self.sensor_models["b2_rf"].predict_proba(sen_scaled)[0]
            + 0.25 * self.sensor_models["b3_et"].predict_proba(sen_scaled)[0]
        )
        sen_idx = int(np.argmax(P_sen))
        sensor_class = CLASSES[sen_idx]
        sensor_conf = float(P_sen[sen_idx])

        # 4. Hierarchical Late-Fusion & Two-Stage Pre-Symptomatic vs. Symptomatic Diagnosis
        alpha = float(self.scalers.get("fusion_alpha", 0.45))
        beta = float(self.scalers.get("fusion_beta", 0.55))
        P_fusion = alpha * P_img + beta * P_sen
        P_fusion = P_fusion / np.sum(P_fusion)
        final_idx = int(np.argmax(P_fusion))
        final_class = CLASSES[final_idx]
        final_conf = float(P_fusion[final_idx])

        if visual_class == "healthy" and sensor_class == "healthy":
            diagnostic_stage = "HEALTHY_NORMAL"
            stage_thai = "🟢 ปกติสมบูรณ์ (ทั้งใบพืชและสารละลายอยู่ในเกณฑ์มาตรฐาน)"
        elif visual_class == "healthy" and sensor_class != "healthy":
            diagnostic_stage = "PRE_SYMPTOMATIC_EARLY_WARNING"
            stage_thai = (
                f"🟡 เตือนล่วงหน้าระยะแฝง (Pre-Symptomatic): ใบยังเขียวปกติ ({visual_conf*100:.1f}%) "
                f"แต่สารละลายในถังมีแนวโน้ม {THAI_CLASS_NAMES[sensor_class]} ({sensor_conf*100:.1f}%)"
            )
        else:
            diagnostic_stage = "SYMPTOMATIC_DEFICIENCY_CONFIRMED"
            stage_thai = (
                f"🔴 ยืนยันอาการทางใบ (Symptomatic): ตรวจพบอาการบนใบ {THAI_CLASS_NAMES[visual_class]} ({visual_conf*100:.1f}%) "
                f"สอดคล้องกับสถานะสารละลาย"
            )

        return {
            "final_class": final_class,
            "final_class_thai": THAI_CLASS_NAMES[final_class],
            "final_confidence": round(final_conf, 4),
            "diagnostic_stage": diagnostic_stage,
            "diagnostic_message_thai": stage_thai,
            "visual_leaf_status": {
                "predicted_class": visual_class,
                "confidence": round(visual_conf, 4),
                "probabilities": {c: round(float(P_img[i]), 4) for i, c in enumerate(CLASSES)},
                "patches_evaluated": len(all_patches),
                "canopy_bbox": crop_res["canopy_bbox"],
                "hole_bboxes": crop_res["hole_bboxes"],
            },
            "water_sensor_status": {
                "predicted_class": sensor_class,
                "confidence": round(sensor_conf, 4),
                "probabilities": {c: round(float(P_sen[i]), 4) for i, c in enumerate(CLASSES)},
                "ec_ms_cm": ec,
                "ph": ph,
                "water_temp_c": water_temp,
                "ec_change_pct": round(ec_change_pct, 2),
            },
            "fusion_probabilities": {c: round(float(P_fusion[i]), 4) for i, c in enumerate(CLASSES)},
        }


if __name__ == "__main__":
    print("=" * 76)
    print("  📸 Testing ESP32-S3 CAM Top-Down Auto-Crop & Symptom-Gated Ensemble")
    print("=" * 76)
    predictor = HydroponicEnsemblePredictor()

    test_cases = [
        ("Stage 1: Control Tank (23.3L Healthy Leaf + Optimal Water)", ROOT_DIR / "Ai มหาปลัย/dataset_real/images/Control/21_10_2026-time08_00.jpg", 2.68, 5.66, 28.0, 2.641),
        ("Stage 2: Pre-Symptomatic Early Warning (Green Canopy + Depleted -N Water)", ROOT_DIR / "Ai มหาปลัย/dataset_real/images/Control/21_10_2026-time08_00.jpg", 1.86, 6.27, 28.0, 2.572),
        ("Stage 3A: Tank -N Day 5 (Early Visual Chlorosis + Low N Water)", ROOT_DIR / "Ai มหาปลัย/dataset_real/images/N/21_10_2026-time08_00.jpg", 1.86, 6.27, 28.0, 2.572),
        ("Stage 3B: Symptomatic N-Deficient Leaf Reference", ROOT_DIR / "Ai มหาปลัย/dataset_external/images/nitrogen/src05_agronomic_nitrogen_01.jpg", 1.75, 6.30, 28.0, 2.572),
    ]

    for title, img_path, ec, ph, temp, base_ec in test_cases:
        if not img_path.exists():
            continue
        img_bgr = imread_unicode(img_path)
        res = predictor.predict_from_topdown_and_sensor(img_bgr, ec=ec, ph=ph, water_temp=temp, baseline_ec=base_ec)
        print(f"\n🔹 Case: {title}")
        print(f"   • Auto-Cropped Patches: {res['visual_leaf_status']['patches_evaluated']} (Canopy BBox: {res['visual_leaf_status']['canopy_bbox']})")
        print(f"   • Stream A (Vision Leaf):  {res['visual_leaf_status']['predicted_class']} ({res['visual_leaf_status']['confidence']*100:.1f}%)")
        print(f"   • Stream B (Water Sensor): {res['water_sensor_status']['predicted_class']} ({res['water_sensor_status']['confidence']*100:.1f}%)")
        print(f"   • Diagnostic Stage:        {res['diagnostic_stage']}")
        print(f"   • Summary:                 {res['diagnostic_message_thai']}")

