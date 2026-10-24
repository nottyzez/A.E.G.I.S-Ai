"""
update_and_retrain.py — One-Command Data Sync, Cropping & Ensemble Retraining Pipeline
for Hydroponic Water Spinach NPK Deficiency Detection (Ready until Nov 9 Presentation).

What this script does automatically:
  1. Checks for new photos in Google Drive (optional --sync-drive) or local folders
     (Ai มหาปลัย/dataset_real/images/{Control,N,P,K,Cup1..Cup8}) and copies any new
     photos to server/static/images_real/ + updates images_manifest.js.
  2. Crops all plant foliage automatically using Excess Green Index (ml/crop_plants.py).
  3. Parses any newly added rows in hydroponic_log.xlsx into data/sensor_log.json
     and server/static/data/sensor_data.js (data/prepare_logs.py).
  4. Runs train_ensemble_model.py (--incremental by default for fast warm-start,
     or --full for complete retraining from scratch) and updates all report figures,
     DATASET_SOURCES_SUMMARY.md, and dashboard AI predictions.

Usage:
  Fast update & incremental retrain (Recommended after adding new photos / Excel rows):
    .\\ai-env312\\Scripts\\python.exe update_and_retrain.py

  Full retrain from scratch:
    .\\ai-env312\\Scripts\\python.exe update_and_retrain.py --full

  Sync from Google Drive first, then update & retrain:
    .\\ai-env312\\Scripts\\python.exe update_and_retrain.py --sync-drive
"""

import os
import sys
import io
import json
import time
import shutil
import argparse
import subprocess
from pathlib import Path

try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
except Exception:
    pass

ROOT_DIR = Path(__file__).resolve().parent
PYTHON_EXE = ROOT_DIR / "ai-env312" / "Scripts" / "python.exe"
if not PYTHON_EXE.exists():
    PYTHON_EXE = Path(sys.executable)

DATASET_IMG_DIR = ROOT_DIR / "Ai มหาปลัย" / "dataset_real" / "images"
STATIC_IMG_DIR = ROOT_DIR / "server" / "static" / "images_real"
MANIFEST_JS_PATH = ROOT_DIR / "server" / "static" / "data" / "images_manifest.js"
MANIFEST_JSON_PATH = ROOT_DIR / "data" / "images_manifest.json"


def sync_local_images_to_static():
    """
    Ensure any new photos dropped directly into Ai มหาปลัย/dataset_real/images/{unit}
    are copied to server/static/images_real/{unit} and registered in images_manifest.js.
    """
    print("\n📂 [Step 1B] Syncing local image folders & updating images_manifest.js...")
    manifest = {}
    if not DATASET_IMG_DIR.exists():
        return

    for sub in sorted(DATASET_IMG_DIR.iterdir()):
        if not sub.is_dir():
            continue
        unit = sub.name
        dest_dir = STATIC_IMG_DIR / unit
        dest_dir.mkdir(parents=True, exist_ok=True)

        files = []
        for img_path in sorted(sub.glob("*.*")):
            if img_path.suffix.lower() in (".jpg", ".jpeg", ".png"):
                files.append(img_path.name)
                dest_file = dest_dir / img_path.name
                if not dest_file.exists() or dest_file.stat().st_size != img_path.stat().st_size:
                    shutil.copy2(img_path, dest_file)
        manifest[unit] = sorted(files)
        print(f"   • {unit:<10}: {len(files):2d} photos synced")

    MANIFEST_JS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_JS_PATH, "w", encoding="utf-8") as f:
        f.write("window.IMAGES_MANIFEST = " + json.dumps(manifest, ensure_ascii=False) + ";\n")

    with open(MANIFEST_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)


def run_step(title, cmd_args):
    print(f"\n🚀 {title}...")
    res = subprocess.run([str(PYTHON_EXE)] + [str(a) for a in cmd_args], cwd=str(ROOT_DIR))
    if res.returncode != 0:
        print(f"  ⚠️ Step exited with code {res.returncode}")
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description="Data Sync, Cropping & Optional Ensemble Retrain")
    parser.add_argument("--sync-drive", action="store_true", help="Download new photos from Google Drive first")
    parser.add_argument("--train", action="store_true", help="Explicitly run Ensemble model training after data sync")
    parser.add_argument("--full", action="store_true", help="Full retrain instead of incremental warm-start (requires --train)")
    args = parser.parse_args()

    t0 = time.time()
    print("=" * 74)
    print("  🔄 HYDROPONIC AI — DATA & DASHBOARD SYNC PIPELINE")
    print("=" * 74)

    # 1. Optional Google Drive sync
    if args.sync_drive:
        run_step("[Step 1A] Downloading new photos from Google Drive", [ROOT_DIR / "data" / "download_dataset.py"])

    # 1B. Always sync local dataset_real/images -> server/static/images_real & manifest
    sync_local_images_to_static()

    # 2. Crop all plant foliage with 3-Layer Auto-Cropper (ml/crop_plants.py)
    run_step("[Step 2] Cropping plant foliage with 3-Layer Auto-Cropper (ml/crop_plants.py)", [ROOT_DIR / "ml" / "crop_plants.py"])

    # 3. Convert updated Excel log (hydroponic_log.xlsx) to sensor_log.json & sensor_data.js
    run_step("[Step 3] Updating sensor logs from hydroponic_log.xlsx (data/prepare_logs.py)", [ROOT_DIR / "data" / "prepare_logs.py"])

    # 4. ONLY Train if explicitly requested via --train
    if args.train:
        run_step("[Step 4] Refreshing multi-patch & external datasets", [ROOT_DIR / "data" / "download_external_datasets.py"])
        train_args = [ROOT_DIR / "Ai มหาปลัย" / "model" / "train_ensemble_model.py"]
        if not args.full:
            train_args.append("--incremental")
        run_step("[Step 5] Training Symptom-Gated Multimodal Ensemble & Updating Report Figures", train_args)
    else:
        print("\n⏸️  [Training Paused by Rule] ซิงก์ข้อมูลและอัปเดต Dashboard เรียบร้อยแล้ว (ยังไม่ได้เริ่มเทรนโมเดล)")
        print("   👉 หากต้องการสั่งเทรนโมเดล ให้รันคำสั่ง: .\\ai-env312\\Scripts\\python.exe update_and_retrain.py --train")

    elapsed = time.time() - t0
    print("\n" + "=" * 74)
    print(f"  ✅ DATA & DASHBOARD SYNC COMPLETED IN {elapsed:.1f}s!")
    print("  📊 Open server/static/dashboard_control.html or dashboard_smooth.html to view.")
    print("=" * 74)


if __name__ == "__main__":
    main()

