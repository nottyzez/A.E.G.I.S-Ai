# คู่มือข้อความและแคปชันวิชาการสำหรับโปสเตอร์งานวิจัย A.E.G.I.S.
## (A.E.G.I.S. Poster Content & Academic Companion Guide)

**โรงเรียน:** โรงเรียนสุวรรณภูมิพิทยไพศาล สพม.ร้อยเอ็ด  
**โครงงาน:** ระบบดูแลพืชแบบไฮโดรโปนิกส์โดยการทำนายปัจจัยในการเจริญเติบโตจากปัญญาประดิษฐ์  
**คณะผู้จัดทำ:** นายกิติภณ แถลงการณ์, นายชยพล นามจันทร์, นายปัญญพัฒน์ วิชาพล  
**ครูที่ปรึกษา:** นางสาวอศัลยา ดวงระหว้า  
**รูปแบบดีไซน์:** พิมพ์เขียววิศวกรรมมินิมอล (Minimal White Engineering Blueprint)

---

## สารบัญภาพพิมพ์เขียววิศวกรรม (Engineering Blueprint Files)

| ลำดับ | ชื่อไฟล์เวกเตอร์ (SVG) | ชื่อไฟล์ความละเอียดสูง (PNG 300 DPI) | สัดส่วน/ขนาด | คำอธิบายเนื้อหา |
| :---: | :--- | :--- | :---: | :--- |
| **Card 1** | [`blueprint_closed_loop_fsm.svg`](../assets/blueprints/blueprint_closed_loop_fsm.svg) | [`blueprint_closed_loop_fsm.png`](../assets/blueprints/blueprint_closed_loop_fsm.png) | 2850 × 1907 px | ผังวงจรของไหล 6 ขั้นตอน, ขา GPIO 1–11 และการควบคุม Two-Tier Dosing |
| **Card 2** | [`blueprint_multimodal_ai.svg`](../assets/blueprints/blueprint_multimodal_ai.svg) | [`blueprint_multimodal_ai.png`](../assets/blueprints/blueprint_multimodal_ai.png) | 2850 × 1907 px | ผังปัญญาประดิษฐ์สองสาย A.E.G.I.S. Late-Fusion, Symptom-Gating และ Grad-CAM |
| **Card 3** | [`blueprint_performance_charts.svg`](../assets/blueprints/blueprint_performance_charts.svg) | [`blueprint_performance_charts.png`](../assets/blueprints/blueprint_performance_charts.png) | 3176 × 2236 px | แผนภูมิ Ablation Study (+40.24%) และกราฟแท่งชีวมวลสด Day 22 ผักบุ้งจีน |
| **Card 4** | [`blueprint_key_metrics_summary.svg`](../assets/blueprints/blueprint_key_metrics_summary.svg) | [`blueprint_key_metrics_summary.png`](../assets/blueprints/blueprint_key_metrics_summary.png) | 2493 × 1907 px | การ์ด 4 ตัวเลขผลลัพธ์เด่น (100%), เกณฑ์ความปลอดภัย และ GitHub QR Code |

---

## หมวดที่ 1: ข้อความสำหรับคัดลอกลงโปสเตอร์ (Copy-Paste Ready Text)

### 📌 การ์ดที่ 1: ผังกลศาสตร์ของไหลและการควบคุมวงปิด (Two-Tier Closed-Loop FSM)
*อ้างอิงจากเล่มวิจัย: บทที่ 3.3.1, บทที่ 4.3.1, ตารางที่ 4.4, ภาคผนวก ข และ ภาคผนวก ค*

**หัวข้อหลัก (Headline):**  
`สถาปัตยกรรมกลศาสตร์ของไหล 6 ขั้นตอน และระบบควบคุมการจ่ายปุ๋ยแบบวงปิดสองระดับ (Two-Tier Closed-Loop Fluidic FSM)`

**เนื้อหาย่อสำหรับวางใต้ภาพ (Bullet Points):**
*   **ระบบตรวจวัดสามเซนเซอร์ (Sensors):** pH Probe (GPIO 1), EC/TDS Probe ชดเชยอุณหภูมิ 25°C อัตโนมัติ (GPIO 2), และโพรบวัดอุณหภูมิดิจิทัล DS18B20 สแตนเลส (GPIO 4)
*   **วงจรของไหลอัตโนมัติ 6 ขั้นตอน (6-Phase Fluidic Sequence):**
    1.  *Phase 1 (Sampling):* ปั๊มไดอะแฟรม 1 (GPIO 5, 6s) ดูดน้ำตัวอย่างเข้ากระบอกวัด V-102
    2.  *Phase 2 (Sensing):* พักน้ำนิ่ง 3s สุ่มอ่าน 15 ครั้ง กรองสัญญาณรบกวนด้วย Moving Median Filter
    3.  *Phase 3 (Recovery):* ปั๊มไดอะแฟรม 2 (GPIO 6, 7s) วนน้ำคืนถังปลูก 100% ไม่สูญเสียน้ำปุ๋ย
    4.  *Phase 4 (Two-Tier Dosing Decision):*
        *   **Tier 1 Baseline Priming:** เมื่อ $EC < 0.8\text{ mS/cm}$ สั่งเติมปุ๋ยพื้นฐานสลับกันทีละปั๊มเว้น 10 วินาที ป้องกันเกลือตกตะกอน
        *   **Tier 1 Hard Safety Lockout:** ตัดการทำงานทันทีใน 0 วินาที หาก $EC > 2.5\text{ mS/cm}$ หรือ $pH < 4.0$ (ป้องกันรากไหม้และภาวะกรดดิ่งฉับพลัน Acid Shock)
        *   **Tier 2 Predictive AI Modulation:** สั่งเดินปั๊มรีดสายเฉพาะสูตรที่ขาด (Pump 1/GPIO 9 เน้น N, Pump 2/GPIO 10 เน้น P, Pump 3/GPIO 11 เน้น K) รอบละ 5–10 วินาที (หน่วง Cooldown 6–12 ชม.)
    5.  *Phase 5 (Probe Wash):* ปั๊มไดอะแฟรม 3 (GPIO 7, 5s) สูบน้ำสะอาด RO ชะล้างคราบเกลือบนหัวโพรบ
    6.  *Phase 6 (Waste Drain):* โซลินอยด์วาล์ว 12V (GPIO 8, 6s) เปิดเดรนน้ำล้างทิ้งสู่ถังของเสีย

---

### 📌 การ์ดที่ 2: สถาปัตยกรรมปัญญาประดิษฐ์ A.E.G.I.S. (Multimodal Late-Fusion Pipeline)
*อ้างอิงจากเล่มวิจัย: บทที่ 2.4–2.7, บทที่ 3.3.4, บทที่ 4.2, แผนภูมิที่ 4.1, ตารางที่ 4.2 ก-ข, ตารางที่ 4.3*

**หัวข้อหลัก (Headline):**  
`สถาปัตยกรรมปัญญาประดิษฐ์ผสานข้อมูลภาพถ่ายพุ่มใบและอนุกรมเวลาเซนเซอร์ (Hierarchical Multimodal Late-Fusion)`

**เนื้อหาย่อสำหรับวางใต้ภาพ (Bullet Points):**
*   **สายภาพถ่ายพุ่มใบ (Stream A - Visual Foliar CNN):**
    *   กล้องมุมสูง ESP32-S3 CAM ประมวลผลตัดแยกพุ่มใบด้วย CLAHE และดัชนีพืชพรรณ Excess Green Index ($ExG = 2G - R - B$) ร่วมกับ Otsu Adaptive Thresholding
    *   **กลไก Symptom-Gated Filtering (จุดเด่นนวัตกรรม):** คัดกรองภาพระยะแฝง (Pre-symptomatic) ที่ใบยังเขียวสดออก 122 ภาพ จาก 304 ภาพฐาน เพื่อขจัด Label Noise และนำเฉพาะภาพแสดงอาการ 182 ภาพไปทำ Data Augmentation เป็น 786 ภาพ
    *   โครงข่าย MobileNetV2 ผสาน Squeeze-and-Excitation (SE-Attention Block) ช่วยโฟกัสรอยโรคเฉพาะจุด แม่นยำถึง **95.12%**
    *   ยืนยันเหตุผลการตัดสินใจด้วย **Grad-CAM Saliency Map** โฟกัสอาการทางสรีรวิทยาจริง (ขอบใบไหม้, ใบเหลืองซีด)
*   **สายเซนเซอร์สารละลาย (Stream B - Physicochemical Feature Ensemble):**
    *   สกัดคุณสมบัติ 7 มิติ ($EC_t, pH_t, Temp_t, \Delta EC_{\text{baseline}}, \Delta EC_{24h}, \Delta pH_{24h}, \text{Age}$)
    *   โมเดลกลุ่มต้นไม้ตัดสินใจ (GBDT 100%, Random Forest 97.56%, Extra Trees 92.68%) รวม Soft-Vote ได้ความแม่นยำ **97.56%**
*   **การรวมผลระดับการตัดสินใจ (Late-Fusion Stacking Meta-Classifier):**
    *   Stacking Logistic Regression ถ่วงน้ำหนัก $P_{\text{fused}} = (0.35 \times P_{\text{vision}}) + (0.65 \times P_{\text{sensor}})$
    *   **ความแม่นยำรวมระดับ Holdout Test สูงถึง 100.00%** (Macro F1-Score = 1.000, 95% CI: [100.0%, 100.0%])
    *   ทดสอบในแปลงปลูกผักบุ้งจีนจริง 12 หน่วยทดลอง (4 ถังหลัก + 8 แก้วทดลองซ้ำ): **วินิจฉัยถูกต้องครบถ้วน 12 / 12 หน่วย (100.0%)**

---

### 📌 การ์ดที่ 3: แผนภูมิผลการทดลองและการเติบโตของผักบุ้งจีน (Ablation & Biomass Charts)
*อ้างอิงจากเล่มวิจัย: บทที่ 4.2.1, ตารางที่ 4.2 (ก), ตารางที่ 4.2 (ข), ภาคผนวก ก ข้อ 3*

**หัวข้อหลัก (Headline):**  
`การศึกษาเปรียบเทียบประสิทธิภาพโมเดล (Ablation Study) และผลผลิตชีวมวลสดของผักบุ้งจีน ณ วันเก็บเกี่ยว (Day 22)`

**เนื้อหาย่อสำหรับวางใต้ภาพ (Bullet Points):**
*   **ประสิทธิผลของกลไก Symptom-Gated Filtering (ตารางที่ 4.2 ก):**
    *   โมเดล Vision A1 (MobileNetV2): ความแม่นยำพุ่งจาก $65.91\% \rightarrow 85.37\%$ ($+19.46\%$)
    *   โมเดล Vision A2 (Multi-Scale SE-CNN): ความแม่นยำพุ่งจาก $50.00\% \rightarrow 90.24\%$ ($+40.24\%$)
    *   โมเดล Vision A3 (Color-Texture Expert 44-D): พุ่งจาก $61.36\% \rightarrow 87.80\%$ ($+26.44\%$)
    *   รวมสายภาพ Stream A Ensemble: เพิ่มขึ้นจาก $72.73\% \rightarrow 95.12\%$ ($+22.39\%$)
*   **การผสานพลังสองสาย (ตารางที่ 4.2 ข):**
    *   Stream A (ภาพ 95.12%) + Stream B (เซนเซอร์ 97.56%) $\rightarrow$ A.E.G.I.S. Multimodal Late-Fusion บรรลุ **100.00%**
*   **ผลผลิตชีวมวลสดและการเจริญเติบโตของผักบุ้งจีน (ภาคผนวก ก ข้อ 3):**
    *   **กลุ่มควบคุม (Control - สมบูรณ์):** น้ำหนักชีวมวลสด **$54.3 \pm 4.2\text{ กรัม/ต้น}$** (100.0%), ความสูง $39.6\text{ ซม.}$, ใบจริง $20.4\text{ ใบ}$
    *   **กลุ่มขาดไนโตรเจน (-N):** น้ำหนัก **$19.8 \pm 2.4\text{ กรัม/ต้น}$** ($36.5\%$, ผลผลิตลดลง $-63.5\%$) เกิดจากการสลาย RuBisCO และการเคลื่อนย้าย N ย้อนกลับ
    *   **กลุ่มขาดฟอสฟอรัส (-P):** น้ำหนัก **$32.2 \pm 3.0\text{ กรัม/ต้น}$** ($59.3\%$, ลดลง $-40.7\%$) ลำต้นแคระแกร็นและมีสีเขียวเข้มคล้ำอมม่วงจาก Anthocyanin
    *   **กลุ่มขาดโพแทสเซียม (-K):** น้ำหนัก **$37.9 \pm 3.4\text{ กรัม/ต้น}$** ($69.8\%$, ลดลง $-30.2\%$) เกิดอาการขอบใบและปลายใบม้วนไหม้สีน้ำตาล

---

### 📌 การ์ดที่ 4: สรุปผลลัพธ์เชิงตัวเลขและคลังข้อมูลวิจัยเปิด (Key Metrics & Open Science)
*อ้างอิงจากเล่มวิจัย: บทคัดย่อ, บทที่ 4.1.1, ตารางที่ 4.1, บทที่ 4.3.2, ภาคผนวก ก-ค*

**หัวข้อหลัก (Headline):**  
`สรุปตัวเลขผลงานเชิงประจักษ์ เกณฑ์ความปลอดภัย และคลังข้อมูลวิจัยเปิด (Open Science Repository)`

**เนื้อหาย่อสำหรับวางใต้ภาพ (Bullet Points):**
*   **4 ตัวเลขความสำเร็จหลัก (Key Metric Highlights):**
    *   `100.00%` — ความแม่นยำในการวินิจฉัยธาตุอาหาร N-P-K แบบผสานข้อมูล (Macro F1 = 1.000)
    *   `12 / 12` — วินิจฉัยแปลงปลูกจริงถูกต้องครบทุกชุดทดลอง (4 ถังหลัก 23.3L + 8 แก้วทดลอง 750mL)
    *   `122 ภาพ` — กลไก Symptom-Gating ขจัดภาพระยะแฝง ยกระดับความแม่นยำโครงข่าย SE-CNN สูงขึ้น +40.24%
    *   `0% ตกตะกอน` — แยกขวดแม่ปุ๋ยแคลเซียม (Stock A) ออกจากฟอสเฟต (Stock B) และเว้นระยะปั๊ม 10 วินาที
*   **เกณฑ์ล็อกเอาต์ความปลอดภัยฉุกเฉิน (Safety Guardrails):**
    *   *Hard Lockout:* ตัดการทำงานของปั๊มใน 0 วินาที เมื่อ $EC > 2.5\text{ mS/cm}$ หรือ $pH < 4.0$ ป้องกันภาวะกรดดิ่งฉับพลัน (Acid Shock pH 1.58)
    *   *การวนน้ำคืนถัง 100%:* ปั๊มน้ำทดสอบกลับถังปลูกภายใน 7 วินาที
    *   *การล้างหัวโพรบอัตโนมัติ:* ล้างน้ำสะอาด RO 5 วินาที และเปิดเดรน 6 วินาที ยืดอายุการใช้งานโพรบเกิน 300%
*   **สแกน QR Code เพื่อเข้าถึงข้อมูลวิจัยเปิด:**
    *   GitHub: `https://github.com/nottyzez/A.E.G.I.S-Ai`
    *   เข้าถึงชุดข้อมูลโทรมาตรอนุกรมเวลา 143 รายการบันทึก, แบบพิมพ์เขียววงจร IEEE-315 4K, ผัง ISA-5.1 P&ID และซอร์สโค้ดเฟิร์มแวร์ C++ ทั้งหมด

---

## หมวดที่ 2: คำแนะนำการจัดวางบนโปสเตอร์ (Poster Layout Instructions)

1.  **การแทรกภาพลงใน Canva / Photoshop:**
    *   ภาพ PNG ในโฟลเดอร์ `assets/blueprints/` ถูกเรนเดอร์ที่ความละเอียด $2850 \times 1907$ ถึง $3176 \times 2236$ พิกเซล (300 DPI) ซึ่งคมชัดเป็นพิเศษเมื่อขยายเต็มพื้นที่
    *   สามารถแทรกไฟล์ภาพทั้ง 4 ภาพลงในโปสเตอร์ และใช้เครื่องมือ Crop หรือปรับขนาดได้โดยไม่สูญเสียความละเอียด
2.  **การจัดหมวดหมู่เนื้อหา:**
    *   **ส่วนกระบวนการทำงาน (Methodology):** วาง `Card 1 (Fluidic FSM)` และ `Card 2 (Multimodal AI)` เคียงข้างกันเพื่อแสดงการทำงานของระบบ
    *   **ส่วนผลการวิจัย (Results & Discussion):** วาง `Card 3 (Ablation & Biomass Charts)` ใกล้กับส่วนสรุปผลการวิจัย
    *   **ส่วนท้ายบอร์ด (Footer / Highlights):** วาง `Card 4 (Key Metrics Summary & QR Code)` ไว้ที่แถบด้านล่างหรือมุมล่างขวา เพื่อให้ผู้ตรวจประเมินสามารถสแกน QR Code ไปดูข้อมูลสดบน GitHub ได้ทันที
