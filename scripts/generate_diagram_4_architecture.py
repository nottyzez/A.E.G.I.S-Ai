import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches

os.environ['MPLCONFIGDIR'] = str(Path.cwd() / '.matplotlib_cache')

out_dir = Path("docs/figures")
out_dir.mkdir(parents=True, exist_ok=True)

plt.rcParams['font.sans-serif'] = ['Leelawadee UI', 'TH Sarabun New', 'Tahoma', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(figsize=(15.5, 10.0), dpi=300)
ax.set_xlim(0, 15.5)
ax.set_ylim(0, 10.0)
ax.axis('off')

# Title
fig.text(0.5, 0.96, 'ผังสถาปัตยกรรมระบบรวม A.E.G.I.S. แบบบูรณาการ (End-to-End System Architecture)',
         fontsize=16, fontweight='bold', ha='center', color='#1A237E')
fig.text(0.5, 0.92, 'ระบบปัญญาประดิษฐ์ผสานข้อมูลหลากรูปแบบและการควบคุมสารละลายแบบวงปิดสองระดับ สำหรับพืชไฮโดรโปนิกส์',
         fontsize=12, ha='center', color='#455A64')

# 4 Horizontal Architecture Layers
layers = [
    # (y, h, title, border, bg)
    (7.0, 1.9, "1. ชั้นฮาร์ดแวร์ตรวจวัดและแปลงปลูก (Edge Sensing & Cultivation Layer)", "#00695C", "#E0F2F1"),
    (4.8, 1.9, "2. ชั้นประมวลผลบนคลาวด์และไปป์ไลน์ข้อมูล (Cloud Backend & Processing Layer)", "#1565C0", "#E3F2FD"),
    (2.6, 1.9, "3. ชั้นปัญญาประดิษฐ์วิเคราะห์สภาวะธาตุอาหาร (A.E.G.I.S. AI Engine Layer)", "#6A1B9A", "#F3E5F5"),
    (0.4, 1.9, "4. ชั้นปฏิบัติงานแบบวงปิดและส่วนต่อประสานผู้ใช้ (Two-Tier Actuation & UI Layer)", "#C62828", "#FFEBEE")
]

for ly, lh, ltitle, lborder, lbg in layers:
    l_box = patches.FancyBboxPatch((0.5, ly), 14.5, lh, boxstyle="round,pad=0.15",
                                  ec=lborder, fc=lbg, lw=2.2)
    ax.add_patch(l_box)
    ax.text(0.8, ly + lh - 0.28, ltitle, fontsize=11, fontweight='bold', color=lborder)

# --- Components in Layer 1 (Edge Sensing) ---
c1 = [
    (1.0, 7.2, 3.8, 1.1, "แปลงปลูกผักบุ้งจีน DWC (23.3L)\n4 กลุ่มทดลอง: Control, -N, -P, -K", "#004D40", "#FFFFFF"),
    (5.2, 7.2, 4.3, 1.1, "โหนดตรวจวัดเซนเซอร์ (ESP32-S3 N16R8)\nโพรบ pH (GPIO 1), EC (GPIO 2), Temp (GPIO 4)", "#00796B", "#FFFFFF"),
    (9.9, 7.2, 4.6, 1.1, "โหนดบันทึกภาพมุมสูง (ESP32-S3 CAM)\nเซนเซอร์ OV5640 5MP แนวดิ่ง 90° (Nadir View)", "#00897B", "#FFFFFF")
]
for cx, cy, cw, ch, ctxt, ccol, cbg in c1:
    b = patches.FancyBboxPatch((cx, cy), cw, ch, boxstyle="round,pad=0.08", ec=ccol, fc=cbg, lw=1.5)
    ax.add_patch(b)
    ax.text(cx + cw/2, cy + ch/2, ctxt, fontsize=8.5, ha='center', va='center', fontweight='bold', color=ccol)

# --- Components in Layer 2 (Cloud Backend) ---
c2 = [
    (1.0, 5.0, 4.2, 1.1, "FastAPI High-Performance Server\n(DigitalOcean VPS Ubuntu 22.04 LTS)", "#0D47A1", "#FFFFFF"),
    (5.6, 5.0, 4.0, 1.1, "ฐานข้อมูลโทรมาตร (SQLite Database)\nบันทึก 143 รายการ พร้อม Quality Events", "#1565C0", "#FFFFFF"),
    (10.0, 5.0, 4.5, 1.1, "ไปป์ไลน์ตัดครอบพุ่มใบ 3 ชั้น (3-Layer Cropper)\nCLAHE + ExG + HSV + CIELAB Halo Mask", "#1976D2", "#FFFFFF")
]
for cx, cy, cw, ch, ctxt, ccol, cbg in c2:
    b = patches.FancyBboxPatch((cx, cy), cw, ch, boxstyle="round,pad=0.08", ec=ccol, fc=cbg, lw=1.5)
    ax.add_patch(b)
    ax.text(cx + cw/2, cy + ch/2, ctxt, fontsize=8.5, ha='center', va='center', fontweight='bold', color=ccol)

# --- Components in Layer 3 (A.E.G.I.S. AI Engine) ---
c3 = [
    (1.0, 2.8, 4.0, 1.1, "Stream A: Vision Ensemble (95.12%)\nMobileNetV2 + SE-CNN + Color-Texture RF", "#4A148C", "#FFFFFF"),
    (5.4, 2.8, 4.2, 1.1, "Stream B: Sensor Ensemble (97.56%)\nStacking: GBDT + RF + ET + Logistic Regression", "#6A1B9A", "#FFFFFF"),
    (10.0, 2.8, 4.5, 1.1, "Late-Fusion Stacking Decision (100.00%)\nP_fused = 0.45*P_vision + 0.55*P_sensor\nพร้อม XAI แผนที่ความร้อน Grad-CAM", "#8E24AA", "#FFFFFF")
]
for cx, cy, cw, ch, ctxt, ccol, cbg in c3:
    b = patches.FancyBboxPatch((cx, cy), cw, ch, boxstyle="round,pad=0.08", ec=ccol, fc=cbg, lw=1.5)
    ax.add_patch(b)
    ax.text(cx + cw/2, cy + ch/2, ctxt, fontsize=8.5, ha='center', va='center', fontweight='bold', color=ccol)

# --- Components in Layer 4 (Actuation & UI) ---
c4 = [
    (1.0, 0.6, 4.0, 1.1, "ชุดจ่ายปุ๋ย 3 ขวด (Peristaltic Assembly)\nขวด 1 (N), ขวด 2 (P), ขวด 3 (K) ป้องกันตกตะกอน", "#B71C1C", "#FFFFFF"),
    (5.4, 0.6, 4.2, 1.1, "การควบคุมแบบวงปิดสองระดับ (Two-Tier)\nTier 1: ปูพื้นฐาน EC | Tier 2: AI สั่งจ่ายปุ๋ยเฉพาะจุด", "#C62828", "#FFFFFF"),
    (10.0, 0.6, 4.5, 1.1, "เว็บแดชบอร์ด & ฝาแฝดดิจิทัล 3 มิติ\n(Web Telemetry Dashboard + Three.js 3D Twin)", "#D32F2F", "#FFFFFF")
]
for cx, cy, cw, ch, ctxt, ccol, cbg in c4:
    b = patches.FancyBboxPatch((cx, cy), cw, ch, boxstyle="round,pad=0.08", ec=ccol, fc=cbg, lw=1.5)
    ax.add_patch(b)
    ax.text(cx + cw/2, cy + ch/2, ctxt, fontsize=8.5, ha='center', va='center', fontweight='bold', color=ccol)

# Vertical Dataflow Connectors
# Layer 1 -> Layer 2
ax.annotate("", xy=(3.0, 6.1), xytext=(3.0, 7.2), arrowprops=dict(arrowstyle="->", color="#00695C", lw=2.5))
ax.annotate("", xy=(7.3, 6.1), xytext=(7.3, 7.2), arrowprops=dict(arrowstyle="->", color="#00796B", lw=2.5))
ax.annotate("", xy=(12.2, 6.1), xytext=(12.2, 7.2), arrowprops=dict(arrowstyle="->", color="#00897B", lw=2.5))

# Layer 2 -> Layer 3
ax.annotate("", xy=(3.0, 3.9), xytext=(3.0, 5.0), arrowprops=dict(arrowstyle="->", color="#1565C0", lw=2.5))
ax.annotate("", xy=(7.5, 3.9), xytext=(7.5, 5.0), arrowprops=dict(arrowstyle="->", color="#1565C0", lw=2.5))
ax.annotate("", xy=(12.2, 3.9), xytext=(12.2, 5.0), arrowprops=dict(arrowstyle="->", color="#1565C0", lw=2.5))

# Layer 3 -> Layer 4
ax.annotate("", xy=(3.0, 1.7), xytext=(3.0, 2.8), arrowprops=dict(arrowstyle="->", color="#6A1B9A", lw=2.5))
ax.annotate("", xy=(7.5, 1.7), xytext=(7.5, 2.8), arrowprops=dict(arrowstyle="->", color="#6A1B9A", lw=2.5))
ax.annotate("", xy=(12.2, 1.7), xytext=(12.2, 2.8), arrowprops=dict(arrowstyle="->", color="#6A1B9A", lw=2.5))

# Closed-Loop Feedback Arrow (Actuation back to Cultivation)
ax.annotate("", xy=(0.5, 7.95), xytext=(0.5, 1.15),
            arrowprops=dict(arrowstyle="->", color="#C62828", lw=3, linestyle="dashed",
                            connectionstyle="arc3,rad=0.35"))
ax.text(0.1, 4.5, "Closed-Loop Feedback: ปรับสภาพน้ำและสารละลายธาตุอาหารกลับคืนถังปลูก",
        fontsize=9, fontweight='bold', color="#C62828", rotation=90, va='center', ha='center')

plt.tight_layout()
out_path = out_dir / "diagram_4_system_architecture.png"
plt.savefig(out_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Successfully generated {out_path} ({os.path.getsize(out_path):,} bytes)")
