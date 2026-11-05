#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A.E.G.I.S. Poster Engineering Blueprints Generator (Maximum Legibility & Anti-Crowding Edition)
Generates 6 publication-ready Monochrome Technical Drafting vector graphics
(SVG + 300 DPI PNG) strictly aligned with the 55-page A.E.G.I.S. thesis.

Typography Philosophy:
- Frame-Filling & Maximum Readability ("เต็มกรอบ อ่านง่าย ไม่เบียด"):
  Titles 16-24pt, Section Headers 13-16pt, Badge Numbers 38-42pt,
  Block Titles 13.5-14.5pt, Body Text & Bullets 11.5-13pt.
- Balanced Layouts with zero horizontal cramping.
- Pure Monochrome Engineering Aesthetic (#FFFFFF, #0A0A0A, #0F172A).
"""

import os
import sys
import tempfile
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Setup temporary cache directory for Matplotlib
os.environ['MPLCONFIGDIR'] = os.path.join(tempfile.gettempdir(), 'mpl_cache')
os.makedirs(os.environ['MPLCONFIGDIR'], exist_ok=True)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

OUTPUT_DIR = Path("assets/blueprints")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
QR_PATH = Path("assets/qr_code.png")

# Setup style parameters
plt.rcParams['font.sans-serif'] = ['Leelawadee UI', 'Tahoma', 'Segoe UI', 'DejaVu Sans', 'Arial']
plt.rcParams['font.monospace'] = ['Consolas', 'Courier New', 'DejaVu Sans Mono']
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.edgecolor'] = '#0A0A0A'
plt.rcParams['axes.linewidth'] = 1.4

def draw_title_block(ax, dwg_no, title, date="2026-10-31", rev="REV 4.0"):
    """Draw an ISO/IEEE standard technical blueprint title block with high-contrast bold fonts."""
    # Outer frame
    ax.add_patch(patches.Rectangle((0.008, 0.008), 0.984, 0.984, fill=False, edgecolor='#0A0A0A', linewidth=2.4))
    # Inner border line
    ax.add_patch(patches.Rectangle((0.012, 0.012), 0.976, 0.976, fill=False, edgecolor='#94A3B8', linewidth=0.9, linestyle='--'))
    
    # Title block in bottom-right
    tb_x, tb_y, tb_w, tb_h = 0.58, 0.018, 0.40, 0.082
    ax.add_patch(patches.Rectangle((tb_x, tb_y), tb_w, tb_h, fill=True, facecolor='#F8FAFC', edgecolor='#0A0A0A', linewidth=1.6))
    ax.plot([tb_x, tb_x + tb_w], [tb_y + tb_h * 0.5, tb_y + tb_h * 0.5], color='#0A0A0A', linewidth=1.2)
    ax.plot([tb_x + tb_w * 0.56, tb_x + tb_w * 0.56], [tb_y, tb_y + tb_h], color='#0A0A0A', linewidth=1.2)
    
    ax.text(tb_x + 0.012, tb_y + tb_h * 0.72, "PROJECT: A.E.G.I.S. RESEARCH", fontsize=10.5, fontweight='bold', color='#0F172A', fontfamily='monospace')
    ax.text(tb_x + 0.012, tb_y + tb_h * 0.22, f"SHEET: {title[:28]}", fontsize=9.5, fontweight='bold', color='#334155', fontfamily='monospace')
    ax.text(tb_x + tb_w * 0.58, tb_y + tb_h * 0.72, f"DWG: {dwg_no} | {rev}", fontsize=10.0, fontweight='bold', color='#0F172A', fontfamily='monospace')
    ax.text(tb_x + tb_w * 0.58, tb_y + tb_h * 0.22, f"DATE: {date} | SCALE: NTS", fontsize=9.5, fontweight='bold', color='#64748B', fontfamily='monospace')

    # Top Header
    ax.text(0.025, 0.965, f"A.E.G.I.S. ENGINEERING BLUEPRINT // {dwg_no} // TECHNICAL DRAFTING", fontsize=13.0, fontweight='bold', color='#0F172A', fontfamily='monospace')
    ax.text(0.025, 0.930, title.upper(), fontsize=21.0, fontweight='heavy', color='#0A0A0A')
    ax.plot([0.025, 0.975], [0.914, 0.914], color='#0A0A0A', linewidth=2.0)

# ==============================================================================
# CARD 1: TWO-TIER CLOSED-LOOP FLUIDIC FSM & HARDWARE BLUEPRINT
# ==============================================================================
def generate_card_1():
    print("Generating Card 1: Two-Tier Closed-Loop Fluidic FSM (Frame-Filling Edition)...")
    fig = plt.figure(figsize=(18, 11.5), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    draw_title_block(ax, "AEGIS-DWG-001", "Two-Tier Closed-Loop Fluidic Control & Maintenance FSM")
    
    # SECTION 1: SENSORS
    ax.text(0.025, 0.880, "SECTION 1: SENSOR INSTRUMENTATION & CALIBRATION [GPIO 1, 2, 4]", fontsize=14.0, fontweight='bold', fontfamily='monospace', color='#0F172A')
    
    sensors = [
        {"pin": "GPIO 1 (ADC1_CH0)", "name": "Analog pH Probe Kit", "spec": "• Range: 0-3.3V | pH = -8.487V + 29.59\n• Two-Point Calib (pH 4.01 & 6.86)\n• Filter: Median Filter & Outlier Cut"},
        {"pin": "GPIO 2 (ADC1_CH1)", "name": "Analog EC/TDS Probe", "spec": "• AC Excitation (Ground Isolated)\n• ATC Normalized to 25°C Standard\n• EC25 = ECT / [1 + 0.0191(T - 25)]"},
        {"pin": "GPIO 4 (OneWire)", "name": "DS18B20 Temp Probe", "spec": "• Digital Stainless Waterproof Probe\n• 4.7kΩ Pull-up Resistor on Bus\n• Accuracy: ±0.5°C (-10°C to +85°C)"}
    ]
    
    for i, s in enumerate(sensors):
        x = 0.025 + i * 0.320
        y = 0.740
        w, h = 0.310, 0.125
        ax.add_patch(patches.Rectangle((x, y), w, h, fill=True, facecolor='#FFFFFF', edgecolor='#0A0A0A', linewidth=1.6))
        ax.add_patch(patches.Rectangle((x, y + h - 0.038), w, 0.038, fill=True, facecolor='#0F172A', edgecolor='#0A0A0A', linewidth=1.2))
        ax.text(x + 0.012, y + h - 0.022, s['pin'], color='#FFFFFF', fontsize=12.5, fontweight='bold', fontfamily='monospace')
        ax.text(x + 0.012, y + 0.056, s['name'], color='#0F172A', fontsize=13.5, fontweight='bold')
        ax.text(x + 0.012, y + 0.010, s['spec'], color='#1E293B', fontsize=11.5, fontfamily='monospace', linespacing=1.3)

    # SECTION 2: 6-PHASE FLUIDIC AUTOMATION
    ax.text(0.025, 0.705, "SECTION 2: 6-PHASE FLUIDIC AUTOMATION PIPELINE (SEQUENTIAL FSM)", fontsize=14.0, fontweight='bold', fontfamily='monospace', color='#0F172A')
    
    phases = [
        {"num": "Phase 1", "name": "Sampling", "time": "6s", "act": "Diaphragm 1 [GPIO 5]", "desc": "Pumps water from 23.3L tank to V-102 cell"},
        {"num": "Phase 2", "name": "Sensing", "time": "3s", "act": "Probes [GPIO 1, 2, 4]", "desc": "Settling delay; 15 ADC samples -> EC & pH"},
        {"num": "Phase 3", "name": "Recovery", "time": "7s", "act": "Diaphragm 2 [GPIO 6]", "desc": "100% Water return to tank (Zero Loss)"},
        {"num": "Phase 4", "name": "Dosing", "time": "5-10s", "act": "Peristaltic [GPIO 9-11]", "desc": "Tier 1 Priming / Tier 2 Targeted N-P-K"},
        {"num": "Phase 5", "name": "Probe Wash", "time": "5s", "act": "Diaphragm 3 [GPIO 7]", "desc": "Clean RO water flush over all probes"},
        {"num": "Phase 6", "name": "Waste Drain", "time": "6s", "act": "Solenoid 12V [GPIO 8]", "desc": "Gravity drain valve opens to purge waste"}
    ]
    
    for i, p in enumerate(phases):
        row = i // 3
        col = i % 3
        x = 0.025 + col * 0.320
        y = 0.550 - row * 0.145
        w, h = 0.310, 0.130
        
        ax.add_patch(patches.Rectangle((x, y), w, h, fill=True, facecolor='#F8FAFC', edgecolor='#0A0A0A', linewidth=1.6))
        ax.add_patch(patches.Rectangle((x, y + h - 0.038), w, 0.038, fill=True, facecolor='#1E293B', edgecolor='#0A0A0A', linewidth=1.2))
        ax.text(x + 0.012, y + h - 0.022, f"{p['num']} : {p['name'].upper()} ({p['time']})", color='#FFFFFF', fontsize=12.5, fontweight='bold', fontfamily='monospace')
        
        ax.text(x + 0.012, y + 0.056, f"ACTUATOR: {p['act']}", color='#0F172A', fontsize=12.0, fontweight='bold', fontfamily='monospace')
        ax.text(x + 0.012, y + 0.012, p['desc'], color='#1E293B', fontsize=11.5, fontweight='bold', linespacing=1.25)
        
        if i < 5 and col < 2:
            ax.annotate("", xy=(x + w + 0.009, y + h/2), xytext=(x + w + 0.001, y + h/2),
                        arrowprops=dict(arrowstyle="->", color="#0A0A0A", lw=2.0))
        elif i == 2:
            ax.annotate("", xy=(x + w/2, y - 0.014), xytext=(x + w/2, y - 0.002),
                        arrowprops=dict(arrowstyle="->", color="#0A0A0A", lw=2.0))

    # SECTION 3: TWO-TIER DOSING & OPERATIONAL LIMITS
    ax.text(0.025, 0.245, "SECTION 3: TWO-TIER CLOSED-LOOP DOSING ARCHITECTURE & SAFETY LIMITS", fontsize=14.0, fontweight='bold', fontfamily='monospace', color='#0F172A')
    
    t_box_x, t_box_y, t_box_w, t_box_h = 0.025, 0.020, 0.540, 0.215
    ax.add_patch(patches.Rectangle((t_box_x, t_box_y), t_box_w, t_box_h, fill=True, facecolor='#FFFFFF', edgecolor='#0A0A0A', linewidth=1.8))
    
    lines = [
        ("• TIER 1 BASELINE PRIMING: EC < 0.8 mS/cm -> Staggered Pumps 1, 2, 3", "#0F172A", True),
        ("  (Staggered 10s delay between pumps prevents calcium phosphate precipitation)", "#475569", False),
        ("• TIER 1 HARD SAFETY LOCKOUT: EC > 2.5 mS/cm OR pH < 4.0", "#DC2626", True),
        ("  (Immediate 0s abort prevents root osmotic shock & acid rhizotoxicity pH 1.58)", "#991B1B", False),
        ("• TIER 2 PREDICTIVE AI: Pump 1 [GPIO 9, N] | Pump 2 [GPIO 10, P] | Pump 3 [GPIO 11, K]", "#0F172A", True),
        ("• OPERATING LIMITS: Target pulse 5-10s | Max duration ≤ 25s | Cooldown 6-12 hours", "#1E293B", True),
        ("• POWER ARCHITECTURE: Solar 18V 30W + SLA 12V 7.5Ah + Buck Converter 5V 3A", "#475569", False)
    ]
    
    for i, (text_str, col, is_b) in enumerate(lines):
        ly = t_box_y + t_box_h - 0.028 - i * 0.027
        weight = 'bold' if is_b else 'normal'
        ax.text(t_box_x + 0.012, ly, text_str, fontsize=11.2, fontweight=weight, color=col, fontfamily='monospace')

    svg_out = str(OUTPUT_DIR / "blueprint_closed_loop_fsm.svg")
    png_out = str(OUTPUT_DIR / "blueprint_closed_loop_fsm.png")
    plt.savefig(svg_out, format='svg', bbox_inches='tight')
    plt.savefig(png_out, format='png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {svg_out} and {png_out}")

# ==============================================================================
# CARD 2: A.E.G.I.S. MULTIMODAL LATE-FUSION PIPELINE
# ==============================================================================
def generate_card_2():
    print("Generating Card 2: A.E.G.I.S. Multimodal Late-Fusion Pipeline (Frame-Filling Edition)...")
    fig = plt.figure(figsize=(18, 11.5), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    draw_title_block(ax, "AEGIS-DWG-002", "A.E.G.I.S. Multimodal Late-Fusion Prediction Pipeline")
    
    # STREAM A (LEFT)
    sa_x, sa_y, sa_w, sa_h = 0.025, 0.380, 0.465, 0.515
    ax.add_patch(patches.Rectangle((sa_x, sa_y), sa_w, sa_h, fill=True, facecolor='#FFFFFF', edgecolor='#0A0A0A', linewidth=1.8))
    ax.add_patch(patches.Rectangle((sa_x, sa_y + sa_h - 0.045), sa_w, 0.045, fill=True, facecolor='#0F172A', edgecolor='#0A0A0A', linewidth=1.2))
    ax.text(sa_x + 0.015, sa_y + sa_h - 0.028, "STREAM A: VISUAL FOLIAR CNN (IMAGE MODEL) // 95.12%", color='#FFFFFF', fontsize=13.0, fontweight='bold', fontfamily='monospace')
    
    stream_a_steps = [
        ("1. ESP32-S3 CAM (OV5640)", "High-angle canopy images 224x224 RGB | 160MHz clock"),
        ("2. Preprocessing & ExG", "CLAHE balance + ExG (2G-R-B) + Otsu Adaptive Threshold"),
        ("3. Symptom-Gated Filtering (NOVEL)", "122 Latent Images Filtered out (Label Noise Removed)\n182 Symptom Images Retained -> 786 Augmented Images"),
        ("4. MobileNetV2 + SE-Attention", "Depthwise Separable + Channel Attention (GAP/FC/Scale)"),
        ("5. Vision Ensemble (A1+A2+A3)", "MobileNet (85.37%) + SE-CNN (90.24%) + Color (87.80%)\nStream A Weighted Ensemble Accuracy: 95.12%"),
        ("6. Explainability: Grad-CAM", "Heatmap confirms focus on chlorosis, purple, scorch")
    ]
    
    for i, (title, desc) in enumerate(stream_a_steps):
        sy = sa_y + sa_h - 0.080 - i * 0.072
        ax.text(sa_x + 0.015, sy + 0.016, title, fontsize=12.5, fontweight='bold', color='#0F172A', fontfamily='monospace')
        ax.text(sa_x + 0.015, sy - 0.014, desc, fontsize=11.2, fontweight='bold', color='#334155', linespacing=1.25)
        if i < len(stream_a_steps) - 1:
            ax.plot([sa_x + 0.015, sa_x + sa_w - 0.015], [sy - 0.025, sy - 0.025], color='#E2E8F0', linewidth=1.0)

    # STREAM B (RIGHT)
    sb_x, sb_y, sb_w, sb_h = 0.510, 0.380, 0.465, 0.515
    ax.add_patch(patches.Rectangle((sb_x, sb_y), sb_w, sb_h, fill=True, facecolor='#FFFFFF', edgecolor='#0A0A0A', linewidth=1.8))
    ax.add_patch(patches.Rectangle((sb_x, sb_y + sb_h - 0.045), sb_w, 0.045, fill=True, facecolor='#0F172A', edgecolor='#0A0A0A', linewidth=1.2))
    ax.text(sb_x + 0.015, sb_y + sb_h - 0.028, "STREAM B: SOLUTION SENSOR ENSEMBLE // 97.56%", color='#FFFFFF', fontsize=13.0, fontweight='bold', fontfamily='monospace')
    
    stream_b_steps = [
        ("1. Physicochemical Feature Vector", "7-D Vector: EC(t), pH(t), Temp(t), dEC_base, dEC_24h, dpH, Age"),
        ("2. Kohlrausch Law & ATC", "Total ionic conductivity Sigma = Sum(ci*|zi|*li) + 25°C ATC"),
        ("3. Tree-Based Gradient Ensembling", "Robust to non-linear chemical solution buffering dynamics"),
        ("4. Sensor B1: Gradient Boosting", "GBDT Accuracy: 100.00% | Precision: 100.00% | F1: 1.000"),
        ("5. Sensor B2: Random Forest (RF)", "RF Accuracy: 97.56% | Precision: 97.50% (100 Trees)"),
        ("6. Stream B Soft-Voting Ensemble", "Soft-vote probability weighting -> P_sensor = 97.56%")
    ]
    
    for i, (title, desc) in enumerate(stream_b_steps):
        sy = sb_y + sb_h - 0.080 - i * 0.072
        ax.text(sb_x + 0.015, sy + 0.016, title, fontsize=12.5, fontweight='bold', color='#0F172A', fontfamily='monospace')
        ax.text(sb_x + 0.015, sy - 0.014, desc, fontsize=11.2, fontweight='bold', color='#334155', linespacing=1.25)
        if i < len(stream_b_steps) - 1:
            ax.plot([sb_x + 0.015, sb_x + sb_w - 0.015], [sy - 0.025, sy - 0.025], color='#E2E8F0', linewidth=1.0)

    # LATE FUSION META-CLASSIFIER LAYER (BOTTOM)
    mf_x, mf_y, mf_w, mf_h = 0.025, 0.110, 0.950, 0.250
    ax.add_patch(patches.Rectangle((mf_x, mf_y), mf_w, mf_h, fill=True, facecolor='#F8FAFC', edgecolor='#0A0A0A', linewidth=2.0))
    
    ax.add_patch(patches.Rectangle((mf_x, mf_y + mf_h - 0.040), mf_w, 0.040, fill=True, facecolor='#0F172A', edgecolor='#0A0A0A', linewidth=1.2))
    ax.text(mf_x + 0.015, mf_y + mf_h - 0.026, "HIERARCHICAL MULTIMODAL LATE-FUSION STACKING META-CLASSIFIER // 100.00% ACCURACY", color='#FFFFFF', fontsize=13.5, fontweight='bold', fontfamily='monospace')
    
    ax.text(mf_x + 0.018, mf_y + 0.160, "FUSION FORMULA: P_fused = (0.35 * P_vision) + (0.65 * P_sensor)   [Stacking Logistic Regression]",
            fontsize=13.5, fontweight='heavy', fontfamily='monospace', color='#1D4ED8')
    
    col1_text = (
        "• ORTHOGONAL COMPLEMENTARITY:\n"
        "  - Early Stage: Sensor detects ion drop before leaf symptoms.\n"
        "  - Late Stage: Vision differentiates single-element N-P-K.\n"
        "• CASE STUDY - TANK P (DEFICIENT PHOSPHORUS):\n"
        "  - Vision alone: 43.23% (dark purplish green looks normal)\n"
        "  - Sensor alone: 97.01% (detects anomalous EC & pH curve)\n"
        "  - Fused A.E.G.I.S.: 80.49% -> Correctly diagnosed!"
    )
    ax.text(mf_x + 0.018, mf_y + 0.018, col1_text, fontsize=11.5, fontweight='bold', color='#1E293B', linespacing=1.25)
    
    col2_text = (
        "• HOLDOUT TEST ACCURACY: 100.00% (F1 = 1.000)\n"
        "• 95% CONFIDENCE INTERVAL: [100.0%, 100.0%]\n"
        "• REAL-WORLD VERIFICATION: 12 / 12 Units Correct (100%)\n"
        "  - 4 Primary Tanks (23.3L) + 8 Replicate Cups (750mL)\n"
        "  - Mean Confidence: 83.96% ± 6.22% (SD)\n"
        "  - Published in alignment with Elsherbiny et al. (2022)"
    )
    ax.text(mf_x + 0.500, mf_y + 0.018, col2_text, fontsize=11.5, fontweight='bold', color='#0F172A', fontfamily='monospace', linespacing=1.25)

    svg_out = str(OUTPUT_DIR / "blueprint_multimodal_ai.svg")
    png_out = str(OUTPUT_DIR / "blueprint_multimodal_ai.png")
    plt.savefig(svg_out, format='svg', bbox_inches='tight')
    plt.savefig(png_out, format='png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {svg_out} and {png_out}")

# ==============================================================================
# CARD 3: EMPIRICAL VALIDATION & PLANT PHYSIOLOGY ABLATION CHARTS
# ==============================================================================
def generate_card_3():
    print("Generating Card 3: Empirical Validation & Biomass Charts (Frame-Filling Edition)...")
    fig = plt.figure(figsize=(18, 11.5), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    
    # Outer frame & Title block
    ax_bg = fig.add_axes([0, 0, 1, 1])
    ax_bg.set_xlim(0, 1)
    ax_bg.set_ylim(0, 1)
    ax_bg.axis('off')
    draw_title_block(ax_bg, "AEGIS-DWG-003", "Empirical Validation & Plant Physiology Ablation Analysis")
    
    # SUBPLOT 1: ABLATION STUDY (LEFT)
    ax_chart1 = fig.add_axes([0.065, 0.220, 0.420, 0.670])
    ax_chart1.set_facecolor('#FFFFFF')
    
    models = [
        "A.E.G.I.S. (Multimodal)",
        "Stream B: Sensor Ensemble",
        "Stream A: Vision Ensemble",
        "Vision A2 (SE-CNN)",
        "Vision A3 (Color-Texture)",
        "Vision A1 (MobileNetV2)",
        "Sensor B0 (Logistic Reg)",
        "Naive Majority Baseline"
    ]
    
    gated_acc = [100.00, 97.56, 95.12, 90.24, 87.80, 85.37, 82.93, 46.34]
    ungated_acc = [None, None, 72.73, 50.00, 61.36, 65.91, None, None]
    y_pos = range(len(models))
    
    ax_chart1.barh(y_pos, gated_acc, height=0.54, color='#0F172A', edgecolor='#0A0A0A', linewidth=1.4, label='Gated / Final Accuracy')
    
    for i, un in enumerate(ungated_acc):
        if un is not None:
            ax_chart1.plot(un, i, marker='o', markersize=8.0, color='#FFFFFF', markeredgecolor='#DC2626', markeredgewidth=2.2)
            ax_chart1.annotate("", xy=(gated_acc[i] - 1.2, i), xytext=(un + 1.2, i),
                               arrowprops=dict(arrowstyle="->", color="#DC2626", lw=1.8))
            ax_chart1.text((un + gated_acc[i]) / 2, i + 0.32, f"+{gated_acc[i] - un:.1f}%", 
                           ha='center', va='bottom', fontsize=11.5, fontweight='bold', color='#DC2626', fontfamily='monospace')
    
    ax_chart1.plot([], [], marker='o', markersize=7.5, color='#FFFFFF', markeredgecolor='#DC2626', markeredgewidth=2.2, linestyle='none', label='Ungated (Pre-symptomatic)')
    
    for i, v in enumerate(gated_acc):
        ax_chart1.text(v + 1.5, i, f"{v:.2f}%", va='center', fontsize=12.5, fontweight='bold', fontfamily='monospace', color='#0A0A0A')
    
    ax_chart1.set_yticks(y_pos)
    ax_chart1.set_yticklabels(models, fontsize=12.5, fontweight='bold', fontfamily='monospace')
    ax_chart1.set_xlim(0, 122)
    ax_chart1.invert_yaxis()
    ax_chart1.set_xlabel("Accuracy (%) // Holdout Test Set (N=41)", fontsize=13.0, fontweight='bold', fontfamily='monospace')
    ax_chart1.set_title("ABLATION STUDY: SYMPTOM-GATED EFFECT\n(Table 4.2 a, b // Up to +40.24% Accuracy Boost)", fontsize=15.0, fontweight='heavy', pad=12)
    ax_chart1.grid(axis='x', linestyle=':', color='#CBD5E1', alpha=0.7)
    ax_chart1.legend(loc='lower left', fontsize=11.5, framealpha=0.9, edgecolor='#0A0A0A')
    
    # SUBPLOT 2: WATER SPINACH BIOMASS (RIGHT)
    ax_chart2 = fig.add_axes([0.550, 0.220, 0.400, 0.670])
    ax_chart2.set_facecolor('#FFFFFF')
    treatments = ["Control\n(Healthy)", "Tank -K\n(Potassium)", "Tank -P\n(Phosphorus)", "Tank -N\n(Nitrogen)"]
    biomass = [54.3, 37.9, 32.2, 19.8]
    errors = [4.2, 3.4, 3.0, 2.4]
    pct_control = [100.0, 69.8, 59.3, 36.5]
    heights = [39.6, 32.8, 28.3, 22.4]
    leaf_counts = [20.4, 16.5, 14.8, 10.5]
    
    x_pos = range(len(treatments))
    bars2 = ax_chart2.bar(x_pos, biomass, yerr=errors, capsize=6, width=0.54, color='#F8FAFC', edgecolor='#0A0A0A', linewidth=1.6)
    bars2[0].set_facecolor('#0F172A')
    
    for i, b in enumerate(biomass):
        t_color = '#FFFFFF' if i == 0 else '#0F172A'
        ax_chart2.text(i, b / 2, f"{b:.1f}g\n({pct_control[i]:.1f}%)", ha='center', va='center', fontsize=14.5, fontweight='bold', fontfamily='monospace', color=t_color)
        ax_chart2.text(i, b + errors[i] + 2.5, f"H: {heights[i]}cm\nLeaves: {leaf_counts[i]}", ha='center', va='bottom', fontsize=12.0, fontweight='bold', fontfamily='monospace', color='#1E293B')

    ax_chart2.set_xticks(x_pos)
    ax_chart2.set_xticklabels(treatments, fontsize=13.5, fontweight='bold')
    ax_chart2.set_ylim(0, 80)
    ax_chart2.set_ylabel("Fresh Biomass per Plant (g) at Day 22 Harvest", fontsize=13.0, fontweight='bold', fontfamily='monospace')
    ax_chart2.set_title("WATER SPINACH BIOMASS AT DAY 22 HARVEST\n(Appendix A Table 3 // -63.5% Loss in -N Group)", fontsize=15.0, fontweight='heavy', pad=12)
    ax_chart2.grid(axis='y', linestyle=':', color='#CBD5E1', alpha=0.7)

    # Bottom Notes Banner
    notes_box = (
        "PHYSIOLOGICAL MECHANISMS IDENTIFIED AT DAY 22 HARVEST:\n"
        "• -N (19.8g, -63.5% drop): RuBisCO breakdown & mobile N remobilization -> uniform leaf chlorosis\n"
        "• -P (32.2g, -40.7% drop): Sugar accumulation & anthocyanin synthesis -> dark purplish green & stunting\n"
        "• -K (37.9g, -30.2% drop): Osmotic stress & toxic putrescine accumulation -> marginal leaf scorch & necrosis"
    )
    ax_bg.text(0.285, 0.055, notes_box, ha='center', fontsize=10.5, fontfamily='monospace', fontweight='bold', color='#0F172A',
               bbox=dict(boxstyle="square,pad=0.5", facecolor='#F8FAFC', edgecolor='#0A0A0A', lw=1.3))

    svg_out = str(OUTPUT_DIR / "blueprint_performance_charts.svg")
    png_out = str(OUTPUT_DIR / "blueprint_performance_charts.png")
    plt.savefig(svg_out, format='svg', bbox_inches='tight')
    plt.savefig(png_out, format='png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {svg_out} and {png_out}")

# ==============================================================================
# CARD 4: KEY METRICS SUMMARY & GITHUB REPO BLUEPRINT
# ==============================================================================
def generate_card_4():
    print("Generating Card 4: Key Metrics Summary & GitHub QR Code (Frame-Filling Edition)...")
    fig = plt.figure(figsize=(18, 11.5), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    draw_title_block(ax, "AEGIS-DWG-004", "A.E.G.I.S. System Telemetry, Specifications & Open Science Repo")
    
    # 4 GIANT ACHIEVEMENT BADGES
    ax.text(0.025, 0.880, "KEY RESEARCH HIGHLIGHTS & EMPIRICAL METRICS // N=143 READINGS", fontsize=14.0, fontweight='bold', fontfamily='monospace', color='#0F172A')
    
    badges = [
        {"num": "100.00%", "lbl": "MULTIMODAL ACCURACY", "sub": "Macro F1-Score = 1.000\nLate-Fusion Stacking"},
        {"num": "12 / 12", "lbl": "UNITS VERIFIED", "sub": "100% Real Hydroponic Units\nMean Conf 83.96% ± 6.22%"},
        {"num": "122", "lbl": "LATENT IMAGES CUT", "sub": "Symptom-Gated Filtering\n+40.24% SE-CNN Accuracy"},
        {"num": "0%", "lbl": "SALT PRECIPITATION", "sub": "Zero Nutrient Lockout\n10s Staggered Dosing Guard"}
    ]
    
    for i, b in enumerate(badges):
        x = 0.025 + i * 0.240
        y = 0.690
        w, h = 0.230, 0.170
        
        ax.add_patch(patches.Rectangle((x, y), w, h, fill=True, facecolor='#FFFFFF', edgecolor='#0A0A0A', linewidth=2.0))
        ax.add_patch(patches.Rectangle((x, y + h - 0.038), w, 0.038, fill=True, facecolor='#0F172A', edgecolor='#0A0A0A', linewidth=1.2))
        ax.text(x + w/2, y + h - 0.022, b['lbl'], ha='center', va='center', color='#FFFFFF', fontsize=12.5, fontweight='bold', fontfamily='monospace')
        
        ax.text(x + w/2, y + 0.075, b['num'], ha='center', va='center', color='#0A0A0A', fontsize=38.0, fontweight='heavy', fontfamily='monospace')
        ax.text(x + w/2, y + 0.025, b['sub'], ha='center', va='center', color='#1E293B', fontsize=11.5, fontweight='bold', fontfamily='monospace', linespacing=1.25)

    # SYSTEM SAFETY & OPERATIONAL GUARDRAILS
    ax.text(0.025, 0.645, "SYSTEM SAFETY STANDARDS & MULTI-TIER GUARDRAILS", fontsize=14.0, fontweight='bold', fontfamily='monospace', color='#0F172A')
    
    gb_x, gb_y, gb_w, gb_h = 0.025, 0.115, 0.585, 0.515
    ax.add_patch(patches.Rectangle((gb_x, gb_y), gb_w, gb_h, fill=True, facecolor='#F8FAFC', edgecolor='#0A0A0A', linewidth=1.8))
    
    rules = [
        ("HARD SAFETY LOCKOUT: EC > 2.5 mS/cm or pH < 4.0",
         "Immediate 0s abort cuts all pumps. Protects roots from osmotic shock\nand acid rhizotoxicity (Acid Shock pH 1.58 prevention)."),
        ("100% FLUIDIC SAMPLE RECOVERY (7.0s)",
         "Diaphragm Pump 2 cycles 100% of tested solution back into 23.3L tank.\nZero solution depletion during automated 4-hour monitoring cycles."),
        ("AUTOMATIC PROBE INTEGRITY SYSTEM",
         "Diaphragm Pump 3 flushes RO water (5.0s) + Solenoid drain opens (6.0s).\nEliminates salt crusting; extends sensor probe lifespan by >300%."),
        ("CHEMICAL SEPARATION (CALCIUM-PHOSPHATE)",
         "Stock A (Ca+Fe) isolated from Stock B/C (PO4/SO4). 10s inter-pump delay\nprevents insoluble Ca3(PO4)2 and CaSO4 precipitation in lines."),
        ("PREDICTIVE DOSING COOLDOWN",
         "Targeted pulse strictly 5-10s per cycle (maximum safety cutoff at 25,000ms).\nMandatory 6-12 hour cooldown allows biological plant uptake.")
    ]
    
    for i, (rtitle, rdesc) in enumerate(rules):
        ry = gb_y + gb_h - 0.050 - i * 0.098
        ax.text(gb_x + 0.015, ry + 0.015, f"[{i+1}] {rtitle}", fontsize=12.5, fontweight='bold', color='#0F172A', fontfamily='monospace')
        ax.text(gb_x + 0.015, ry - 0.025, rdesc, fontsize=11.2, fontweight='bold', color='#334155', linespacing=1.25)
        if i < len(rules) - 1:
            ax.plot([gb_x + 0.015, gb_x + gb_w - 0.015], [ry - 0.036, ry - 0.036], color='#CBD5E1', linewidth=1.0, linestyle='--')

    # REPOSITORY QR CODE
    qr_box_x, qr_box_y, qr_box_w, qr_box_h = 0.635, 0.115, 0.335, 0.515
    ax.add_patch(patches.Rectangle((qr_box_x, qr_box_y), qr_box_w, qr_box_h, fill=True, facecolor='#FFFFFF', edgecolor='#0A0A0A', linewidth=1.8))
    ax.add_patch(patches.Rectangle((qr_box_x, qr_box_y + qr_box_h - 0.040), qr_box_w, 0.040, fill=True, facecolor='#0F172A', edgecolor='#0A0A0A', linewidth=1.2))
    ax.text(qr_box_x + qr_box_w/2, qr_box_y + qr_box_h - 0.024, "OPEN SCIENCE // GITHUB REPOSITORY", ha='center', va='center', color='#FFFFFF', fontsize=12.5, fontweight='bold', fontfamily='monospace')
    
    if QR_PATH.exists():
        qr_img = Image.open(QR_PATH)
        ax.imshow(qr_img, extent=[qr_box_x + 0.055, qr_box_x + qr_box_w - 0.055, qr_box_y + 0.160, qr_box_y + qr_box_h - 0.060], zorder=10, aspect='auto')
        ax.set_aspect('auto')
    
    ax.text(qr_box_x + qr_box_w/2, qr_box_y + 0.120, "github.com/nottyzez/A.E.G.I.S-Ai", ha='center', fontsize=13.5, fontweight='heavy', fontfamily='monospace', color='#1D4ED8')
    qr_sub = "SCAN FOR FULL TELEMETRY DATA\n• 143 Time-Series Telemetry Logs\n• IEEE-315 Schematics & P&ID 4K\n• Arduino C++ ESP32 Firmware\n• Pretrained Ensemble Keras Weights"
    ax.text(qr_box_x + qr_box_w/2, qr_box_y + 0.030, qr_sub, ha='center', fontsize=11.0, fontweight='bold', fontfamily='monospace', color='#1E293B', linespacing=1.25)

    svg_out = str(OUTPUT_DIR / "blueprint_key_metrics_summary.svg")
    png_out = str(OUTPUT_DIR / "blueprint_key_metrics_summary.png")
    plt.savefig(svg_out, format='svg', bbox_inches='tight')
    plt.savefig(png_out, format='png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {svg_out} and {png_out}")

# ==============================================================================
# CARD 5 (COMBO): UNIFIED EMPIRICAL RESULTS, BIOMASS & TELEMETRY BLUEPRINT
# ==============================================================================
def generate_card_combo():
    print("Generating Card 5: Unified Results & Telemetry Combo Blueprint (2-Column Balanced & Maximum Readability)...")
    fig = plt.figure(figsize=(22, 12), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    
    # Base background axis for architectural layout & borders
    ax_bg = fig.add_axes([0, 0, 1, 1])
    ax_bg.set_xlim(0, 1)
    ax_bg.set_ylim(0, 1)
    ax_bg.axis('off')
    
    # Outer double engineering frame
    ax_bg.add_patch(patches.Rectangle((0.008, 0.008), 0.984, 0.984, fill=False, edgecolor='#0A0A0A', linewidth=2.6))
    ax_bg.add_patch(patches.Rectangle((0.012, 0.012), 0.976, 0.976, fill=False, edgecolor='#94A3B8', linewidth=0.9, linestyle='--'))
    
    # Top Header (Huge & Bold)
    ax_bg.text(0.025, 0.965, "A.E.G.I.S. ENGINEERING BLUEPRINT // DWG-AEGIS-COMBO-005 // MONOCHROME TECHNICAL DRAFTING", 
               fontsize=13.0, fontweight='bold', color='#0F172A', fontfamily='monospace')
    ax_bg.text(0.025, 0.932, "UNIFIED EMPIRICAL VALIDATION, WATER SPINACH BIOMASS & SYSTEM TELEMETRY SUMMARY", 
               fontsize=22.0, fontweight='heavy', color='#0A0A0A')
    ax_bg.plot([0.025, 0.975], [0.916, 0.916], color='#0A0A0A', linewidth=2.0)
    
    # Central dividing line between Left Half (Charts) and Right Half (Badges & Open Science)
    ax_bg.plot([0.505, 0.505], [0.025, 0.916], color='#0A0A0A', linewidth=1.6, linestyle='-')
    
    # ==========================================================================
    # LEFT HALF: TWO STACKED FULL-WIDTH CHARTS (ZERO CROWDING, MASSIVE LABELS)
    # ==========================================================================
    
    # SUBPLOT 1: ABLATION STUDY (TOP LEFT)
    ax_chart1 = fig.add_axes([0.065, 0.535, 0.415, 0.355])
    ax_chart1.set_facecolor('#FFFFFF')
    
    models = [
        "Late-Fusion Stacking",
        "Physicochemical GBDT",
        "Visual CNN Ensemble",
        "Multi-Scale SE-CNN",
        "Color-Texture Expert",
        "MobileNetV2 Trunk"
    ]
    gated_acc = [100.00, 97.56, 95.12, 90.24, 87.80, 85.37]
    ungated_acc = [None, None, 72.73, 50.00, 61.36, 65.91]
    y_pos = range(len(models))
    
    ax_chart1.barh(y_pos, gated_acc, height=0.52, color='#0F172A', edgecolor='#0A0A0A', linewidth=1.4, label='Gated / Final Accuracy')
    
    for i, un in enumerate(ungated_acc):
        if un is not None:
            ax_chart1.plot(un, i, marker='o', markersize=8.5, color='#FFFFFF', markeredgecolor='#DC2626', markeredgewidth=2.2)
            ax_chart1.annotate("", xy=(gated_acc[i] - 1.2, i), xytext=(un + 1.2, i),
                               arrowprops=dict(arrowstyle="->", color="#DC2626", lw=1.8))
            ax_chart1.text((un + gated_acc[i]) / 2, i + 0.30, f"+{gated_acc[i] - un:.1f}%", 
                           ha='center', va='bottom', fontsize=11.5, fontweight='bold', color='#DC2626', fontfamily='monospace')
    
    ax_chart1.plot([], [], marker='o', markersize=8, color='#FFFFFF', markeredgecolor='#DC2626', markeredgewidth=2.2, linestyle='none', label='Ungated (Pre-symptomatic)')
    
    for i, v in enumerate(gated_acc):
        ax_chart1.text(v + 1.8, i, f"{v:.2f}%", va='center', fontsize=13.0, fontweight='bold', fontfamily='monospace', color='#0A0A0A')
        
    ax_chart1.set_yticks(y_pos)
    ax_chart1.set_yticklabels(models, fontsize=13.0, fontweight='bold', fontfamily='monospace')
    ax_chart1.set_xlim(0, 122)
    ax_chart1.invert_yaxis()
    ax_chart1.set_xlabel("Accuracy (%) // Holdout Test Set (N=41)", fontsize=13.0, fontweight='bold', fontfamily='monospace')
    ax_chart1.set_title("ABLATION STUDY: SYMPTOM-GATED EFFECT\n(Table 4.2 // Up to +40.24% Boost)", fontsize=15.0, fontweight='heavy', pad=10)
    ax_chart1.grid(axis='x', linestyle=':', color='#CBD5E1', alpha=0.7)
    ax_chart1.legend(loc='lower left', fontsize=11.5, framealpha=0.9, edgecolor='#0A0A0A')
    
    # SUBPLOT 2: DAY 22 WATER SPINACH BIOMASS (BOTTOM LEFT)
    ax_chart2 = fig.add_axes([0.065, 0.115, 0.415, 0.340])
    ax_chart2.set_facecolor('#FFFFFF')
    
    treatments = ["Control\n(Healthy)", "Tank -K\n(Potassium)", "Tank -P\n(Phosphorus)", "Tank -N\n(Nitrogen)"]
    biomass = [54.3, 37.9, 32.2, 19.8]
    errors = [4.2, 3.4, 3.0, 2.4]
    pct_control = [100.0, 69.8, 59.3, 36.5]
    heights = [39.6, 32.8, 28.3, 22.4]
    leaf_counts = [20.4, 16.5, 14.8, 10.5]
    
    x_pos = range(len(treatments))
    bars2 = ax_chart2.bar(x_pos, biomass, yerr=errors, capsize=6, width=0.52, color='#F8FAFC', edgecolor='#0A0A0A', linewidth=1.6)
    bars2[0].set_facecolor('#0F172A')
    
    for i, b in enumerate(biomass):
        t_color = '#FFFFFF' if i == 0 else '#0F172A'
        ax_chart2.text(i, b / 2, f"{b:.1f}g\n({pct_control[i]:.1f}%)", ha='center', va='center', fontsize=14.0, fontweight='bold', fontfamily='monospace', color=t_color)
        ax_chart2.text(i, b + errors[i] + 2.5, f"H: {heights[i]}cm\nLeaves: {leaf_counts[i]}", ha='center', va='bottom', fontsize=11.5, fontweight='bold', fontfamily='monospace', color='#1E293B')

    ax_chart2.set_xticks(x_pos)
    ax_chart2.set_xticklabels(treatments, fontsize=13.0, fontweight='bold')
    ax_chart2.set_ylim(0, 80)
    ax_chart2.set_ylabel("Fresh Biomass (g/plant)", fontsize=13.0, fontweight='bold', fontfamily='monospace')
    ax_chart2.set_title("WATER SPINACH DAY 22 BIOMASS (APPENDIX A)", fontsize=15.0, fontweight='heavy', pad=10)
    ax_chart2.grid(axis='y', linestyle=':', color='#CBD5E1', alpha=0.7)
    
    # Left Bottom High-Impact Banner
    notes_banner = "[*] EMPIRICAL PROOF: 100.00% MULTIMODAL ACCURACY | 54.3g CONTROL BIOMASS | 0% SALT LOCKOUT"
    ax_bg.text(0.265, 0.045, notes_banner, ha='center', va='center', fontsize=12.5, fontweight='bold', fontfamily='monospace', color='#0A0A0A',
               bbox=dict(boxstyle="square,pad=0.6", facecolor='#F8FAFC', edgecolor='#0A0A0A', lw=1.4))

    # ==========================================================================
    # RIGHT HALF: 4 ENORMOUS METRIC BADGES + EXPANSIVE OPEN SCIENCE REPOSITORY
    # ==========================================================================
    ax_bg.text(0.530, 0.890, "KEY RESEARCH HIGHLIGHTS & TELEMETRY // N=143 READINGS", fontsize=15.0, fontweight='bold', fontfamily='monospace', color='#0F172A')
    
    badges = [
        {"num": "100.00%", "lbl": "MULTIMODAL ACCURACY", "sub": "Late-Fusion (Macro F1 = 1.000)"},
        {"num": "12 / 12", "lbl": "UNITS VERIFIED", "sub": "100% Real DWC Units Correct"},
        {"num": "122", "lbl": "LATENT IMAGES CUT", "sub": "Symptom-Gating (+40.24% Boost)"},
        {"num": "0%", "lbl": "SALT PRECIPITATION", "sub": "10s Staggered Dosing Guard Active"}
    ]
    
    for i, b in enumerate(badges):
        col = i % 2
        row = i // 2
        bx = 0.530 + col * 0.225
        by = 0.690 - row * 0.185
        bw, bh = 0.215, 0.170
        
        ax_bg.add_patch(patches.Rectangle((bx, by), bw, bh, fill=True, facecolor='#FFFFFF', edgecolor='#0A0A0A', linewidth=2.0))
        ax_bg.add_patch(patches.Rectangle((bx, by + bh - 0.038), bw, 0.038, fill=True, facecolor='#0F172A', edgecolor='#0A0A0A', linewidth=1.3))
        ax_bg.text(bx + bw/2, by + bh - 0.022, b['lbl'], ha='center', va='center', color='#FFFFFF', fontsize=13.0, fontweight='bold', fontfamily='monospace')
        ax_bg.text(bx + bw/2, by + 0.075, b['num'], ha='center', va='center', color='#0A0A0A', fontsize=40.0, fontweight='heavy', fontfamily='monospace')
        ax_bg.text(bx + bw/2, by + 0.025, b['sub'], ha='center', va='center', color='#1E293B', fontsize=11.5, fontweight='bold', fontfamily='monospace')

    # BOTTOM RIGHT: OPEN SCIENCE & GITHUB REPOSITORY CONTAINER (EXPANSIVE)
    repo_box_x, repo_box_y, repo_box_w, repo_box_h = 0.530, 0.065, 0.440, 0.395
    ax_bg.add_patch(patches.Rectangle((repo_box_x, repo_box_y), repo_box_w, repo_box_h, fill=True, facecolor='#F8FAFC', edgecolor='#0A0A0A', linewidth=2.0))
    ax_bg.add_patch(patches.Rectangle((repo_box_x, repo_box_y + repo_box_h - 0.045), repo_box_w, 0.045, fill=True, facecolor='#0F172A', edgecolor='#0A0A0A', linewidth=1.3))
    ax_bg.text(repo_box_x + repo_box_w/2, repo_box_y + repo_box_h - 0.025, "OPEN SCIENCE REPOSITORY // GITHUB 4K TELEMETRY & SCHEMATICS", 
               ha='center', va='center', color='#FFFFFF', fontsize=13.5, fontweight='bold', fontfamily='monospace')
    
    # Large QR Code on Left
    qr_w, qr_h = 0.155, 0.300
    qr_x, qr_y = repo_box_x + 0.020, repo_box_y + 0.025
    ax_bg.add_patch(patches.Rectangle((qr_x, qr_y), qr_w, qr_h, fill=True, facecolor='#FFFFFF', edgecolor='#0A0A0A', linewidth=1.5))
    if QR_PATH.exists():
        qr_img = Image.open(QR_PATH)
        ax_bg.imshow(qr_img, extent=[qr_x + 0.010, qr_x + qr_w - 0.010, qr_y + 0.010, qr_y + qr_h - 0.010], zorder=10, aspect='auto')
        ax_bg.set_aspect('auto')
        
    # Text details on Right of QR code
    text_x = repo_box_x + 0.190
    ax_bg.text(text_x, repo_box_y + 0.285, "GITHUB REPOSITORY:", fontsize=13.0, fontweight='bold', fontfamily='monospace', color='#0F172A')
    ax_bg.text(text_x, repo_box_y + 0.245, "github.com/nottyzez/A.E.G.I.S-Ai", fontsize=16.5, fontweight='heavy', fontfamily='monospace', color='#1D4ED8')
    
    bullets = [
        "• 143 Time-Series Telemetry Sensor Records (EC, pH, Temp)",
        "• Full IEEE-315 Circuit Schematics & ISA-5.1 P&ID Diagrams",
        "• Production C++ ESP32 Firmware & Pretrained Keras Models",
        "• Hard Safety Lockout Architecture: EC > 2.5 mS/cm | pH < 4.0"
    ]
    for bi, blt in enumerate(bullets):
        ax_bg.text(text_x, repo_box_y + 0.185 - bi * 0.045, blt, fontsize=12.0, fontfamily='monospace', fontweight='bold', color='#1E293B')
    
    # ISO Drawing Stamp (Bottom Right)
    ax_bg.text(0.975, 0.020, "DWG: DWG-AEGIS-COMBO-005 | REV 4.0 | SCALE: NTS | STATUS: RELEASED", ha='right', fontsize=9.5, fontweight='bold', fontfamily='monospace', color='#0F172A')
    
    combo_svg = str(OUTPUT_DIR / "blueprint_unified_results_metrics.svg")
    combo_png = str(OUTPUT_DIR / "blueprint_unified_results_metrics.png")
    plt.savefig(combo_svg, format='svg', bbox_inches='tight')
    plt.savefig(combo_png, format='png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {combo_svg} and {combo_png}")

# ==============================================================================
# CARD 6: MASTER CLOSED-LOOP AI & ESP32 ACTUATION FLOWCHART BLUEPRINT
# ==============================================================================
def generate_card_flowchart():
    print("Generating Card 6: AI & ESP32 Closed-Loop Pump Actuation Flowchart (Frame-Filling Edition)...")
    fig = plt.figure(figsize=(22, 11.5), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    # Outer double engineering frame
    ax.add_patch(patches.Rectangle((0.008, 0.008), 0.984, 0.984, fill=False, edgecolor='#0A0A0A', linewidth=2.6))
    ax.add_patch(patches.Rectangle((0.012, 0.012), 0.976, 0.976, fill=False, edgecolor='#94A3B8', linewidth=0.9, linestyle='--'))
    
    # Top Header
    ax.text(0.025, 0.965, "A.E.G.I.S. ENGINEERING BLUEPRINT // DWG-AEGIS-FLOW-006 // CLOSED-LOOP FLOWCHART", 
            fontsize=13.0, fontweight='bold', color='#0F172A', fontfamily='monospace')
    ax.text(0.025, 0.930, "END-TO-END WORKFLOW: MULTIMODAL AI & ESP32-S3 CLOSED-LOOP FLUIDIC ACTUATION PIPELINE", 
            fontsize=22.5, fontweight='heavy', color='#0A0A0A')
    ax.plot([0.025, 0.975], [0.914, 0.914], color='#0A0A0A', linewidth=2.0)

    # 4 STAGE DEFINITIONS (PROPORTIONAL, SPACIOUS & FULL OF CONTENT)
    stages = [
        {
            "num": "STAGE 1",
            "title": "ESP32-S3 SAMPLING & SENSING",
            "subtitle": "PHYSICAL DWC ROOT TANK (23.3L)",
            "x": 0.030, "w": 0.202,
            "blocks": [
                {"title": "DWC PLANT ROOT TANK", "desc": "• Deep Water Culture (23.3L Tank)\n• Continuous Oxygen Aeration\n• Water Spinach (Ipomoea aquatica)", "h": 0.125, "accent": False},
                {"title": "PHASE 0 & 1: SAMPLING", "desc": "• Pre-Return (4.0s) [Pump 2, GPIO 6]\n• Sample Inflow (6.0s) [Pump 1, GPIO 5]\n• Static Settling Delay (3.0s delay)", "h": 0.135, "accent": True},
                {"title": "SENSING PROBES & CAMERA", "desc": "• Analog pH Probe Kit [GPIO 1]\n• EC / TDS Probe (ATC 25°C) [GPIO 2]\n• DS18B20 Temp Probe [GPIO 4]\n• ESP32-S3 CAM (224x224 RGB)", "h": 0.195, "accent": False},
                {"title": "PHASE 3: RETURN TO TANK", "desc": "• 100% Water Return to Tank (7.0s)\n• Zero Nutrient Solution Depletion\n• Closed Hydraulic Sample Circuit", "h": 0.125, "accent": True}
            ]
        },
        {
            "num": "STAGE 2",
            "title": "A.E.G.I.S. MULTIMODAL AI",
            "subtitle": "CLOUD/SERVER INFERENCE ENGINE",
            "x": 0.276, "w": 0.202,
            "blocks": [
                {"title": "STREAM A: CANOPY VISION", "desc": "• MobileNetV2 + SE-Attention\n• CLAHE + ExG Foliar Masking\n• Stream A Accuracy: 95.12%", "h": 0.135, "accent": False},
                {"title": "SYMPTOM-GATING (NOVEL)", "desc": "• 122 Latent Images Filtered Cut\n• Eliminates Early Label Ambiguity\n• SE-CNN Accuracy Boost: +40.24%", "h": 0.145, "accent": True},
                {"title": "STREAM B: SENSOR ML", "desc": "• 7-D Physicochemical Feature Vector\n• GBDT Gradient Boosting Model\n• Stream B Accuracy: 97.56%", "h": 0.135, "accent": False},
                {"title": "LATE-FUSION STACKING", "desc": "Pfused = (0.35*Pvis) + (0.65*Psens)\n[RESULT] 100.00% ACCURACY\n[Healthy | Deficient N-P-K]", "h": 0.150, "accent": True}
            ]
        },
        {
            "num": "STAGE 3",
            "title": "TWO-TIER SAFETY & MCU",
            "subtitle": "ESP32-S3 DUAL-CORE MCU LOGIC",
            "x": 0.522, "w": 0.202,
            "blocks": [
                {"title": "ESP32-S3 CONTROLLER", "desc": "• Dual-Core Xtensa @ 160MHz\n• Boot-Glitch Lockout Active\n• FreeRTOS Deterministic Tasks", "h": 0.130, "accent": False},
                {"title": "TIER 1: SAFETY LOCKOUT", "desc": "• HARD ABORT: EC > 2.5 or pH < 4.0\n  -> Immediate 0s Emergency Cut\n• BASELINE PRIMING: EC < 0.8 mS/cm", "h": 0.155, "accent": True},
                {"title": "TIER 2: TARGETED DOSING", "desc": "• Precision Micro-Pulse: 5-10s\n• Hard Safety Cap: Max ≤ 25,000ms\n• 10s Inter-Pump Anti-Precipitation", "h": 0.145, "accent": False},
                {"title": "BIOLOGICAL COOLDOWN", "desc": "• 6-12h Nutrient Uptake Pause\n• Root Equilibrium Assimilation\n• Prevents Osmotic Rhizotoxicity", "h": 0.140, "accent": True}
            ]
        },
        {
            "num": "STAGE 4",
            "title": "PUMPS & PROBE FLUSH",
            "subtitle": "6 ACTUATORS & FLUIDIC PIPELINE",
            "x": 0.768, "w": 0.204,
            "blocks": [
                {"title": "PERISTALTIC PUMPS [GPIO 9-11]", "desc": "• Pump 1 [GPIO 9] -> Stock A (N)\n• Pump 2 [GPIO 10] -> Stock B (P)\n• Pump 3 [GPIO 11] -> Stock C (K)\n• 0% Salt Precipitation (10s Delay)", "h": 0.165, "accent": True},
                {"title": "PHASE 5-6: FLUSH & DRAIN", "desc": "• RO Water Flush (5.0s) [Pump 3, GPIO 7]\n• Gravity Waste Drain (6.0s) [Valve, GPIO 8]\n• Cleans Salts from Chamber & Probes", "h": 0.140, "accent": False},
                {"title": "PHASE 7: PROBE PRESERVE", "desc": "• Sample Soak Pulse (3.0s) [Pump 1, GPIO 5]\n• Soaks pH Bulb in Nutrient Water\n• ZERO Sensor Reading during Standby", "h": 0.140, "accent": True},
                {"title": "PROBE SYSTEM INTEGRITY", "desc": "[STATUS] LIFESPAN EXTENDED >300%\n• Stable Calibration Over 22 Days\n• 100% Reliability in Real Tanks", "h": 0.135, "accent": False}
            ]
        }
    ]

    # Draw Stage Containers & Blocks
    sy_top = 0.885
    for stg in stages:
        sx, sw = stg['x'], stg['w']
        
        # Outer Stage Box
        ax.add_patch(patches.Rectangle((sx, 0.165), sw, 0.720, fill=True, facecolor='#FFFFFF', edgecolor='#0A0A0A', linewidth=2.0))
        
        # Stage Header Cap
        ax.add_patch(patches.Rectangle((sx, sy_top - 0.055), sw, 0.055, fill=True, facecolor='#0F172A', edgecolor='#0A0A0A', linewidth=1.4))
        ax.text(sx + sw/2, sy_top - 0.020, stg['title'], ha='center', va='center', color='#FFFFFF', fontsize=13.0, fontweight='bold', fontfamily='monospace')
        ax.text(sx + sw/2, sy_top - 0.040, stg['subtitle'], ha='center', va='center', color='#94A3B8', fontsize=10.5, fontfamily='monospace')

        # Sub-blocks inside stage
        curr_y = sy_top - 0.068
        for blk in stg['blocks']:
            bh = blk['h']
            by = curr_y - bh
            
            bg_col = '#F1F5F9' if blk['accent'] else '#FFFFFF'
            border_col = '#0A0A0A' if blk['accent'] else '#334155'
            lw = 1.6 if blk['accent'] else 1.2
            
            ax.add_patch(patches.Rectangle((sx + 0.007, by), sw - 0.014, bh, fill=True, facecolor=bg_col, edgecolor=border_col, linewidth=lw))
            
            # Title of block
            t_col = '#0A0A0A' if not blk['accent'] else '#0F172A'
            ax.text(sx + 0.014, by + bh - 0.025, blk['title'], fontsize=13.5, fontweight='bold', fontfamily='monospace', color=t_col)
            
            # Description lines (Clean & Bold)
            ax.text(sx + 0.014, by + bh - 0.048, blk['desc'], fontsize=11.8, fontweight='bold', fontfamily='monospace', color='#1E293B', linespacing=1.30, va='top')
            
            curr_y = by - 0.012

    # Draw Inter-Stage Flow Conduit Arrows with Clear Boxed Badges
    flow_arrows = [
        (0.232, 0.276, 0.540, "TELEMETRY\nJSON", 0.254),
        (0.478, 0.522, 0.540, "TARGETED\nAI DOSING", 0.500),
        (0.724, 0.768, 0.540, "ACTUATION\nPULSES", 0.746)
    ]
    for x1, x2, y, label, cx in flow_arrows:
        # Arrow line
        ax.annotate("", xy=(x2, y), xytext=(x1, y),
                    arrowprops=dict(arrowstyle="-|>", color="#0A0A0A", lw=2.8, mutation_scale=18))
        # Clear boxed label
        ax.text(cx, y + 0.045, label, ha='center', va='center', fontsize=10.5, fontweight='heavy', fontfamily='monospace', color='#0A0A0A',
                bbox=dict(boxstyle="square,pad=0.35", facecolor='#FFFFFF', edgecolor='#0A0A0A', lw=1.5))

    # Draw Big Closed-Loop Return Pipe (Bottom)
    ax.annotate("", xy=(0.040, 0.165), xytext=(0.040, 0.070),
                arrowprops=dict(arrowstyle="-", color="#0A0A0A", lw=2.6))
    ax.annotate("", xy=(0.040, 0.165), xytext=(0.040, 0.155),
                arrowprops=dict(arrowstyle="-|>", color="#0A0A0A", lw=2.6, mutation_scale=18))
    ax.plot([0.040, 0.870], [0.070, 0.070], color='#0A0A0A', linewidth=2.6)
    ax.plot([0.870, 0.870], [0.165, 0.070], color='#0A0A0A', linewidth=2.6)
    
    # Label inside closed-loop return pipe
    loop_tag = "<== 100% CLOSED-LOOP NUTRIENT STABILIZATION: REBALANCED SOLUTION RECIRCULATED TO DWC TANK (4-HOUR CYCLE) <=="
    ax.text(0.455, 0.090, loop_tag, ha='center', va='center', fontsize=13.0, fontweight='heavy', fontfamily='monospace', color='#0F172A',
            bbox=dict(boxstyle="square,pad=0.55", facecolor='#F8FAFC', edgecolor='#0A0A0A', lw=1.6))

    # Bottom Right ISO Drawing Stamp
    ax.text(0.975, 0.035, "DWG: DWG-AEGIS-FLOW-006 | REV 4.0 | SCALE: NTS", ha='right', fontsize=10.0, fontweight='bold', fontfamily='monospace', color='#0F172A')
    ax.text(0.975, 0.018, "A.E.G.I.S. RESEARCH TEAM // SUWANNAPHUM PHITTHAYAPHASAN", ha='right', fontsize=9.0, fontfamily='monospace', color='#64748B')
    
    flow_svg = str(OUTPUT_DIR / "blueprint_ai_esp32_flowchart.svg")
    flow_png = str(OUTPUT_DIR / "blueprint_ai_esp32_flowchart.png")
    plt.savefig(flow_svg, format='svg', bbox_inches='tight')
    plt.savefig(flow_png, format='png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {flow_svg} and {flow_png}")

# ==============================================================================
# CARD 7: COMPACT METHODOLOGY FLOWCHART (4:3 VERTICAL FOR CANVA POSTER BOX)
# ==============================================================================
def generate_card_methodology_compact():
    print("Generating Card 7: Compact Methodology Flowchart (4:3 Vertical Canva Box)...")
    fig = plt.figure(figsize=(12, 14), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    # Outer double engineering frame
    ax.add_patch(patches.Rectangle((0.012, 0.010), 0.976, 0.980, fill=False, edgecolor='#0A0A0A', linewidth=2.6))
    ax.add_patch(patches.Rectangle((0.018, 0.015), 0.964, 0.970, fill=False, edgecolor='#94A3B8', linewidth=0.9, linestyle='--'))
    
    # Top Header
    ax.text(0.040, 0.965, "A.E.G.I.S. WORKFLOW // การดำเนินงานระบบดูแลพืชอัจฉริยะ", 
            fontsize=15.0, fontweight='bold', color='#0F172A', fontfamily='sans-serif')
    ax.text(0.040, 0.932, "ESP32-S3 & MULTIMODAL AI CLOSED-LOOP PIPELINE", 
            fontsize=19.0, fontweight='heavy', color='#0A0A0A', fontfamily='sans-serif')
    ax.plot([0.040, 0.960], [0.916, 0.916], color='#0A0A0A', linewidth=2.0)

    # 4 SEQUENTIAL STAGE BLOCKS (TOP TO BOTTOM)
    stages = [
        {
            "num": "STAGE 1",
            "title": "1. ตรวจวัดค่าน้ำ & ถ่ายภาพใบ (SENSING)",
            "bullets": [
                "• Phase 0 คืนน้ำแช่ (4s) + Phase 1 ดูดน้ำตรวจวัด (6s) [GPIO 5, 6]",
                "• เซนเซอร์วัดคุณภาพน้ำ: EC เหนี่ยวนำ AC [GPIO 2] + pH [GPIO 1] + อุณหภูมิ [GPIO 4]",
                "• กล้อง ESP32-S3 CAM บันทึกภาพมุมสูงทรงพุ่มใบพืช (224×224 RGB)",
            ],
            "accent": False,
            "badge": "ข้อมูล Real-time"
        },
        {
            "num": "STAGE 2",
            "title": "2. AI วิเคราะห์สภาวะขาดธาตุอาหาร (AI CORE)",
            "bullets": [
                "• โมเดลภาพใบ (MobileNetV2 + SE-Attention): จำแนกอาการแม่นยำ 95.12%",
                "• โมเดลสารละลาย (GBDT คุณสมบัติเคมี 7 มิติ): ตรวจจับไอออนแม่นยำ 97.56%",
                "• ผสานข้อมูล (Late-Fusion Stacking): ความแม่นยำรวม 100.00% (F1 = 1.000)",
                "• ผลการวินิจฉัย: พืชสมบูรณ์ดี (Control) หรือ ขาดธาตุ N, P, K",
            ],
            "accent": True,
            "badge": "ผลการวินิจฉัย"
        },
        {
            "num": "STAGE 3",
            "title": "3. ตรวจสอบความปลอดภัย 2 ชั้น (SAFETY MCU)",
            "bullets": [
                "• Tier 1 ล็อกฉุกเฉิน: หาก EC > 2.5 หรือ pH < 4.0 สั่งตัดการทำงานทันที (0s Cut)",
                "• Tier 2 คำนวณชดเชย: ควบคุมเวลาเปิดปั๊มแม่นยำระดับ 5–10 วินาที (Max ≤ 25s)",
                "• เว้นระยะห่างปั๊มละ 10 วินาที ป้องกันปุ๋ยตกตะกอน (0% Salt Precipitation)",
                "• หน่วงเวลาชีวภาพ 6–12 ชม. เพื่อให้รากดูดซึม ป้องกันสารเคมีเป็นพิษต่อราก",
            ],
            "accent": False,
            "badge": "พัลส์สั่งการปั๊ม"
        },
        {
            "num": "STAGE 4",
            "title": "4. ปั๊มปุ๋ยแยกธาตุ & ถนอมหัววัด pH (ACTUATION)",
            "bullets": [
                "• ปั๊มรีดสาย 3 ตัว [GPIO 9-11] จ่ายแม่ปุ๋ย N, P, K ตามคำสั่ง AI แม่นยำระดับหยด",
                "• คืนน้ำตัวอย่าง 100% (7s) + ล้างน้ำ RO (5s) + เดรนทิ้ง (6s) [GPIO 6, 7, 8]",
                "• Phase 7 ดูดน้ำตัวอย่างแช่โพรบ pH ช่วง Standby (3s) ป้องกันหัววัดแห้ง ไม่วัดค่า",
            ],
            "accent": True,
            "badge": None
        }
    ]

    bx, bw = 0.045, 0.910
    start_y = 0.895
    block_h = 0.160
    gap = 0.038

    for i, stg in enumerate(stages):
        by = start_y - (i + 1) * block_h - i * gap + 0.015
        
        bg_col = '#F8FAFC' if stg['accent'] else '#FFFFFF'
        border_col = '#0A0A0A'
        lw = 1.8 if stg['accent'] else 1.4
        
        # Outer block box
        ax.add_patch(patches.Rectangle((bx, by), bw, block_h, fill=True, facecolor=bg_col, edgecolor=border_col, linewidth=lw))
        
        # Title Cap
        cap_h = 0.038
        cap_col = '#0F172A' if stg['accent'] else '#1E293B'
        ax.add_patch(patches.Rectangle((bx, by + block_h - cap_h), bw, cap_h, fill=True, facecolor=cap_col, edgecolor='#0A0A0A', linewidth=1.2))
        ax.text(bx + 0.020, by + block_h - 0.020, stg['title'], color='#FFFFFF', fontsize=14.5, fontweight='bold', fontfamily='sans-serif', va='center')
        
        # Bullets
        for line_idx, blt in enumerate(stg['bullets']):
            line_y = by + block_h - cap_h - 0.028 - line_idx * 0.027
            t_col = '#1D4ED8' if "100.00%" in blt else ('#DC2626' if "EC > 2.5" in blt else '#1E293B')
            ax.text(bx + 0.020, line_y, blt, fontsize=12.8, fontweight='bold', fontfamily='sans-serif', color=t_col)

        # Downward Arrow with Boxed Badge to next stage
        if i < 3:
            arrow_top = by
            arrow_bot = by - gap
            arrow_cx = bx + bw / 2
            ax.annotate("", xy=(arrow_cx, arrow_bot), xytext=(arrow_cx, arrow_top),
                        arrowprops=dict(arrowstyle="-|>", color="#0A0A0A", lw=2.8, mutation_scale=18))
            if stg['badge']:
                ax.text(arrow_cx + 0.120, (arrow_top + arrow_bot) / 2, stg['badge'], ha='left', va='center',
                        fontsize=11.5, fontweight='bold', fontfamily='sans-serif', color='#0F172A',
                        bbox=dict(boxstyle="square,pad=0.25", facecolor='#FFFFFF', edgecolor='#0A0A0A', lw=1.2))

    # Closed-Loop Bottom Banner
    loop_text = "<== ระบบควบคุมแบบวงปิด (Closed-Loop) หมุนเวียนตรวจสอบอัตโนมัติทุก 4 ชั่วโมง <=="
    ax.text(0.500, 0.048, loop_text, ha='center', va='center', fontsize=13.5, fontweight='heavy', fontfamily='sans-serif', color='#0F172A',
            bbox=dict(boxstyle="square,pad=0.50", facecolor='#F8FAFC', edgecolor='#0A0A0A', lw=1.6))
    
    ax.text(0.960, 0.016, "DWG: AEGIS-FLOW-COMPACT-007 | REV 1.0 | POWER TEN SYMPOSIUM 2026", ha='right', fontsize=9.0, fontweight='bold', fontfamily='monospace', color='#64748B')

    comp_svg = str(OUTPUT_DIR / "blueprint_methodology_flowchart_compact.svg")
    comp_png = str(OUTPUT_DIR / "blueprint_methodology_flowchart_compact.png")
    plt.savefig(comp_svg, format='svg', bbox_inches='tight')
    plt.savefig(comp_png, format='png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {comp_svg} and {comp_png}")

# ==============================================================================
# CARD 8: COMPACT RESULTS & BIOMASS CHART (4:3 VERTICAL FOR CANVA POSTER BOX)
# ==============================================================================
def generate_card_results_compact():
    print("Generating Card 8: Compact Results & Biomass Chart (4:3 Vertical Canva Box)...")
    fig = plt.figure(figsize=(12, 14), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    
    ax_bg = fig.add_axes([0, 0, 1, 1])
    ax_bg.set_xlim(0, 1)
    ax_bg.set_ylim(0, 1)
    ax_bg.axis('off')
    
    # Outer double engineering frame
    ax_bg.add_patch(patches.Rectangle((0.012, 0.010), 0.976, 0.980, fill=False, edgecolor='#0A0A0A', linewidth=2.6))
    ax_bg.add_patch(patches.Rectangle((0.018, 0.015), 0.964, 0.970, fill=False, edgecolor='#94A3B8', linewidth=0.9, linestyle='--'))
    
    # Top Header
    ax_bg.text(0.040, 0.965, "A.E.G.I.S. RESULTS // สรุปผลการทดลองและการวินิจฉัย", 
               fontsize=15.0, fontweight='bold', color='#0F172A', fontfamily='sans-serif')
    ax_bg.text(0.040, 0.932, "EMPIRICAL BIOMASS HARVEST & AI ACCURACY VERIFICATION", 
               fontsize=19.0, fontweight='heavy', color='#0A0A0A', fontfamily='sans-serif')
    ax_bg.plot([0.040, 0.960], [0.916, 0.916], color='#0A0A0A', linewidth=2.0)

    # 2 GIANT METRIC BADGES (TOP HALF)
    badges = [
        {"num": "100.00%", "lbl": "ความแม่นยำของ AI (ACCURACY)", "sub": "โมเดลผสานภาพและเคมี (F1 = 1.000)\nLate-Fusion Stacking"},
        {"num": "12 / 12", "lbl": "ยืนยันผลในถังปลูกจริง (VERIFIED)", "sub": "วินิจฉัยถูกต้องครบทุกถังปลูก\nความเชื่อมั่นเฉลี่ย 83.96%"}
    ]
    
    for i, b in enumerate(badges):
        bx = 0.045 + i * 0.465
        by = 0.725
        bw, bh = 0.445, 0.170
        
        ax_bg.add_patch(patches.Rectangle((bx, by), bw, bh, fill=True, facecolor='#FFFFFF', edgecolor='#0A0A0A', linewidth=2.0))
        ax_bg.add_patch(patches.Rectangle((bx, by + bh - 0.038), bw, 0.038, fill=True, facecolor='#0F172A', edgecolor='#0A0A0A', linewidth=1.2))
        ax_bg.text(bx + bw/2, by + bh - 0.020, b['lbl'], ha='center', va='center', color='#FFFFFF', fontsize=13.0, fontweight='bold', fontfamily='sans-serif')
        
        ax_bg.text(bx + bw/2, by + 0.075, b['num'], ha='center', va='center', color='#0A0A0A', fontsize=44.0, fontweight='heavy', fontfamily='monospace')
        ax_bg.text(bx + bw/2, by + 0.025, b['sub'], ha='center', va='center', color='#1E293B', fontsize=12.0, fontweight='bold', fontfamily='sans-serif', linespacing=1.25)

    # GIANT BAR CHART: WATER SPINACH BIOMASS AT DAY 22 HARVEST
    ax_chart = fig.add_axes([0.085, 0.165, 0.855, 0.510])
    ax_chart.set_facecolor('#FFFFFF')
    
    treatments = ["ถังปกติ\n(Control)", "ขาดโพแทสเซียม\n(Tank -K)", "ขาดฟอสฟอรัส\n(Tank -P)", "ขาดไนโตรเจน\n(Tank -N)"]
    biomass = [54.3, 37.9, 32.2, 19.8]
    errors = [4.2, 3.4, 3.0, 2.4]
    pct_control = [100.0, 69.8, 59.3, 36.5]
    heights = [39.6, 32.8, 28.3, 22.4]
    leaf_counts = [20.4, 16.5, 14.8, 10.5]
    
    x_pos = range(len(treatments))
    bars = ax_chart.bar(x_pos, biomass, yerr=errors, capsize=8, width=0.55, color='#F8FAFC', edgecolor='#0A0A0A', linewidth=2.0)
    bars[0].set_facecolor('#0F172A')
    
    for i, b in enumerate(biomass):
        t_color = '#FFFFFF' if i == 0 else '#0F172A'
        # Text inside bar
        ax_chart.text(i, b / 2, f"{b:.1f}g\n({pct_control[i]:.1f}%)", ha='center', va='center', fontsize=18.0, fontweight='heavy', fontfamily='monospace', color=t_color)
        # Annotation above error bar
        ax_chart.text(i, b + errors[i] + 2.5, f"สูง {heights[i]} cm\n{leaf_counts[i]} ใบ", ha='center', va='bottom', fontsize=13.0, fontweight='bold', fontfamily='sans-serif', color='#1E293B')

    ax_chart.set_xticks(x_pos)
    ax_chart.set_xticklabels(treatments, fontsize=15.0, fontweight='bold')
    ax_chart.set_ylim(0, 82)
    ax_chart.set_ylabel("น้ำหนักสดต่อต้น (กรัม)", fontsize=14.0, fontweight='bold', fontfamily='sans-serif')
    ax_chart.set_title("ผลผลิตน้ำหนักสดผักบุ้งจีน ณ วันเก็บเกี่ยว วันที่ 22 (ภาคผนวก ก ตารางที่ 3)", fontsize=16.5, fontweight='heavy', pad=14, fontfamily='sans-serif')
    ax_chart.grid(axis='y', linestyle=':', color='#CBD5E1', alpha=0.7)

    # Bottom Summary Box
    summary_msg = "[*] สรุปผล: โมเดล AI วินิจฉัยแม่นยำ 100% | ขาดไนโตรเจนชะงักการโตสูงสุด (-63.5%) | ปุ๋ยไม่ตกตะกอน 0%"
    ax_bg.text(0.500, 0.050, summary_msg, ha='center', va='center', fontsize=13.0, fontweight='heavy', fontfamily='sans-serif', color='#0F172A',
               bbox=dict(boxstyle="square,pad=0.50", facecolor='#F8FAFC', edgecolor='#0A0A0A', lw=1.6))
    
    ax_bg.text(0.960, 0.016, "DWG: AEGIS-RESULTS-COMPACT-008 | REV 1.0 | POWER TEN SYMPOSIUM 2026", ha='right', fontsize=9.0, fontweight='bold', fontfamily='monospace', color='#64748B')

    res_svg = str(OUTPUT_DIR / "blueprint_results_biomass_compact.svg")
    res_png = str(OUTPUT_DIR / "blueprint_results_biomass_compact.png")
    plt.savefig(res_svg, format='svg', bbox_inches='tight')
    plt.savefig(res_png, format='png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {res_svg} and {res_png}")

# ==============================================================================
# CARD 9: DEDICATED 4-STAGE AI WORKFLOW FLOWCHART (4:3 VERTICAL BLUEPRINT)
# ==============================================================================
def generate_card_ai_workflow_flowchart():
    print("Generating Card 9: Dedicated 4-Stage AI Workflow Flowchart (300 DPI)...")
    fig = plt.figure(figsize=(12, 14), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    # Outer double engineering frame
    ax.add_patch(patches.Rectangle((0.012, 0.010), 0.976, 0.980, fill=False, edgecolor='#0A0A0A', linewidth=2.6))
    ax.add_patch(patches.Rectangle((0.018, 0.015), 0.964, 0.970, fill=False, edgecolor='#94A3B8', linewidth=0.9, linestyle='--'))
    
    # Top Header
    ax.text(0.040, 0.965, "A.E.G.I.S. AI WORKFLOW // ผังการทำงานของระบบปัญญาประดิษฐ์", 
            fontsize=15.0, fontweight='bold', color='#0F172A', fontfamily='sans-serif')
    ax.text(0.040, 0.932, "MULTIMODAL LATE-FUSION PREDICTION & DOSING PIPELINE", 
            fontsize=19.0, fontweight='heavy', color='#0A0A0A', fontfamily='sans-serif')
    ax.plot([0.040, 0.960], [0.916, 0.916], color='#0A0A0A', linewidth=2.0)

    # 4 STAGE PIPELINE
    stages = [
        {
            "num": "STAGE 1",
            "title": "1. รับข้อมูลนำเข้า 2 ทาง (DUAL INPUT)",
            "bullets": [
                "• ข้อมูลภาพ: กล้อง ESP32-S3 CAM ถ่ายภาพมุมสูงทรงพุ่มใบ (224×224 RGB)",
                "• ข้อมูลเคมี: เซนเซอร์วัดค่าน้ำ 7 มิติ (EC, pH, อุณหภูมิ, อัตราลดลงใน 24 ชม.)",
            ],
            "accent": False,
            "badge": "ข้อมูลนำเข้า Real-time"
        },
        {
            "num": "STAGE 2",
            "title": "2. แยกประมวลผล AI คู่ขนาน (PARALLEL AI CORE)",
            "bullets": [
                "• สายภาพ (MobileNetV2): กรองภาพระยะแฝง 122 ภาพ -> จำแนกแม่นยำ 95.12%",
                "• สายเคมี (GBDT Model): วิเคราะห์การลดลงของไอออนปุ๋ย -> จำแนกแม่นยำ 97.56%",
            ],
            "accent": True,
            "badge": "ความน่าจะเป็น 2 สาย"
        },
        {
            "num": "STAGE 3",
            "title": "3. ผสานผลการตัดสินใจ (LATE-FUSION STACKING)",
            "bullets": [
                "• สูตรถ่วงน้ำหนัก: Pfused = (ผลวิเคราะห์ภาพ × 35%) + (ผลวิเคราะห์ค่าน้ำ × 65%)",
                "• ความแม่นยำรวม: 100.00% (ตรวจแปลงปลูกจริงถูกต้องครบ 12/12 ถัง, F1 = 1.000)",
            ],
            "accent": False,
            "badge": "ผลการวินิจฉัย N-P-K"
        },
        {
            "num": "STAGE 4",
            "title": "4. วินิจฉัยผล & สั่งการปั๊มปุ๋ย (OUTPUT & CONTROL)",
            "bullets": [
                "• ผลวินิจฉัย: พืชสมบูรณ์ดี (Control) หรือ ขาดธาตุอาหาร N, P หรือ K",
                "• สั่งการ: ESP32 สั่งปั๊มรีดสายเติมปุ๋ยเฉพาะธาตุที่ขาดทันที (พัลส์ 5–10 วินาที)",
            ],
            "accent": True,
            "badge": None
        }
    ]

    bx, bw = 0.045, 0.910
    start_y = 0.895
    block_h = 0.160
    gap = 0.038

    for i, stg in enumerate(stages):
        by = start_y - (i + 1) * block_h - i * gap + 0.015
        
        bg_col = '#F8FAFC' if stg['accent'] else '#FFFFFF'
        border_col = '#0A0A0A'
        lw = 1.8 if stg['accent'] else 1.4
        
        # Outer block box
        ax.add_patch(patches.Rectangle((bx, by), bw, block_h, fill=True, facecolor=bg_col, edgecolor=border_col, linewidth=lw))
        
        # Title Cap
        cap_h = 0.038
        cap_col = '#0F172A' if stg['accent'] else '#1E293B'
        ax.add_patch(patches.Rectangle((bx, by + block_h - cap_h), bw, cap_h, fill=True, facecolor=cap_col, edgecolor='#0A0A0A', linewidth=1.2))
        ax.text(bx + 0.020, by + block_h - 0.020, stg['title'], color='#FFFFFF', fontsize=14.5, fontweight='bold', fontfamily='sans-serif', va='center')
        
        # Bullets
        for line_idx, blt in enumerate(stg['bullets']):
            line_y = by + block_h - cap_h - 0.035 - line_idx * 0.036
            t_col = '#1D4ED8' if "100.00%" in blt else ('#0F172A' if "Pfused" in blt else '#1E293B')
            ax.text(bx + 0.020, line_y, blt, fontsize=13.0, fontweight='bold', fontfamily='sans-serif', color=t_col)

        # Downward Arrow with Boxed Badge to next stage
        if i < 3:
            arrow_top = by
            arrow_bot = by - gap
            arrow_cx = bx + bw / 2
            ax.annotate("", xy=(arrow_cx, arrow_bot), xytext=(arrow_cx, arrow_top),
                        arrowprops=dict(arrowstyle="-|>", color="#0A0A0A", lw=2.8, mutation_scale=18))
            if stg['badge']:
                ax.text(arrow_cx + 0.120, (arrow_top + arrow_bot) / 2, stg['badge'], ha='left', va='center',
                        fontsize=11.5, fontweight='bold', fontfamily='sans-serif', color='#0F172A',
                        bbox=dict(boxstyle="square,pad=0.25", facecolor='#FFFFFF', edgecolor='#0A0A0A', lw=1.2))

    # Closed-Loop Bottom Banner
    loop_text = "<== ระบบควบคุมแบบวงปิด (Closed-Loop) หมุนเวียนตรวจสอบอัตโนมัติทุก 4 ชั่วโมง <=="
    ax.text(0.500, 0.048, loop_text, ha='center', va='center', fontsize=13.5, fontweight='heavy', fontfamily='sans-serif', color='#0F172A',
            bbox=dict(boxstyle="square,pad=0.50", facecolor='#F8FAFC', edgecolor='#0A0A0A', lw=1.6))
    
    ax.text(0.960, 0.016, "DWG: AEGIS-AI-FLOW-009 | REV 1.0 | POWER TEN SYMPOSIUM 2026", ha='right', fontsize=9.0, fontweight='bold', fontfamily='monospace', color='#64748B')

    ai_flow_svg = str(OUTPUT_DIR / "blueprint_ai_workflow_flowchart.svg")
    ai_flow_png = str(OUTPUT_DIR / "blueprint_ai_workflow_flowchart.png")
    plt.savefig(ai_flow_svg, format='svg', bbox_inches='tight')
    plt.savefig(ai_flow_png, format='png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {ai_flow_svg} and {ai_flow_png}")

# ==============================================================================
# CARD 10: 3-METRIC PLANT GROWTH COMPARISON GROUPED BAR CHART (STANDALONE)
# ==============================================================================
def generate_card_growth_morphology_3d():
    print("Generating Card 10: Standalone 3-Metric Plant Growth Comparison Grouped Bar Chart...")
    fig = plt.figure(figsize=(12, 14), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    
    ax_bg = fig.add_axes([0, 0, 1, 1])
    ax_bg.set_xlim(0, 1)
    ax_bg.set_ylim(0, 1)
    ax_bg.axis('off')
    
    # Outer double engineering frame
    ax_bg.add_patch(patches.Rectangle((0.012, 0.010), 0.976, 0.980, fill=False, edgecolor='#0A0A0A', linewidth=2.6))
    ax_bg.add_patch(patches.Rectangle((0.018, 0.015), 0.964, 0.970, fill=False, edgecolor='#94A3B8', linewidth=0.9, linestyle='--'))
    
    # Top Header
    ax_bg.text(0.040, 0.965, "A.E.G.I.S. MORPHOLOGY // สรุปการเจริญเติบโตพืช 3 มิติ", 
               fontsize=15.0, fontweight='bold', color='#0F172A', fontfamily='sans-serif')
    ax_bg.text(0.040, 0.932, "3-METRIC PLANT GROWTH COMPARISON (HEIGHT, LEAF COUNT, BIOMASS)", 
               fontsize=18.0, fontweight='heavy', color='#0A0A0A', fontfamily='sans-serif')
    ax_bg.plot([0.040, 0.960], [0.916, 0.916], color='#0A0A0A', linewidth=2.0)

    # 3 SUMMARY BADGES AT TOP
    badges = [
        {"num": "54.3 g", "lbl": "ชีวมวลสูงสุด (CONTROL)", "sub": "สมบูรณ์กว่ากลุ่มขาด N 2.7 เท่า"},
        {"num": "-63.5%", "lbl": "ชะงักการโตสูงสุด (-N)", "sub": "เหลือ 19.8g จาก RuBisCO สลาย"},
        {"num": "100%", "lbl": "AI วินิจฉัยแม่นยำ", "sub": "ทำนายสอดคล้องกับสรีรวิทยา"}
    ]
    for i, b in enumerate(badges):
        bx = 0.045 + i * 0.310
        by = 0.770
        bw, bh = 0.290, 0.130
        ax_bg.add_patch(patches.Rectangle((bx, by), bw, bh, fill=True, facecolor='#FFFFFF', edgecolor='#0A0A0A', linewidth=1.8))
        ax_bg.add_patch(patches.Rectangle((bx, by + bh - 0.034), bw, 0.034, fill=True, facecolor='#0F172A', edgecolor='#0A0A0A', linewidth=1.1))
        ax_bg.text(bx + bw/2, by + bh - 0.018, b['lbl'], ha='center', va='center', color='#FFFFFF', fontsize=11.5, fontweight='bold', fontfamily='sans-serif')
        ax_bg.text(bx + bw/2, by + 0.055, b['num'], ha='center', va='center', color='#0A0A0A', fontsize=28.0, fontweight='heavy', fontfamily='monospace')
        ax_bg.text(bx + bw/2, by + 0.018, b['sub'], ha='center', va='center', color='#334155', fontsize=10.0, fontweight='bold', fontfamily='sans-serif')

    # GROUPED BAR CHART
    ax_chart = fig.add_axes([0.085, 0.165, 0.855, 0.560])
    ax_chart.set_facecolor('#FFFFFF')
    
    import numpy as np
    tanks = ["ถังปกติ\n(Control)", "ขาดโพแทสเซียม\n(Tank -K)", "ขาดฟอสฟอรัส\n(Tank -P)", "ขาดไนโตรเจน\n(Tank -N)"]
    x = np.arange(len(tanks))
    width = 0.24
    
    heights = [39.6, 32.8, 28.3, 22.4]
    leaves = [20.4, 16.5, 14.8, 10.5]
    biomass = [54.3, 37.9, 32.2, 19.8]
    
    rects1 = ax_chart.bar(x - width, heights, width, label='ความสูงต้น (ซม.)', color='#94A3B8', edgecolor='#0A0A0A', linewidth=1.6)
    rects2 = ax_chart.bar(x, leaves, width, label='จำนวนใบจริง (ใบ)', color='#475569', edgecolor='#0A0A0A', linewidth=1.6)
    rects3 = ax_chart.bar(x + width, biomass, width, label='น้ำหนักสด (กรัม/ต้น)', color='#0F172A', edgecolor='#0A0A0A', linewidth=1.8)
    
    # Add values on top of bars
    for rect in rects1:
        h = rect.get_height()
        ax_chart.text(rect.get_x() + rect.get_width()/2., h + 1.2, f'{h:.1f}', ha='center', va='bottom', fontsize=11.0, fontweight='bold', fontfamily='monospace')
    for rect in rects2:
        h = rect.get_height()
        ax_chart.text(rect.get_x() + rect.get_width()/2., h + 1.2, f'{h:.1f}', ha='center', va='bottom', fontsize=11.0, fontweight='bold', fontfamily='monospace')
    for rect in rects3:
        h = rect.get_height()
        ax_chart.text(rect.get_x() + rect.get_width()/2., h + 1.2, f'{h:.1f}g', ha='center', va='bottom', fontsize=12.5, fontweight='heavy', fontfamily='monospace', color='#0F172A')

    ax_chart.set_xticks(x)
    ax_chart.set_xticklabels(tanks, fontsize=14.0, fontweight='bold')
    ax_chart.set_ylim(0, 68)
    ax_chart.set_ylabel("ค่าการเจริญเติบโต (ซม. / ใบ / กรัม)", fontsize=13.5, fontweight='bold', fontfamily='sans-serif')
    ax_chart.set_title("เปรียบเทียบการเจริญเติบโตผักบุ้งจีน 3 มิติ ณ วันเก็บเกี่ยว วันที่ 22 (ภาคผนวก ก)", fontsize=16.0, fontweight='heavy', pad=14, fontfamily='sans-serif')
    ax_chart.grid(axis='y', linestyle=':', color='#CBD5E1', alpha=0.7)
    ax_chart.legend(loc='upper right', fontsize=12.0, framealpha=0.95, edgecolor='#0A0A0A')

    # Bottom Summary Box
    summary_msg = "[*] สรุป: ขาด N ส่งผลให้ชะงักการโตสูงสุดทั้ง 3 มิติ (ลดลง 43-63%) | Control เจริญเติบโตสมบูรณ์ที่สุดในระบบ DWC"
    ax_bg.text(0.500, 0.050, summary_msg, ha='center', va='center', fontsize=12.5, fontweight='heavy', fontfamily='sans-serif', color='#0F172A',
               bbox=dict(boxstyle="square,pad=0.50", facecolor='#F8FAFC', edgecolor='#0A0A0A', lw=1.6))
    
    ax_bg.text(0.960, 0.016, "DWG: AEGIS-GROWTH-010 | REV 1.0 | POWER TEN SYMPOSIUM 2026", ha='right', fontsize=9.0, fontweight='bold', fontfamily='monospace', color='#64748B')

    growth_svg = str(OUTPUT_DIR / "blueprint_growth_morphology_3d.svg")
    growth_png = str(OUTPUT_DIR / "blueprint_growth_morphology_3d.png")
    plt.savefig(growth_svg, format='svg', bbox_inches='tight')
    plt.savefig(growth_png, format='png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {growth_svg} and {growth_png}")

# ==============================================================================
# CARD 11: AI EVALUATION & DIAGNOSIS SUMMARY TABLE BLUEPRINT (300 DPI)
# ==============================================================================
def generate_card_ai_evaluation_table():
    print("Generating Card 11: AI Evaluation & Diagnosis Summary Table Blueprint (300 DPI)...")
    fig = plt.figure(figsize=(14, 11), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    # Outer double engineering frame
    ax.add_patch(patches.Rectangle((0.010, 0.010), 0.980, 0.980, fill=False, edgecolor='#0A0A0A', linewidth=2.6))
    ax.add_patch(patches.Rectangle((0.015, 0.015), 0.970, 0.970, fill=False, edgecolor='#94A3B8', linewidth=0.9, linestyle='--'))
    
    # Top Header
    ax.text(0.035, 0.965, "A.E.G.I.S. EVALUATION // ตารางสรุปผลการทดสอบและวินิจฉัยโมเดล AI", 
            fontsize=15.0, fontweight='bold', color='#0F172A', fontfamily='sans-serif')
    ax.text(0.035, 0.932, "HIERARCHICAL MULTIMODAL LATE-FUSION VALIDATION & DIAGNOSIS SUMMARY", 
            fontsize=19.0, fontweight='heavy', color='#0A0A0A', fontfamily='sans-serif')
    ax.plot([0.035, 0.965], [0.916, 0.916], color='#0A0A0A', linewidth=2.0)

    # 3 GIANT HIGHLIGHT BADGES AT TOP
    badges = [
        {"num": "100.00%", "lbl": "ความแม่นยำชุดทดสอบ (TEST SET)", "sub": "Macro F1-Score = 1.0000\nชุดทดสอบหลังคัดกรองภาพแฝง"},
        {"num": "12 / 12", "lbl": "วินิจฉัยแปลงจริง (UNIT-LEVEL)", "sub": "ถูกต้อง 100% ครบทุกถังทดสอบ\n4 ถังหลัก + 8 แก้วทดลองซ้ำ"},
        {"num": "83.96%", "lbl": "ความเชื่อมั่นเฉลี่ยรวม (CONFIDENCE)", "sub": "SD = ±6.22% (รวมสองสาย)\nเซนเซอร์ 90.78% / ภาพ 72.60%"}
    ]
    for i, b in enumerate(badges):
        bx = 0.035 + i * 0.315
        by = 0.735
        bw, bh = 0.300, 0.160
        ax.add_patch(patches.Rectangle((bx, by), bw, bh, fill=True, facecolor='#FFFFFF', edgecolor='#0A0A0A', linewidth=2.0))
        ax.add_patch(patches.Rectangle((bx, by + bh - 0.036), bw, 0.036, fill=True, facecolor='#0F172A', edgecolor='#0A0A0A', linewidth=1.2))
        ax.text(bx + bw/2, by + bh - 0.018, b['lbl'], ha='center', va='center', color='#FFFFFF', fontsize=12.0, fontweight='bold', fontfamily='sans-serif')
        ax.text(bx + bw/2, by + 0.070, b['num'], ha='center', va='center', color='#0A0A0A', fontsize=36.0, fontweight='heavy', fontfamily='monospace')
        ax.text(bx + bw/2, by + 0.022, b['sub'], ha='center', va='center', color='#334155', fontsize=11.0, fontweight='bold', fontfamily='sans-serif', linespacing=1.2)

    # MASTER SUMMARY TABLE
    tx, ty = 0.035, 0.150
    tw, th = 0.930, 0.550
    
    # Columns: 30%, 30%, 40%
    c1_w = tw * 0.30
    c2_w = tw * 0.28
    c3_w = tw * 0.42
    c1_x = tx
    c2_x = tx + c1_w
    c3_x = tx + c1_w + c2_w
    
    # Table Header Cap
    head_h = 0.055
    head_y = ty + th - head_h
    ax.add_patch(patches.Rectangle((tx, head_y), tw, head_h, fill=True, facecolor='#0F172A', edgecolor='#0A0A0A', linewidth=1.6))
    ax.plot([c2_x, c2_x], [head_y, head_y + head_h], color='#FFFFFF', linewidth=1.2)
    ax.plot([c3_x, c3_x], [head_y, head_y + head_h], color='#FFFFFF', linewidth=1.2)
    
    ax.text(c1_x + 0.015, head_y + head_h/2, "ตัวชี้วัดประสิทธิภาพ (Evaluation Metric)", va='center', color='#FFFFFF', fontsize=13.0, fontweight='bold', fontfamily='sans-serif')
    ax.text(c2_x + 0.015, head_y + head_h/2, "ค่าผลลัพธ์ (Result)", va='center', color='#FFFFFF', fontsize=13.0, fontweight='bold', fontfamily='sans-serif')
    ax.text(c3_x + 0.015, head_y + head_h/2, "พารามิเตอร์และรายละเอียดอ้างอิง (Details)", va='center', color='#FFFFFF', fontsize=13.0, fontweight='bold', fontfamily='sans-serif')

    # Table Rows
    rows = [
        ("สถาปัตยกรรมโมเดล", "Hierarchical Late-Fusion", "ถ่วงน้ำหนัก w_img = 0.35 (ภาพ) : w_sen = 0.65 (เซนเซอร์)", True),
        ("ความแม่นยำบนชุดทดสอบ (Accuracy)", "100.00% (F1 = 1.000)", "ชุดทดสอบหลังคัดกรองภาพระยะแฝง 122 ภาพ (Holdout N=41)", False),
        ("ความถูกต้องแปลงทดลองจริง (Unit-Level)", "12 / 12 หน่วย (100.00%)", "4 ถังหลัก (Control, -N, -P, -K) + 8 แก้วทดลองซ้ำ (Cup 1–8)", True),
        ("ความเชื่อมั่นรวมเฉลี่ย (Mean Confidence)", "83.96% ± 6.22%", "ค่าความเชื่อมั่นเฉลี่ยของการตัดสินใจขั้นสุดท้ายรวมสองสาย", False),
        ("  • ความเชื่อมั่นสายเซนเซอร์ (Sensor Stream)", "90.78%", "วิเคราะห์คุณสมบัติสารละลาย 7 มิติ (GBDT Gradient Boosting)", True),
        ("  • ความเชื่อมั่นสายภาพถ่าย (Vision Stream)", "72.60%", "วิเคราะห์ลักษณะอาการพุ่มใบมุมสูง (MobileNetV2 + SE)", False),
    ]

    row_h = (th - head_h) / len(rows)
    for idx, (col1, col2, col3, is_alt) in enumerate(rows):
        ry = head_y - (idx + 1) * row_h
        row_bg = '#F8FAFC' if is_alt else '#FFFFFF'
        
        ax.add_patch(patches.Rectangle((tx, ry), tw, row_h, fill=True, facecolor=row_bg, edgecolor='#0A0A0A', linewidth=1.2))
        ax.plot([c2_x, c2_x], [ry, ry + row_h], color='#CBD5E1', linewidth=1.2)
        ax.plot([c3_x, c3_x], [ry, ry + row_h], color='#CBD5E1', linewidth=1.2)
        
        t1_col = '#0F172A'
        t2_col = '#1D4ED8' if "100.00%" in col2 else ('#0F172A' if "12 / 12" in col2 else '#1E293B')
        
        ax.text(c1_x + 0.015, ry + row_h/2, col1, va='center', color=t1_col, fontsize=12.5, fontweight='bold', fontfamily='sans-serif')
        ax.text(c2_x + 0.015, ry + row_h/2, col2, va='center', color=t2_col, fontsize=13.0, fontweight='heavy', fontfamily='sans-serif')
        ax.text(c3_x + 0.015, ry + row_h/2, col3, va='center', color='#334155', fontsize=12.0, fontweight='bold', fontfamily='sans-serif')

    # Bottom Summary Note Banner
    notes_banner = "[*] สรุป: โมเดลผสาน Late-Fusion ดึงจุดเด่นเซนเซอร์เคมี (90.78%) ร่วมกับภาพถ่ายใบ (72.60%) บรรลุความแม่นยำสมบูรณ์ 100% ในแปลงจริง"
    ax.text(0.500, 0.065, notes_banner, ha='center', va='center', fontsize=12.5, fontweight='heavy', fontfamily='sans-serif', color='#0F172A',
            bbox=dict(boxstyle="square,pad=0.55", facecolor='#F8FAFC', edgecolor='#0A0A0A', lw=1.6))
    
    ax.text(0.965, 0.020, "DWG: AEGIS-EVAL-TABLE-011 | REV 1.0 | POWER TEN SYMPOSIUM 2026", ha='right', fontsize=9.5, fontweight='bold', fontfamily='monospace', color='#64748B')

    eval_svg = str(OUTPUT_DIR / "blueprint_ai_evaluation_table.svg")
    eval_png = str(OUTPUT_DIR / "blueprint_ai_evaluation_table.png")
    plt.savefig(eval_svg, format='svg', bbox_inches='tight')
    plt.savefig(eval_png, format='png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {eval_svg} and {eval_png}")

def main():
    generate_card_1()
    generate_card_2()
    generate_card_3()
    generate_card_4()
    generate_card_combo()
    generate_card_flowchart()
    generate_card_methodology_compact()
    generate_card_results_compact()
    generate_card_ai_workflow_flowchart()
    generate_card_growth_morphology_3d()
    generate_card_ai_evaluation_table()
    print("All 11 blueprints successfully generated!")

if __name__ == "__main__":
    main()
