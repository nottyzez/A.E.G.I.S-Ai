"""
╔══════════════════════════════════════════════════════════════════╗
║  Hydroponic Water-Spinach NPK Deficiency Detector               ║
║  Two-Stage Fine-Tuning + Late Fusion (Image CNN + Sensor MLP)   ║
║  + Grad-CAM Visualization for Project Report                    ║
╚══════════════════════════════════════════════════════════════════╝

Architecture:
  Stream A — MobileNetV2 (Fine-Tuned) → softmax → P_img(class)
  Stream B — Sensor MLP (EC, pH, temp, EC_trend) → softmax → P_sen(class)
  Late Fusion — weighted average at probability level:
      P_final = w_img * P_img + w_sen * P_sen

Dataset:
  - 44 real hydroponic top-view photos (4 tanks × ~11 time-points)
  - EC / pH / temperature sensor logs from Excel
  - Heavy augmentation (×30 per image) to expand to ~1,320 samples
"""

import os
import sys
import io
import re
import glob
import warnings
import pickle
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')           # ไม่ต้องเปิดหน้าต่าง
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns

import tensorflow as tf
from tensorflow.keras import layers, Model, regularizers
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.callbacks import (
    EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
)
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    confusion_matrix, classification_report, ConfusionMatrixDisplay,
    accuracy_score, f1_score
)

# ── ปิด warning ที่ไม่จำเป็น ──────────────────────────────────────────────────
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# ── ตั้งค่า stdout เป็น UTF-8 เพื่อรองรับภาษาไทย ──────────────────────────────
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
except:
    pass

# ==============================================================================
# CONFIG
# ==============================================================================
# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = Path(r'D:\Code มหาปลัย\Ai มหาปลัย')
DATASET_DIR = BASE_DIR / 'dataset_real' / 'images'
EXCEL_PATH  = BASE_DIR / 'dataset_real' / 'hydroponic_log.xlsx'
OUTPUT_DIR  = BASE_DIR / 'model' / 'output'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Hyper-parameters ──────────────────────────────────────────────────────────
IMG_SIZE       = (224, 224)
BATCH_SIZE     = 8           # เล็ก เพราะ dataset น้อย
STAGE1_EPOCHS  = 30          # Freeze base — train head only
STAGE2_EPOCHS  = 40          # Fine-tune top layers
STAGE1_LR      = 1e-3
STAGE2_LR      = 1e-5
NUM_CLASSES    = 4
CLASSES        = ['healthy', 'nitrogen', 'phosphorus', 'potassium']
AUGMENT_FACTOR = 30          # แต่ละรูป augment กี่ครั้ง

# ── Fusion weights (ปรับตามวันที่/ระยะการเจริญเติบโต) ─────────────────────────
W_IMG_DEFAULT  = 0.55
W_SEN_DEFAULT  = 0.45

# ── Folder → Label mapping ────────────────────────────────────────────────────
FOLDER_TO_LABEL = {
    'Control': 'healthy',
    'N':       'nitrogen',
    'P':       'phosphorus',
    'K':       'potassium',
}

LABEL_TO_THAI = {
    'healthy':    'ปกติ (Control)',
    'nitrogen':   'ขาด N (Nitrogen)',
    'phosphorus': 'ขาด P (Phosphorus)',
    'potassium':  'ขาด K (Potassium)',
}

print("=" * 70)
print("  🌱 Hydroponic Water-Spinach NPK Deficiency Detector")
print("  📐 Two-Stage Fine-Tuning + Late Fusion + Grad-CAM")
print("=" * 70)


# ==============================================================================
# STEP 1 — LOAD & PARSE SENSOR DATA FROM EXCEL
# ==============================================================================
print("\n📊 [Step 1] Loading sensor data from Excel...")

def parse_sensor_sheet(excel_path, sheet_name, label):
    """อ่านข้อมูลเซนเซอร์จาก sheet ที่มี format แบบ manual log"""
    df_raw = pd.read_excel(excel_path, sheet_name=sheet_name, header=None)

    # หาแถวที่เป็น header (มีคำว่า 'วันที่')
    header_row = None
    baseline_ec = None
    for i, row in df_raw.iterrows():
        vals = [str(v) for v in row.values]
        joined = ' '.join(vals)
        if 'Baseline' in joined:
            # หา baseline EC
            for v in row.values:
                try:
                    val = float(v)
                    if 0.5 < val < 10:
                        baseline_ec = val
                except (ValueError, TypeError):
                    pass
        if 'วันที่' in joined:
            header_row = i
            break

    if header_row is None:
        print(f"  ⚠️  ไม่พบ header ใน sheet '{sheet_name}'")
        return pd.DataFrame()

    # อ่านข้อมูลหลัง header
    df = df_raw.iloc[header_row + 1:].copy()
    df.columns = ['date', 'time', 'EC', 'pH_before', 'pH_after',
                  'water_temp', 'EC_change_pct', 'image_file', 'note', 'round']

    # แปลงค่า
    records = []
    for _, row in df.iterrows():
        try:
            ec_val = float(row['EC'])
        except (ValueError, TypeError):
            continue  # skip rows ที่ไม่มีค่า EC

        # ใช้ pH หลังปรับ (pH_after) ถ้ามี ไม่งั้นใช้ pH ก่อนปรับ
        ph_val = None
        for ph_col in ['pH_after', 'pH_before']:
            try:
                ph_val = float(row[ph_col])
                break
            except (ValueError, TypeError):
                continue
        if ph_val is None:
            ph_val = 6.5  # default

        temp_val = 28.0
        try:
            temp_val = float(row['water_temp'])
        except (ValueError, TypeError):
            pass

        # คำนวณ EC deviation จาก baseline
        ec_dev = 0.0
        if baseline_ec and baseline_ec > 0:
            ec_dev = (ec_val - baseline_ec) / baseline_ec

        # parse datetime เพื่อจับคู่กับรูปภาพ
        date_str = str(row['date']).split(' ')[0] if pd.notna(row['date']) else None
        time_str = str(row['time']).strip() if pd.notna(row['time']) else None

        records.append({
            'date_str':     date_str,
            'time_str':     time_str,
            'EC':           ec_val,
            'pH':           ph_val,
            'water_temp':   temp_val,
            'EC_baseline':  baseline_ec or ec_val,
            'EC_change':    ec_dev,
            'label':        label,
        })

    return pd.DataFrame(records)


# อ่านทุก sheet
sensor_dfs = []
sheet_map = {
    'Control': 'healthy',
    'ขาด N':  'nitrogen',
    'ขาด P':  'phosphorus',
    'ขาด K':  'potassium',
}

for sheet_name, label in sheet_map.items():
    df_sheet = parse_sensor_sheet(EXCEL_PATH, sheet_name, label)
    if len(df_sheet) > 0:
        sensor_dfs.append(df_sheet)
        print(f"  ✅ Sheet '{sheet_name}' → {len(df_sheet)} records (label: {label})")

df_sensor = pd.concat(sensor_dfs, ignore_index=True)
print(f"\n  📋 Total sensor records: {len(df_sensor)}")
print(f"  📋 Label distribution:\n{df_sensor['label'].value_counts().to_string()}")


# ==============================================================================
# STEP 2 — LOAD IMAGES & MATCH WITH SENSOR DATA
# ==============================================================================
print("\n📸 [Step 2] Loading images & matching with sensor data...")

def parse_image_datetime(filename):
    """แปลงชื่อไฟล์ภาพ → (date, time_approx)
    Examples: '10_10_2026.jpg', '11_10_2026-time18_00.jpg', '11_10_2026_time-10_00.jpg'
    """
    name = Path(filename).stem
    # ลอง pattern: DD_MM_YYYY-timeHH_MM หรือ DD_MM_YYYY_time-HH_MM
    m = re.match(r'(\d{2})_(\d{2})_(\d{4})(?:[-_]time[-_]?(\d{1,2})_(\d{2}))?', name)
    if m:
        day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
        hour = int(m.group(4)) if m.group(4) else 12
        minute = int(m.group(5)) if m.group(5) else 0
        try:
            dt = datetime(year, month, day, hour, minute)
            return dt
        except ValueError:
            pass
    return None


def find_closest_sensor(img_dt, label, df_sensor, max_hours=12):
    """หาแถวเซนเซอร์ที่ใกล้เคียงที่สุดกับเวลาถ่ายรูป"""
    df_match = df_sensor[df_sensor['label'] == label].copy()
    if len(df_match) == 0:
        return None

    best_diff = timedelta(hours=999)
    best_row = None

    for _, row in df_match.iterrows():
        try:
            date_parts = row['date_str'].split('-')
            d = datetime.strptime(date_parts[0], '%Y')
            # parse YYYY-MM-DD
            d = datetime.strptime(row['date_str'], '%Y-%m-%d')

            # parse time
            t_str = str(row['time_str']).replace(' ', '')
            t_parts = t_str.split(':')
            d = d.replace(hour=int(t_parts[0]), minute=int(t_parts[1]))
        except Exception:
            continue

        diff = abs(img_dt - d)
        if diff < best_diff:
            best_diff = diff
            best_row = row

    if best_diff > timedelta(hours=max_hours):
        return None
    return best_row


# สร้าง paired dataset: (image_path, sensor_features, label)
paired_data = []

for folder_name, label in FOLDER_TO_LABEL.items():
    folder_path = DATASET_DIR / folder_name
    if not folder_path.exists():
        print(f"  ⚠️  ไม่พบ folder: {folder_path}")
        continue

    images = sorted(glob.glob(str(folder_path / '*.jpg')))
    for img_path in images:
        img_dt = parse_image_datetime(Path(img_path).name)
        if img_dt is None:
            continue

        sensor_row = find_closest_sensor(img_dt, label, df_sensor)

        if sensor_row is not None:
            paired_data.append({
                'image_path': img_path,
                'label':      label,
                'EC':         sensor_row['EC'],
                'pH':         sensor_row['pH'],
                'water_temp': sensor_row['water_temp'],
                'EC_change':  sensor_row['EC_change'],
                'datetime':   img_dt,
            })
        else:
            # ถ้าไม่เจอเซนเซอร์ที่ตรง ใช้ค่าเฉลี่ยของ label นั้น
            df_label = df_sensor[df_sensor['label'] == label]
            paired_data.append({
                'image_path': img_path,
                'label':      label,
                'EC':         df_label['EC'].mean(),
                'pH':         df_label['pH'].mean(),
                'water_temp': df_label['water_temp'].mean(),
                'EC_change':  df_label['EC_change'].mean(),
                'datetime':   img_dt,
            })

df_paired = pd.DataFrame(paired_data)
print(f"\n  📋 Paired samples (image + sensor): {len(df_paired)}")
print(f"  📋 Per-class: {dict(df_paired['label'].value_counts())}")


# ==============================================================================
# STEP 3 — HEAVY IMAGE AUGMENTATION (Small Dataset Strategy)
# ==============================================================================
print(f"\n🔄 [Step 3] Heavy augmentation (×{AUGMENT_FACTOR} per image)...")
print("  ⏳ Loading & augmenting images — this may take a minute...")

# Augmentation pipeline (ใน tf.data)
augmentation_layer = tf.keras.Sequential([
    layers.RandomFlip("horizontal_and_vertical"),
    layers.RandomRotation(0.20),
    layers.RandomZoom((-0.15, 0.15)),
    layers.RandomContrast(0.15),
    layers.RandomBrightness(0.1),
    layers.RandomTranslation(0.1, 0.1),
], name='augmentation')


def load_and_preprocess_image(path, augment=False):
    """โหลดรูปภาพ → resize → normalize"""
    img = tf.io.read_file(path)
    img = tf.image.decode_jpeg(img, channels=3)
    img = tf.image.resize(img, IMG_SIZE)
    img = tf.cast(img, tf.float32) / 255.0
    if augment:
        img = augmentation_layer(img, training=True)
        img = tf.clip_by_value(img, 0.0, 1.0)
    return img


# สร้าง augmented dataset
all_images = []
all_sensors = []
all_labels = []

le = LabelEncoder()
le.fit(CLASSES)

for _, row in df_paired.iterrows():
    img_path = row['image_path']
    label_enc = le.transform([row['label']])[0]
    sensor_feat = [row['EC'], row['pH'], row['water_temp'], row['EC_change']]

    # Original
    try:
        img_orig = load_and_preprocess_image(img_path, augment=False)
        all_images.append(img_orig.numpy())
        all_sensors.append(sensor_feat)
        all_labels.append(label_enc)
    except Exception as e:
        print(f"  ❌ Error loading {img_path}: {e}")
        continue

    # Augmented copies
    for _ in range(AUGMENT_FACTOR):
        try:
            img_aug = load_and_preprocess_image(img_path, augment=True)
            # Sensor ก็เพิ่ม noise เล็กน้อย (±5%) เพื่อให้โมเดลทนทาน
            noisy_sensor = [
                v * np.random.uniform(0.95, 1.05) for v in sensor_feat
            ]
            all_images.append(img_aug.numpy())
            all_sensors.append(noisy_sensor)
            all_labels.append(label_enc)
        except:
            pass

X_images  = np.array(all_images)
X_sensors = np.array(all_sensors, dtype=np.float32)
y_labels  = np.array(all_labels)

print(f"\n  ✅ Augmented dataset size: {len(X_images)} samples")
print(f"  ✅ Image shape:  {X_images.shape}")
print(f"  ✅ Sensor shape: {X_sensors.shape}")
print(f"  ✅ Labels:       {dict(zip(*np.unique(y_labels, return_counts=True)))}")


# ==============================================================================
# STEP 4 — TRAIN/VAL SPLIT (Stratified)
# ==============================================================================
print("\n✂️  [Step 4] Stratified train/val split (80/20)...")

# Scale sensor features
scaler = StandardScaler()
X_sensors_scaled = scaler.fit_transform(X_sensors)

(X_train_img, X_val_img,
 X_train_sen, X_val_sen,
 y_train, y_val) = train_test_split(
    X_images, X_sensors_scaled, y_labels,
    test_size=0.2, random_state=42, stratify=y_labels
)

print(f"  Train: {len(y_train)}  |  Val: {len(y_val)}")
print(f"  Train dist: {dict(zip(*np.unique(y_train, return_counts=True)))}")
print(f"  Val dist:   {dict(zip(*np.unique(y_val, return_counts=True)))}")


# ==============================================================================
# STEP 5 — BUILD IMAGE MODEL (MobileNetV2 — Two-Stage Fine-Tuning)
# ==============================================================================
print("\n🧠 [Step 5] Building Image Model (MobileNetV2)...")

def build_image_model():
    base_model = MobileNetV2(
        input_shape=(*IMG_SIZE, 3),
        include_top=False,
        weights='imagenet'
    )
    # Stage 1: Freeze ทั้งหมด
    base_model.trainable = False

    inputs = layers.Input(shape=(*IMG_SIZE, 3), name='image_input')
    x = base_model(inputs, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dense(256, activation='relu',
                     kernel_regularizer=regularizers.l2(1e-4))(x)
    x = layers.Dropout(0.5)(x)
    x = layers.Dense(128, activation='relu',
                     kernel_regularizer=regularizers.l2(1e-4))(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(NUM_CLASSES, activation='softmax', name='img_output')(x)

    model = Model(inputs=inputs, outputs=outputs, name='ImageModel_MobileNetV2')
    return model, base_model


img_model, base_mobilenet = build_image_model()
img_model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=STAGE1_LR),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

print(f"  ✅ Image model params: {img_model.count_params():,}")
print(f"  ✅ Trainable params (Stage 1 — Head only): "
      f"{sum(tf.keras.backend.count_params(w) for w in img_model.trainable_weights):,}")


# ── Stage 1: Train Head Only ─────────────────────────────────────────────────
print(f"\n🚀 [Stage 1] Training HEAD only ({STAGE1_EPOCHS} epochs, lr={STAGE1_LR})...")

callbacks_s1 = [
    EarlyStopping(patience=8, restore_best_weights=True, monitor='val_accuracy'),
    ReduceLROnPlateau(patience=4, factor=0.5, min_lr=1e-6, monitor='val_loss'),
]

history_s1 = img_model.fit(
    X_train_img, y_train,
    validation_data=(X_val_img, y_val),
    epochs=STAGE1_EPOCHS,
    batch_size=BATCH_SIZE,
    callbacks=callbacks_s1,
    verbose=1
)

s1_val_acc = max(history_s1.history['val_accuracy'])
print(f"  ✅ Stage 1 Best Val Accuracy: {s1_val_acc:.4f}")


# ── Stage 2: Fine-Tune Top Layers ────────────────────────────────────────────
print(f"\n🔬 [Stage 2] Fine-tuning TOP 30 layers ({STAGE2_EPOCHS} epochs, lr={STAGE2_LR})...")

base_mobilenet.trainable = True
# Freeze ทุกชั้นยกเว้น 30 ชั้นบนสุด
for layer in base_mobilenet.layers[:-30]:
    layer.trainable = False

trainable_count = sum(
    tf.keras.backend.count_params(w) for w in img_model.trainable_weights
)
print(f"  ✅ Trainable params (Stage 2): {trainable_count:,}")

img_model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=STAGE2_LR),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

callbacks_s2 = [
    EarlyStopping(patience=10, restore_best_weights=True, monitor='val_accuracy'),
    ReduceLROnPlateau(patience=5, factor=0.5, min_lr=1e-7, monitor='val_loss'),
    ModelCheckpoint(
        str(OUTPUT_DIR / 'best_image_model.keras'),
        save_best_only=True, monitor='val_accuracy'
    ),
]

history_s2 = img_model.fit(
    X_train_img, y_train,
    validation_data=(X_val_img, y_val),
    epochs=STAGE2_EPOCHS,
    batch_size=BATCH_SIZE,
    callbacks=callbacks_s2,
    verbose=1
)

s2_val_acc = max(history_s2.history['val_accuracy'])
print(f"  ✅ Stage 2 Best Val Accuracy: {s2_val_acc:.4f}")


# ==============================================================================
# STEP 6 — BUILD & TRAIN SENSOR MODEL (Gradient Boosting + MLP)
# ==============================================================================
print("\n📡 [Step 6] Training Sensor Model (GradientBoosting + MLP ensemble)...")

# ── Gradient Boosting (robust กับ small data) ─────────────────────────────────
gb_model = GradientBoostingClassifier(
    n_estimators=200,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.8,
    random_state=42,
)
gb_model.fit(X_train_sen, y_train)
gb_val_acc = accuracy_score(y_val, gb_model.predict(X_val_sen))
print(f"  ✅ GradientBoosting Val Accuracy: {gb_val_acc:.4f}")

# ── Random Forest (สำรอง) ─────────────────────────────────────────────────────
rf_model = RandomForestClassifier(
    n_estimators=300,
    max_depth=6,
    min_samples_leaf=3,
    random_state=42,
)
rf_model.fit(X_train_sen, y_train)
rf_val_acc = accuracy_score(y_val, rf_model.predict(X_val_sen))
print(f"  ✅ RandomForest Val Accuracy:     {rf_val_acc:.4f}")

# เลือกตัวที่ดีกว่า
if gb_val_acc >= rf_val_acc:
    sensor_model = gb_model
    sensor_model_name = 'GradientBoosting'
else:
    sensor_model = rf_model
    sensor_model_name = 'RandomForest'
print(f"  🏆 Selected: {sensor_model_name} (val_acc={max(gb_val_acc, rf_val_acc):.4f})")


# ==============================================================================
# STEP 7 — LATE FUSION (Weighted Probability Averaging)
# ==============================================================================
print("\n🔀 [Step 7] Late Fusion — Adaptive Weighted Averaging...")

# Image probabilities
P_img = img_model.predict(X_val_img, verbose=0)

# Sensor probabilities
P_sen = sensor_model.predict_proba(X_val_sen)

# ค้นหาน้ำหนัก fusion ที่ดีที่สุด (Grid Search)
best_w_img = 0.5
best_fusion_acc = 0.0

for w in np.arange(0.0, 1.05, 0.05):
    P_fused = w * P_img + (1.0 - w) * P_sen
    y_fused = np.argmax(P_fused, axis=1)
    acc = accuracy_score(y_val, y_fused)
    if acc > best_fusion_acc:
        best_fusion_acc = acc
        best_w_img = w

best_w_sen = round(1.0 - best_w_img, 2)
best_w_img = round(best_w_img, 2)

print(f"  🏆 Best Fusion Weights: w_img={best_w_img}, w_sen={best_w_sen}")
print(f"  🏆 Fusion Val Accuracy: {best_fusion_acc:.4f}")

# Final fusion predictions
P_final = best_w_img * P_img + best_w_sen * P_sen
y_pred_fusion = np.argmax(P_final, axis=1)

# เปรียบเทียบ
print(f"\n  📊 Comparison:")
print(f"     Image-only Val Acc:  {accuracy_score(y_val, np.argmax(P_img, axis=1)):.4f}")
print(f"     Sensor-only Val Acc: {accuracy_score(y_val, np.argmax(P_sen, axis=1)):.4f}")
print(f"     Fused Val Acc:       {best_fusion_acc:.4f}")


# ==============================================================================
# STEP 8 — SAVE MODELS
# ==============================================================================
print("\n💾 [Step 8] Saving all models & artifacts...")

img_model.save(str(OUTPUT_DIR / 'image_model.keras'))
with open(str(OUTPUT_DIR / 'sensor_model.pkl'), 'wb') as f:
    pickle.dump(sensor_model, f)
with open(str(OUTPUT_DIR / 'scaler.pkl'), 'wb') as f:
    pickle.dump(scaler, f)
with open(str(OUTPUT_DIR / 'label_encoder.pkl'), 'wb') as f:
    pickle.dump(le, f)
with open(str(OUTPUT_DIR / 'fusion_weights.pkl'), 'wb') as f:
    pickle.dump({'w_img': best_w_img, 'w_sen': best_w_sen}, f)

print(f"  ✅ Saved to: {OUTPUT_DIR}")


# ==============================================================================
# STEP 9 — PUBLICATION-QUALITY PLOTS FOR REPORT
# ==============================================================================
print("\n📊 [Step 9] Generating publication-quality plots...")

# ── Plot Style ────────────────────────────────────────────────────────────────
plt.rcParams.update({
    'figure.dpi':       150,
    'savefig.dpi':      300,
    'font.size':        11,
    'axes.titlesize':   13,
    'axes.labelsize':   11,
    'xtick.labelsize':  10,
    'ytick.labelsize':  10,
    'legend.fontsize':  10,
    'figure.facecolor': 'white',
    'axes.facecolor':   'white',
    'axes.grid':        True,
    'grid.alpha':       0.3,
})

COLORS = {
    'train':      '#2196F3',
    'val':        '#FF5722',
    'accent1':    '#4CAF50',
    'accent2':    '#FF9800',
    'bg_dark':    '#1a1a2e',
}


# ── 9A: Training History (Stage 1 + Stage 2 Combined) ────────────────────────
def combine_histories(h1, h2):
    combined = {}
    for key in h1.history:
        combined[key] = h1.history[key] + h2.history[key]
    return combined

history_all = combine_histories(history_s1, history_s2)
total_epochs = len(history_all['accuracy'])
stage1_end = len(history_s1.history['accuracy'])

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Accuracy
ax = axes[0]
ax.plot(range(1, total_epochs + 1), history_all['accuracy'],
        color=COLORS['train'], linewidth=2, label='Train Accuracy')
ax.plot(range(1, total_epochs + 1), history_all['val_accuracy'],
        color=COLORS['val'], linewidth=2, label='Validation Accuracy')
ax.axvline(x=stage1_end, color='gray', linestyle='--', alpha=0.7, label='Fine-tune Start')
ax.fill_betweenx([0, 1], 0, stage1_end, alpha=0.05, color='blue')
ax.fill_betweenx([0, 1], stage1_end, total_epochs, alpha=0.05, color='red')
ax.set_xlabel('Epoch')
ax.set_ylabel('Accuracy')
ax.set_title('Training & Validation Accuracy\n(Two-Stage Fine-Tuning)')
ax.legend(loc='lower right')
ax.set_ylim([0, 1.05])
ax.text(stage1_end / 2, 0.02, 'Stage 1\n(Head Only)',
        ha='center', fontsize=9, color='gray')
ax.text(stage1_end + (total_epochs - stage1_end) / 2, 0.02,
        'Stage 2\n(Fine-Tune)', ha='center', fontsize=9, color='gray')

# Loss
ax = axes[1]
ax.plot(range(1, total_epochs + 1), history_all['loss'],
        color=COLORS['train'], linewidth=2, label='Train Loss')
ax.plot(range(1, total_epochs + 1), history_all['val_loss'],
        color=COLORS['val'], linewidth=2, label='Validation Loss')
ax.axvline(x=stage1_end, color='gray', linestyle='--', alpha=0.7, label='Fine-tune Start')
ax.set_xlabel('Epoch')
ax.set_ylabel('Loss')
ax.set_title('Training & Validation Loss\n(Two-Stage Fine-Tuning)')
ax.legend(loc='upper right')

plt.tight_layout()
plt.savefig(str(OUTPUT_DIR / 'fig1_training_history.png'),
            bbox_inches='tight', facecolor='white')
plt.close()
print("  ✅ fig1_training_history.png")


# ── 9B: Confusion Matrix (Image Model) ──────────────────────────────────────
y_pred_img = np.argmax(P_img, axis=1)

fig, axes = plt.subplots(1, 3, figsize=(20, 5.5))

# Image-only CM
cm_img = confusion_matrix(y_val, y_pred_img)
sns.heatmap(cm_img, annot=True, fmt='d', cmap='Blues',
            xticklabels=CLASSES, yticklabels=CLASSES, ax=axes[0],
            cbar_kws={'shrink': 0.8})
axes[0].set_title('Image Model (MobileNetV2)\nConfusion Matrix')
axes[0].set_ylabel('Actual')
axes[0].set_xlabel('Predicted')

# Sensor-only CM
y_pred_sen = np.argmax(P_sen, axis=1)
cm_sen = confusion_matrix(y_val, y_pred_sen)
sns.heatmap(cm_sen, annot=True, fmt='d', cmap='Greens',
            xticklabels=CLASSES, yticklabels=CLASSES, ax=axes[1],
            cbar_kws={'shrink': 0.8})
axes[1].set_title(f'Sensor Model ({sensor_model_name})\nConfusion Matrix')
axes[1].set_ylabel('Actual')
axes[1].set_xlabel('Predicted')

# Fusion CM
cm_fusion = confusion_matrix(y_val, y_pred_fusion)
sns.heatmap(cm_fusion, annot=True, fmt='d', cmap='Oranges',
            xticklabels=CLASSES, yticklabels=CLASSES, ax=axes[2],
            cbar_kws={'shrink': 0.8})
axes[2].set_title(f'Late Fusion (w_img={best_w_img}, w_sen={best_w_sen})\nConfusion Matrix')
axes[2].set_ylabel('Actual')
axes[2].set_xlabel('Predicted')

plt.tight_layout()
plt.savefig(str(OUTPUT_DIR / 'fig2_confusion_matrices.png'),
            bbox_inches='tight', facecolor='white')
plt.close()
print("  ✅ fig2_confusion_matrices.png")


# ── 9C: Classification Report (Text → Image) ────────────────────────────────
report_fusion = classification_report(y_val, y_pred_fusion,
                                       target_names=CLASSES, output_dict=True)
report_img    = classification_report(y_val, y_pred_img,
                                       target_names=CLASSES, output_dict=True)
report_sen    = classification_report(y_val, y_pred_sen,
                                       target_names=CLASSES, output_dict=True)

# สรุปเป็นตาราง
fig, ax = plt.subplots(figsize=(10, 4))
ax.axis('off')

table_data = [['Model', 'Accuracy', 'F1 (macro)', 'Precision (macro)', 'Recall (macro)']]
for name, report in [('Image (CNN)', report_img),
                     (f'Sensor ({sensor_model_name})', report_sen),
                     ('Late Fusion', report_fusion)]:
    table_data.append([
        name,
        f"{report['accuracy']:.4f}",
        f"{report['macro avg']['f1-score']:.4f}",
        f"{report['macro avg']['precision']:.4f}",
        f"{report['macro avg']['recall']:.4f}",
    ])

table = ax.table(cellText=table_data[1:], colLabels=table_data[0],
                 loc='center', cellLoc='center')
table.auto_set_font_size(False)
table.set_fontsize(11)
table.scale(1.2, 1.8)

# Style header
for j in range(5):
    table[0, j].set_facecolor('#2196F3')
    table[0, j].set_text_props(color='white', fontweight='bold')

# Highlight best row
best_row = np.argmax([float(table_data[i+1][1]) for i in range(3)]) + 1
for j in range(5):
    table[best_row, j].set_facecolor('#E8F5E9')

ax.set_title('Model Performance Comparison', fontsize=14, fontweight='bold', pad=20)
plt.savefig(str(OUTPUT_DIR / 'fig3_performance_table.png'),
            bbox_inches='tight', facecolor='white')
plt.close()
print("  ✅ fig3_performance_table.png")


# ── 9D: Accuracy Comparison Bar Chart ─────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))

model_names = ['Image\n(MobileNetV2)', f'Sensor\n({sensor_model_name})',
               f'Late Fusion\n(w={best_w_img}/{best_w_sen})']
accs = [
    accuracy_score(y_val, y_pred_img),
    accuracy_score(y_val, y_pred_sen),
    best_fusion_acc
]
colors = ['#2196F3', '#4CAF50', '#FF9800']
bars = ax.bar(model_names, accs, color=colors, width=0.5, edgecolor='white')

for bar, acc in zip(bars, accs):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
            f'{acc:.1%}', ha='center', va='bottom', fontweight='bold', fontsize=12)

ax.set_ylim([0, 1.15])
ax.set_ylabel('Accuracy')
ax.set_title('Validation Accuracy Comparison\n(Image vs Sensor vs Late Fusion)')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig(str(OUTPUT_DIR / 'fig4_accuracy_comparison.png'),
            bbox_inches='tight', facecolor='white')
plt.close()
print("  ✅ fig4_accuracy_comparison.png")


# ── 9E: Sensor Feature Importance ────────────────────────────────────────────
feature_names = ['EC (mS/cm)', 'pH', 'Water Temp (°C)', 'EC Change (%)']

if hasattr(sensor_model, 'feature_importances_'):
    importances = sensor_model.feature_importances_
    fig, ax = plt.subplots(figsize=(8, 4))
    sorted_idx = np.argsort(importances)
    ax.barh(range(len(sorted_idx)), importances[sorted_idx],
            color='#4CAF50', edgecolor='white')
    ax.set_yticks(range(len(sorted_idx)))
    ax.set_yticklabels([feature_names[i] for i in sorted_idx])
    ax.set_xlabel('Feature Importance')
    ax.set_title(f'Sensor Feature Importance ({sensor_model_name})')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig(str(OUTPUT_DIR / 'fig5_feature_importance.png'),
                bbox_inches='tight', facecolor='white')
    plt.close()
    print("  ✅ fig5_feature_importance.png")


# ==============================================================================
# STEP 10 — GRAD-CAM VISUALIZATION
# ==============================================================================
print("\n🔥 [Step 10] Generating Grad-CAM heatmaps...")


def make_gradcam_heatmap(img_array, model, last_conv_layer_name=None):
    """สร้าง Grad-CAM heatmap จากภาพ"""
    # หา last conv layer อัตโนมัติ
    if last_conv_layer_name is None:
        for layer in reversed(model.layers):
            if isinstance(layer, tf.keras.Model):
                # ใน base model (MobileNetV2) หา conv layer สุดท้าย
                for sub_layer in reversed(layer.layers):
                    if len(sub_layer.output_shape) == 4:  # conv layer
                        last_conv_layer_name = sub_layer.name
                        base_for_gradcam = layer
                        break
                break

    if last_conv_layer_name is None:
        return None

    # สร้างโมเดลย่อยสำหรับ Grad-CAM
    # ใช้ functional approach ที่ทำงานกับ nested model
    try:
        # สร้าง sub-model ที่ output ทั้ง conv features และ predictions
        grad_model = tf.keras.Model(
            inputs=model.input,
            outputs=[
                base_for_gradcam.get_layer(last_conv_layer_name).output,
                model.output
            ]
        )

        with tf.GradientTape() as tape:
            img_tensor = tf.cast(img_array, tf.float32)
            conv_outputs, predictions = grad_model(img_tensor)
            pred_index = tf.argmax(predictions[0])
            class_channel = predictions[:, pred_index]

        grads = tape.gradient(class_channel, conv_outputs)
        if grads is None:
            return None

        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        conv_outputs = conv_outputs[0]
        heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)
        heatmap = tf.maximum(heatmap, 0) / (tf.math.reduce_max(heatmap) + 1e-8)

        return heatmap.numpy()
    except Exception as e:
        print(f"    Grad-CAM error: {e}")
        return None


def overlay_gradcam(img, heatmap, alpha=0.4):
    """ซ้อน heatmap ลงบนภาพต้นฉบับ"""
    heatmap_resized = tf.image.resize(
        heatmap[..., np.newaxis], (img.shape[0], img.shape[1])
    ).numpy().squeeze()

    # สร้าง colormap
    cmap = plt.cm.jet
    heatmap_colored = cmap(heatmap_resized)[:, :, :3]

    superimposed = heatmap_colored * alpha + img * (1 - alpha)
    return np.clip(superimposed, 0, 1)


# เลือกตัวอย่างจาก val set (1 รูปต่อ class)
fig, axes = plt.subplots(NUM_CLASSES, 3, figsize=(14, 4 * NUM_CLASSES))

for class_idx in range(NUM_CLASSES):
    # หาตัวอย่างแรกของแต่ละ class ใน val set
    sample_indices = np.where(y_val == class_idx)[0]
    if len(sample_indices) == 0:
        continue

    sample_idx = sample_indices[0]
    img = X_val_img[sample_idx]
    img_batch = np.expand_dims(img, axis=0)

    # Prediction
    pred_probs = img_model.predict(img_batch, verbose=0)[0]
    pred_class = CLASSES[np.argmax(pred_probs)]
    pred_conf = np.max(pred_probs) * 100

    # Original image
    axes[class_idx, 0].imshow(img)
    axes[class_idx, 0].set_title(f'Original\nTrue: {CLASSES[class_idx]}')
    axes[class_idx, 0].axis('off')

    # Grad-CAM heatmap
    heatmap = make_gradcam_heatmap(img_batch, img_model)

    if heatmap is not None:
        axes[class_idx, 1].imshow(heatmap, cmap='jet')
        axes[class_idx, 1].set_title('Grad-CAM Heatmap')
        axes[class_idx, 1].axis('off')

        # Overlay
        overlay = overlay_gradcam(img, heatmap)
        axes[class_idx, 2].imshow(overlay)
        axes[class_idx, 2].set_title(
            f'Overlay\nPred: {pred_class} ({pred_conf:.1f}%)')
        axes[class_idx, 2].axis('off')
    else:
        axes[class_idx, 1].text(0.5, 0.5, 'Grad-CAM\nN/A',
                                ha='center', va='center', fontsize=14)
        axes[class_idx, 1].axis('off')
        axes[class_idx, 2].text(0.5, 0.5, 'N/A',
                                ha='center', va='center', fontsize=14)
        axes[class_idx, 2].axis('off')

plt.suptitle('Grad-CAM Visualization — Where AI Looks on Leaves',
             fontsize=16, fontweight='bold', y=1.01)
plt.tight_layout()
plt.savefig(str(OUTPUT_DIR / 'fig6_gradcam.png'),
            bbox_inches='tight', facecolor='white')
plt.close()
print("  ✅ fig6_gradcam.png")


# ── 10B: Grad-CAM Grid (หลายตัวอย่าง) ────────────────────────────────────────
# เลือก 3 ตัวอย่างต่อ class
n_samples_per_class = 3
fig, axes = plt.subplots(NUM_CLASSES, n_samples_per_class, figsize=(12, 4 * NUM_CLASSES))

for class_idx in range(NUM_CLASSES):
    sample_indices = np.where(y_val == class_idx)[0]
    for j in range(min(n_samples_per_class, len(sample_indices))):
        idx = sample_indices[j]
        img = X_val_img[idx]
        img_batch = np.expand_dims(img, axis=0)

        pred_probs = img_model.predict(img_batch, verbose=0)[0]
        pred_class = CLASSES[np.argmax(pred_probs)]

        heatmap = make_gradcam_heatmap(img_batch, img_model)
        if heatmap is not None:
            overlay = overlay_gradcam(img, heatmap)
            axes[class_idx, j].imshow(overlay)
        else:
            axes[class_idx, j].imshow(img)

        axes[class_idx, j].set_title(
            f'{CLASSES[class_idx]}\n→ {pred_class} ({np.max(pred_probs)*100:.0f}%)',
            fontsize=9)
        axes[class_idx, j].axis('off')

plt.suptitle('Grad-CAM Grid — Multiple Samples per Class',
             fontsize=14, fontweight='bold', y=1.01)
plt.tight_layout()
plt.savefig(str(OUTPUT_DIR / 'fig7_gradcam_grid.png'),
            bbox_inches='tight', facecolor='white')
plt.close()
print("  ✅ fig7_gradcam_grid.png")


# ==============================================================================
# STEP 11 — EC/pH TREND PLOTS (จากข้อมูลจริง)
# ==============================================================================
print("\n📈 [Step 11] Sensor trend plots from real data...")

tank_colors = {
    'healthy':    '#4CAF50',
    'nitrogen':   '#FFC107',
    'phosphorus': '#FF5722',
    'potassium':  '#9C27B0',
}

tank_labels = {
    'healthy':    'Control (ครบธาตุ)',
    'nitrogen':   'Tank -N',
    'phosphorus': 'Tank -P',
    'potassium':  'Tank -K',
}

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

for label in CLASSES:
    df_tank = df_sensor[df_sensor['label'] == label].copy()
    if len(df_tank) == 0:
        continue
    df_tank = df_tank.reset_index(drop=True)

    # EC plot
    axes[0].plot(range(len(df_tank)), df_tank['EC'].values,
                 marker='o', color=tank_colors[label],
                 linewidth=2, markersize=4, label=tank_labels[label])
    # pH plot
    axes[1].plot(range(len(df_tank)), df_tank['pH'].values,
                 marker='s', color=tank_colors[label],
                 linewidth=2, markersize=4, label=tank_labels[label])

axes[0].set_xlabel('Measurement Index')
axes[0].set_ylabel('EC (mS/cm)')
axes[0].set_title('EC Trend Over Time — 4 Tanks')
axes[0].legend(fontsize=9)
axes[0].axhline(y=2.0, color='gray', linestyle=':', alpha=0.5, label='Target EC')

axes[1].set_xlabel('Measurement Index')
axes[1].set_ylabel('pH')
axes[1].set_title('pH Trend Over Time — 4 Tanks')
axes[1].legend(fontsize=9)
axes[1].axhspan(5.8, 6.5, alpha=0.1, color='green', label='Optimal pH Range')

plt.tight_layout()
plt.savefig(str(OUTPUT_DIR / 'fig8_sensor_trends.png'),
            bbox_inches='tight', facecolor='white')
plt.close()
print("  ✅ fig8_sensor_trends.png")


# ==============================================================================
# STEP 12 — ARCHITECTURE DIAGRAM
# ==============================================================================
print("\n🏗️  [Step 12] Model architecture summary...")

fig, ax = plt.subplots(figsize=(12, 6))
ax.axis('off')

arch_text = """
┌─────────────────────────────────────────────────────────────────────────┐
│                    Late Fusion Architecture                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌──────────────────────┐      ┌──────────────────────┐                │
│  │   Stream A: Image    │      │  Stream B: Sensor    │                │
│  │                      │      │                      │                │
│  │  Input: 224×224×3    │      │  Input: 4 features   │
│  │  MobileNetV2 (FT)    │      │  (EC, pH, Temp,      │                │
│  │  → GAP → BN          │      │   EC_change)         │                │
│  │  → Dense(256) → DO   │      │                      │                │
│  │  → Dense(128) → DO   │      │  StandardScaler      │                │
│  │  → Softmax(4)        │      │  → GradientBoosting  │                │
│  │                      │      │  → predict_proba(4)  │                │
│  │  → P_img(class)      │      │  → P_sen(class)      │                │
│  └──────────┬───────────┘      └──────────┬───────────┘                │
│             │                              │                            │
│             └──────────┐    ┌──────────────┘                            │
│                        ▼    ▼                                           │
│              ┌─────────────────────┐                                    │
│              │   Weighted Average  │                                    │
│              │ w_img×P_img +       │                                    │
│              │ w_sen×P_sen         │                                    │
│              └─────────┬───────────┘                                    │
│                        ▼                                                │
│              ┌─────────────────────┐                                    │
│              │    Final Decision   │                                    │
│              │  healthy│-N│-P│-K   │                                    │
│              └─────────────────────┘                                    │
└─────────────────────────────────────────────────────────────────────────┘
"""

ax.text(0.05, 0.95, arch_text, transform=ax.transAxes,
        fontsize=9, verticalalignment='top', fontfamily='monospace',
        bbox=dict(boxstyle='round', facecolor='#f0f0f0', alpha=0.8))

plt.savefig(str(OUTPUT_DIR / 'fig9_architecture.png'),
            bbox_inches='tight', facecolor='white')
plt.close()
print("  ✅ fig9_architecture.png")


# ==============================================================================
# STEP 13 — PRINT CLASSIFICATION REPORT
# ==============================================================================
print("\n" + "=" * 70)
print("  📊 FINAL CLASSIFICATION REPORT (Late Fusion)")
print("=" * 70)
print(classification_report(y_val, y_pred_fusion, target_names=CLASSES))

print("=" * 70)
print("  📊 IMAGE MODEL REPORT")
print("=" * 70)
print(classification_report(y_val, y_pred_img, target_names=CLASSES))

print("=" * 70)
print(f"  📊 SENSOR MODEL REPORT ({sensor_model_name})")
print("=" * 70)
print(classification_report(y_val, y_pred_sen, target_names=CLASSES))


# ==============================================================================
# STEP 14 — SUMMARY
# ==============================================================================
print("\n" + "=" * 70)
print("  🎉 TRAINING COMPLETE!")
print("=" * 70)
print(f"""
  Dataset:
    • Original images:        {len(df_paired)} (4 tanks × ~11 time-points)
    • After augmentation:     {len(X_images)} samples (×{AUGMENT_FACTOR})
    • Sensor records:         {len(df_sensor)} measurements
    • Train / Val split:      {len(y_train)} / {len(y_val)}

  Image Model (MobileNetV2 Two-Stage Fine-Tuning):
    • Stage 1 Val Accuracy:   {s1_val_acc:.4f} (Head Only, {len(history_s1.history['accuracy'])} epochs)
    • Stage 2 Val Accuracy:   {s2_val_acc:.4f} (Fine-Tune Top 30, {len(history_s2.history['accuracy'])} epochs)

  Sensor Model ({sensor_model_name}):
    • Val Accuracy:           {max(gb_val_acc, rf_val_acc):.4f}

  Late Fusion:
    • Optimal Weights:        w_img={best_w_img}, w_sen={best_w_sen}
    • Fusion Val Accuracy:    {best_fusion_acc:.4f}

  Saved Models:
    • {OUTPUT_DIR / 'image_model.keras'}
    • {OUTPUT_DIR / 'sensor_model.pkl'}
    • {OUTPUT_DIR / 'scaler.pkl'}
    • {OUTPUT_DIR / 'label_encoder.pkl'}
    • {OUTPUT_DIR / 'fusion_weights.pkl'}

  Report Figures ({OUTPUT_DIR}):
    • fig1_training_history.png     — Accuracy/Loss curves (Two-Stage)
    • fig2_confusion_matrices.png   — CM: Image, Sensor, Fusion
    • fig3_performance_table.png    — Model comparison table
    • fig4_accuracy_comparison.png  — Bar chart comparison
    • fig5_feature_importance.png   — Sensor feature importance
    • fig6_gradcam.png              — Grad-CAM per class
    • fig7_gradcam_grid.png         — Grad-CAM grid (multiple samples)
    • fig8_sensor_trends.png        — EC/pH trends from real data
    • fig9_architecture.png         — System architecture diagram
""")
