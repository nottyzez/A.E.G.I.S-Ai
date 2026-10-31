#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A.E.G.I.S. Poster Engineering Blueprints Generator
Generates 4 publication-ready Minimal White Engineering Blueprint vector graphics
(SVG + 300 DPI PNG, 2400x1600 px) strictly aligned with the 55-page A.E.G.I.S. thesis.
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
from matplotlib.gridspec import GridSpec
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "assets" / "blueprints"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
QR_PATH = PROJECT_ROOT / "assets" / "qr_code.png"

# Setup style parameters
plt.rcParams['font.sans-serif'] = ['Leelawadee UI', 'Tahoma', 'Segoe UI', 'DejaVu Sans', 'Arial']
plt.rcParams['font.monospace'] = ['Consolas', 'Courier New', 'DejaVu Sans Mono']
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.edgecolor'] = '#111111'
plt.rcParams['axes.linewidth'] = 1.2

def draw_title_block(ax, dwg_no, title, date="2026-10-31"):
    """Draw an ISO/IEEE standard technical blueprint title block."""
    # Outer frame
    ax.add_patch(patches.Rectangle((0.01, 0.01), 0.98, 0.98, fill=False, edgecolor='#111111', linewidth=2.0))
    # Inner border line
    ax.add_patch(patches.Rectangle((0.015, 0.015), 0.97, 0.97, fill=False, edgecolor='#64748B', linewidth=0.8, linestyle='--'))
    
    # Title block in bottom-right
    tb_x, tb_y, tb_w, tb_h = 0.62, 0.02, 0.36, 0.09
    ax.add_patch(patches.Rectangle((tb_x, tb_y), tb_w, tb_h, fill=True, facecolor='#F8FAFC', edgecolor='#111111', linewidth=1.5))
    ax.plot([tb_x, tb_x + tb_w], [tb_y + tb_h * 0.5, tb_y + tb_h * 0.5], color='#111111', linewidth=1.0)
    ax.plot([tb_x + tb_w * 0.55, tb_x + tb_w * 0.55], [tb_y, tb_y + tb_h], color='#111111', linewidth=1.0)
    
    ax.text(tb_x + 0.01, tb_y + tb_h * 0.72, "PROJECT: A.E.G.I.S. RESEARCH", fontsize=8, fontweight='bold', color='#111111', fontfamily='monospace')
    ax.text(tb_x + 0.01, tb_y + tb_h * 0.22, f"SHEET: {title[:28]}", fontsize=7.5, color='#334155', fontfamily='monospace')
    ax.text(tb_x + tb_w * 0.57, tb_y + tb_h * 0.72, f"DWG: {dwg_no} | REV 3.2", fontsize=7.5, fontweight='bold', color='#111111', fontfamily='monospace')
    ax.text(tb_x + tb_w * 0.57, tb_y + tb_h * 0.22, f"DATE: {date} | SCALE: NTS", fontsize=7, color='#64748B', fontfamily='monospace')

    # Top Header
    ax.text(0.04, 0.95, f"A.E.G.I.S. ENGINEERING BLUEPRINT // {dwg_no}", fontsize=11, fontweight='bold', color='#111111', fontfamily='monospace')
    ax.text(0.04, 0.92, title.upper(), fontsize=16, fontweight='heavy', color='#0A0A0A')
    ax.plot([0.04, 0.96], [0.905, 0.905], color='#111111', linewidth=1.5)

# ==============================================================================
# CARD 1: TWO-TIER CLOSED-LOOP FLUIDIC FSM & HARDWARE BLUEPRINT
# ==============================================================================
def generate_card_1():
    print("Generating Card 1: Two-Tier Closed-Loop Fluidic FSM...")
    fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    draw_title_block(ax, "AEGIS-DWG-001", "Two-Tier Closed-Loop Fluidic Control & Maintenance FSM")
    
    # ----------------------------------------------------
    # SECTION 1: SENSORS & INPUT INSTRUMENTATION (TOP ROW)
    # ----------------------------------------------------
    ax.text(0.04, 0.865, "SECTION 1: SENSOR INSTRUMENTATION & CALIBRATION [GPIO 1, 2, 4]", fontsize=10, fontweight='bold', fontfamily='monospace', color='#0F172A')
    
    sensors = [
        {"pin": "GPIO 1 (ADC1_CH0)", "name": "Analog pH Probe Kit", "spec": "Range 0-3.3V | pH = -8.487V + 29.59\nTwo-Point Calib (pH 4.01 & 6.86)\nNoise: Median Filter & Outlier Cut"},
        {"pin": "GPIO 2 (ADC1_CH1)", "name": "Analog EC/TDS Probe", "spec": "AC Excitation (Ground Isolated)\nATC Normalized to 25°C\nEC25 = ECT / [1 + 0.0191(T - 25)]"},
        {"pin": "GPIO 4 (OneWire)", "name": "DS18B20 Temp Probe", "spec": "Digital Stainless Waterproof\n4.7kΩ Pull-up Resistor on Bus\nAccuracy ±0.5°C (-10°C to +85°C)"}
    ]
    
    for i, s in enumerate(sensors):
        x = 0.04 + i * 0.31
        y = 0.725
        w, h = 0.29, 0.13
        ax.add_patch(patches.Rectangle((x, y), w, h, fill=True, facecolor='#FFFFFF', edgecolor='#111111', linewidth=1.2))
        # Top banner for pin
        ax.add_patch(patches.Rectangle((x, y + h - 0.035), w, 0.035, fill=True, facecolor='#0F172A', edgecolor='#111111', linewidth=1.2))
        ax.text(x + 0.01, y + h - 0.024, s['pin'], color='#FFFFFF', fontsize=8, fontweight='bold', fontfamily='monospace')
        ax.text(x + 0.01, y + 0.065, s['name'], color='#0F172A', fontsize=9.5, fontweight='bold')
        ax.text(x + 0.01, y + 0.015, s['spec'], color='#334155', fontsize=7.2, fontfamily='monospace', linespacing=1.3)

    # ----------------------------------------------------
    # SECTION 2: 6-PHASE FLUIDIC SEQUENCE PIPELINE (MIDDLE)
    # ----------------------------------------------------
    ax.text(0.04, 0.69, "SECTION 2: 6-PHASE FLUIDIC AUTOMATION PIPELINE (SEQUENTIAL FSM)", fontsize=10, fontweight='bold', fontfamily='monospace', color='#0F172A')
    
    phases = [
        {"num": "Phase 1", "name": "Sampling", "time": "6s", "act": "Diaphragm 1 [GPIO 5]", "desc": "Pumps water from tank 23.3L to measurement cell V-102"},
        {"num": "Phase 2", "name": "Sensing", "time": "3s", "act": "Probes [GPIO 1, 2, 4]", "desc": "Settling delay; 15 ADC samples; computes median EC25 & pH"},
        {"num": "Phase 3", "name": "Recovery", "time": "7s", "act": "Diaphragm 2 [GPIO 6]", "desc": "Returns 100% test water back to culture tank (Zero Loss)"},
        {"num": "Phase 4", "name": "Dosing", "time": "5-10s", "act": "Peristaltic 1-3 [GPIO 9-11]", "desc": "Tier 1: Priming / Hard Lockout\nTier 2: Targeted N-P-K Pulses"},
        {"num": "Phase 5", "name": "Probe Wash", "time": "5s", "act": "Diaphragm 3 [GPIO 7]", "desc": "Flushes sensor probes with clean RO water from rinse tank"},
        {"num": "Phase 6", "name": "Waste Drain", "time": "6s", "act": "Solenoid 12V [GPIO 8]", "desc": "Opens gravity drain valve to purge rinse water to waste basin"}
    ]
    
    for i, p in enumerate(phases):
        row = i // 3
        col = i % 3
        x = 0.04 + col * 0.31
        y = 0.53 - row * 0.155
        w, h = 0.29, 0.135
        
        ax.add_patch(patches.Rectangle((x, y), w, h, fill=True, facecolor='#F8FAFC', edgecolor='#111111', linewidth=1.2))
        # Step header
        ax.add_patch(patches.Rectangle((x, y + h - 0.035), w, 0.035, fill=True, facecolor='#1E293B', edgecolor='#111111', linewidth=1.2))
        ax.text(x + 0.01, y + h - 0.024, f"{p['num']} : {p['name'].upper()} ({p['time']})", color='#FFFFFF', fontsize=8, fontweight='bold', fontfamily='monospace')
        
        ax.text(x + 0.01, y + 0.068, f"ACTUATOR: {p['act']}", color='#0F172A', fontsize=8, fontweight='bold', fontfamily='monospace')
        ax.text(x + 0.01, y + 0.015, p['desc'], color='#334155', fontsize=7.2, linespacing=1.3)
        
        # Connective arrows
        if i < 5 and col < 2:
            ax.annotate("", xy=(x + w + 0.018, y + h/2), xytext=(x + w + 0.002, y + h/2),
                        arrowprops=dict(arrowstyle="->", color="#111111", lw=1.5))
        elif i == 2:
            # Dropdown arrow from row 1 to row 2
            ax.annotate("", xy=(x + w/2, y - 0.022), xytext=(x + w/2, y - 0.005),
                        arrowprops=dict(arrowstyle="->", color="#111111", lw=1.5))

    # ----------------------------------------------------
    # SECTION 3: TWO-TIER DOSING & SAFETY SPECIFICATION (BOTTOM)
    # ----------------------------------------------------
    ax.text(0.04, 0.20, "SECTION 3: TWO-TIER CLOSED-LOOP DOSING ARCHITECTURE [GPIO 9, 10, 11]", fontsize=10, fontweight='bold', fontfamily='monospace', color='#0F172A')
    
    t_box_x, t_box_y, t_box_w, t_box_h = 0.04, 0.04, 0.56, 0.145
    ax.add_patch(patches.Rectangle((t_box_x, t_box_y), t_box_w, t_box_h, fill=True, facecolor='#FFFFFF', edgecolor='#111111', linewidth=1.4))
    
    ax.text(t_box_x + 0.015, t_box_y + 0.115, "• TIER 1 BASELINE PRIMING: EC < 0.8 mS/cm -> Staggered Pumps 1, 2, 3 (10s delay to prevent salt precipitation)", fontsize=7.5, fontweight='bold', color='#0F172A', fontfamily='monospace')
    ax.text(t_box_x + 0.015, t_box_y + 0.088, "• TIER 1 HARD SAFETY LOCKOUT: EC > 2.5 mS/cm OR pH < 4.0 -> Immediate 0s cutoff (Prevents Acid Shock pH 1.58)", fontsize=7.5, fontweight='bold', color='#DC2626', fontfamily='monospace')
    ax.text(t_box_x + 0.015, t_box_y + 0.061, "• TIER 2 PREDICTIVE AI: Pump 1 [GPIO 9, Stock A/N] | Pump 2 [GPIO 10, Stock B/P] | Pump 3 [GPIO 11, Stock C/K]", fontsize=7.5, color='#0F172A', fontfamily='monospace')
    ax.text(t_box_x + 0.015, t_box_y + 0.034, "• OPERATING LIMITS: Targeted pulse 5-10s | Max duration ≤ 25s | Cooldown period 6-12 hours | Sleep 4h", fontsize=7.5, color='#334155', fontfamily='monospace')
    ax.text(t_box_x + 0.015, t_box_y + 0.010, "• POWER ARCHITECTURE: 18V 30W Monocrystalline Solar + 12V 7.5Ah SLA + Buck Converter 5V 3A -> ESP32-S3", fontsize=7.2, color='#64748B', fontfamily='monospace')

    svg_out = OUTPUT_DIR / "blueprint_closed_loop_fsm.svg"
    png_out = OUTPUT_DIR / "blueprint_closed_loop_fsm.png"
    plt.savefig(svg_out, format='svg', bbox_inches='tight')
    plt.savefig(png_out, format='png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {svg_out} and {png_out}")

# ==============================================================================
# CARD 2: A.E.G.I.S. MULTIMODAL LATE-FUSION PIPELINE
# ==============================================================================
def generate_card_2():
    print("Generating Card 2: A.E.G.I.S. Multimodal Late-Fusion Pipeline...")
    fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    draw_title_block(ax, "AEGIS-DWG-002", "A.E.G.I.S. Multimodal Late-Fusion Prediction Pipeline")
    
    # ----------------------------------------------------
    # STREAM A: VISUAL FOLIAR STREAM (LEFT COLUMN)
    # ----------------------------------------------------
    sa_x, sa_y, sa_w, sa_h = 0.04, 0.40, 0.44, 0.485
    ax.add_patch(patches.Rectangle((sa_x, sa_y), sa_w, sa_h, fill=True, facecolor='#FFFFFF', edgecolor='#111111', linewidth=1.5))
    ax.add_patch(patches.Rectangle((sa_x, sa_y + sa_h - 0.04), sa_w, 0.04, fill=True, facecolor='#0F172A', edgecolor='#111111', linewidth=1.2))
    ax.text(sa_x + 0.015, sa_y + sa_h - 0.026, "STREAM A: VISUAL FOLIAR CNN (IMAGE MODEL) // 95.12%", color='#FFFFFF', fontsize=8.5, fontweight='bold', fontfamily='monospace')
    
    stream_a_steps = [
        ("1. ESP32-S3 CAM (OV5640)", "High-angle canopy images 224x224 RGB; Clock 160MHz + WIFI_PS_MIN_MODEM"),
        ("2. Preprocessing & Segmentation", "CLAHE light balance; ExG = 2G - R - B; Otsu Adaptive Thresholding"),
        ("3. Symptom-Gated Filtering (NOVEL)", "Filtered out 122 latent green images from 304 base images (Label Noise Cut)\nRetained 182 genuine symptom images -> Augmented to 786 training images"),
        ("4. MobileNetV2 + SE-Attention Block", "Depthwise Separable Conv + Channel Attention (Squeeze GAP, Excitation FC, Scale)"),
        ("5. Ensemble (A1 + A2 + A3)", "Vision A1 (85.37%) + SE-CNN A2 (90.24%) + Color A3 (87.80%) -> P_vision = 95.12%"),
        ("6. Explainable AI: Grad-CAM Saliency", "Heatmap localization verifies focus on chlorosis (-N), purple (-P), scorch (-K)")
    ]
    
    for i, (title, desc) in enumerate(stream_a_steps):
        sy = sa_y + sa_h - 0.09 - i * 0.068
        ax.text(sa_x + 0.015, sy + 0.018, title, fontsize=8, fontweight='bold', color='#0F172A', fontfamily='monospace')
        ax.text(sa_x + 0.015, sy - 0.012, desc, fontsize=6.8, color='#334155', linespacing=1.2)
        if i < len(stream_a_steps) - 1:
            ax.plot([sa_x + 0.015, sa_x + sa_w - 0.015], [sy - 0.025, sy - 0.025], color='#E2E8F0', linewidth=0.8)

    # ----------------------------------------------------
    # STREAM B: SOLUTION FEATURE STREAM (RIGHT COLUMN)
    # ----------------------------------------------------
    sb_x, sb_y, sb_w, sb_h = 0.52, 0.40, 0.44, 0.485
    ax.add_patch(patches.Rectangle((sb_x, sb_y), sb_w, sb_h, fill=True, facecolor='#FFFFFF', edgecolor='#111111', linewidth=1.5))
    ax.add_patch(patches.Rectangle((sb_x, sb_y + sb_h - 0.04), sb_w, 0.04, fill=True, facecolor='#0F172A', edgecolor='#111111', linewidth=1.2))
    ax.text(sb_x + 0.015, sb_y + sb_h - 0.026, "STREAM B: SOLUTION SENSOR ENSEMBLE // 97.56%", color='#FFFFFF', fontsize=8.5, fontweight='bold', fontfamily='monospace')
    
    stream_b_steps = [
        ("1. Physicochemical Feature Vector", "7 Dimensions: EC(t), pH(t), Temp(t), Delta_EC_base, Delta_EC_24h, Delta_pH_24h, Age"),
        ("2. Kohlrausch Ionic Law Compensation", "Detects total ionic conductivity Sigma = Sum(c_i * |z_i| * lambda_i) with auto 25°C ATC"),
        ("3. Tree-Based Gradient Ensembling", "Combines decision trees robust to non-linear chemical buffer dynamics"),
        ("4. Sensor B1: Gradient Boosting (GBDT)", "Accuracy: 100.00% | Precision: 100.00% | F1: 1.000 (Top Individual)"),
        ("5. Sensor B2: Random Forest (RF)", "Accuracy: 97.56% | Precision: 97.50% | F1: 0.9702 (100 Decision Trees)"),
        ("6. Stream B Soft-Voting Ensemble", "Soft-vote probability weighting (B1 + B2 + B3) -> P_sensor = 97.56%")
    ]
    
    for i, (title, desc) in enumerate(stream_b_steps):
        sy = sb_y + sb_h - 0.09 - i * 0.068
        ax.text(sb_x + 0.015, sy + 0.018, title, fontsize=8, fontweight='bold', color='#0F172A', fontfamily='monospace')
        ax.text(sb_x + 0.015, sy - 0.012, desc, fontsize=6.8, color='#334155', linespacing=1.2)
        if i < len(stream_b_steps) - 1:
            ax.plot([sb_x + 0.015, sb_x + sb_w - 0.015], [sy - 0.025, sy - 0.025], color='#E2E8F0', linewidth=0.8)

    # ----------------------------------------------------
    # LATE FUSION META-CLASSIFIER LAYER (BOTTOM)
    # ----------------------------------------------------
    mf_x, mf_y, mf_w, mf_h = 0.04, 0.12, 0.92, 0.25
    ax.add_patch(patches.Rectangle((mf_x, mf_y), mf_w, mf_h, fill=True, facecolor='#F8FAFC', edgecolor='#111111', linewidth=1.8))
    
    # Header bar
    ax.add_patch(patches.Rectangle((mf_x, mf_y + mf_h - 0.035), mf_w, 0.035, fill=True, facecolor='#0F172A', edgecolor='#111111', linewidth=1.2))
    ax.text(mf_x + 0.015, mf_y + mf_h - 0.024, "HIERARCHICAL MULTIMODAL LATE-FUSION STACKING META-CLASSIFIER // 100.00% ACCURACY", color='#FFFFFF', fontsize=9, fontweight='bold', fontfamily='monospace')
    
    # Formulas and details
    ax.text(mf_x + 0.02, mf_y + 0.155, "MATHEMATICAL FUSION FORMULA:", fontsize=8.5, fontweight='bold', fontfamily='monospace', color='#0F172A')
    ax.text(mf_x + 0.02, mf_y + 0.115, "P_fused = (0.35 * P_vision) + (0.65 * P_sensor)    [Learned Weights: w_img = 0.35, w_sen = 0.65 via Stacking Logistic Regression]",
            fontsize=8.5, fontweight='bold', fontfamily='monospace', color='#1D4ED8')
    
    col1_text = (
        "• ORTHOGONAL COMPLEMENTARITY:\n"
        "  - Early Stage (Day 1-4): Sensor detects ion uptake drop before leaf symptoms appear.\n"
        "  - Late Stage (Day 5-14): Foliar vision differentiates single-element deficiency (-N vs -P vs -K).\n"
        "• CASE STUDY - TANK P (DEFICIENT PHOSPHORUS):\n"
        "  - Vision alone: 43.23% confidence (subtle dark purplish leaf resembles normal canopy).\n"
        "  - Sensor alone: 97.01% confidence (detects anomalous EC & pH buffering curve).\n"
        "  - Fused A.E.G.I.S.: 80.49% confidence -> Correctly diagnosed without false alarm!"
    )
    ax.text(mf_x + 0.02, mf_y + 0.015, col1_text, fontsize=7.2, color='#334155', linespacing=1.2)
    
    col2_text = (
        "• HOLDOUT TEST ACCURACY: 100.00% (Macro F1 = 1.0000)\n"
        "• 95% CONFIDENCE INTERVAL: [100.0%, 100.0%]\n"
        "• REAL-WORLD VERIFICATION: 12 / 12 Units Correct (100%)\n"
        "  - 4 Primary Tanks (23.3L) + 8 Replicate Cups (750mL)\n"
        "  - Mean System Confidence: 83.96% ± 6.22% (SD)\n"
        "  - Published in alignment with Elsherbiny et al. (2022)"
    )
    ax.text(mf_x + 0.52, mf_y + 0.015, col2_text, fontsize=7.2, fontweight='bold', color='#0F172A', fontfamily='monospace', linespacing=1.2)

    svg_out = OUTPUT_DIR / "blueprint_multimodal_ai.svg"
    png_out = OUTPUT_DIR / "blueprint_multimodal_ai.png"
    plt.savefig(svg_out, format='svg', bbox_inches='tight')
    plt.savefig(png_out, format='png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {svg_out} and {png_out}")

# ==============================================================================
# CARD 3: EMPIRICAL VALIDATION & PLANT PHYSIOLOGY ABLATION CHARTS
# ==============================================================================
def generate_card_3():
    print("Generating Card 3: Empirical Validation & Biomass Charts...")
    fig, (ax_chart1, ax_chart2) = plt.subplots(1, 2, figsize=(12, 8), dpi=300)
    
    # Outer frame on figure
    fig.patch.set_facecolor('#FFFFFF')
    
    # ----------------------------------------------------
    # CHART 1: ABLATION STUDY COMPARISON (LEFT)
    # ----------------------------------------------------
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
    
    # Gated accuracies (or final accuracies)
    gated_acc = [100.00, 97.56, 95.12, 90.24, 87.80, 85.37, 82.93, 46.34]
    # Ungated accuracies for vision models
    ungated_acc = [None, None, 72.73, 50.00, 61.36, 65.91, None, None]
    
    y_pos = range(len(models))
    
    # Draw bars
    bars = ax_chart1.barh(y_pos, gated_acc, height=0.55, color='#0F172A', edgecolor='#111111', linewidth=1.2, label='Gated / Final Accuracy')
    
    # Draw ungated markers
    for i, un in enumerate(ungated_acc):
        if un is not None:
            ax_chart1.plot(un, i, marker='o', markersize=8, color='#FFFFFF', markeredgecolor='#DC2626', markeredgewidth=2.0)
            # Arrow connecting ungated to gated
            ax_chart1.annotate("", xy=(gated_acc[i] - 1.5, i), xytext=(un + 1.5, i),
                               arrowprops=dict(arrowstyle="->", color="#DC2626", lw=1.5))
    
    # Custom dummy plot for legend
    ax_chart1.plot([], [], marker='o', markersize=7, color='#FFFFFF', markeredgecolor='#DC2626', markeredgewidth=2.0, linestyle='none', label='Ungated (Before Filtering)')
    
    for i, v in enumerate(gated_acc):
        ax_chart1.text(v + 1.2, i, f"{v:.2f}%", va='center', fontsize=8, fontweight='bold', fontfamily='monospace', color='#0F172A')
    
    ax_chart1.set_yticks(y_pos)
    ax_chart1.set_yticklabels(models, fontsize=8, fontweight='bold', fontfamily='monospace')
    ax_chart1.set_xlim(0, 115)
    ax_chart1.invert_yaxis()
    ax_chart1.set_xlabel("Accuracy (%) // Holdout Test Set (N=41)", fontsize=8.5, fontweight='bold', fontfamily='monospace')
    ax_chart1.set_title("ABLATION STUDY: SYMPTOM-GATED EFFECT\n(Table 4.2 a, b // Up to +40.24% Accuracy Boost)", fontsize=10, fontweight='heavy', pad=12)
    ax_chart1.grid(axis='x', linestyle=':', color='#CBD5E1', alpha=0.7)
    ax_chart1.legend(loc='lower left', fontsize=7.5, framealpha=0.9, edgecolor='#111111')
    
    # ----------------------------------------------------
    # CHART 2: WATER SPINACH BIOMASS & GROWTH (RIGHT)
    # ----------------------------------------------------
    ax_chart2.set_facecolor('#FFFFFF')
    treatments = ["Control\n(Healthy)", "Tank -N\n(Nitrogen)", "Tank -P\n(Phosphorus)", "Tank -K\n(Potassium)"]
    biomass = [54.3, 19.8, 32.2, 37.9]
    errors = [4.2, 2.4, 3.0, 3.4]
    pct_control = [100.0, 36.5, 59.3, 69.8]
    heights = [39.6, 22.4, 28.3, 32.8]
    leaf_counts = [20.4, 10.5, 14.8, 16.5]
    
    x_pos = range(len(treatments))
    bars2 = ax_chart2.bar(x_pos, biomass, yerr=errors, capsize=5, width=0.55, color='#F8FAFC', edgecolor='#111111', linewidth=1.5)
    
    # Highlight Control bar
    bars2[0].set_facecolor('#0F172A')
    bars2[0].set_edgecolor('#111111')
    
    for i, b in enumerate(biomass):
        t_color = '#FFFFFF' if i == 0 else '#0F172A'
        ax_chart2.text(i, b / 2, f"{b:.1f}g\n({pct_control[i]:.1f}%)", ha='center', va='center', fontsize=8.5, fontweight='bold', fontfamily='monospace', color=t_color)
        ax_chart2.text(i, b + errors[i] + 2.5, f"H: {heights[i]}cm\nLeaves: {leaf_counts[i]}", ha='center', va='bottom', fontsize=7.2, fontfamily='monospace', color='#334155')

    ax_chart2.set_xticks(x_pos)
    ax_chart2.set_xticklabels(treatments, fontsize=8.5, fontweight='bold')
    ax_chart2.set_ylim(0, 75)
    ax_chart2.set_ylabel("Fresh Biomass per Plant (g) at Day 22 Harvest", fontsize=8.5, fontweight='bold', fontfamily='monospace')
    ax_chart2.set_title("WATER SPINACH BIOMASS AT DAY 22 HARVEST\n(Appendix A Table 3 // -63.5% Loss in -N Group)", fontsize=10, fontweight='heavy', pad=12)
    ax_chart2.grid(axis='y', linestyle=':', color='#CBD5E1', alpha=0.7)

    # Annotations on physiological causes
    notes_box = (
        "PHYSIOLOGICAL MECHANISMS IDENTIFIED:\n"
        "• -N (19.8g, -63.5%): RuBisCO breakdown & mobile N remobilization -> severe stunting & uniform leaf chlorosis\n"
        "• -P (32.2g, -40.7%): Sugar accumulation activates anthocyanin -> dark purplish green & restricted root energy\n"
        "• -K (37.9g, -30.2%): Osmotic stress & putrescine accumulation -> marginal necrosis & leaf scorch"
    )
    fig.text(0.5, 0.03, notes_box, ha='center', fontsize=7.5, fontfamily='monospace', color='#0F172A',
             bbox=dict(boxstyle="square,pad=0.6", facecolor='#F8FAFC', edgecolor='#111111', lw=1.2))

    plt.subplots_adjust(bottom=0.20, top=0.88, left=0.22, right=0.95, wspace=0.35)
    
    svg_out = OUTPUT_DIR / "blueprint_performance_charts.svg"
    png_out = OUTPUT_DIR / "blueprint_performance_charts.png"
    plt.savefig(svg_out, format='svg', bbox_inches='tight')
    plt.savefig(png_out, format='png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {svg_out} and {png_out}")

# ==============================================================================
# CARD 4: KEY METRICS SUMMARY & GITHUB REPO BLUEPRINT
# ==============================================================================
def generate_card_4():
    print("Generating Card 4: Key Metrics Summary & GitHub QR Code...")
    fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    draw_title_block(ax, "AEGIS-DWG-004", "A.E.G.I.S. System Telemetry, Specifications & Open Science Repo")
    
    # ----------------------------------------------------
    # SECTION 1: 4 GIANT ACHIEVEMENT BADGES (TOP)
    # ----------------------------------------------------
    ax.text(0.04, 0.865, "KEY RESEARCH HIGHLIGHTS & EMPIRICAL METRICS // N=143 READINGS", fontsize=10, fontweight='bold', fontfamily='monospace', color='#0F172A')
    
    badges = [
        {"num": "100.00%", "lbl": "MULTIMODAL ACCURACY", "sub": "Macro F1-Score = 1.000\nLate-Fusion Stacking"},
        {"num": "12 / 12", "lbl": "UNITS VERIFIED", "sub": "100% Real Hydroponic Units\nMean Conf 83.96% ± 6.22%"},
        {"num": "122", "lbl": "LATENT IMAGES CUT", "sub": "Symptom-Gated Filtering\n+40.24% SE-CNN Accuracy"},
        {"num": "0%", "lbl": "SALT PRECIPITATION", "sub": "Zero Nutrient Lockout\n10s Staggered Dosing Guard"}
    ]
    
    for i, b in enumerate(badges):
        x = 0.04 + i * 0.235
        y = 0.70
        w, h = 0.215, 0.155
        
        ax.add_patch(patches.Rectangle((x, y), w, h, fill=True, facecolor='#FFFFFF', edgecolor='#111111', linewidth=1.8))
        ax.add_patch(patches.Rectangle((x, y + h - 0.03), w, 0.03, fill=True, facecolor='#0F172A', edgecolor='#111111', linewidth=1.0))
        ax.text(x + w/2, y + h - 0.02, b['lbl'], ha='center', va='center', color='#FFFFFF', fontsize=7.5, fontweight='bold', fontfamily='monospace')
        
        ax.text(x + w/2, y + 0.068, b['num'], ha='center', va='center', color='#0A0A0A', fontsize=20, fontweight='heavy', fontfamily='monospace')
        ax.text(x + w/2, y + 0.022, b['sub'], ha='center', va='center', color='#334155', fontsize=6.8, fontfamily='monospace', linespacing=1.2)

    # ----------------------------------------------------
    # SECTION 2: SYSTEM SAFETY & OPERATIONAL GUARDRAILS (LEFT)
    # ----------------------------------------------------
    ax.text(0.04, 0.655, "SYSTEM SAFETY STANDARDS & MULTI-TIER GUARDRAILS", fontsize=9.5, fontweight='bold', fontfamily='monospace', color='#0F172A')
    
    gb_x, gb_y, gb_w, gb_h = 0.04, 0.12, 0.58, 0.515
    ax.add_patch(patches.Rectangle((gb_x, gb_y), gb_w, gb_h, fill=True, facecolor='#F8FAFC', edgecolor='#111111', linewidth=1.5))
    
    rules = [
        ("HARD SAFETY LOCKOUT (0s ABORT)", "Triggers when EC > 2.5 mS/cm OR pH < 4.0. Immediately cuts all peristaltic pumps to protect roots from osmotic shock & acid rhizotoxicity (Acid Shock pH 1.58 prevention)."),
        ("100% FLUIDIC SAMPLE RECOVERY", "Diaphragm Pump 2 runs for 7.0s to cycle 100% of tested nutrient solution back into the 23.3L cultivation tank. Prevents nutrient depletion during 4-hour automated test cycles."),
        ("AUTOMATIC PROBE INTEGRITY SYSTEM", "After sensing, Diaphragm Pump 3 flushes probes with RO water for 5.0s, followed by 6.0s Solenoid gravity drain. Eliminates sensor salt crusting and extends probe lifespan by >300%."),
        ("CALCIUM-PHOSPHATE SEPARATION", "Stock A (Ca[NO3]2 + Fe) separated from Stock B (H3PO4 + Mg) and Stock C (K2SO4). 10s inter-pump pulse spacing prevents insoluble Ca3(PO4)2 and CaSO4 precipitation in delivery lines."),
        ("PREDICTIVE DOSING COOLDOWN", "Targeted corrective pulse strictly restricted to 5-10s per cycle (maximum safety cutoff at 25,000ms), followed by mandatory 6-12 hour cooldown to allow biological plant absorption.")
    ]
    
    for i, (rtitle, rdesc) in enumerate(rules):
        ry = gb_y + gb_h - 0.05 - i * 0.098
        ax.text(gb_x + 0.015, ry + 0.018, f"[{i+1}] {rtitle}", fontsize=8, fontweight='bold', color='#0F172A', fontfamily='monospace')
        ax.text(gb_x + 0.015, ry - 0.024, rdesc, fontsize=6.8, color='#334155', linespacing=1.25)
        if i < len(rules) - 1:
            ax.plot([gb_x + 0.015, gb_x + gb_w - 0.015], [ry - 0.038, ry - 0.038], color='#CBD5E1', linewidth=0.8, linestyle='--')

    # ----------------------------------------------------
    # SECTION 3: REPOSITORY QR CODE & OPEN SCIENCE (RIGHT)
    # ----------------------------------------------------
    qr_box_x, qr_box_y, qr_box_w, qr_box_h = 0.65, 0.12, 0.31, 0.515
    ax.add_patch(patches.Rectangle((qr_box_x, qr_box_y), qr_box_w, qr_box_h, fill=True, facecolor='#FFFFFF', edgecolor='#111111', linewidth=1.5))
    ax.add_patch(patches.Rectangle((qr_box_x, qr_box_y + qr_box_h - 0.035), qr_box_w, 0.035, fill=True, facecolor='#0F172A', edgecolor='#111111', linewidth=1.0))
    ax.text(qr_box_x + qr_box_w/2, qr_box_y + qr_box_h - 0.024, "OPEN SCIENCE // GITHUB REPOSITORY", ha='center', va='center', color='#FFFFFF', fontsize=7.5, fontweight='bold', fontfamily='monospace')
    
    # Embed QR Code image
    if QR_PATH.exists():
        qr_img = Image.open(QR_PATH)
        # Bbox in data coordinates
        ax.imshow(qr_img, extent=[qr_box_x + 0.05, qr_box_x + qr_box_w - 0.05, qr_box_y + 0.16, qr_box_y + qr_box_h - 0.06], zorder=10)
    
    ax.text(qr_box_x + qr_box_w/2, qr_box_y + 0.115, "github.com/nottyzez/A.E.G.I.S-Ai", ha='center', fontsize=7.2, fontweight='bold', fontfamily='monospace', color='#1D4ED8')
    qr_sub = "SCAN FOR FULL TELEMETRY DATA\n• 143 Time-Series Telemetry Logs\n• IEEE-315 Schematics & P&ID 4K\n• Arduino C++ ESP32 Firmware\n• Pretrained Ensemble Keras Weights"
    ax.text(qr_box_x + qr_box_w/2, qr_box_y + 0.035, qr_sub, ha='center', fontsize=6.6, fontfamily='monospace', color='#475569', linespacing=1.2)

    svg_out = OUTPUT_DIR / "blueprint_key_metrics_summary.svg"
    png_out = OUTPUT_DIR / "blueprint_key_metrics_summary.png"
    plt.savefig(svg_out, format='svg', bbox_inches='tight')
    plt.savefig(png_out, format='png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {svg_out} and {png_out}")

def main():
    generate_card_1()
    generate_card_2()
    generate_card_3()
    generate_card_4()
    print("All 4 blueprints successfully generated!")

if __name__ == "__main__":
    main()
