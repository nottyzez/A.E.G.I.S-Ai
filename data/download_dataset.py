"""
download_dataset.py — Synchronize all plant images from Google Drive dataset.

Downloads:
  1. 4 Foam Tanks (Control, N, P, K) — All images up to 21 Oct 2026
  2. 8 Cups (Cup1 - Cup8) — Images for Replicate 1 & 2 for all 4 groups

Saves to:
  - Ai มหาปลัย/dataset_real/images/{tank}/
  - server/static/images_real/{tank}/
  - Updates server/static/data/images_manifest.js
"""

import urllib.request
import re
import json
import os
import sys
import io
import shutil
from pathlib import Path

# Fix Windows console UTF-8 encoding
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
except Exception:
    pass

ROOT_DIR = Path(__file__).resolve().parent.parent
DATASET_IMG_DIR = ROOT_DIR / "Ai มหาปลัย" / "dataset_real" / "images"
STATIC_IMG_DIR = ROOT_DIR / "server" / "static" / "images_real"
MANIFEST_PATH = ROOT_DIR / "server" / "static" / "data" / "images_manifest.js"

# Structure of Google Drive Folder
FOAM_BOX_FOLDERS = {
    "Control": "1l2we6toFKY0YFRWHuWtqm-oSgw-5kiom",
    "N": "1JjYOOh0ukU2c-_2v47Fy9idTTm7BL2hr",
    "P": "1oB7ZFk8AqJ01v0mF2KpU-EoZeAEP8dLX",
    "K": "11Ut8gaROcAfxiKlPPGFZe8v2DjCl4wP0",
}

# In 'แก้ว 650 ml น้ำดื่ม', each group has subfolder '1' and '2':
CUP_GROUP_FOLDERS = {
    "Control": {
        "folder_id": "1GcSP8ktStIIErPuNIXN-vmMPuyFvhPl9",
        "sub": {"1": "Cup1", "2": "Cup2"}
    },
    "N": {
        "folder_id": "1w7gwMh2YQ-d5Fcby6bM_sQrUJ7LoMpDS",
        "sub": {"1": "Cup3", "2": "Cup4"}
    },
    "P": {
        "folder_id": "1n3odwv3TxMe3vibzZjk4pLjTuMMVViCP",
        "sub": {"1": "Cup5", "2": "Cup6"}
    },
    "K": {
        "folder_id": "1RzUXHQ2vh8Ne0G_7aHoo4cUUfu60oz7n",
        "sub": {"1": "Cup7", "2": "Cup8"}
    },
}


def sanitize_filename(name):
    """Sanitize Google Drive name to safe Windows filename."""
    # Replace slashes and colons: e.g. 20/10/2026-time17:00.jpg -> 20_10_2026-time17_00.jpg
    s = name.replace("/", "_").replace(":", "_").replace("\\", "_")
    return s


def get_folder_items(folder_id):
    """Retrieve list of files/folders in a Google Drive folder."""
    url = f'https://drive.google.com/drive/folders/{folder_id}?usp=sharing'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error fetching folder {folder_id}: {e}")
        return []

    match = re.search(r"window\['_DRIVE_ivd'\]\s*=\s*'([^']+)'", html)
    if not match:
        return []

    encoded_str = match.group(1)
    # decode escape sequences
    decoded_str = encoded_str.encode().decode('unicode_escape')
    data = json.loads(decoded_str)

    items = []
    if data and len(data) > 0 and data[0]:
        for item in data[0]:
            file_id = item[0]
            raw_name = item[2]
            try:
                name = raw_name.encode('latin1').decode('utf-8')
            except Exception:
                name = raw_name
            mime_type = item[3]
            items.append({
                "id": file_id,
                "name": name,
                "mime": mime_type,
            })
    return items


def download_file(file_id, dest_path):
    """Download public Google Drive file."""
    if dest_path.exists() and dest_path.stat().st_size > 10000:
        return True  # Already downloaded

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    url = f"https://drive.usercontent.google.com/download?id={file_id}&export=download"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read()
            with open(dest_path, "wb") as f:
                f.write(content)
        return True
    except Exception as e:
        print(f"  ❌ Error downloading {dest_path.name}: {e}")
        return False


def sync_all():
    print("🚀 Starting Google Drive Dataset Synchronization...")
    all_targets = {}  # unit_name -> list of files

    # 1. Sync Foam Tanks (Control, N, P, K)
    for tank_name, fid in FOAM_BOX_FOLDERS.items():
        print(f"\n📦 Checking Tank: {tank_name} ...")
        dest_ds = DATASET_IMG_DIR / tank_name
        dest_static = STATIC_IMG_DIR / tank_name
        dest_ds.mkdir(parents=True, exist_ok=True)
        dest_static.mkdir(parents=True, exist_ok=True)

        items = get_folder_items(fid)
        files_for_tank = []
        for it in items:
            if "image" in it["mime"] or it["name"].lower().endswith((".jpg", ".png", ".jpeg")):
                safe_name = sanitize_filename(it["name"])
                files_for_tank.append(safe_name)
                f_path = dest_ds / safe_name
                if not f_path.exists() or f_path.stat().st_size < 1000:
                    print(f"  ⬇️ Downloading {tank_name}/{safe_name} ...")
                    if download_file(it["id"], f_path):
                        shutil.copy2(f_path, dest_static / safe_name)
                else:
                    # Ensure static copy exists
                    if not (dest_static / safe_name).exists():
                        shutil.copy2(f_path, dest_static / safe_name)

        all_targets[tank_name] = sorted(files_for_tank)
        print(f"  ✅ Tank {tank_name}: {len(files_for_tank)} images")

    # 2. Sync Cup Groups (Cup1 to Cup8)
    for group_name, group_cfg in CUP_GROUP_FOLDERS.items():
        print(f"\n🥛 Checking Cups Group: {group_name} ...")
        # Get subfolders '1' and '2'
        sub_items = get_folder_items(group_cfg["folder_id"])
        for sub_it in sub_items:
            sub_name = sub_it["name"].strip()
            if sub_name in group_cfg["sub"]:
                cup_id = group_cfg["sub"][sub_name]
                print(f"   🔍 Inspecting {cup_id} (subfolder '{sub_name}')...")
                dest_ds = DATASET_IMG_DIR / cup_id
                dest_static = STATIC_IMG_DIR / cup_id
                dest_ds.mkdir(parents=True, exist_ok=True)
                dest_static.mkdir(parents=True, exist_ok=True)

                cup_files = get_folder_items(sub_it["id"])
                files_for_cup = []
                for it in cup_files:
                    if "image" in it["mime"] or it["name"].lower().endswith((".jpg", ".png", ".jpeg")):
                        safe_name = sanitize_filename(it["name"])
                        files_for_cup.append(safe_name)
                        f_path = dest_ds / safe_name
                        if not f_path.exists() or f_path.stat().st_size < 1000:
                            print(f"     ⬇️ Downloading {cup_id}/{safe_name} ...")
                            if download_file(it["id"], f_path):
                                shutil.copy2(f_path, dest_static / safe_name)
                        else:
                            if not (dest_static / safe_name).exists():
                                shutil.copy2(f_path, dest_static / safe_name)

                all_targets[cup_id] = sorted(files_for_cup)
                print(f"     ✅ {cup_id}: {len(files_for_cup)} images")

    # 3. Write images_manifest.js and images_manifest.json
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    js_content = "window.IMAGES_MANIFEST = " + json.dumps(all_targets, ensure_ascii=False) + ";\n"
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        f.write(js_content)

    json_path = ROOT_DIR / "data" / "images_manifest.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_targets, f, ensure_ascii=False, indent=2)

    print("\n🎉 Synchronization complete!")
    print(f"   Updated manifest at: {MANIFEST_PATH}")
    for k, v in all_targets.items():
        print(f"   - {k}: {len(v)} images")


if __name__ == "__main__":
    sync_all()
