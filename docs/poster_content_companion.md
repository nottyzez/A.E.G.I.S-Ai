# คู่มือข้อความและแคปชันวิชาการสำหรับโปสเตอร์งานวิจัย A.E.G.I.S.
## (A.E.G.I.S. Poster Content & Academic Companion Guide)

**โรงเรียน:** โรงเรียนสุวรรณภูมิพิทยไพศาล สพม.ร้อยเอ็ด  
**โครงงาน:** ระบบดูแลพืชแบบไฮโดรโปนิกส์โดยการทำนายปัจจัยในการเจริญเติบโตจากปัญญาประดิษฐ์  
**คณะผู้จัดทำ:** นายกิติภณ แถลงการณ์, นายชยพล นามจันทร์, นายปัญญพัฒน์ วิชาพล  
**ครูที่ปรึกษา:** นางสาวอศัลยา ดวงระหว้า  
**รูปแบบดีไซน์:** พิมพ์เขียววิศวกรรมมินิมอลขาว-ดำ (Monochrome Technical Drafting Blueprint)

---

# 🎯 หมวดที่ 0: ข้อความสั้นกระชับพิเศษ (Ultra-Short) สำหรับโปสเตอร์ Canva (แก้ปัญหาตัวหนังสือเล็ก 100%)
*(ข้อความถูกตัดคำฟุ่มเฟือยออกทั้งหมด ให้เหลือเฉพาะคีย์เวิร์ดวิชาการและตัวเลขเชิงประจักษ์ 2–3 บรรทัดต่อกล่อง เพื่อให้คุณสามารถ**ขยายขนาดตัวอักษรใน Canva ขึ้นเป็น 20–24 pt** ได้ทันที อ่านชัดเจนจากระยะ 1.5–2 เมตรโดยไม่ล้นกรอบ)*

---

### 🟩 กล่องที่ 1: "บทคัดย่อ" (Abstract) — กล่องแนวนอนเต็มความกว้างด้านบน
```text
• วัตถุประสงค์ & IoT: พัฒนาระบบ DWC ด้วย ESP32-S3 ตรวจวัด EC, pH, Temp (143 ข้อมูล) และกล้องถ่ายภาพพุ่มใบ (304 ภาพ)
• ปัญญาประดิษฐ์ A.E.G.I.S.: โมเดล Multimodal Late-Fusion ผสานกลไกคัดกรองภาพแฝง 122 ภาพ จำแนกการขาด N-P-K แม่นยำ 100.00% (ตรวจแปลงจริงถูก 12/12 ชุด)
• การควบคุมวงปิด Two-Tier: สั่งปั๊มไดอะแฟรมและปั๊มรีดสายปรับสมดุลปุ๋ยอัตโนมัติ ไร้เกลือตกตะกอน และตัดระบบทันทีใน 0s เมื่อวิกฤต

คำสำคัญ: ไฮโดรโปนิกส์, การขาดธาตุอาหาร NPK, ปัญญาประดิษฐ์ผสานข้อมูล, การควบคุมแบบวงปิด, IoT
```

---

### 🟩 กล่องที่ 2: "ที่มาและความสำคัญ" (Background) — กล่องบนซ้าย
```text
• ปัญหาเดิม: ไฮโดรโปนิกส์ทั่วไปวัดได้เพียงค่ารวม EC/pH แต่ไม่สามารถระบุเจาะจงได้ว่า "พืชกำลังขาดธาตุอาหารตัวใด" (N, P หรือ K)
• นวัตกรรม A.E.G.I.S.: ผสานภาพถ่ายพุ่มใบกับข้อมูลเซนเซอร์ วินิจฉัยแม่นยำและสั่งจ่ายปุ๋ยชดเชยเฉพาะสูตรแบบอัตโนมัติ
```

---

### 🟩 กล่องที่ 3: "วัตถุประสงค์" (Objectives) — กล่องกลางซ้าย
```text
1. เพื่อพัฒนาระบบดูแลพืชไฮโดรโปนิกส์และจัดเก็บข้อมูลโทรมาตร IoT สำหรับผักบุ้งจีน
2. เพื่อพัฒนาโมเดลปัญญาประดิษฐ์ A.E.G.I.S. ในการจำแนกการขาดธาตุอาหาร N, P, K
3. เพื่อทดสอบการควบคุมการจ่ายสารละลายแบบวงปิด (Two-Tier Closed-Loop) ร่วมกับ AI
```

---

### 🟩 กล่องที่ 4: "ตัวแปรที่ศึกษา" (Variables) — กล่องบนขวา
```text
• ตัวแปรต้น: สูตรสารละลายธาตุอาหาร 4 กลุ่ม (Control สมบูรณ์, ขาด N, ขาด P, ขาด K)
• ตัวแปรตาม: การเติบโตทางสรีรวิทยา และความแม่นยำในการวินิจฉัยของโมเดล AI (100.00%)
• ตัวแปรควบคุม: ผักบุ้งจีน (Ipomoea aquatica), ระบบ DWC เติมออกซิเจน, สภาพแวดล้อมเดียวกัน
```

---

### 🟩 กล่องที่ 5: "การดำเนินงาน" (Methodology) — กล่องขวาล่าง
```text
1. แปลงทดลอง: ปลูกผักบุ้งจีนระบบ DWC 4 กลุ่ม (4 ถังหลัก 23.3L + 8 แก้วทดลองซ้ำ)
2. จัดเก็บข้อมูล: บันทึกข้อมูลสารละลาย 143 รายการ (EC, pH, Temp) และภาพมุมกะ 304 ภาพ
3. พัฒนา AI: เทรนโมเดล 2 สาย พร้อมกลไก Symptom-Gating ขจัดภาพระยะแฝง 122 ภาพ
4. วงจรของไหล: ควบคุมผ่าน ESP32-S3 สั่งปั๊ม 6 ตัว และวาล์วเดรน 6 ขั้นตอน (GPIO 1–11)
```

---

### 🟩 กล่องที่ 6: "สรุปและอภิปรายผล" (Results & Discussion) — กล่องซ้ายล่าง
```text
• วินิจฉัยแม่นยำ 100.00%: Late-Fusion (ภาพ 95.12% + เซนเซอร์ 97.56%) แม่นยำ 100.00% (ตรวจแปลงจริงถูก 12/12 ชุด)
• ชีวมวลสด Day 22: Control (54.3g) > ขาด K (37.9g) > ขาด P (32.2g) > ขาด N (19.8g, -63.5% จากการสลาย RuBisCO)
• การจ่ายปุ๋ยวงปิด Two-Tier: ปรับสมดุล NPK สำเร็จ เว้นปั๊ม 10s ไร้เกลือตกตะกอน และ Hard Lockout ตัดใน 0s ปลอดภัย 100%
```

---

### 🟩 กล่องที่ 7: "ข้อเสนอแนะ" (Recommendations) — กล่องเต็มความกว้างด้านล่างสุด
```text
1. สารละลายและการบำรุงรักษา: ควรผสมแม่ปุ๋ยด้วยน้ำ RO และตรวจสอบน้ำล้างหัวโพรบสม่ำเสมอเพื่อยืดอายุการใช้งาน
2. การต่อยอดสายพันธุ์: ควรขยายฐานข้อมูลและการทดลองโมเดล A.E.G.I.S. สู่พืชเศรษฐกิจชนิดอื่น เช่น ผักสลัด
3. การพัฒนาในอนาคต: พัฒนาโมเดลให้แยกโรคพืชออกจากอาการขาดธาตุ และติดตั้ง Ion-Selective Electrode (ISE) เจาะจงไอออน
```

---

# 🖼️ การจัดวางภาพพิมพ์เขียววิศวกรรมลงในโปสเตอร์ (Blueprint Placement Guide)

คุณสามารถเลือกจัดวางได้ 2 รูปแบบตามความสะดวกใน Canva:

### 🌟 รูปแบบที่ 1 (แนะนำมากที่สุดสำหรับประกวด Symposium 2026: จับคู่ 2 ภาพพิมพ์เขียวระดับมาสเตอร์)
- **กล่องขวากลาง (ใต้ตัวแปร / ส่วนขั้นตอนระบบ):** ใส่ภาพ [`blueprint_ai_esp32_flowchart.png`](../assets/blueprints/blueprint_ai_esp32_flowchart.png) **(ภาพใหม่ 6660x3360 px)**  
  *(แสดงผังโฟลว์ชาร์ตการทำงานแบบครบวงจร: ESP32-S3 อ่านเซนเซอร์และสูบน้ำ ➔ ส่ง Telemetry สู่ AI ➔ ตัดสินใจความปลอดภัย Two-Tier ➔ สั่งการปั๊มรีดสาย N-P-K และปั๊มล้างหัววัด RO วนกลับสู่ถัง DWC)*
- **กล่องซ้ายล่าง (ใต้สรุปผล / ส่วนผลการทดลอง):** ใส่ภาพ [`blueprint_unified_results_metrics.png`](../assets/blueprints/blueprint_unified_results_metrics.png) **(ภาพคอมโบใหม่ 6297x3360 px)**  
  *(ด้านซ้ายเป็นกราฟแท่งชีวมวลสด Day 22 ผักบุ้งจีน + แผนภูมิความแม่นยำ AI Ablation Study และด้านขวาเป็นการ์ด 4 ตัวเลขเด่น 100%, กฎความปลอดภัย และ QR Code สแกนดู GitHub ตัวหนังสือใหญ่ ชัดเจน อ่านง่าย ไม่รก)*

### 🌟 รูปแบบที่ 2 (แบบแยกชิ้นส่วนตามเดิม):
- **กล่องขวากลาง:** ใส่ [`blueprint_closed_loop_fsm.png`](../assets/blueprints/blueprint_closed_loop_fsm.png) (วงจรของไหล 6 ขั้นตอน)
- **กล่องซ้ายล่าง:** ใส่ [`blueprint_performance_charts.png`](../assets/blueprints/blueprint_performance_charts.png) (กราฟแท่งชีวมวล + Ablation Study)
- **แถบยาวล่างสุด:** ใส่ [`blueprint_key_metrics_summary.png`](../assets/blueprints/blueprint_key_metrics_summary.png) (4 ตัวเลขเด่น + QR Code)

---

## สารบัญภาพพิมพ์เขียววิศวกรรม (Engineering Blueprint Files - 300 DPI)

| ลำดับ | ชื่อไฟล์เวกเตอร์ (SVG) | ชื่อไฟล์ความละเอียดสูง (PNG 300 DPI) | ขนาดพิกเซล | คำอธิบายเนื้อหา |
| :---: | :--- | :--- | :---: | :--- |
| **Card 1** | [`blueprint_closed_loop_fsm.svg`](../assets/blueprints/blueprint_closed_loop_fsm.svg) | [`blueprint_closed_loop_fsm.png`](../assets/blueprints/blueprint_closed_loop_fsm.png) | 3315 × 2208 px | ผังวงจรของไหล 6 ขั้นตอน, ขา GPIO 1–11 และการควบคุม Two-Tier Dosing |
| **Card 2** | [`blueprint_multimodal_ai.svg`](../assets/blueprints/blueprint_multimodal_ai.svg) | [`blueprint_multimodal_ai.png`](../assets/blueprints/blueprint_multimodal_ai.png) | 3315 × 2208 px | ผังปัญญาประดิษฐ์สองสาย A.E.G.I.S. Late-Fusion, Symptom-Gating และ Grad-CAM |
| **Card 3** | [`blueprint_performance_charts.svg`](../assets/blueprints/blueprint_performance_charts.svg) | [`blueprint_performance_charts.png`](../assets/blueprints/blueprint_performance_charts.png) | 3379 × 2566 px | แผนภูมิ Ablation Study (+40.24%) และกราฟแท่งชีวมวลสด Day 22 ผักบุ้งจีน |
| **Card 4** | [`blueprint_key_metrics_summary.svg`](../assets/blueprints/blueprint_key_metrics_summary.svg) | [`blueprint_key_metrics_summary.png`](../assets/blueprints/blueprint_key_metrics_summary.png) | 3315 × 2208 px | การ์ด 4 ตัวเลขผลลัพธ์เด่น (100%), เกณฑ์ความปลอดภัย และ GitHub QR Code |
| **Card 5 (COMBO)** | [`blueprint_unified_results_metrics.svg`](../assets/blueprints/blueprint_unified_results_metrics.svg) | [`blueprint_unified_results_metrics.png`](../assets/blueprints/blueprint_unified_results_metrics.png) | **6855 × 3660 px** | **ภาพคอมโบแนวนอนกว้าง: กราฟชีวมวลสด + แผนภูมิ AI + 4 ตัวเลขเด่น 100% + QR Code (ตัวหนังสือใหญ่)** |
| **Card 6 (FLOWCHART)** | [`blueprint_ai_esp32_flowchart.svg`](../assets/blueprints/blueprint_ai_esp32_flowchart.svg) | [`blueprint_ai_esp32_flowchart.png`](../assets/blueprints/blueprint_ai_esp32_flowchart.png) | **6660 × 3510 px** | **โฟลว์ชาร์ตมาสเตอร์แนวนอน: การทำงาน AI ร่วมกับ ESP32 สั่งการปั๊มแบบครบวงจร 4 Stage** |
| **Card 7 (METHODOLOGY)** | [`blueprint_methodology_flowchart_compact.svg`](../assets/blueprints/blueprint_methodology_flowchart_compact.svg) | [`blueprint_methodology_flowchart_compact.png`](../assets/blueprints/blueprint_methodology_flowchart_compact.png) | **3660 × 4260 px** | **🌟 ผังขั้นตอนการดำเนินงานแนวตั้ง (4:3) สำหรับวางในกล่อง "การดำเนินงาน" ใน Canva ตัวหนังสือยักษ์ สรุป 4 บล็อกชัดเจน** |
| **Card 8 (RESULTS)** | [`blueprint_results_biomass_compact.svg`](../assets/blueprints/blueprint_results_biomass_compact.svg) | [`blueprint_results_biomass_compact.png`](../assets/blueprints/blueprint_results_biomass_compact.png) | **3660 × 4260 px** | **🌟 กราฟสรุปผลแนวตั้ง (4:3) สำหรับวางในกล่อง "สรุปและอภิปรายผล" ใน Canva: การ์ดยืนยัน AI 100% + กราฟแท่งชีวมวล Day 22 ตัวหนังสือยักษ์** |
| **Card 9 (AI FLOWCHART)** | [`blueprint_ai_workflow_flowchart.svg`](../assets/blueprints/blueprint_ai_workflow_flowchart.svg) | [`blueprint_ai_workflow_flowchart.png`](../assets/blueprints/blueprint_ai_workflow_flowchart.png) | **3660 × 4260 px** | **🌟 ผังการทำงานของ AI 4 ขั้นตอน (แนวตั้ง 4:3): รับข้อมูล ➔ AI คู่ขนาน ➔ Late-Fusion 100% ➔ สั่งปั๊ม NPK ตัวหนังสือยักษ์ สั้นกระชับที่สุด** |
| **Card 10 (3D MORPHOLOGY)** | [`blueprint_growth_morphology_3d.svg`](../assets/blueprints/blueprint_growth_morphology_3d.svg) | [`blueprint_growth_morphology_3d.png`](../assets/blueprints/blueprint_growth_morphology_3d.png) | **3660 × 4260 px** | **🌟 กราฟแท่งจัดกลุ่ม 3 มิติ (ความสูง + จำนวนใบ + น้ำหนักสด) เปรียบเทียบ 4 ถังการทดลอง ณ วันเก็บเกี่ยว (ภาคผนวก ก)** |
| **Card 11 (EVALUATION TABLE)** | [`blueprint_ai_evaluation_table.svg`](../assets/blueprints/blueprint_ai_evaluation_table.svg) | [`blueprint_ai_evaluation_table.png`](../assets/blueprints/blueprint_ai_evaluation_table.png) | **4260 × 3360 px** | **🌟 ตารางสรุปผลการประเมินและวินิจฉัยโมเดล AI (A.E.G.I.S.) พร้อม 3 การ์ดยักษ์ 100%, 12/12 ถัง, ความเชื่อมั่น 83.96% (เซนเซอร์ 90.78% / ภาพ 72.60%)** |

---

## คำแนะนำขนาดตัวอักษรใน Canva สำหรับโปสเตอร์ Power Ten 2026
- **หัวข้อหลักประจำกล่อง (Box Title เช่น บทคัดย่อ, ที่มา, วัตถุประสงค์...):** ขนาด **24–28 pt** (ตัวหนา / Bold)
- **เนื้อหาในแต่ละกล่อง (Body Text):** ปรับขยายได้ถึง **20–24 pt** (ระยะห่างบรรทัด 1.2–1.3) ตัวหนังสือจะใหญ่อ่านสบายตามาก ไม่ต้องเพ่ง และไม่ล้นกล่องแน่นอน
- **คำบรรยายใต้ภาพ (Captions):** ขนาด **14–16 pt**

---

# 📚 หมวดที่ 1: รายละเอียดเชิงลึกและการอ้างอิงเล่มวิจัยฉบับสมบูรณ์ (Academic Citations & Thesis References)

### 📌 การ์ดที่ 1: ผังกลศาสตร์ของไหลและการควบคุมวงปิด (Two-Tier Closed-Loop FSM)
*อ้างอิงจากเล่มวิจัย: บทที่ 3.3.1, บทที่ 4.3.1, ตารางที่ 4.4, ภาคผนวก ข และ ภาคผนวก ค*
- **ระบบตรวจวัดสามเซนเซอร์ (Sensors):** pH Probe (GPIO 1), EC/TDS Probe ชดเชยอุณหภูมิ 25°C อัตโนมัติ (GPIO 2), และโพรบวัดอุณหภูมิดิจิทัล DS18B20 สแตนเลส (GPIO 4)
- **วงจรของไหลอัตโนมัติ 6 ขั้นตอน (6-Phase Fluidic Sequence):**
  1. *Phase 1 (Sampling):* ปั๊มไดอะแฟรม 1 (GPIO 5, 6s) ดูดน้ำตัวอย่างเข้ากระบอกวัด V-102
  2. *Phase 2 (Sensing):* พักน้ำนิ่ง 3s สุ่มอ่าน 15 ครั้ง กรองสัญญาณรบกวนด้วย Moving Median Filter
  3. *Phase 3 (Recovery):* ปั๊มไดอะแฟรม 2 (GPIO 6, 7s) วนน้ำคืนถังปลูก 100% ไม่สูญเสียน้ำปุ๋ย
  4. *Phase 4 (Two-Tier Dosing Decision):*
     - **Tier 1 Baseline Priming:** เมื่อ $EC < 0.8\text{ mS/cm}$ สั่งเติมปุ๋ยพื้นฐานสลับกันทีละปั๊มเว้น 10 วินาที ป้องกันเกลือตกตะกอน
     - **Tier 1 Hard Safety Lockout:** ตัดการทำงานทันทีใน 0 วินาที หาก $EC > 2.5\text{ mS/cm}$ หรือ $pH < 4.0$ (ป้องกันรากไหม้และภาวะกรดดิ่งฉับพลัน Acid Shock)
     - **Tier 2 Predictive AI Modulation:** สั่งเดินปั๊มรีดสายเฉพาะสูตรที่ขาด (Pump 1/GPIO 9 เน้น N, Pump 2/GPIO 10 เน้น P, Pump 3/GPIO 11 เน้น K) รอบละ 5–10 วินาที (หน่วง Cooldown 6–12 ชม.)
  5. *Phase 5 (Probe Wash):* ปั๊มไดอะแฟรม 3 (GPIO 7, 5s) สูบน้ำสะอาด RO ชะล้างคราบเกลือบนหัวโพรบ
  6. *Phase 6 (Waste Drain):* โซลินอยด์วาล์ว 12V (GPIO 8, 6s) เปิดเดรนน้ำล้างทิ้งสู่ถังของเสีย

---

### 📌 การ์ดที่ 2: สถาปัตยกรรมปัญญาประดิษฐ์ A.E.G.I.S. (Multimodal Late-Fusion Pipeline)
*อ้างอิงจากเล่มวิจัย: บทที่ 2.4–2.7, บทที่ 3.3.4, บทที่ 4.2, แผนภูมิที่ 4.1, ตารางที่ 4.2 (ก), ตารางที่ 4.2 (ข), ตารางที่ 4.3*
- **สายภาพถ่ายพุ่มใบ (Stream A - Visual Foliar CNN):**
  - กล้องมุมสูง ESP32-S3 CAM ประมวลผลตัดแยกพุ่มใบด้วย CLAHE และดัชนีพืชพรรณ Excess Green Index ($ExG = 2G - R - B$) ร่วมกับ Otsu Adaptive Thresholding
  - **กลไก Symptom-Gated Filtering (จุดเด่นนวัตกรรม):** คัดกรองภาพระยะแฝง (Pre-symptomatic) ที่ใบยังเขียวสดออก 122 ภาพ จาก 304 ภาพฐาน เพื่อขจัด Label Noise และนำเฉพาะภาพแสดงอาการ 182 ภาพไปทำ Data Augmentation เป็น 786 ภาพ
  - โครงข่าย MobileNetV2 ผสาน Squeeze-and-Excitation (SE-Attention Block) ช่วยโฟกัสรอยโรคเฉพาะจุด แม่นยำถึง **95.12%**
  - ยืนยันเหตุผลการตัดสินใจด้วย **Grad-CAM Saliency Map** โฟกัสอาการทางสรีรวิทยาจริง (ขอบใบไหม้, ใบเหลืองซีด)
- **สายเซนเซอร์สารละลาย (Stream B - Physicochemical Feature Ensemble):**
  - สกัดคุณสมบัติ 7 มิติ ($EC_t, pH_t, Temp_t, \Delta EC_{\text{baseline}}, \Delta EC_{24h}, \Delta pH_{24h}, \text{Age}$)
  - โมเดลกลุ่มต้นไม้ตัดสินใจ (GBDT 100%, Random Forest 97.56%, Extra Trees 92.68%) รวม Soft-Vote ได้ความแม่นยำ **97.56%**
- **การรวมผลระดับการตัดสินใจ (Late-Fusion Stacking Meta-Classifier):**
  - Stacking Logistic Regression ถ่วงน้ำหนัก $P_{\text{fused}} = (0.35 \times P_{\text{vision}}) + (0.65 \times P_{\text{sensor}})$
  - **ความแม่นยำรวมระดับ Holdout Test สูงถึง 100.00%** (Macro F1-Score = 1.000, 95% CI: [100.0%, 100.0%])
  - ทดสอบในแปลงปลูกผักบุ้งจีนจริง 12 หน่วยทดลอง (4 ถังหลัก + 8 แก้วทดลองซ้ำ): **วินิจฉัยถูกต้องครบถ้วน 12 / 12 หน่วย (100.0%)**

---

### 📌 การ์ดที่ 3: แผนภูมิผลการทดลองและการเติบโตของผักบุ้งจีน (Ablation & Biomass Charts)
*อ้างอิงจากเล่มวิจัย: บทที่ 4.2.1, ตารางที่ 4.2 (ก), ตารางที่ 4.2 (ข), ภาคผนวก ก ข้อ 3*
- **ประสิทธิผลของกลไก Symptom-Gated Filtering (ตารางที่ 4.2 ก):**
  - โมเดล Vision A1 (MobileNetV2): ความแม่นยำพุ่งจาก $65.91\% \rightarrow 85.37\%$ ($+19.46\%$)
  - โมเดล Vision A2 (Multi-Scale SE-CNN): ความแม่นยำพุ่งจาก $50.00\% \rightarrow 90.24\%$ ($+40.24\%$)
  - รวมสายภาพ Stream A Ensemble: เพิ่มขึ้นจาก $72.73\% \rightarrow 95.12\%$ ($+22.39\%$)
- **การผสานพลังสองสาย (ตารางที่ 4.2 ข):**
  - Stream A (ภาพ 95.12%) + Stream B (เซนเซอร์ 97.56%) $\rightarrow$ A.E.G.I.S. Multimodal Late-Fusion บรรลุ **100.00%**
- **ผลผลิตชีวมวลสดและการเจริญเติบโตของผักบุ้งจีน (ภาคผนวก ก ข้อ 3):**
  - **กลุ่มควบคุม (Control - สมบูรณ์):** น้ำหนักชีวมวลสด **$54.3 \pm 4.2\text{ กรัม/ต้น}$** (100.0%), ความสูง $39.6\text{ ซม.}$, ใบจริง $20.4\text{ ใบ}$
  - **กลุ่มขาดไนโตรเจน (-N):** น้ำหนัก **$19.8 \pm 2.4\text{ กรัม/ต้น}$** ($36.5\%$, ผลผลิตลดลง $-63.5\%$)
  - **กลุ่มขาดฟอสฟอรัส (-P):** น้ำหนัก **$32.2 \pm 3.0\text{ กรัม/ต้น}$** ($59.3\%$, ลดลง $-40.7\%$)
  - **กลุ่มขาดโพแทสเซียม (-K):** น้ำหนัก **$37.9 \pm 3.4\text{ กรัม/ต้น}$** ($69.8\%$, ลดลง $-30.2\%$)

---

### 📌 การ์ดที่ 4: สรุปผลลัพธ์เชิงตัวเลขและคลังข้อมูลวิจัยเปิด (Key Metrics & Open Science)
*อ้างอิงจากเล่มวิจัย: บทคัดย่อ, บทที่ 4.1.1, ตารางที่ 4.1, บทที่ 4.3.2, ภาคผนวก ก-ค*
- **4 ตัวเลขความสำเร็จหลัก:**
  - `100.00%` — ความแม่นยำในการวินิจฉัยธาตุอาหาร N-P-K แบบผสานข้อมูล (Macro F1 = 1.000)
  - `12 / 12` — วินิจฉัยแปลงปลูกผักบุ้งจีนจริงถูกต้องครบทุกชุดทดลอง (4 ถังหลัก 23.3L + 8 แก้วทดลอง 750mL)
  - `122 ภาพ` — กลไก Symptom-Gating ขจัดภาพระยะแฝง ยกระดับความแม่นยำโครงข่าย SE-CNN สูงขึ้น +40.24%
  - `0% ตกตะกอน` — แยกขวดแม่ปุ๋ยแคลเซียม (Stock A) ออกจากฟอสเฟต (Stock B) และเว้นระยะปั๊ม 10 วินาที
- **เกณฑ์ล็อกเอาต์ความปลอดภัยฉุกเฉิน:**
  - *Hard Lockout:* ตัดการทำงานของปั๊มใน 0 วินาที เมื่อ $EC > 2.5\text{ mS/cm}$ หรือ $pH < 4.0$ ป้องกันภาวะกรดดิ่งฉับพลัน (Acid Shock pH 1.58)
  - *การวนน้ำคืนถัง 100%:* ปั๊มน้ำทดสอบกลับถังปลูกภายใน 7 วินาที
- **สแกน QR Code เพื่อเข้าถึงข้อมูลวิจัยเปิด:**
  - GitHub: `https://github.com/nottyzez/A.E.G.I.S-Ai`
