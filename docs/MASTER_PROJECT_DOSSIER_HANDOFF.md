# Master Project Dossier & Context Handoff for Gemini Argon
**Project Title:** ระบบควบคุมและวินิจฉัยการขาดธาตุอาหาร NPK อัตโนมัติในพืชไฮโดรโปนิกส์ด้วยปัญญาประดิษฐ์ A.E.G.I.S. (Autonomous Ensemble for Growth & Ion Sensing)
**Repository Base Path:** `d:\Code มหาปลัย`
**Last Updated:** 2026-10-24 07:45:00 (Experiment Day 16, Complete Day 1-14 Telemetry & ML Results)

---

## 1. ข้อมูลผู้จัดทำและพันธมิตร (Project Creators & AI Alliance)
* **ทีมนักวิจัย/ผู้พัฒนา (3 มนุษย์):**
  1. ชยพล (Chayapon) — ชื่อเล่น: น็อต (Nott)
  2. ปัญญพัฒน์ (Panyapath) — ชื่อเล่น: คิว (Kyu)
  3. กิติพล (Kitipon) — ชื่อเล่น: แสตมป์ (Stamp)
* **พันธมิตรปัญญาประดิษฐ์ (AI Alliance):** Claude, Gemini, GPT
* **ชื่อระบบปัญญาประดิษฐ์:** **A.E.G.I.S.** (*Autonomous Ensemble for Growth & Ion Sensing*)

---

## 2. โครงสร้างไฟล์เอกสารวิทยานิพนธ์ (Thesis Documentation Paths)
ไฟล์เนื้อหารายงานวิจัย 5 บทที่จัดทำเสร็จสมบูรณ์และจัดฟอร์แมตแบบคลีนสำหรับ Google Docs อยู่ในไดเรกทอรี `docs/`:

1. **บทที่ 1: บทนำและนิยามเชิงปฏิบัติการ**
   * **Path:** [`d:\Code มหาปลัย\docs\thesis_chapter1_operational_definitions.md`](file:///d:/Code%20มหาปลัย/docs/thesis_chapter1_operational_definitions.md)
   * **เนื้อหาสำคัญ:** นิยามเชิงปฏิบัติการ 8 ข้อ (DWC, NPK Deficiency, A.E.G.I.S. Multimodal Ensemble, Symptom-Gated Mechanism, Two-Tier Dosing Engine, Physicochemical Parameters, Metrics, Plant Growth) สไตล์กระชับ ชัดเจน
2. **บทที่ 2: วรรณกรรมและงานวิจัยที่เกี่ยวข้อง (Literature Review)**
   * **Path:** [`d:\Code มหาปลัย\docs\thesis_chapter2_literature_review.md`](file:///d:/Code%20มหาปลัย/docs/thesis_chapter2_literature_review.md)
   * **เนื้อหาสำคัญ:** สรีรวิทยาผักบุ้งจีน, กลไก Phloem Mobility N-P-K, ทฤษฎี Acid Shock (His193 Aquaporin Gating), สถาปัตยกรรม MobileNetV2 + SE-Attention, ดัชนี ExG, Grad-CAM, ตาราง State-of-the-Art Synthesis และบรรณานุกรม APA 7th Edition
3. **บทที่ 3: ระเบียบวิธีวิจัย — เครื่องมือและอุปกรณ์ (Section 3.1)**
   * **Path:** [`d:\Code มหาปลัย\docs\thesis_chapter3_materials_equipment.md`](file:///d:/Code%20มหาปลัย/docs/thesis_chapter3_materials_equipment.md)
   * **เนื้อหาสำคัญ:** เครื่องมือ 6 เสาหลัก (ฮาร์ดแวร์ ESP32-S3/OV5640, โมเดล A.E.G.I.S., ระบบน้ำ DWC 23.3L/750ml, คลาวด์เซิร์ฟเวอร์ DigitalOcean Droplet Ubuntu 22.04 LTS, สารเคมี A/B/กรด/บัฟเฟอร์, เมล็ดพันธุ์)
4. **บทที่ 3: ระเบียบวิธีวิจัย — ขั้นตอนการดำเนินงาน 4 ส่วน (Section 3.3)**
   * **Path:** [`d:\Code มหาปลัย\docs\thesis_chapter3_operational_procedures.md`](file:///d:/Code%20มหาปลัย/docs/thesis_chapter3_operational_procedures.md)
   * **เนื้อหาสำคัญ:** ขั้นตอน 4 ด้าน (ระบบปลูกพืช, สารละลายธาตุอาหาร 4 กลุ่ม, ไปป์ไลน์ปัญญาประดิษฐ์ A.E.G.I.S., วงจรอิเล็กทรอนิกส์และเฟิร์มแวร์)
5. **บทที่ 4: ผลการทดลองและวิเคราะห์ผล (Experimental Results)**
   * **Path:** [`d:\Code มหาปลัย\docs\thesis_chapter4_experimental_results.md`](file:///d:/Code%20มหาปลัย/docs/thesis_chapter4_experimental_results.md)
   * **เนื้อหาสำคัญ:** แบ่งตาม 3 วัตถุประสงค์ (4.1 ข้อมูลสารละลาย 143 รายการจาก 12 หน่วยทดลอง และตารางคัดแยกภาพ 304 ภาพ, 4.2 ตาราง Ablation Study 11 โมเดล และตารางทำนายรายหน่วย 12/12 หน่วย แม่นยำ 100%, 4.3 การแปลงคำสั่ง AI สู่ 7 รีเลย์ Two-Tier Dosing และการทดสอบระบบ 12 ข้อ)
6. **รายงานสังเคราะห์งานวิจัยเชิงลึก 4 เสาหลัก (Multi-Agent Research Dossiers)**
   * **Path:** [`d:\Code มหาปลัย\docs\multi_agent_research_dossiers.md`](file:///d:/Code%20มหาปลัย/docs/multi_agent_research_dossiers.md)

---

## 3. ข้อมูลโมเดลปัญญาประดิษฐ์และเมทริกซ์การทดลอง (ML Models & Metrics Paths)
ไฟล์ผลลัพธ์ของโมเดล A.E.G.I.S. ทั้งหมดถูกเซฟไว้ที่: `Ai มหาปลัย\model\output_ensemble\`

1. **Metadata & รายละเอียดการทำนายรายหน่วย (Source of Truth):**
   * **Path:** [`d:\Code มหาปลัย\Ai มหาปลัย\model\output_ensemble\metadata.json`](file:///d:/Code%20มหาปลัย/Ai%20มหาปลัย/model/output_ensemble/metadata.json)
   * **ข้อมูลสำคัญ:** ความเชื่อมั่นและผลการทำนายครบ 12 หน่วย (`Control`, `N`, `P`, `K`, `Cup1`–`Cup8`), ค่าน้ำหนัก Stacking (`w_img: 0.35, w_sen: 0.65`)
2. **ตาราง Ablation Study และเมทริกซ์เปรียบเทียบ:**
   * **Path (CSV):** [`d:\Code มหาปลัย\Ai มหาปลัย\model\output_ensemble\ensemble_ablation_metrics.csv`](file:///d:/Code%20มหาปลัย/Ai%20มหาปลัย/model/output_ensemble/ensemble_ablation_metrics.csv)
   * **Path (Markdown Summary):** [`d:\Code มหาปลัย\Ai มหาปลัย\model\output_ensemble\DATASET_SOURCES_SUMMARY.md`](file:///d:/Code%20มหาปลัย/Ai%20มหาปลัย/model/output_ensemble/DATASET_SOURCES_SUMMARY.md)
3. **ไฟล์โมเดลที่ผ่านการฝึกฝน (Model Weights & Artifacts):**
   * `member_a1_mobilenetv2.keras` (Vision CNN Backbone 1)
   * `member_a2_se_cnn.keras` (Vision CNN Backbone 2 with SE-Attention)
   * `vision_a3_foliar_expert.pkl` (44-D Color/Texture Expert)
   * `sensor_ensemble_models.pkl` (GBDT, Random Forest, Extra Trees, Logistic Regression)
   * `scalers_and_encoder.pkl` (Feature Scalers & Label Encoders)
4. **รูปภาพผลการทดลองความละเอียดสูง (300 DPI Figures):**
   * `fig1_dataset_sources_breakdown.png`: สัดส่วนชุดข้อมูล 5 แหล่งและภาพระยะแฝง
   * `fig2_confusion_matrices_ensemble.png`: Confusion Matrices ของ Vision, Sensor และ Fusion
   * `fig3_ablation_comparison.png`: กราฟแท่งเปรียบเทียบก่อนและหลังคัดกรอง Symptom-Gated
   * `fig4_sensor_feature_importance.png`: ลำดับความสำคัญของตัวแปรเซนเซอร์ (EC, pH, Delta)
   * `fig5_training_history_ensemble.png`: กราฟ Loss & Accuracy ของ MobileNetV2 และ SE-CNN
   * `fig6_foliar_saliency_and_predictions.png`: แผนที่ความร้อน Grad-CAM บนแผ่นใบจริง

---

## 4. ข้อมูลเซนเซอร์และฐานข้อมูลการทดลอง (Telemetry & Sensor Log Paths)
1. **ไฟล์บันทึกเซนเซอร์รวม 143 รายการ (JSON Telemetry):**
   * **Path:** [`d:\Code มหาปลัย\data\sensor_log.json`](file:///d:/Code%20มหาปลัย/data/sensor_log.json)
   * **ข้อมูลสำคัญ:** ค่าอ่าน EC, pH, Temp ทุกรอบเวลาตั้งแต่วันที่ 9–22 ต.ค. 2569 ของถังหลัก 4 ถัง และแก้ว `Cup1`–`Cup8` รวมถึงข้อมูลเหตุการณ์ Acid Shock (pH 1.58)
2. **ไฟล์บันทึกการทดลองต้นฉบับ (Excel Workbook):**
   * **Path:** `Ai มหาปลัย\dataset_real\hydroponic_log.xlsx`
3. **ไฟล์ส่งต่อแดชบอร์ด:**
   * **Path:** [`d:\Code มหาปลัย\server\static\data\sensor_data.js`](file:///d:/Code%20มหาปลัย/server/static/data/sensor_data.js)

---

## 5. ฮาร์ดแวร์ เฟิร์มแวร์ และระบบควบคุม (Firmware & Actuator Paths)
1. **เฟิร์มแวร์หลัก ESP32-S3 (Main Telemetry & 7-Relay Controller):**
   * **Path:** [`d:\Code มหาปลัย\firmware\esp32_main\esp32_main.ino`](file:///d:/Code%20มหาปลัย/firmware/esp32_main/esp32_main.ino)
   * **Configuration:** [`d:\Code มหาปลัย\firmware\esp32_main\config.h`](file:///d:/Code%20มหาปลัย/firmware/esp32_main/config.h) (นิยามพิน pH=GPIO1, EC=GPIO2, Temp=GPIO4, รีเลย์ปั๊ม 7 ตัว GPIO5–11, พารามิเตอร์ FSM และขีดจำกัดความปลอดภัย)
   * **ตัวกรองเซนเซอร์:** [`d:\Code มหาปลัย\firmware\esp32_main\sensor_filters.h`](file:///d:/Code%20มหาปลัย/firmware/esp32_main/sensor_filters.h) (Median Filter + Outlier Truncation)
2. **เฟิร์มแวร์กล้อง ESP32-S3 CAM (Canopy Vision Module):**
   * **Path:** [`d:\Code มหาปลัย\firmware\esp32_cam\esp32_cam.ino`](file:///d:/Code%20มหาปลัย/firmware/esp32_cam/esp32_cam.ino)
   * **Configuration:** [`d:\Code มหาปลัย\firmware\esp32_cam\config.h`](file:///d:/Code%20มหาปลัย/firmware/esp32_cam/config.h) (ลดคล็อกเป็น 160MHz, Modem Sleep, Poll `/api/cam_command`)
3. **ระบบตัดภาพอัตโนมัติ 3 ชั้น (3-Layer Auto-Cropper):**
   * **Path:** [`d:\Code มหาปลัย\ml\crop_plants.py`](file:///d:/Code%20มหาปลัย/ml/crop_plants.py) (CLAHE White Balance + ExG/HSV/LAB Halo + Convex Hull Padding)
4. **ชุดทดสอบระบบอัตโนมัติ (Automated System Test Suite):**
   * **Path:** [`d:\Code มหาปลัย\tests\test_demo_system.py`](file:///d:/Code%20มหาปลัย/tests/test_demo_system.py) (ทดสอบผ่านครบ 12/12 หัวข้อ คิดเป็น 100%)

---

## 6. เซิร์ฟเวอร์และแดชบอร์ด (Cloud Backend & Web Dashboard Paths)
1. **FastAPI Main Backend:**
   * **Path:** [`d:\Code มหาปลัย\main.py`](file:///d:/Code%20มหาปลัย/main.py) (รันบน DigitalOcean Cloud VPS: Ubuntu Linux 22.04 LTS, รองรับ `/api/sensor`, `/api/command`, `/api/cam_command`, `/predict`)
2. **หน้าเว็บแดชบอร์ดและการสั่งการ:**
   * แดชบอร์ดเรียลไทม์: [`server\static\dashboard_smooth.html`](file:///d:/Code%20มหาปลัย/server/static/dashboard_smooth.html)
   * แผงควบคุมการนำเสนอและสั่งกล้อง: [`server\static\presentation_controller.html`](file:///d:/Code%20มหาปลัย/server/static/presentation_controller.html)
   * ภาพถ่ายล่าสุดจากกล้อง: `server\static\latest_capture.jpg`
