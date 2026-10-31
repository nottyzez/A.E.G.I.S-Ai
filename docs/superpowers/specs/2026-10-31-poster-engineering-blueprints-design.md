# Technical Design Document: Minimal White Engineering Blueprint Suite for A.E.G.I.S. Research Poster

**Title:** Complete Modular Blueprint Suite (High-Resolution Vector Graphics & Academic Captions)  
**Target Medium:** Academic Research Poster (Canva / Adobe Illustrator / Print 300 DPI)  
**Style Direction:** Minimal White Engineering Blueprint (Pure white `#FFFFFF`, solid black technical strokes `#000000`, crisp ISO/IEEE engineering annotations)  
**Primary Source:** A.E.G.I.S. 55-page Official Project Thesis Report & Verified Telemetry Datasets  

---

## 1. Intent & Scientific Goals

The goal of this design suite is to translate the core breakthroughs of the 55-page A.E.G.I.S. research thesis into **four publication-ready, modular engineering blueprint graphics** and **academic copy-paste captions**. These assets allow the student researchers to place diagrams, workflows, and empirical charts seamlessly into their presentation poster.

### Visual & Technical Language:
- **Canvas / Background:** Pure clean white (`#FFFFFF`) with subtle engineering coordinate markings (`+`, fine border rules, technical title blocks).
- **Foreground / Lines:** Solid deep black (`#050505` to `#111111`) with calibrated stroke weights ($1.0\text{px}$ for minor guides, $1.5\text{px}$ for data flows, $2.0\text{px}$ for major outlines).
- **Typography:** Technical typography hierarchy (Header: Sans-serif bold, Body: Clean neutral Sans-serif, Data & Pins: Monospace).
- **Resolution:** SVG (infinite vector scalability) + PNG rendered at high-density ($2400 \times 1600\text{ px}$, 300 DPI print-ready).

---

## 2. Modular Asset Specifications

### Module 1: `blueprint_closed_loop_fsm.svg` / `.png`
**"Two-Tier Closed-Loop Fluidic FSM & Hardware Architecture"**
- **Purpose:** Illustrates Objective 3 and Chapter 3.3.1, Chapter 4.3.1, Appendix B, Appendix C.
- **Components:**
  1. **Sensors Subsystem:**
     - Analog pH Kit: `GPIO 1` (ADC1_CH0), $pH = -8.487V + 29.59$
     - Analog EC/TDS Probe: `GPIO 2` (ADC1_CH1), ATC normalized to 25°C ($EC_{25} = \frac{EC_T}{1 + 0.0191(T - 25)}$)
     - DS18B20 Temperature Probe: `GPIO 4` (OneWire bus, $4.7\text{ k}\Omega$ pull-up)
  2. **6-Phase Fluidic Sequence:**
     - `Phase 1 (Sampling)`: Diaphragm 1 (`GPIO 5`, $6\text{s}$) pulls sample from culture tank into chamber V-102.
     - `Phase 2 (Sensing)`: $3\text{s}$ settling time, 15 ADC samples, Moving Median Filter + Outlier Truncation.
     - `Phase 3 (Recovery)`: Diaphragm 2 (`GPIO 6`, $7\text{s}$) returns 100% of water back to the culture tank.
     - `Phase 4 (Two-Tier Dosing Decision)`:
       - *Tier 1 Baseline Priming*: When $EC < 0.8\text{ mS/cm}$, stagger Pumps 1, 2, 3 with $10\text{s}$ intervals.
       - *Tier 1 Hard Safety Lockout*: If $EC > 2.5\text{ mS/cm}$ or $pH < 4.0$, immediate cutoff ($0\text{s}$).
       - *Tier 2 Predictive AI Modulation*: Target pulse ($5-10\text{s}$, max $25\text{s}$, cooldown $6-12\text{h}$) for Pump 1 (High-N, `GPIO 9`), Pump 2 (High-P, `GPIO 10`), or Pump 3 (High-K, `GPIO 11`).
     - `Phase 5 (Probe Wash)`: Diaphragm 3 (`GPIO 7`, $5\text{s}$) sprays clean RO water over probes.
     - `Phase 6 (Waste Drain)`: Solenoid Valve (`GPIO 8`, $6\text{s}$) drains rinse water to waste bucket.
     - `Standby`: 4-Hour scheduled sleep cycle.
  3. **Power Subsystem:** 18V 30W Monocrystalline Solar Panel $\rightarrow$ 30A PWM Charger $\rightarrow$ 12V 7.5Ah SLA Battery $\rightarrow$ Buck Converter 5V 3A to ESP32-S3.

---

### Module 2: `blueprint_multimodal_ai.svg` / `.png`
**"A.E.G.I.S. Multimodal Late-Fusion AI Pipeline"**
- **Purpose:** Illustrates Objective 2 and Chapter 2.4-2.7, Chapter 3.3.4, Chapter 4.2.
- **Components:**
  1. **Stream A (Visual Foliar Stream):**
     - Input: High-angle canopy image ($224 \times 224 \times 3$) captured by ESP32-S3 CAM (OV5640).
     - Image Preprocessing: CLAHE light balancing + Excess Green Index ($ExG = 2G - R - B$) + Otsu Adaptive Thresholding.
     - **Symptom-Gated Filtering (Crucial Breakthrough):** 304 base images $\rightarrow$ 122 pre-symptomatic (latent green) images filtered out $\rightarrow$ 182 genuine symptom images retained $\rightarrow$ Augmented to 786 images.
     - Deep Learning: MobileNetV2 with Squeeze-and-Excitation (SE-Attention Block: Squeeze GAP, Excitation FC layers, Scale Feature Map).
     - Models: Vision A1 (MobileNetV2: 85.37%), Vision A2 (SE-CNN: 90.24%), Vision A3 (Color-Texture Expert: 87.80%) $\rightarrow$ Stream A Ensemble: **95.12%**.
     - XAI: Grad-CAM Saliency Localization proving physiological focus on chlorosis, necrosis, and leaf margins.
  2. **Stream B (Solution Feature Stream):**
     - Input: 7-Dimensional physicochemical feature vector ($EC_t, pH_t, Temp_t, \Delta EC_{\text{baseline}}, \Delta EC_{24h}, \Delta pH_{24h}, \text{Age}$).
     - Models: Gradient Boosting (GBDT: 100%), Random Forest (97.56%), Extra Trees (92.68%) $\rightarrow$ Stream B Soft-Vote Ensemble: **97.56%**.
  3. **Meta-Classifier & Late Fusion:**
     - Stacking Logistic Regression with learned weights: $w_{\text{img}} = 0.35, w_{\text{sen}} = 0.65$.
     - Fusion formula: $P_{\text{fused}} = 0.35 \cdot P_{\text{vision}} + 0.65 \cdot P_{\text{sensor}}$.
     - Result: **100.00% Diagnosis Accuracy** ($F_1 = 1.000$, 95% CI: $[100.0\%, 100.0\%]$).

---

### Module 3: `blueprint_performance_charts.svg` / `.png`
**"Empirical Validation & Plant Physiology Ablation Charts"**
- **Purpose:** Illustrates Chapter 4.1, 4.2.1, and Appendix A Table 3 (Day 22 Harvest).
- **Components:**
  1. **Chart 1: Ablation Study — Model Accuracy Before vs. After Symptom-Gating:**
     - Vision A1 (MobileNetV2): $65.91\% \rightarrow 85.37\%$ ($+19.46\%$)
     - Vision A2 (Multi-Scale SE-CNN): $50.00\% \rightarrow 90.24\%$ ($+40.24\%$)
     - Vision A3 (Foliar 44-D Color): $61.36\% \rightarrow 87.80\%$ ($+26.44\%$)
     - Stream A (Vision Ensemble): $72.73\% \rightarrow 95.12\%$ ($+22.39\%$)
     - Stream B (Sensor Ensemble): $97.56\%$
     - A.E.G.I.S. (Multimodal Late-Fusion): **$100.00\%$**
  2. **Chart 2: Fresh Biomass & Plant Growth at Day 22 (Water Spinach):**
     - Control (Healthy): $54.3\text{ g}$ ($100.0\%$, Height $39.6\text{ cm}$, $20.4$ leaves)
     - Deficient Nitrogen (-N): $19.8\text{ g}$ ($36.5\%$, $-63.5\%$ drop; chlorosis due to RuBisCO breakdown)
     - Deficient Phosphorus (-P): $32.2\text{ g}$ ($59.3\%$, $-40.7\%$ drop; stunted, purplish dark green)
     - Deficient Potassium (-K): $37.9\text{ g}$ ($69.8\%$, $-30.2\%$ drop; marginal leaf necrosis)

---

### Module 4: `blueprint_key_metrics_summary.svg` / `.png`
**"Key Achievement Metrics, Safety Specs & Open Science Repository"**
- **Purpose:** Provides a concise data badge card with scannable QR Code and safety lockout thresholds.
- **Components:**
  1. **Big Number Badges:**
     - `100.00%` — Multimodal Overall Diagnosis Accuracy ($F_1 = 1.000$)
     - `12 / 12` — Real-world Hydroponic Units Correctly Classified (100%)
     - `122 Images` — Latent Pre-symptomatic Leaves Filtered (Eliminated Label Noise)
     - `0% Precipitation` — $10\text{s}$ Staggered Dosing prevents Calcium Phosphate lockout
  2. **Safety Thresholds:**
     - $EC > 2.5\text{ mS/cm}$ or $pH < 4.0 \rightarrow$ Immediate Hard Lockout ($0\text{s}$)
     - Cooldown period: $6 - 12\text{ hours}$ between targeted nutrient pulses
     - Fluidic return: $100\%$ test sample cycled back to main tank ($7\text{s}$)
  3. **High-Resolution QR Code:**
     - Direct link to `https://github.com/nottyzez/A.E.G.I.S-Ai` (Open Science, IEEE-315 blueprints, C++ firmware).

---

## 3. Academic Captions & Companion Guide

Accompanying the 4 graphics, a dedicated markdown/Word-ready text file (`docs/poster_content_companion.md`) will provide:
1. Ready-to-paste Thai titles, subtitles, and explanatory paragraphs for each card.
2. Short bullet points tailored for poster readability (large font friendly, concise scientific phrasing).
3. Exact figure references mapping to the 55-page thesis (e.g. ตารางที่ 4.1, 4.2 ก-ข, ตารางที่ 4.4, ภาคผนวก ก-ค).

---

## 4. Verification & Generation Plan

1. **Generation Script (`scripts/generate_poster_blueprints.py`):**
   - Use Python with `matplotlib`, `cairosvg` or pure SVG vector generators to produce pixel-perfect, scalable SVGs and render $2400 \times 1600\text{ px}$ 300 DPI PNGs.
   - Embed real QR Code into Module 4.
2. **Automated Verification (`tests/test_poster_blueprints.py`):**
   - Verify all 4 SVG files exist and are valid XML.
   - Verify all 4 PNG files exist and are $> 100\text{ KB}$ with $2400 \times 1600$ resolution.
   - Verify exact matching of all critical metrics ($100.00\%$, $12/12$, $122$ images, $54.3\text{ g}$, $19.8\text{ g}$, GPIO 1-11).
