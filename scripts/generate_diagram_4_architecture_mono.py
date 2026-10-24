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

# Title (International IEEE Layered Architecture)
fig.text(0.5, 0.96, 'END-TO-END AUTONOMOUS AIoT SYSTEM ARCHITECTURE',
         fontsize=15, fontweight='bold', ha='center', color='#000000')
fig.text(0.5, 0.92, 'Integrated Multi-Tier Architecture: Edge Sensing, Cloud Telemetry, Multimodal AI, and Closed-Loop Dosing',
         fontsize=11, ha='center', color='#333333', style='italic')

# 4 Horizontal Architectural Layers (Grayscale/Monochrome)
layers = [
    # (y, h, title_en, title_th, fill_color)
    (7.0, 1.9, "LAYER 1: PHYSICAL CULTIVATION & EDGE SENSING", "ชั้นฮาร์ดแวร์แปลงปลูกและโหนดตรวจวัด", "#FAFAFA"),
    (4.8, 1.9, "LAYER 2: CLOUD BACKEND & DATA PREPROCESSING", "ชั้นแม่ข่ายบนคลาวด์และไปป์ไลน์ข้อมูล", "#FFFFFF"),
    (2.6, 1.9, "LAYER 3: A.E.G.I.S. MULTIMODAL AI ENSEMBLE ENGINE", "ชั้นปัญญาประดิษฐ์วินิจฉัยสภาวะธาตุอาหาร", "#FAFAFA"),
    (0.4, 1.9, "LAYER 4: CLOSED-LOOP ACTUATION & USER INTERFACE", "ชั้นหน่วยควบคุมของไหลแบบวงปิดและส่วนต่อประสาน", "#FFFFFF")
]

for ly, lh, len_title, lth_title, lbg in layers:
    l_box = patches.Rectangle((0.6, ly), 14.3, lh, ec="#000000", fc=lbg, lw=2.2)
    ax.add_patch(l_box)
    ax.text(0.9, ly + lh - 0.28, f"{len_title} ({lth_title})", fontsize=10.5, fontweight='bold', color="#000000")

# --- Layer 1 Components ---
c1 = [
    (1.0, 7.2, 4.0, 1.1, "DWC Culture Tanks (23.3 L)\n4 Nutritional Regimes: Control, -N, -P, -K\nWater Spinach (Ipomoea aquatica)", "Cultivation Basin"),
    (5.4, 7.2, 4.2, 1.1, "Edge Controller (ESP32-S3 N16R8)\nAnalog pH (GPIO 1), EC/TDS (GPIO 2)\nDS18B20 OneWire Temp (GPIO 4)", "Sensor Node"),
    (10.0, 7.2, 4.5, 1.1, "Canopy Camera (ESP32-S3 CAM)\nOV5640 5MP Sensor @ 90° Nadir View\n160MHz CPU / Low-Thermal Config", "Vision Node")
]
for cx, cy, cw, ch, ctxt, ctag in c1:
    b = patches.Rectangle((cx, cy), cw, ch, ec="#000000", fc="#FFFFFF", lw=1.5)
    ax.add_patch(b)
    ax.text(cx + cw/2, cy + ch/2, ctxt, fontsize=8, ha='center', va='center', fontweight='bold')

# --- Layer 2 Components ---
c2 = [
    (1.0, 5.0, 4.0, 1.1, "FastAPI High-Performance Server\nDigitalOcean VPS (Ubuntu 22.04 LTS)\nEndpoints: /api/sensor, /api/image", "RESTful Server"),
    (5.4, 5.0, 4.2, 1.1, "Telemetry Database (SQLite)\n143 Experimental Readings Logged\n11 Quality Anomalies & Event Logs", "Data Persistence"),
    (10.0, 5.0, 4.5, 1.1, "3-Layer Computer Vision Pipeline\nLayer 1: CLAHE + Gray-World Lighting\nLayer 2: ExG + HSV + CIELAB Halo Mask", "Foliage Segmenter")
]
for cx, cy, cw, ch, ctxt, ctag in c2:
    b = patches.Rectangle((cx, cy), cw, ch, ec="#000000", fc="#FAFAFA", lw=1.5)
    ax.add_patch(b)
    ax.text(cx + cw/2, cy + ch/2, ctxt, fontsize=8, ha='center', va='center', fontweight='bold')

# --- Layer 3 Components ---
c3 = [
    (1.0, 2.8, 4.0, 1.1, "Stream A: Vision Ensemble (95.12%)\nMobileNetV2 (0.40) + SE-CNN (0.40)\n+ Color-Texture Random Forest (0.20)", "Vision Stream"),
    (5.4, 2.8, 4.2, 1.1, "Stream B: Sensor Ensemble (97.56%)\nStacking Classifier (Meta-Learner):\nGBDT + RF + ExtraTrees + LogisticReg", "Sensor Stream"),
    (10.0, 2.8, 4.5, 1.1, "Late-Fusion Decision Engine (100.00%)\nP_fused = 0.45*P_vis + 0.55*P_sen\nExplainable AI: Grad-CAM Saliency", "Multimodal Fusion")
]
for cx, cy, cw, ch, ctxt, ctag in c3:
    b = patches.Rectangle((cx, cy), cw, ch, ec="#000000", fc="#FFFFFF", lw=1.5)
    ax.add_patch(b)
    ax.text(cx + cw/2, cy + ch/2, ctxt, fontsize=8, ha='center', va='center', fontweight='bold')

# --- Layer 4 Components ---
c4 = [
    (1.0, 0.6, 4.0, 1.1, "3-Bottle Dosing Assembly (Peristaltic)\nBottle 1 (Stock A/N), Bottle 2 (High-P)\nBottle 3 (High-K) - Anti-Precipitate", "Dosing Actuators"),
    (5.4, 0.6, 4.2, 1.1, "Two-Tier Closed-Loop Actuator\nTier 1: Baseline EC Priming (< 0.8)\nTier 2: Targeted AI Dosing (3-5s)", "Control Logic"),
    (10.0, 0.6, 4.5, 1.1, "Web Dashboard & 3D Digital Twin\nReal-time Telemetry Charts (Chart.js)\nThree.js 3D Virtual Presentation Twin", "Presentation UI")
]
for cx, cy, cw, ch, ctxt, ctag in c4:
    b = patches.Rectangle((cx, cy), cw, ch, ec="#000000", fc="#FAFAFA", lw=1.5)
    ax.add_patch(b)
    ax.text(cx + cw/2, cy + ch/2, ctxt, fontsize=8, ha='center', va='center', fontweight='bold')

# Connective Dataflow Arrows (Solid for Data, Dashed for Feedback)
# L1 -> L2
ax.annotate("", xy=(3.0, 6.1), xytext=(3.0, 7.2), arrowprops=dict(arrowstyle="->", color="#000000", lw=2))
ax.annotate("", xy=(7.5, 6.1), xytext=(7.5, 7.2), arrowprops=dict(arrowstyle="->", color="#000000", lw=2))
ax.annotate("", xy=(12.25, 6.1), xytext=(12.25, 7.2), arrowprops=dict(arrowstyle="->", color="#000000", lw=2))

# L2 -> L3
ax.annotate("", xy=(3.0, 3.9), xytext=(3.0, 5.0), arrowprops=dict(arrowstyle="->", color="#000000", lw=2))
ax.annotate("", xy=(7.5, 3.9), xytext=(7.5, 5.0), arrowprops=dict(arrowstyle="->", color="#000000", lw=2))
ax.annotate("", xy=(12.25, 3.9), xytext=(12.25, 5.0), arrowprops=dict(arrowstyle="->", color="#000000", lw=2))

# L3 -> L4
ax.annotate("", xy=(3.0, 1.7), xytext=(3.0, 2.8), arrowprops=dict(arrowstyle="->", color="#000000", lw=2))
ax.annotate("", xy=(7.5, 1.7), xytext=(7.5, 2.8), arrowprops=dict(arrowstyle="->", color="#000000", lw=2))
ax.annotate("", xy=(12.25, 1.7), xytext=(12.25, 2.8), arrowprops=dict(arrowstyle="->", color="#000000", lw=2))

# Closed-Loop Feedback Path
ax.annotate("", xy=(0.6, 7.95), xytext=(0.6, 1.15),
            arrowprops=dict(arrowstyle="->", color="#000000", lw=2.5, linestyle="--",
                            connectionstyle="arc3,rad=0.35"))
ax.text(0.18, 4.5, "CLOSED-LOOP FEEDBACK: Nutrient correction injected directly into culture tank",
        fontsize=8.2, fontweight='bold', color="#000000", rotation=90, va='center', ha='center')

plt.tight_layout()
out_path = out_dir / "diagram_4_system_architecture_mono.png"
plt.savefig(out_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Successfully generated {out_path} ({os.path.getsize(out_path):,} bytes)")
