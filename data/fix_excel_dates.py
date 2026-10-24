"""
fix_excel_dates.py — Update September dates in hydroponic_log.xlsx to October.
"""
import sys
import io
import os
import openpyxl
from datetime import datetime

try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
except Exception:
    pass

EXCEL_PATH = os.path.join(r"d:\Code มหาปลัย", "Ai มหาปลัย", "dataset_real", "hydroponic_log.xlsx")

wb = openpyxl.load_workbook(EXCEL_PATH)
modified_count = 0

for sheet in wb.sheetnames:
    ws = wb[sheet]
    for r in range(1, ws.max_row + 1):
        for c in range(1, ws.max_column + 1):
            val = ws.cell(r, c).value
            if isinstance(val, datetime) and val.month != 10:
                old_val = val
                new_val = datetime(val.year, 10, val.day, val.hour, val.minute, val.second)
                ws.cell(r, c).value = new_val
                print(f"Sheet '{sheet}' R{r}C{c}: {old_val} -> {new_val}")
                modified_count += 1

wb.save(EXCEL_PATH)
print(f"\n✅ Successfully updated {modified_count} date cells in {EXCEL_PATH} to October.")

