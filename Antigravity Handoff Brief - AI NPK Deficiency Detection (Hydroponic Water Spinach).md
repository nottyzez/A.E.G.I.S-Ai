# Antigravity Handoff Brief: AI ตรวจจับและทำนายการขาดธาตุ N-P-K ของผักบุ้งไฮโดรโปนิกส์

**Owner:** Thai university student. **Report due:** 25 Oct 2026. **Presentation:** 9 Nov 2026. **Today:** 17 Oct 2026 (experiment Day 9, Day 1 = 9 Oct). **Language:** dashboard UI and figure labels in Thai; code, comments and README in English.

## 0. Working rules

- Read the whole brief first, then build in the priority order of Section 10.
- Never fabricate data, metrics or screenshots. If real data is missing, use clearly labelled synthetic data behind a `DEMO_MODE` flag and show a visible Demo badge in the UI.
- Ask the owner (Section 12) instead of guessing hardware or data facts.
- Reproducible: fixed seeds, pinned `requirements.txt`, one command per stage, versioned model artifacts with `metadata.json`.
- The 4 experiment tanks keep fixed recipes. No automation may touch them.

## 1. Concept (คอนเซปโครงงาน)

**ภาษาไทย:** ระบบ AI ตรวจจับและทำนายแนวโน้มการขาดธาตุอาหารหลัก (N, P, K) ของผักบุ้งในระบบไฮโดรโปนิกส์แบบน้ำนิ่งเติมอากาศ (DWC) โดยวิเคราะห์ภาพถ่ายมุมสูงจากกล้อง ESP32-CAM ร่วมกับค่า EC, pH และอุณหภูมิน้ำจากเซนเซอร์ ประมวลผลบนเซิร์ฟเวอร์ แล้วแสดงผลและแจ้งเตือนผ่านเว็บแดชบอร์ดที่พัฒนาเอง จุดเด่นคือ (1) การทดลองควบคุมสูตรธาตุอาหาร 4 ถัง (Control, ขาด N, ขาด P, ขาด K) เพื่อสร้างชุดข้อมูลที่มี label จากการออกแบบการทดลอง (2) โมเดลแบบ Late Fusion/Ensemble ระหว่างภาพกับเซนเซอร์ ฝึกด้วย Transfer Learning ร่วมกับข้อมูลภายนอกจากงานวิจัย (3) การเตือนล่วงหน้าจากแนวโน้มค่า EC และความมั่นใจของโมเดล (4) รอบทดสอบสนามแบบ blind test (5) ข้อเสนอแนะอนาคต: ระบบเติมปุ๋ยอัตโนมัติแบบวงปิด

**English summary:** Multimodal (image + EC/pH/temperature) classifier and early-warning system for N/P/K deficiency in hydroponic water spinach, with a self-built live dashboard. The main contribution is a reproducible controlled experiment with honest evaluation, not a production agronomy product.

## 2. Experiment design (labels come from the design)

- Crop: water spinach (ผักบุ้งจีน), aerated static DWC. 4 foam boxes (34 x 49 cm, 23.3 L each) with black liner, 8 plants per box. Day 1 = 9 Oct 2026 (transplanted after pre-germination in sponge).
- Nutrient: Green Plant AB (label: 5 cc/L each of A and B for ผักบุ้งจีน; the label gives no N-P-K analysis). Deficiency is made by diluting A or B, so it is **partial and not chemically pure** (A is believed to carry N, Ca, micros; B is believed to carry P, K, Mg; unverified).

| Tank | Class | Intended recipe per 23.3 L | Acid for pH-down |
| --- | --- | --- | --- |
| Control | `control` | A 117 cc + B 117 cc | nitric 6.8% |
| -N | `N` | A 29 cc + B 117 cc | phosphoric 85% only |
| -P | `P` | A 117 cc + B 29 cc + K2SO4 about 7-10 g | nitric only |
| -K | `K` | A 117 cc + B 29 cc + phosphoric about 1.5 ml | phosphoric or nitric |

- Target pH 5.5-6.5. Solution replaced every 5-7 days (`solution_round`).
- Measured about 08:00 and 17:00: EC, pH (before/after adjustment), water temperature, one top-down photo per box.
- Round 2 (planned 26 Oct - 8 Nov): separate box, trained system predicts blind, owner compares with ground truth.

## 3. Data status, schema and the key risk

Latest log (15 Oct, EC mS/cm; baseline in brackets): Control 2.744 (2.641), N 1.866 (2.572), P 2.496 (3.512), K 1.282 (2.196). Latest pH: Control 6.19, N 6.27, P 5.54, K 6.03.

**No visible deficiency symptoms as of 17 Oct (Day 9).** Image labels are therefore *tank-assigned*, not symptom-confirmed.

**Hypothesis H1 (untested):** nutrient pool is too generous for small seedlings (about 2.9 L per plant; 25% dose is still about 1.25 cc/L; EC stays 1.3-2.5 mS/cm), so deficiency is delayed. Planned test: at the next solution change set the deficient component to about 5% (-N: A about 6 cc; -P and -K: B about 6 cc), log it as `solution_round` 2 with the new recipe. Do not mix pre- and post-change images without the round flag. EC drops of 27-42% are partly dilution from top-ups after leaks, so EC alone is not proof of uptake.

**Source of truth:** `hydroponic_log.xlsx`, one sheet per tank (`Control`, `ขาด N`, `ขาด P`, `ขาด K`), header on row 6, data from row 7. Columns: date, time, EC (mS/cm), pH before, pH after, water temp (C), % EC change vs baseline (formula), image filename, notes, solution round. Baseline EC is in cell B4 of each sheet. **Blank means NOT MEASURED, never zero.**

Task: write `data/prepare_logs.py` to convert the workbook to a tidy CSV with columns `tank, ts, ec, ph_before, ph_after, temp, image, solution_round, notes, quality_flag` using NaN for blanks.

Images: whole-box top-down photos named `{Tank}_Day{NN}_{AM|PM}.jpg` in one folder per tank. Plant holes are at fixed positions, so crop per-hole patches from a config file `config/holes_{tank}.yaml`; build a small click-to-annotate tool to create it.

Known data-quality events (flag them, do not silently drop):

- Days 1-3: transplant shock; box liner leaked and solution was replaced; water level too low at one point.
- 11 Oct: Control pH jumped 5.67 to 8.09 in one day (cause unresolved).
- -P tank: phosphoric acid added by mistake once; baseline EC 3.512 is abnormal.
- Handheld pH pen faulty for a period; ESP32 pH module calibrated on 11 Oct.
- Missing readings (forgotten or not measured).

## 4. Hardware and firmware (context)

- Main controller ESP32-S3 N16R8; camera ESP32-S3 CAM N16R8 (OV5640) mounted top-down; relay modules 4ch x2 and 2ch x2; analog pH module; EC/TDS sensor x1; water temperature sensor x1; 12 V peristaltic pumps x3; 12 V solenoid valves x6; air pumps; 18 V 30 W solar panel, 30 A charge controller, 7.5 Ah battery; buck converter 12 V to 5 V.
- pH calibration (done): pH 4.00 = 3.015 V, pH 6.86 = 2.678 V on GPIO1 (12-bit ADC, 3.3 V reference). Formula: `pH = -8.487 * V + 29.59`. No temperature compensation yet; recalibrate every 1-2 weeks.
- Firmware tasks: median-filtered sampling; EC with temperature compensation; DS18B20 on OneWire; POST readings every 5 min; camera uploads a JPEG every 12 h or on demand. Relays for pumps and valves exist but dosing code must be **disabled by default**.
- Reading payload fields: `tank`, `ts` (ISO 8601), `ec_ms_cm`, `ph`, `temp_c`, `source` (`esp32` or `manual`), `fw_version`.

## 5. ML plan

### 5.1 Data preparation

- Crop per hole, resize to 224x224, MobileNetV2 preprocessing.
- **Split by tank and time, never by random image** (adjacent-day photos of the same plant are near duplicates and leak). Example: train Day 1-8, validation Day 9-10, test Day 11+; also report leave-one-day-out CV.
- Label strategy: (a) tank label for images after Day 3; (b) manual `symptom_severity` 0-3 by the owner via a simple labelling CSV/UI; (c) report results on the severity >= 1 subset separately and compare with (a).
- External data: search public NPK-deficiency leaf datasets (Kaggle, Mendeley, papers; prefer water spinach, kale, lettuce). Tag `source=external`, harmonise class names, record licence, measure domain shift, never put external images in validation or test sets.
- Augmentation: flip, small rotation, brightness/contrast, slight zoom. Keep hue changes minimal because colour is the signal.

### 5.2 Models

- **A. Image model:** MobileNetV2 (or EfficientNetB0) transfer learning, freeze base then optionally fine-tune last blocks, dropout, class weights, early stopping. 4 classes (control, N, P, K); also try a two-stage variant (healthy vs deficient, then N/P/K).
- **B. Sensor model:** features EC, pH, temperature, EC delta vs baseline, 24 h EC slope, 24 h pH slope, hours since solution change. Logistic regression and random forest or gradient boosting, evaluated with CV (small data).
- **C. Late-fusion ensemble:** `p = w_img * p_img + w_sens * p_sens`, weights tuned on validation (start 0.7 / 0.3); also a stacked logistic regression on the probabilities.
- **D. Optional early-fusion multimodal** (image branch + sensor MLP), for comparison only.
- **E. Early-warning risk score** per tank per day from EC slope (falling = depletion), trend of model confidence for a deficiency class, and pH drift; output risk 0-100 and suspected nutrient; threshold configurable. It is a trend layer on top of the ML models; validate it retrospectively on logged days.
- EC alone cannot identify which nutrient is lacking (it measures total ionic strength), so treat EC as a supporting feature.

### 5.3 Evaluation (save CSV and PNG, Thai axis labels optional)

Accuracy; per-class precision, recall, F1; macro and weighted averages; confusion matrix (counts and normalised); mean and SD across folds or days; ablation (image-only, sensor-only, ensemble, early-fusion); training curves; Grad-CAM examples; calibration (ECE). Round-2 blind-test accuracy is reported separately. Never present demo or sample-run numbers as real results.

### 5.4 Export

Keras SavedModel and TFLite for images, `joblib` for the sensor model, `models/<version>/metadata.json` containing data hash, date, metrics and class order.

## 6. Dashboard spec

- Backend FastAPI (or Flask) + SQLite (SQLAlchemy). Frontend: single-page HTML/JS with Chart.js, Thai UI, mobile-first, light and dark theme.
- Endpoints: `POST /api/sensor`, `POST /api/image` (multipart, runs inference, stores prediction), `GET /api/latest`, `GET /api/history?tank=&start_date=&end_date=`, `GET /api/predictions?tank=`, `GET /api/alerts`, `POST /api/alerts/{id}/resolve`, `GET /api/health`, `GET /api/export.csv`.
- Tables: `readings(tank, ts, ec, ph, temp, source)`, `images(tank, ts, path)`, `predictions(image_id, class_probs, model_version)`, `alerts(tank, ts, risk, suspected, status, message)`.
- Pages: (1) **Live:** 4 tank cards with EC, pH, temperature, last update, status colour, latest photo, predicted class and confidence; polling every 3-5 s (SSE or WebSocket optional). (2) **History:** date-range and tank filter, EC/pH/temperature charts, % EC change vs baseline, solution-change markers, photo timeline with predictions. (3) **Alerts:** risk trend per tank and a banner when risk exceeds the threshold. (4) **Model:** confusion matrix, metrics and ablation table read from `metadata.json`. (5) **Data entry:** manual reading form (handheld measurements) and Excel/CSV import.
- Shared-password or token header for POST endpoints. No actuator control from the dashboard in v1.

## 7. Suggested repo structure

```
project/
  config/            holes_*.yaml, thresholds.yaml
  data/              prepare_logs.py, crop_holes.py, split.py, label_tool/
  ml/                train_image.py, train_sensor.py, ensemble.py, risk_score.py, evaluate.py, gradcam.py
  models/            <version>/ (model files + metadata.json)
  server/            main.py, db.py, inference.py, static/ (dashboard)
  firmware/          esp32_main/, esp32_cam/ (stubs, dosing disabled)
  reports/           figures/, tables/
  README.md  requirements.txt  Makefile
```

## 8. Deliverables and acceptance criteria

1. Tidy CSV generated from the Excel log with quality flags, plus a data-quality report.
2. Cropped image dataset with a leak-free split and a documented label strategy.
3. Trained models A, B, C (D optional) with the Section 5.3 outputs reproducible by one command.
4. Dashboard running locally with `DEMO_MODE` and with real imported data; all endpoints in Section 6 working.
5. Risk score and alerts with a retrospective validation figure.
6. Report-ready figures and tables (Thai labels), architecture diagram, README for every stage.
7. Acceptance: no hard-coded metrics, seeds fixed, no external image in validation or test, every number in the report traceable to a saved file.

## 9. Future work (document only, do not build now)

Closed-loop dosing: plants start in plain water, base AB is dosed when EC is low, and single-salt top-ups (Ca nitrate for N, phosphoric acid for P, K2SO4 for K) are triggered by the model plus EC trend. Rules: never premix concentrated stocks (calcium precipitates with sulfate and phosphate); keep separate stock bottles and use valves to switch pump sources; add a daily dose cap, a 12 h cooldown, measure-after-dose feedback, hard EC and pH limits, and manual override. Use a separate round-2 box, never the 4 experiment tanks.

## 10. Priority and timeline

- **P0 (by 22 Oct):** data preparation scripts, tidy CSV, dashboard v1 (live and history from imported CSV), baseline image model.
- **P1 (by 25 Oct, report):** trained models and evaluation figures and tables, labelled with the data actually used even if small; architecture diagrams; README.
- **P2 (26 Oct - 8 Nov):** round-2 blind-test pipeline, risk score and alerts, dashboard polish, slide-ready assets.
- **P3:** future-work design only.

## 11. Guardrails

- Be explicit about small sample size, partial deficiency and label noise in every results table.
- Do not claim the system diagnoses nutrients from EC alone.
- Keep Thai wording natural for UI and figure captions; keep code identifiers in English.

## 12. Open questions for the owner

1. Were K2SO4 and MKP actually added to the -P and -K tanks, or is Section 2 only the intended recipe?
2. Is the 5% deficiency test (H1) going ahead, and on what date is the solution round 2 change?
3. Do you have an external dataset in mind, and what is the intended licence use?
4. Where will the server run (laptop, Raspberry Pi, cloud) and is the ESP32 on the same Wi-Fi?
5. Does the owner want the labelling tool to run on a phone browser?
