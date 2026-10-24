"""
ไฟล์ที่ 1: เตรียมข้อมูล
- โครงสร้างโฟลเดอร์รูปภาพ
- สร้างข้อมูล EC/pH/ความชื้น (Synthetic)
"""

import numpy as np
import pandas as pd
import os

# ============================================================
# 1. โครงสร้างโฟลเดอร์ที่ต้องมี
# ============================================================
# dataset/
# ├── train/
# │   ├── normal/        ← รูปใบปกติ
# │   ├── nitrogen/      ← รูปใบขาด N
# │   ├── phosphorus/    ← รูปใบขาด P
# │   └── potassium/     ← รูปใบขาด K
# └── val/
#     ├── normal/
#     ├── nitrogen/
#     ├── phosphorus/
#     └── potassium/

# ============================================================
# 2. ค่ามาตรฐานผักเคล
# ============================================================
STANDARD = {
    'pH':       {'min': 6.0, 'max': 7.0, 'mid': 6.5},
    'EC':       {'min': 1.5, 'max': 2.5, 'mid': 2.0},
    'moisture': {'min': 60,  'max': 80,  'mid': 70}
}

# ============================================================
# 3. สร้างข้อมูล Synthetic (ใช้ระหว่างรอเก็บข้อมูลจริง)
# ============================================================
np.random.seed(42)
n = 200

data = []

# Normal
for _ in range(n):
    data.append([np.random.uniform(6.0, 7.0),
                 np.random.uniform(1.5, 2.5),
                 np.random.uniform(60, 80), 'normal'])

# ขาด N (pH ต่ำ, EC ต่ำ, ความชื้นต่ำ)
for _ in range(n):
    data.append([np.random.uniform(4.5, 5.5),
                 np.random.uniform(0.3, 1.0),
                 np.random.uniform(30, 50), 'nitrogen'])

# ขาด P (pH สูง, EC ต่ำ)
for _ in range(n):
    data.append([np.random.uniform(7.5, 8.5),
                 np.random.uniform(0.3, 0.8),
                 np.random.uniform(30, 45), 'phosphorus'])

# ขาด K (EC ต่ำมาก)
for _ in range(n):
    data.append([np.random.uniform(6.0, 7.0),
                 np.random.uniform(0.1, 0.5),
                 np.random.uniform(40, 60), 'potassium'])

df = pd.DataFrame(data, columns=['pH', 'EC', 'moisture', 'label'])

# ============================================================
# 4. เพิ่ม Feature ค่าเบี่ยงเบนจากมาตรฐาน
# ============================================================
df['pH_dev']       = df['pH']       - STANDARD['pH']['mid']
df['EC_dev']       = df['EC']       - STANDARD['EC']['mid']
df['moisture_dev'] = df['moisture'] - STANDARD['moisture']['mid']

df['pH_out']       = (~df['pH'].between(6.0, 7.0)).astype(int)
df['EC_out']       = (~df['EC'].between(1.5, 2.5)).astype(int)
df['moisture_out'] = (~df['moisture'].between(60, 80)).astype(int)

os.makedirs('dataset', exist_ok=True)
df.to_csv('dataset/sensor_data.csv', index=False)

print("✅ สร้างข้อมูลเสร็จแล้ว!")
print(df['label'].value_counts())
print(df.head())
