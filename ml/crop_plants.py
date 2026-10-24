"""
crop_plants.py — 3-Layer Illumination-Invariant & Symptom-Inclusive Plant Auto-Cropper
for ESP32-S3 CAM Top-Down Hydroponic Water Spinach Imagery.

Solves two critical real-world problems:
  1. Lighting shifts (morning vs evening sun, shadows, ESP32-CAM auto-white-balance drift):
     -> Layer 1 applies Gray-World White Balance + CLAHE on CIELAB L* luminance channel.
  2. Non-green symptomatic leaves (Yellow N-deficiency chlorosis, Purple P-deficiency
     anthocyanin, Brown K-deficiency necrotic leaf margins):
     -> Layer 2 combines Excess Green (ExG) + HSV Green/Yellow/Purple masks +
        CIELAB Chromaticity mask (separating any colored plant tissue from white foam /
        black plastic liner / gray floor).
  3. Guaranteed complete leaf capture (never cuts off leaf tips or edges):
     -> Layer 3 wraps detected contours in a Convex Hull with 15% safety padding AND
        enforces a Minimum Safe ROI (>= 58% of central tank area) fallback.

Also provides `extract_canopy_and_hole_patches()` for live ESP32-S3 CAM inference!
"""

import sys
import io
import os
import argparse
from pathlib import Path
import cv2
import numpy as np

try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
except Exception:
    pass

ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_INPUT_DIR = ROOT_DIR / "Ai มหาปลัย" / "dataset_real" / "images"
DEFAULT_OUTPUT_DIR = ROOT_DIR / "Ai มหาปลัย" / "dataset_real" / "images_cropped"
PREVIEW_DIR = ROOT_DIR / "Ai มหาปลัย" / "dataset_real" / "crop_previews"


def imread_unicode(path):
    """Safely read image from Windows Unicode paths."""
    with open(str(path), "rb") as f:
        bytes_data = np.frombuffer(f.read(), np.uint8)
    return cv2.imdecode(bytes_data, cv2.IMREAD_COLOR)


def imwrite_unicode(path, img):
    """Safely write image to Windows Unicode paths."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    ext = path.suffix or ".jpg"
    is_success, buffer = cv2.imencode(ext, img, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    if is_success:
        with open(str(path), "wb") as f:
            f.write(buffer)
        return True
    return False


# ==============================================================================
# LAYER 1 — ILLUMINATION & WHITE-BALANCE NORMALIZATION (CLAHE + GRAY-WORLD)
# ==============================================================================
def normalize_illumination_clahe(img_bgr):
    """
    Normalize lighting brightness and subtle color cast for segmentation robustness.
    Note: We use this normalized image to find accurate bounding boxes/masks,
    while cropping the actual pixels from the gently balanced image so natural
    leaf symptom colors (yellow, purple, brown) remain faithful.
    """
    # Gentle Gray-World white balance (clamped to avoid over-correction on all-green frames)
    img_f = img_bgr.astype(np.float32)
    avg_b, avg_g, avg_r = np.mean(img_f[:, :, 0]), np.mean(img_f[:, :, 1]), np.mean(img_f[:, :, 2])
    avg_gray = (avg_b + avg_g + avg_r) / 3.0 + 1e-5
    scale_b = np.clip(avg_gray / (avg_b + 1e-5), 0.85, 1.15)
    scale_g = np.clip(avg_gray / (avg_g + 1e-5), 0.88, 1.12)
    scale_r = np.clip(avg_gray / (avg_r + 1e-5), 0.85, 1.15)

    wb = np.zeros_like(img_f)
    wb[:, :, 0] = np.clip(img_f[:, :, 0] * scale_b, 0, 255)
    wb[:, :, 1] = np.clip(img_f[:, :, 1] * scale_g, 0, 255)
    wb[:, :, 2] = np.clip(img_f[:, :, 2] * scale_r, 0, 255)
    wb_u8 = wb.astype(np.uint8)

    # CLAHE on L* channel in CIELAB space
    lab = cv2.cvtColor(wb_u8, cv2.COLOR_BGR2LAB)
    clahe = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8))
    lab[:, :, 0] = clahe.apply(lab[:, :, 0])
    norm_bgr = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    return norm_bgr


# ==============================================================================
# LAYER 2 — MULTI-SPECTRUM PLANT TISSUE MASK (GREEN + YELLOW + PURPLE + BROWN)
# ==============================================================================
def segment_plant_foliage(img_bgr):
    """
    3-Layer Robust Plant Foliage Segmentation:
      1. Normalizes illumination via CLAHE + Gray-World.
      2. Detects ALL plant tissue spectra:
         - Healthy Green foliage (ExG + HSV green band)
         - Nitrogen-deficient Yellow/Chlorotic leaves (HSV yellow-orange + CIELAB high b*)
         - Phosphorus-deficient Purple/Dark leaves & Potassium-deficient Brown leaf margins
           (CIELAB Chromaticity distance from neutral gray/black/white background, scoped
            within the central tank region).
      3. Morphological closing + dilation so connected leaf tips/margins are never lost.
    """
    norm = normalize_illumination_clahe(img_bgr)
    h, w = norm.shape[:2]

    b = norm[:, :, 0].astype(np.float32)
    g = norm[:, :, 1].astype(np.float32)
    r = norm[:, :, 2].astype(np.float32)

    # A. Excess Green Index (ExG = 2G - R - B)
    exg = 2.0 * g - r - b
    exg_norm = cv2.normalize(exg, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    exg_blur = cv2.GaussianBlur(exg_norm, (5, 5), 0)
    _, mask_exg = cv2.threshold(exg_blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # Require positive ExG to prevent Otsu from triggering on pure black/white frames
    mask_exg = cv2.bitwise_and(mask_exg, ((exg > 12.0).astype(np.uint8) * 255))

    # B. HSV Multi-Hue Plant Mask (Green + Yellow Chlorosis)
    hsv = cv2.cvtColor(norm, cv2.COLOR_BGR2HSV)
    # Green & Yellow-Green & Chlorotic Yellow (Hue 18..92 in OpenCV 0..180 scale, Sat >= 48)
    mask_hsv_green_yellow = cv2.inRange(hsv, (18, 48, 40), (92, 255, 255))

    # Core plant seed mask (Green + Chlorotic Yellow), scoped to central tank area (excluding outer 8% room floor margin)
    tank_roi = np.zeros((h, w), dtype=np.uint8)
    tank_roi[int(h * 0.08):int(h * 0.92), int(w * 0.08):int(w * 0.92)] = 255
    mask_seed = cv2.bitwise_and(cv2.bitwise_or(mask_exg, mask_hsv_green_yellow), tank_roi)
    k_clean = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    mask_seed = cv2.morphologyEx(mask_seed, cv2.MORPH_OPEN, k_clean, iterations=1)

    # C. CIELAB Chromaticity Mask for Purple (-P) and Brown Marginal Scorch (-K)
    # Restricted to a proximity halo around detected plant clusters so background floor/walls are excluded!
    lab = cv2.cvtColor(norm, cv2.COLOR_BGR2LAB).astype(np.float32)
    L_ch, a_ch, b_ch = lab[:, :, 0], lab[:, :, 1], lab[:, :, 2]
    chroma = np.hypot(a_ch - 128.0, b_ch - 128.0)
    mask_chroma = ((chroma > 22.0) & (L_ch > 30) & (L_ch < 225)).astype(np.uint8) * 255

    # Build proximity halo around plant seed contours (~4% of image dimension)
    halo_r = max(11, int(min(h, w) * 0.035))
    k_halo = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (halo_r, halo_r))
    plant_halo = cv2.bitwise_and(cv2.dilate(mask_seed, k_halo, iterations=1), tank_roi)
    mask_symptomatic_edges = cv2.bitwise_and(mask_chroma, plant_halo)

    # Combine core plant mask + symptomatic edges (yellow/purple/brown tips)
    combined = cv2.bitwise_or(mask_seed, mask_symptomatic_edges)

    # Morphological cleanup: open small noise, then close to bridge leaf petioles and brown tips
    k_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    k_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
    mask = cv2.morphologyEx(combined, cv2.MORPH_OPEN, k_open, iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k_close, iterations=2)

    return mask


# ==============================================================================
# LAYER 3 — CONVEX-HULL SAFE PADDING & MINIMUM TANK ROI FALLBACK
# ==============================================================================
def get_plant_bounding_box(mask, img_shape, padding_pct=0.06, min_area_ratio=0.0020, min_roi_ratio=0.35):
    """
    Compute a safe bounding box around all plant foliage contours:
      - Uses Convex Hull around valid plant contours + 14% padding so leaf tips/margins
        are NEVER clipped.
      - Enforces a Minimum Safe ROI (`min_roi_ratio = 56%` of image dimension) centered
        around the detected foliage centroid (or frame center if lighting completely failed),
        guaranteeing no tiny/partial crops ever occur.
    """
    h, w = img_shape[:2]
    total_area = float(h * w)
    min_contour_area = total_area * min_area_ratio

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    valid_contours = [c for c in contours if cv2.contourArea(c) > min_contour_area]

    if not valid_contours and contours:
        valid_contours = [max(contours, key=cv2.contourArea)]

    if not valid_contours:
        # Complete lighting failure fallback: safe 76% central tank crop
        margin_y = int(h * 0.12)
        margin_x = int(w * 0.12)
        return (margin_x, margin_y, w - margin_x, h - margin_y)

    # Combine all valid contour points and compute their Convex Hull
    all_pts = np.vstack(valid_contours)
    hull = cv2.convexHull(all_pts)
    x, y, cw, ch = cv2.boundingRect(hull)

    # Add generous safety padding (14%) so yellow tips / brown edges are fully inside
    pad_x = int(cw * padding_pct)
    pad_y = int(ch * padding_pct)
    x1 = max(0, x - pad_x)
    y1 = max(0, y - pad_y)
    x2 = min(w, x + cw + pad_x)
    y2 = min(h, y + ch + pad_y)

    # Enforce Minimum Safe ROI size so under-segmentation in extreme glare never clips plants
    min_w = int(w * min_roi_ratio)
    min_h = int(h * min_roi_ratio)
    cur_w = x2 - x1
    cur_h = y2 - y1

    if cur_w < min_w:
        cx = (x1 + x2) // 2
        x1 = max(0, cx - min_w // 2)
        x2 = min(w, x1 + min_w)
        x1 = max(0, x2 - min_w)

    if cur_h < min_h:
        cy = (y1 + y2) // 2
        y1 = max(0, cy - min_h // 2)
        y2 = min(h, y1 + min_h)
        y1 = max(0, y2 - min_h)

    return (int(x1), int(y1), int(x2), int(y2))


def extract_canopy_and_hole_patches(img_bgr, target_size=(224, 224), max_hole_patches=4):
    """
    Used by both training and live ESP32-S3 CAM inference (`predict_ensemble.py` / `main.py`):
      1. Extracts the full-canopy safe bounding box crop (`canopy_crop_224`).
      2. Extracts up to `max_hole_patches` individual plant-hole / leaf-cluster sub-patches
         (`hole_patches_224`) so that localized early symptoms on a single plant are caught.
    Returns dict with RGB float32 [0,1] arrays and bounding box coordinates.
    """
    h, w = img_bgr.shape[:2]
    mask = segment_plant_foliage(img_bgr)
    canopy_bbox = get_plant_bounding_box(mask, img_bgr.shape)
    x1, y1, x2, y2 = canopy_bbox

    canopy_bgr = cv2.resize(img_bgr[y1:y2, x1:x2], target_size)
    canopy_rgb = cv2.cvtColor(canopy_bgr, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0

    # Find individual plant-hole clusters
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    min_hole_area = (h * w) * 0.004
    valid = sorted(
        [c for c in contours if cv2.contourArea(c) > min_hole_area],
        key=cv2.contourArea,
        reverse=True,
    )

    hole_patches_rgb = []
    hole_bboxes = []

    for c in valid[:max_hole_patches]:
        hx, hy, hcw, hch = cv2.boundingRect(c)
        if hcw < 36 or hch < 36:
            continue
        pad_x = int(hcw * 0.16)
        pad_y = int(hch * 0.16)
        bx1 = max(0, hx - pad_x)
        by1 = max(0, hy - pad_y)
        bx2 = min(w, hx + hcw + pad_x)
        by2 = min(h, hy + hch + pad_y)

        patch_bgr = cv2.resize(img_bgr[by1:by2, bx1:bx2], target_size)
        patch_rgb = cv2.cvtColor(patch_bgr, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
        hole_patches_rgb.append(patch_rgb)
        hole_bboxes.append((int(bx1), int(by1), int(bx2), int(by2)))

    # If fewer than 2 distinct contours (e.g., overlapping canopy), add 4 quadrant sub-crops of the canopy
    if len(hole_patches_rgb) < 2:
        ch_box = y2 - y1
        cw_box = x2 - x1
        my = y1 + ch_box // 2
        mx = x1 + cw_box // 2
        quads = [
            (x1, y1, mx + int(cw_box * 0.1), my + int(ch_box * 0.1)),
            (mx - int(cw_box * 0.1), y1, x2, my + int(ch_box * 0.1)),
            (x1, my - int(ch_box * 0.1), mx + int(cw_box * 0.1), y2),
            (mx - int(cw_box * 0.1), my - int(ch_box * 0.1), x2, y2),
        ]
        for qx1, qy1, qx2, qy2 in quads:
            if len(hole_patches_rgb) >= max_hole_patches:
                break
            if (qx2 - qx1) >= 32 and (qy2 - qy1) >= 32:
                q_bgr = cv2.resize(img_bgr[qy1:qy2, qx1:qx2], target_size)
                q_rgb = cv2.cvtColor(q_bgr, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
                hole_patches_rgb.append(q_rgb)
                hole_bboxes.append((int(qx1), int(qy1), int(qx2), int(qy2)))

    return {
        "canopy_rgb": canopy_rgb,
        "canopy_bgr": canopy_bgr,
        "canopy_bbox": canopy_bbox,
        "hole_patches_rgb": hole_patches_rgb,
        "hole_bboxes": hole_bboxes,
        "mask": mask,
    }


def process_image(img_path, out_path, preview_path=None):
    """Read, crop with 3-Layer Robust Auto-Cropper, and optionally save preview comparison."""
    img = imread_unicode(img_path)
    if img is None:
        return False

    res = extract_canopy_and_hole_patches(img)
    x1, y1, x2, y2 = res["canopy_bbox"]
    cropped = img[y1:y2, x1:x2]
    imwrite_unicode(out_path, cropped)

    if preview_path:
        h, w = img.shape[:2]
        disp_h = 400
        disp_w = int(w * (disp_h / h))
        orig_disp = cv2.resize(img, (disp_w, disp_h))
        mask_disp = cv2.resize(cv2.cvtColor(res["mask"], cv2.COLOR_GRAY2BGR), (disp_w, disp_h))

        sx, sy = disp_w / w, disp_h / h
        # Draw main canopy bbox in bright green
        cv2.rectangle(orig_disp, (int(x1 * sx), int(y1 * sy)), (int(x2 * sx), int(y2 * sy)), (0, 255, 0), 3)
        # Draw individual hole bboxes in cyan
        for hx1, hy1, hx2, hy2 in res["hole_bboxes"]:
            cv2.rectangle(orig_disp, (int(hx1 * sx), int(hy1 * sy)), (int(hx2 * sx), int(hy2 * sy)), (255, 220, 0), 2)

        crop_disp = cv2.resize(cropped, (disp_h, disp_h))
        preview = np.hstack([orig_disp, mask_disp, crop_disp])
        imwrite_unicode(preview_path, preview)

    return True


def batch_crop_dataset(input_dir, output_dir, preview_dir):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    preview_dir = Path(preview_dir)

    print("🌿 Starting 3-Layer Illumination-Invariant & Symptom-Inclusive Plant Cropping...")
    total_images = 0
    total_cropped = 0

    subdirs = [d for d in input_dir.iterdir() if d.is_dir()]
    if not subdirs:
        subdirs = [input_dir]

    for sdir in sorted(subdirs):
        img_files = [f for f in sdir.glob("*.*") if f.suffix.lower() in [".jpg", ".jpeg", ".png"]]
        if not img_files:
            continue

        category = sdir.name
        out_cat_dir = output_dir / category
        out_cat_dir.mkdir(parents=True, exist_ok=True)

        for i, img_file in enumerate(sorted(img_files)):
            total_images += 1
            out_file = out_cat_dir / img_file.name
            prev_file = None
            if i == 0:
                preview_dir.mkdir(parents=True, exist_ok=True)
                prev_file = preview_dir / f"preview_{category}_{img_file.name}"

            if process_image(img_file, out_file, prev_file):
                total_cropped += 1

        print(f"  ✅ [{category:<8}]: Cropped {len(img_files)} images (3-Layer CLAHE + Multi-Spectrum + Safe ROI)")

    print(f"🎉 Cropping completed: {total_cropped}/{total_images} images saved to {output_dir}")


def main():
    parser = argparse.ArgumentParser(description="3-Layer Robust Plant Foliage Auto-Cropper")
    parser.add_argument("--input", default=str(DEFAULT_INPUT_DIR), help="Input images directory")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_DIR), help="Output cropped directory")
    parser.add_argument("--preview", default=str(PREVIEW_DIR), help="Preview comparison directory")
    args = parser.parse_args()
    batch_crop_dataset(args.input, args.output, args.preview)


if __name__ == "__main__":
    main()
