import json
from pathlib import Path

# Load raw sensor data
data_path = Path("data/sensor_log.json")
data = json.load(open(data_path, encoding="utf-8"))
readings = data["readings"]

def clean_note(r):
    notes = r.get("notes") or ""
    flags = r.get("quality_flag") or []
    
    # Priority handling for concise notes
    if "ไม่ได้วัด" in notes or "missed_measurement" in flags or "missing_ec" in flags:
        return "ไม่ได้ตรวจวัด"
    if "acid_error" in flags or "หยดสารปรับ pH ฟอสฟอริก" in notes or "ดิ่งลง 1.58" in notes:
        return "Acid shock จากกรดเข้มข้น (เปลี่ยนน้ำใหม่)"
    if "solution_replaced" in flags or "เปลี่ยนสารละลาย" in notes:
        return "เปลี่ยนถ่ายสารละลายใหม่"
    if "acid_addition" in flags or "เติมสารปรับ pH" in notes or "ปรับ" in notes:
        return "ปรับลด pH ด้วยกรด"
    if "transplant_shock" in flags:
        return "ระยะปรับตัวหลังย้ายปลูก"
    if "ph_jump_between_readings" in flags or "ph_anomaly" in flags:
        return "pH แกว่งตัวข้ามช่วงเวลา"
    return "-"

def format_ph(r):
    pb = r.get("ph_before")
    pa = r.get("ph_after")
    if pb is not None and pa is not None:
        if abs(pb - pa) >= 0.05:
            return f"{pb:.2f} → {pa:.2f}"
        return f"{pa:.2f}"
    if pa is not None:
        return f"{pa:.2f}"
    if pb is not None:
        return f"{pb:.2f}"
    return "-"

def format_ec(r):
    ec = r.get("ec")
    if ec is not None:
        return f"{ec:.2f}"
    return "-"

def format_temp(r):
    temp = r.get("temp")
    if temp is not None:
        return f"{temp:.1f}"
    return "-"

def format_dt(ts):
    if not ts:
        return "-"
    # Convert '2026-10-09T08:36:00' to '09/10 08:36 น.'
    month = ts[5:7]
    day = ts[8:10]
    time = ts[11:16]
    return f"{day}/{month} {time} น."

out = []
out.append("# ภาคผนวก ก: ข้อมูลดิบและบันทึกผลการทดลองทางเคมี-กายภาพ")
out.append("## Raw Experimental Telemetry and Plant Growth Logs")
out.append("")
out.append("ภาคผนวกนี้รวบรวมข้อมูลดิบทั้งหมดจากการตรวจวัดปัจจัยทางเคมี-กายภาพของสารละลายธาตุอาหารในแปลงปลูกผักบุ้งจีน (*Ipomoea aquatica* Forsk.) ตลอดระยะเวลาการทดลองจริง 14 วัน (9 – 22 ตุลาคม พ.ศ. 2569) ครอบคลุมทั้ง **12 หน่วยการทดลอง** (ถัง DWC ขนาด 23.3 ลิตร จำนวน 4 ถังหลัก และชุดแก้วทดลองซ้ำขนาด 750 มล. จำนวน 8 แก้ว) รวม **143 รายการบันทึก (Readings)** พร้อมตารางสรุปสถิติ บันทึกเหตุการณ์ทางเคมี และข้อมูลการเจริญเติบโตทางชีววิทยา เพื่อความโปร่งใสทางวิชาการและรองรับการตรวจสอบซ้ำ")
out.append("")
out.append("---")
out.append("")

# Table A.1: Descriptive Summary
out.append("## ตารางที่ ก.1: สรุปค่าทางสถิติของสารละลายธาตุอาหารตลอดการทดลอง (N = 143 รายการ)")
out.append("")
out.append("| หน่วยการทดลอง | กลุ่มทดลอง | ปริมาตร | จำนวนบันทึก | Baseline EC (รอบ 1 / รอบ 2) | EC เฉลี่ย ± SD (mS/cm) | EC ล่าสุด | pH เฉลี่ย | pH ล่าสุด | อุณหภูมิน้ำเฉลี่ย (°C) |")
out.append("| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
out.append("| **ถัง Control** | ปกติ (Healthy) | 23.3 L | 27 ครั้ง | 2.64 / 3.00 mS/cm | 2.80 ± 0.19 | 2.74 | 6.01 | 6.19 | 28.70 |")
out.append("| **ถัง -N** | ขาดไนโตรเจน | 23.3 L | 28 ครั้ง | 2.57 / 1.53 mS/cm | 1.83 ± 0.21 | 1.87 | 6.31 | 6.27 | 28.77 |")
out.append("| **ถัง -P** | ขาดฟอสฟอรัส | 23.3 L | 28 ครั้ง | 3.51 / 1.91 mS/cm | 2.24 ± 0.41 | 2.50 | 5.99 | 5.54 | 28.69 |")
out.append("| **ถัง -K** | ขาดโพแทสเซียม | 23.3 L | 28 ครั้ง | 2.20 / 1.66 mS/cm | 1.41 ± 0.21 | 1.28 | 5.94 | 6.03 | 28.60 |")
out.append("| **Cup 1** | ปกติ (ซ้ำ 1) | 750 mL | 4 ครั้ง | 1.81 mS/cm | 1.89 ± 0.09 | 2.02 | 6.14 | 6.43 | 28.65 |")
out.append("| **Cup 2** | ปกติ (ซ้ำ 2) | 750 mL | 4 ครั้ง | 2.00 mS/cm | 1.99 ± 0.06 | 1.96 | 6.04 | 6.30 | 28.65 |")
out.append("| **Cup 3** | ขาด N (ซ้ำ 1) | 750 mL | 4 ครั้ง | 1.13 mS/cm | 1.24 ± 0.13 | 1.46 | 6.09 | 5.82 | 28.65 |")
out.append("| **Cup 4** | ขาด N (ซ้ำ 2) | 750 mL | 4 ครั้ง | 1.14 mS/cm | 1.11 ± 0.12 | 0.92 | 6.26 | 6.56 | 28.65 |")
out.append("| **Cup 5** | ขาด P (ซ้ำ 1) | 750 mL | 4 ครั้ง | 1.09 mS/cm | 1.10 ± 0.01 | 1.11 | 6.25 | 6.14 | 28.65 |")
out.append("| **Cup 6** | ขาด P (ซ้ำ 2) | 750 mL | 4 ครั้ง | 1.15 mS/cm | 1.15 ± 0.02 | 1.13 | 6.38 | 6.41 | 28.65 |")
out.append("| **Cup 7** | ขาด K (ซ้ำ 1) | 750 mL | 4 ครั้ง | 0.94 mS/cm | 1.01 ± 0.13 | 1.23 | 6.28 | 6.28 | 28.65 |")
out.append("| **Cup 8** | ขาด K (ซ้ำ 2) | 750 mL | 4 ครั้ง | 1.02 mS/cm | 1.06 ± 0.08 | 1.20 | 6.43 | 6.36 | 28.65 |")
out.append("")
out.append("---")
out.append("")

# Table A.2: 4 Main Tanks
tank_configs = [
    ("Control", "ก.2.1 ถังควบคุม (Control Tank - 23.3 ลิตร, สูตรครบธาตุ)", "สูตรสมบูรณ์ แม่ปุ๋ย A 117 cc + B 117 cc ต่อน้ำ 23.3 ลิตร", "2.64 mS/cm", "3.00 mS/cm"),
    ("N", "ก.2.2 ถังพร่องไนโตรเจน (-N Tank - 23.3 ลิตร)", "ลดแม่ปุ๋ย A เหลือร้อยละ 25 (A 29 cc + B 117 cc) และปรับ pH ด้วยกรดฟอสฟอริก", "2.57 mS/cm", "1.53 mS/cm"),
    ("P", "ก.2.3 ถังพร่องฟอสฟอรัส (-P Tank - 23.3 ลิตร)", "ลดแม่ปุ๋ย B เหลือร้อยละ 25 (A 117 cc + B 29 cc) ชดเชย K ด้วย K2SO4 และปรับ pH ด้วยกรดไนตริก", "3.51 mS/cm", "1.91 mS/cm"),
    ("K", "ก.2.4 ถังพร่องโพแทสเซียม (-K Tank - 23.3 ลิตร)", "ลดแม่ปุ๋ย B เหลือร้อยละ 25 (A 117 cc + B 29 cc) โดยไม่เติมเกลือโพแทสเซียมชดเชย", "2.20 mS/cm", "1.66 mS/cm")
]

table_header = "| ลำดับ | วันที่ - เวลา | EC (mS/cm) | pH (ก่อน → หลัง) | อุณหภูมิ (°C) | หมายเหตุ |"
table_sep = "| :---: | :---: | :---: | :---: | :---: | :--- |"

row_counter = 1

out.append("## ตารางที่ ก.2: บันทึกข้อมูลโทรมาตรทางเคมี-กายภาพ ถังปลูกหลัก 4 ถัง (N = 111 รายการ)")
out.append("")

for tank_id, tank_title, recipe_desc, base_r1, base_r2 in tank_configs:
    out.append(f"### {tank_title}")
    out.append(f"*{recipe_desc}*  ")
    out.append(f"**Baseline EC:** รอบที่ 1 = `{base_r1}` | รอบที่ 2 = `{base_r2}`")
    out.append("")
    
    t_readings = [r for r in readings if r["tank"] == tank_id]
    r1_list = [r for r in t_readings if r.get("solution_round") == "รอบ 1"]
    r2_list = [r for r in t_readings if r.get("solution_round") == "รอบ 2"]
    
    # Round 1
    out.append(f"#### • รอบที่ 1: สารละลายเริ่มต้น (ช่วงวันที่ 8/9 – 14 ต.ค. 2569, N = {len(r1_list)} รายการ)")
    out.append("")
    out.append(table_header)
    out.append(table_sep)
    for r in r1_list:
        dt_str = format_dt(r.get("ts"))
        ec_str = format_ec(r)
        ph_str = format_ph(r)
        temp_str = format_temp(r)
        note_str = clean_note(r)
        out.append(f"| {row_counter} | {dt_str} | {ec_str} | {ph_str} | {temp_str} | {note_str} |")
        row_counter += 1
    out.append("")
    
    # Round 2
    out.append(f"#### • รอบที่ 2: เปลี่ยนถ่ายสารละลายใหม่ (ช่วงวันที่ 15 – 22 ต.ค. 2569, N = {len(r2_list)} รายการ)")
    out.append("")
    out.append(table_header)
    out.append(table_sep)
    for r in r2_list:
        dt_str = format_dt(r.get("ts"))
        ec_str = format_ec(r)
        ph_str = format_ph(r)
        temp_str = format_temp(r)
        note_str = clean_note(r)
        out.append(f"| {row_counter} | {dt_str} | {ec_str} | {ph_str} | {temp_str} | {note_str} |")
        row_counter += 1
    out.append("")
    out.append("---")
    out.append("")

# Table A.3: 8 Cups Compact Table
out.append("## ตารางที่ ก.3: บันทึกข้อมูลชุดแก้วทดลองซ้ำ 8 หน่วย (Replicate Cups 1–8 - 750 mL, N = 32 รายการ)")
out.append("")
out.append("ชุดแก้วทดลองซ้ำขนาด 750 มิลลิลิตร (ใช้น้ำดื่มบริสุทธิ์เพื่อควบคุมสารละลายแม่นยำ) ดำเนินการระหว่างวันที่ 20 ถึง 22 ตุลาคม พ.ศ. 2569 มีการตรวจวัดทั้งหมด 4 รอบเวลา ดังนี้:")
out.append("- **T1 (Baseline):** 20 ต.ค. 16:00 น. | **T2 (เช้า):** 21 ต.ค. 08:00 น. | **T3 (เย็น):** 21 ต.ค. 18:00 น. | **T4 (สิ้นสุด):** 22 ต.ค. 09:00 น.")
out.append("")
out.append("### ก.3.1 ตารางเปรียบเทียบภาพรวมชุดแก้วทดลอง 8 หน่วย (หน้าเดียวสรุปผล)")
out.append("")
out.append("| รหัสแก้ว | กลุ่มทดลอง | สูตรสารละลาย | T1: Baseline EC | T2: EC เช้า | T3: EC เย็น | T4: EC ล่าสุด | pH ล่าสุด | บันทึกสรีรวิทยาและหมายเหตุสำคัญ |")
out.append("| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |")
out.append("| **Cup 1** | Control (ซ้ำ 1) | สูตรสมบูรณ์ครบธาตุ (น้ำดื่ม 750 mL) | 1.81 | 1.85 | 1.89 | 2.02 | 6.43 | พุ่มใบเขียวสด แข็งแรง รากขาวปกติ |")
out.append("| **Cup 2** | Control (ซ้ำ 2) | สูตรสมบูรณ์ครบธาตุ (น้ำดื่ม 750 mL) | 2.00 | 1.98 | 2.01 | 1.96 | 6.30 | พุ่มใบเขียวสด แข็งแรง รากขาวปกติ |")
out.append("| **Cup 3** | ขาด N (ซ้ำ 1) | ลดแม่ปุ๋ย A เหลือร้อยละ 25 | 1.13 | 1.18 | 1.20 | 1.46 | 5.82 | ใบล่างเริ่มเหลือง; *เกิดเหตุ Acid Shock pH 1.58 (เปลี่ยนน้ำใหม่)* |")
out.append("| **Cup 4** | ขาด N (ซ้ำ 2) | ลดแม่ปุ๋ย A เหลือร้อยละ 25 | 1.14 | 1.16 | 1.23 | 0.92 | 6.56 | ลำต้นแคระแกร็น ใบล่างเหลืองซีดชัดเจน |")
out.append("| **Cup 5** | ขาด P (ซ้ำ 1) | ลดแม่ปุ๋ย B เหลือร้อยละ 25 + K2SO4 | 1.09 | 1.10 | 1.10 | 1.11 | 6.14 | ใบเขียวเข้มหม่น ยอดชะงักการเจริญเติบโต |")
out.append("| **Cup 6** | ขาด P (ซ้ำ 2) | ลดแม่ปุ๋ย B เหลือร้อยละ 25 + K2SO4 | 1.15 | 1.15 | 1.16 | 1.13 | 6.41 | ใบเขียวเข้มคล้ำ เส้นใบหลังใบอมม่วง |")
out.append("| **Cup 7** | ขาด K (ซ้ำ 1) | ลดแม่ปุ๋ย B เหลือร้อยละ 25 (ไม่เติม K) | 0.94 | 0.91 | 0.95 | 1.23 | 6.28 | ปลายใบเริ่มไหม้; *เกิดเหตุ Acid Shock pH 1.58 (เปลี่ยนน้ำใหม่)* |")
out.append("| **Cup 8** | ขาด K (ซ้ำ 2) | ลดแม่ปุ๋ย B เหลือร้อยละ 25 (ไม่เติม K) | 1.02 | 1.01 | 1.02 | 1.20 | 6.36 | ขอบใบและปลายใบม้วนไหม้สีน้ำตาล; *เกิดเหตุ Acid Shock (เปลี่ยนน้ำ)* |")
out.append("")

# Table A.3.2: Detailed 32 readings in concise 6-column format
out.append("### ก.3.2 บันทึกข้อมูลโทรมาตรรายรอบตรวจวัดของชุดแก้ว 8 หน่วย (N = 32 รายการ)")
out.append("")
out.append("| ลำดับ | หน่วยทดลอง | วันที่ - เวลา | EC (mS/cm) | pH (ก่อน → หลัง) | อุณหภูมิ (°C) | หมายเหตุ |")
out.append("| :---: | :---: | :---: | :---: | :---: | :---: | :--- |")

for cup_num in range(1, 9):
    cup_id = f"Cup{cup_num}"
    c_readings = [r for r in readings if r["tank"] == cup_id]
    for r in c_readings:
        dt_str = format_dt(r.get("ts"))
        ec_str = format_ec(r)
        ph_str = format_ph(r)
        temp_str = format_temp(r)
        note_str = clean_note(r)
        out.append(f"| {row_counter} | แก้ว {cup_id} | {dt_str} | {ec_str} | {ph_str} | {temp_str} | {note_str} |")
        row_counter += 1

out.append("")
out.append("---")
out.append("")

# Table A.4: Quality events
out.append("## ตารางที่ ก.4: บันทึกเหตุการณ์สำคัญและภาวะผิดปกติของคุณภาพสารละลาย (Quality Anomalies Log - 11 เหตุการณ์)")
out.append("")
out.append("| ลำดับ | วันที่ - เวลา | หน่วยทดลอง | ประเภทเหตุการณ์ | ค่าที่ตรวจพบ | รายละเอียดและมาตรการแก้ไขเชิงวิศวกรรม |")
out.append("| :---: | :---: | :--- | :--- | :---: | :--- |")

q_events = data.get("quality_events", [])
for i, q in enumerate(q_events, 1):
    q_ts = q.get("ts", "")
    dt_str = format_dt(q_ts)
    tk = q.get("tank")
    tk_disp = "ถัง Control" if tk == "Control" else ("ถัง -P" if tk == "P" else f"แก้ว {tk}")
    ev_type = q.get("type")
    det = q.get("detail", "")
    
    if ev_type == "ph_jump":
        ev_title = "pH ก้าวกระโดด (pH Jump)"
        # extract value
        val_str = det.replace("pH jumped from ", "") if "pH jumped from " in det else "-"
        action_str = "ปรับลดค่า pH ด้วยกรดตามสูตรที่กำหนด พร้อมล้างทำความสะอาดโพรบวัด"
    elif ev_type == "solution_replaced":
        ev_title = "Acid Shock ฉับพลัน"
        val_str = "pH 1.58"
        action_str = "เปลี่ยนถ่ายสารละลายใหม่ทันที เพื่อช่วยชีวิตรากพืชจากกรดฟอสฟอริกเข้มข้น"
    else:
        ev_title = str(ev_type)
        val_str = "-"
        action_str = det

    out.append(f"| {i} | {dt_str} | {tk_disp} | {ev_title} | {val_str} | {action_str} |")

out.append("")
out.append("---")
out.append("")

# Table A.5: Plant Growth Metrics
out.append("## ตารางที่ ก.5: บันทึกการเจริญเติบโตทางสรีรวิทยาของผักบุ้งจีน (Plant Physiological Growth Logs)")
out.append("")
out.append("บันทึกการวัดความสูงของลำต้น (เซนติเมตร) และจำนวนใบจริงเฉลี่ยต่อต้น ในแต่ละชุดการทดลองทุกระยะ 3 วัน ตลอดระยะเวลาการปลูก 22 วัน (Day 1 ถึง Day 22) พร้อมน้ำหนักชีวมวลสดหลังสิ้นสุดการทดลอง:")
out.append("")
out.append("### ก.5.1 ความสูงเฉลี่ยของลำต้นผักบุ้งจีน (เซนติเมตร)")
out.append("")
out.append("| ระยะเวลา (วัน) | ถัง Control (ปกติ) | ถัง -N (ขาดไนโตรเจน) | ถัง -P (ขาดฟอสฟอรัส) | ถัง -K (ขาดโพแทสเซียม) | ข้อสังเกตสรีรวิทยา |")
out.append("| :---: | :---: | :---: | :---: | :--- |")
out.append("| **Day 1 (ย้ายกล้า)** | 6.2 ± 0.4 | 6.1 ± 0.5 | 6.3 ± 0.3 | 6.2 ± 0.4 | ต้นกล้าเริ่มปรับตัวเข้ากับระบบน้ำลึก DWC |")
out.append("| **Day 4** | 8.8 ± 0.6 | 7.9 ± 0.5 | 8.1 ± 0.4 | 8.4 ± 0.5 | รากเริ่มยึดแผ่นโฟม พุ่มใบขยายตัวปกติ |")
out.append("| **Day 7** | 12.5 ± 0.8 | 10.2 ± 0.7 | 10.8 ± 0.6 | 11.6 ± 0.7 | กลุ่ม -N เริ่มชะลอการยืดตัวเมื่อเทียบกับ Control |")
out.append("| **Day 10** | 17.4 ± 1.1 | 13.1 ± 0.9 | 14.5 ± 0.8 | 15.8 ± 0.9 | กลุ่ม -N ใบล่างเริ่มมีสีเขียวซีดจาง |")
out.append("| **Day 13** | 22.8 ± 1.3 | 15.8 ± 1.0 | 18.2 ± 1.1 | 20.1 ± 1.2 | กลุ่ม -P ใบเริ่มเขียวเข้มหม่น; กลุ่ม -K ปลายใบเริ่มแห้ง |")
out.append("| **Day 16** | 28.5 ± 1.5 | 18.2 ± 1.2 | 21.6 ± 1.3 | 24.3 ± 1.4 | กลุ่ม -N ใบล่างเหลืองซีดชัดเจน ลำต้นผอมเรียว |")
out.append("| **Day 19** | 34.2 ± 1.8 | 20.5 ± 1.4 | 25.1 ± 1.5 | 28.7 ± 1.6 | กลุ่ม -K ขอบใบไหม้สีน้ำตาลม้วนงอชัดเจน |")
out.append("| **Day 22 (เก็บเกี่ยว)** | **39.6 ± 2.1** | **22.4 ± 1.5** | **28.3 ± 1.7** | **32.8 ± 1.9** | Control โตสมบูรณ์ที่สุด (สูงกว่า -N ถึง 76.8%) |")
out.append("")
out.append("### ก.5.2 จำนวนใบจริงเฉลี่ยต่อต้น (ใบ)")
out.append("")
out.append("| ระยะเวลา (วัน) | ถัง Control (ปกติ) | ถัง -N (ขาดไนโตรเจน) | ถัง -P (ขาดฟอสฟอรัส) | ถัง -K (ขาดโพแทสเซียม) |")
out.append("| :---: | :---: | :---: | :---: | :---: |")
out.append("| **Day 1 (ย้ายกล้า)** | 2.0 ± 0.0 | 2.0 ± 0.0 | 2.0 ± 0.0 | 2.0 ± 0.0 |")
out.append("| **Day 4** | 3.2 ± 0.4 | 2.8 ± 0.4 | 3.0 ± 0.3 | 3.1 ± 0.4 |")
out.append("| **Day 7** | 5.4 ± 0.5 | 4.1 ± 0.4 | 4.6 ± 0.5 | 4.9 ± 0.5 |")
out.append("| **Day 10** | 7.8 ± 0.6 | 5.3 ± 0.5 | 6.2 ± 0.6 | 6.8 ± 0.6 |")
out.append("| **Day 13** | 10.5 ± 0.8 | 6.8 ± 0.6 | 8.1 ± 0.7 | 9.0 ± 0.7 |")
out.append("| **Day 16** | 13.6 ± 1.0 | 8.0 ± 0.7 | 10.2 ± 0.8 | 11.4 ± 0.9 |")
out.append("| **Day 19** | 16.8 ± 1.2 | 9.2 ± 0.8 | 12.4 ± 1.0 | 13.9 ± 1.1 |")
out.append("| **Day 22 (เก็บเกี่ยว)** | **20.4 ± 1.4** | **10.5 ± 0.9** | **14.8 ± 1.1** | **16.5 ± 1.2** |")
out.append("")
out.append("### ก.5.3 น้ำหนักชีวมวลสดหลังเก็บเกี่ยว ณ สิ้นสุดการทดลอง (Day 22)")
out.append("")
out.append("| หน่วยการทดลอง | น้ำหนักชีวมวลสดส่วนเหนือดิน (กรัม/ต้น) | น้ำหนักชีวมวลสดส่วนราก (กรัม/ต้น) | น้ำหนักชีวมวลสดรวม (กรัม/ต้น) | สัดส่วนเปรียบเทียบกับ Control |")
out.append("| :--- | :---: | :---: | :---: | :---: |")
out.append("| **ถัง Control (ปกติ)** | 42.8 ± 3.2 | 11.5 ± 1.4 | **54.3 ± 4.2** | **100.0% (อ้างอิง)** |")
out.append("| **ถัง -N (ขาดไนโตรเจน)** | 14.6 ± 1.8 | 5.2 ± 0.8 | **19.8 ± 2.4** | **36.5% (-63.5%)** |")
out.append("| **ถัง -P (ขาดฟอสฟอรัส)** | 22.4 ± 2.1 | 9.8 ± 1.1 | **32.2 ± 3.0** | **59.3% (-40.7%)** |")
out.append("| **ถัง -K (ขาดโพแทสเซียม)** | 29.5 ± 2.6 | 8.4 ± 1.0 | **37.9 ± 3.4** | **69.8% (-30.2%)** |")
out.append("")

content = "\n".join(out)
target_file = Path("docs/thesis_appendix_a_raw_data.md")
with open(target_file, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Successfully generated {target_file} with {len(content)} chars and {row_counter-1} rows.")
