"""
add_cup_sheets.py — Add sheets for the 8-cup experiment (750ml drinking water)
to hydroponic_log.xlsx with formulas, temperature columns, and formatting.
"""

import sys
import io
import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from datetime import datetime, time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

EXCEL_PATH = r"d:\Code มหาปลัย\Ai มหาปลัย\dataset_real\hydroponic_log.xlsx"

# Cups metadata: (cup_no, group_name, group_code, baseline_ec, formula_desc, acid_desc)
CUPS = [
    (1, "Control แก้ว 1", "Control", 1.144, "สูตรสมบูรณ์ (ครบธาตุ) ในน้ำดื่ม 750 ml", "กรดไนตริก"),
    (2, "Control แก้ว 2", "Control", 1.150, "สูตรสมบูรณ์ (ครบธาตุ) ในน้ำดื่ม 750 ml", "กรดไนตริก"),
    (3, "ขาด N แก้ว 1", "-N", 1.808, "สูตรขาด N ในน้ำดื่ม 750 ml", "กรดฟอสฟอริก"),
    (4, "ขาด N แก้ว 2", "-N", 1.996, "สูตรขาด N ในน้ำดื่ม 750 ml", "กรดฟอสฟอริก"),
    (5, "ขาด P แก้ว 1", "-P", 1.130, "สูตรขาด P ในน้ำดื่ม 750 ml", "กรดไนตริก"),
    (6, "ขาด P แก้ว 2", "-P", 1.144, "สูตรขาด P ในน้ำดื่ม 750 ml", "กรดไนตริก"),
    (7, "ขาด K แก้ว 1", "-K", 0.938, "สูตรขาด K ในน้ำดื่ม 750 ml", "กรดฟอสฟอริก"),
    (8, "ขาด K แก้ว 2", "-K", 1.020, "สูตรขาด K ในน้ำดื่ม 750 ml", "กรดฟอสฟอริก"),
]

# Initial data recorded on 20-21 Oct 2026
DATA = {
    1: [
        {"date": datetime(2026, 10, 20), "time": time(16, 0), "ec": 1.086, "ph_before": 6.51, "ph_after": 6.51, "temp": None, "note": ""},
        {"date": datetime(2026, 10, 21), "time": time(8, 0), "ec": 1.092, "ph_before": 7.20, "ph_after": 6.11, "temp": None, "note": ""},
    ],
    2: [
        {"date": datetime(2026, 10, 20), "time": time(16, 0), "ec": 1.150, "ph_before": 6.18, "ph_after": 6.18, "temp": None, "note": ""},
        {"date": datetime(2026, 10, 21), "time": time(8, 0), "ec": 1.130, "ph_before": 7.08, "ph_after": 6.43, "temp": None, "note": ""},
    ],
    3: [
        {"date": datetime(2026, 10, 20), "time": time(16, 0), "ec": 1.808, "ph_before": 5.75, "ph_after": 5.75, "temp": None, "note": ""},
        {"date": datetime(2026, 10, 21), "time": time(8, 0), "ec": 1.806, "ph_before": 6.15, "ph_after": 6.15, "temp": None, "note": ""},
    ],
    4: [
        {"date": datetime(2026, 10, 20), "time": time(16, 0), "ec": 1.996, "ph_before": 5.58, "ph_after": 5.58, "temp": None, "note": ""},
        {"date": datetime(2026, 10, 21), "time": time(8, 0), "ec": 1.920, "ph_before": 6.12, "ph_after": 6.12, "temp": None, "note": ""},
    ],
    5: [
        {"date": datetime(2026, 10, 20), "time": time(16, 0), "ec": 1.130, "ph_before": 5.70, "ph_after": 5.70, "temp": None, "note": ""},
        {"date": datetime(2026, 10, 21), "time": time(8, 0), "ec": 1.160, "ph_before": 6.56, "ph_after": 6.35, "temp": None, "note": ""},
    ],
    6: [
        {"date": datetime(2026, 10, 20), "time": time(16, 0), "ec": 1.144, "ph_before": 5.80, "ph_after": 5.80, "temp": None, "note": ""},
        {"date": datetime(2026, 10, 21), "time": time(8, 0), "ec": 1.184, "ph_before": 6.56, "ph_after": 6.25, "temp": None, "note": ""},
    ],
    7: [
        {"date": datetime(2026, 10, 20), "time": time(16, 0), "ec": 0.938, "ph_before": 7.44, "ph_after": 6.15, "temp": None, "note": ""},
        {"date": datetime(2026, 10, 21), "time": time(8, 0), "ec": 0.910, "ph_before": 6.86, "ph_after": 6.40, "temp": None, "note": ""},
    ],
    8: [
        {"date": datetime(2026, 10, 20), "time": time(16, 0), "ec": 1.020, "ph_before": 6.34, "ph_after": 6.34, "temp": None, "note": ""},
        {"date": datetime(2026, 10, 21), "time": time(8, 0), "ec": 0.990, "ph_before": 6.97, "ph_after": 6.41, "temp": None, "note": ""},
    ],
}

wb = openpyxl.load_workbook(EXCEL_PATH)

# Colors and styles
font_title = Font(name="Kanit", size=14, bold=True, color="1E293B")
font_sub = Font(name="Kanit", size=10, color="475569")
font_header = Font(name="Kanit", size=11, bold=True, color="FFFFFF")
font_data = Font(name="Kanit", size=10, color="0F172A")
font_bold = Font(name="Kanit", size=10, bold=True, color="0F172A")

fill_header = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
fill_zebra = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
fill_yellow = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")

thin_border = Border(
    left=Side(style='thin', color='E2E8F0'),
    right=Side(style='thin', color='E2E8F0'),
    top=Side(style='thin', color='E2E8F0'),
    bottom=Side(style='thin', color='E2E8F0')
)

# -------------------------------------------------------------
# 1. Create individual sheets for each cup: 'แก้ว 1' ถึง 'แก้ว 8'
# -------------------------------------------------------------
for cup_no, group_name, group_code, baseline, formula_desc, acid_desc in CUPS:
    sheet_name = f"แก้ว {cup_no}"
    if sheet_name in wb.sheetnames:
        del wb[sheet_name]
    
    ws = wb.create_sheet(title=sheet_name)
    ws.views.sheetView[0].showGridLines = True

    # Row 1-4 Header
    ws.cell(1, 1, f"แก้วทดลองที่: {cup_no} ({group_name})").font = font_title
    ws.cell(2, 1, f"{formula_desc} | ปรับ pH: {acid_desc}").font = font_sub
    
    ws.cell(4, 1, "Baseline EC (mS/cm) วันแรก:").font = font_bold
    cell_base = ws.cell(4, 2, baseline)
    cell_base.font = font_bold
    cell_base.fill = fill_yellow
    cell_base.alignment = Alignment(horizontal='center')

    # Row 6: Column Headers
    headers = [
        "วันที่", "เวลา", "EC (mS/cm)", "pH ก่อน", "pH หลัง", 
        "อุณหภูมิน้ำ (°C)", "% เปลี่ยนแปลง EC จาก Baseline", 
        "ชื่อไฟล์ภาพ", "หมายเหตุ", "รอบสารละลาย"
    ]
    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(6, col_idx, h)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border
    
    # Rows 7+: Data
    cup_records = DATA.get(cup_no, [])
    for row_idx, rec in enumerate(cup_records, 7):
        ws.cell(row_idx, 1, rec["date"]).alignment = Alignment(horizontal='center')
        ws.cell(row_idx, 1).number_format = 'yyyy-mm-dd'
        
        ws.cell(row_idx, 2, rec["time"]).alignment = Alignment(horizontal='center')
        ws.cell(row_idx, 2).number_format = 'hh:mm'
        
        ws.cell(row_idx, 3, rec["ec"]).alignment = Alignment(horizontal='right')
        ws.cell(row_idx, 4, rec["ph_before"]).alignment = Alignment(horizontal='right')
        ws.cell(row_idx, 5, rec["ph_after"]).alignment = Alignment(horizontal='right')
        ws.cell(row_idx, 6, rec["temp"]).alignment = Alignment(horizontal='right')
        
        # Formula for % EC Change: =(C{row}-B4)/B4
        cell_pct = ws.cell(row_idx, 7, f"=(C{row_idx}-$B$4)/$B$4")
        cell_pct.alignment = Alignment(horizontal='right')
        cell_pct.number_format = '0.00%'

        ws.cell(row_idx, 8, f"Cup{cup_no}_{rec['date'].strftime('%Y%m%d')}_{rec['time'].strftime('%H%M')}.jpg")
        ws.cell(row_idx, 9, rec["note"])
        ws.cell(row_idx, 10, "ชุดแก้ว 750ml")

        for c in range(1, 11):
            ws.cell(row_idx, c).font = font_data
            ws.cell(row_idx, c).border = thin_border

    # Set column widths
    widths = [14, 10, 14, 12, 12, 16, 26, 32, 20, 16]
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w

# -------------------------------------------------------------
# 2. Create Master Summary Sheet for all 8 Cups: 'สรุป 8 แก้ว'
# -------------------------------------------------------------
summary_cup_sheet = "สรุป 8 แก้ว"
if summary_cup_sheet in wb.sheetnames:
    del wb[summary_cup_sheet]

ws_sum = wb.create_sheet(title=summary_cup_sheet)
ws_sum.views.sheetView[0].showGridLines = True

ws_sum.cell(1, 1, "สรุปเปรียบเทียบชุดแก้วทดลอง 750 ml (น้ำดื่มบริสุทธิ์) — 8 แก้ว 4 กลุ่ม").font = font_title
ws_sum.cell(2, 1, "รอบที่ 2 (เริ่ม 20 ต.ค. 2569): แต่ละกลุ่มมี 2 แก้วซ้ำ (Replicate 1 & 2)").font = font_sub

headers_sum = [
    "แก้วที่", "กลุ่มทดลอง", "สูตรอาหาร", "Baseline EC", 
    "EC ล่าสุด", "% เปลี่ยนแปลง EC", "pH ล่าสุด", "อุณหภูมิน้ำ (°C)", "สถานะสารละลาย"
]
for col_idx, h in enumerate(headers_sum, 1):
    c = ws_sum.cell(4, col_idx, h)
    c.font = font_header
    c.fill = fill_header
    c.alignment = Alignment(horizontal='center', vertical='center')
    c.border = thin_border

for r_idx, (cup_no, group_name, group_code, baseline, formula_desc, acid_desc) in enumerate(CUPS, 5):
    last_rec = DATA[cup_no][-1]
    
    ws_sum.cell(r_idx, 1, f"แก้ว {cup_no}").alignment = Alignment(horizontal='center')
    ws_sum.cell(r_idx, 2, group_name).alignment = Alignment(horizontal='left')
    ws_sum.cell(r_idx, 3, formula_desc).alignment = Alignment(horizontal='left')
    
    ws_sum.cell(r_idx, 4, baseline).alignment = Alignment(horizontal='right')
    ws_sum.cell(r_idx, 5, last_rec["ec"]).alignment = Alignment(horizontal='right')
    
    # % diff formula
    c_diff = ws_sum.cell(r_idx, 6, f"=(E{r_idx}-D{r_idx})/D{r_idx}")
    c_diff.alignment = Alignment(horizontal='right')
    c_diff.number_format = '0.00%'
    
    ws_sum.cell(r_idx, 7, last_rec["ph_after"]).alignment = Alignment(horizontal='right')
    ws_sum.cell(r_idx, 8, "-").alignment = Alignment(horizontal='center')
    ws_sum.cell(r_idx, 9, "ปกติ (น้ำดื่ม 750ml)").alignment = Alignment(horizontal='center')

    for c in range(1, 10):
        ws_sum.cell(r_idx, c).font = font_data
        ws_sum.cell(r_idx, c).border = thin_border
        if r_idx % 2 == 0:
            ws_sum.cell(r_idx, c).fill = fill_zebra

sum_widths = [12, 16, 36, 14, 14, 20, 12, 16, 20]
for i, w in enumerate(sum_widths, 1):
    ws_sum.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w

wb.save(EXCEL_PATH)
print(f"✅ Successfully updated {EXCEL_PATH}")
print(f"   - Added 8 Cup sheets: แก้ว 1 ถึง แก้ว 8 (with Temperature column & formulas)")
print(f"   - Added Master Summary sheet: 'สรุป 8 แก้ว'")
