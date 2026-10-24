import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches

os.environ['MPLCONFIGDIR'] = str(Path.cwd() / '.matplotlib_cache')

out_dir = Path("docs/figures")
out_dir.mkdir(parents=True, exist_ok=True)

plt.rcParams['font.sans-serif'] = ['Leelawadee UI', 'TH Sarabun New', 'Tahoma', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(figsize=(15, 9.5), dpi=300)
ax.set_xlim(0, 15)
ax.set_ylim(0, 9.5)
ax.axis('off')

# Title
fig.text(0.5, 0.95, 'แผนผังการเชื่อมต่อวงจรอิเล็กทรอนิกส์และพินเอาต์ (Electronic Pinout & Wiring Diagram)',
         fontsize=16, fontweight='bold', ha='center', color='#1A237E')
fig.text(0.5, 0.91, 'บอร์ดควบคุมหลัก ESP32-S3 N16R8 ร่วมกับโมดูลเซนเซอร์ รีเลย์ 8 ช่องสัญญาณ และภาคจ่ายไฟ PDB',
         fontsize=12, ha='center', color='#455A64')

# 1. Central Microcontroller (ESP32-S3)
esp_box = patches.FancyBboxPatch((5.5, 2.5), 4.0, 5.8, boxstyle="round,pad=0.2",
                                ec="#1565C0", fc="#E3F2FD", lw=3)
ax.add_patch(esp_box)
ax.text(7.5, 8.0, "ไมโครคอนโทรลเลอร์ ESP32-S3\n(N16R8: Flash 16MB / PSRAM 8MB)",
        fontsize=12, fontweight='bold', ha='center', va='center', color="#0D47A1")

# Left Column: Sensors & Inputs
ax.text(2.5, 8.3, "เซนเซอร์ตรวจวัด (Sensor Inputs)", fontsize=13, fontweight='bold', ha='center', color="#00695C")

# Sensor 1: pH
s_ph = patches.FancyBboxPatch((0.6, 6.8), 3.8, 1.2, boxstyle="round,pad=0.1", ec="#E91E63", fc="#FCE4EC", lw=2)
ax.add_patch(s_ph)
ax.text(2.5, 7.5, "โพรบวัดค่าความเป็นกรด-ด่าง (pH Sensor Kit)\nสัญญาณแอนะล็อก 0 - 3.3V (ADC1)", fontsize=9.5, fontweight='bold', ha='center', va='center', color="#AD1457")
ax.text(2.5, 7.05, "pH = -8.487 x V + 29.59", fontsize=8.5, ha='center', color="#C2185B", style='italic')

# Sensor 2: EC
s_ec = patches.FancyBboxPatch((0.6, 5.2), 3.8, 1.2, boxstyle="round,pad=0.1", ec="#00897B", fc="#E0F2F1", lw=2)
ax.add_patch(s_ec)
ax.text(2.5, 5.9, "โพรบวัดค่าการนำไฟฟ้า (Analog EC/TDS)\nสัญญาณแอนะล็อก 0 - 3.3V (ADC1)", fontsize=9.5, fontweight='bold', ha='center', va='center', color="#004D40")
ax.text(2.5, 5.45, "Moving Median 15 ตัวอย่าง + ชดเชยอุณหภูมิ 25°C", fontsize=8.5, ha='center', color="#00695C", style='italic')

# Sensor 3: Temp
s_temp = patches.FancyBboxPatch((0.6, 3.6), 3.8, 1.2, boxstyle="round,pad=0.1", ec="#FB8C00", fc="#FFF3E0", lw=2)
ax.add_patch(s_temp)
ax.text(2.5, 4.3, "เซนเซอร์อุณหภูมิของเหลว DS18B20\n(Stainless Waterproof Probe)", fontsize=9.5, fontweight='bold', ha='center', va='center', color="#E65100")
ax.text(2.5, 3.85, "บัส OneWire (Digital) พร้อม Pull-up 4.7 kOhm", fontsize=8.5, ha='center', color="#EF6C00", style='italic')

# Sensor 4: Camera Module
s_cam = patches.FancyBboxPatch((0.6, 2.0), 3.8, 1.2, boxstyle="round,pad=0.1", ec="#5E35B1", fc="#EDE7F6", lw=2)
ax.add_patch(s_cam)
ax.text(2.5, 2.7, "โมดูลกล้อง ESP32-S3 CAM (OV5640 5MP)\nถ่ายภาพมุมสูงพุ่มใบแนวดิ่ง 90° (Nadir View)", fontsize=9.5, fontweight='bold', ha='center', va='center', color="#4527A0")
ax.text(2.5, 2.25, "เชื่อมต่อคลาวด์ผ่าน HTTP POST / Wi-Fi 2.4GHz", fontsize=8.5, ha='center', color="#512DA8", style='italic')

# Wires from Sensors to ESP32
ax.annotate("", xy=(5.5, 7.4), xytext=(4.4, 7.4), arrowprops=dict(arrowstyle="->", color="#E91E63", lw=2.5))
ax.text(4.95, 7.6, "GPIO 1", fontsize=9, fontweight='bold', color="#E91E63", ha='center')

ax.annotate("", xy=(5.5, 5.8), xytext=(4.4, 5.8), arrowprops=dict(arrowstyle="->", color="#00897B", lw=2.5))
ax.text(4.95, 6.0, "GPIO 2", fontsize=9, fontweight='bold', color="#00897B", ha='center')

ax.annotate("", xy=(5.5, 4.2), xytext=(4.4, 4.2), arrowprops=dict(arrowstyle="->", color="#FB8C00", lw=2.5))
ax.text(4.95, 4.4, "GPIO 4", fontsize=9, fontweight='bold', color="#FB8C00", ha='center')

ax.annotate("", xy=(5.5, 2.6), xytext=(4.4, 2.6), arrowprops=dict(arrowstyle="<->", color="#5E35B1", lw=2.5))
ax.text(4.95, 2.8, "Wi-Fi LAN", fontsize=8.5, fontweight='bold', color="#5E35B1", ha='center')

# Right Column: Relay Module & Actuators
ax.text(12.5, 8.3, "หน่วยปฏิบัติงานและรีเลย์ 8 ช่อง (Actuators)", fontsize=13, fontweight='bold', ha='center', color="#C62828")

relay_items = [
    (7.4, "Ch 1: ปั๊มไดอะแฟรม 1 (GPIO 5)\nดึงน้ำเข้ากระบอกวัด (Sample In)", "#1565C0"),
    (6.6, "Ch 2: ปั๊มไดอะแฟรม 2 (GPIO 6)\nดูดน้ำส่งคืนถังปลูก (Sample Return)", "#2E7D32"),
    (5.8, "Ch 3: ปั๊มไดอะแฟรม 3 (GPIO 7)\nฉีดน้ำสะอาดล้างโพรบ (Probe Rinse)", "#00838F"),
    (5.0, "Ch 4: โซลินอยด์วาล์ว 12V (GPIO 8)\nเปิดระบายน้ำทิ้ง (Drain Valve)", "#D32F2F"),
    (4.2, "Ch 5: ปั๊มรีดสาย 1 (GPIO 9)\nจ่ายปุ๋ยขวดที่ 1 (สูตรแก้พร่อง N)", "#E65100"),
    (3.4, "Ch 6: ปั๊มรีดสาย 2 (GPIO 10)\nจ่ายปุ๋ยขวดที่ 2 (สูตรแก้พร่อง P)", "#689F38"),
    (2.6, "Ch 7: ปั๊มรีดสาย 3 (GPIO 11)\nจ่ายปุ๋ยขวดที่ 3 (สูตรแก้พร่อง K)", "#0288D1"),
]

for ry, rtext, rcolor in relay_items:
    r_patch = patches.FancyBboxPatch((10.5, ry - 0.3), 4.0, 0.65, boxstyle="round,pad=0.08",
                                     ec=rcolor, fc="#FAFAFA", lw=1.8)
    ax.add_patch(r_patch)
    ax.text(12.5, ry, rtext, fontsize=8.5, ha='center', va='center', color=rcolor, fontweight='bold')
    
    # Wire from ESP32 to Relay
    ax.annotate("", xy=(10.5, ry), xytext=(9.5, ry), arrowprops=dict(arrowstyle="->", color=rcolor, lw=2))

# Bottom Box: Power Distribution Board (PDB)
pdb_box = patches.FancyBboxPatch((0.6, 0.4), 13.8, 1.2, boxstyle="round,pad=0.1",
                                ec="#37474F", fc="#ECEFF1", lw=2)
ax.add_patch(pdb_box)
ax.text(7.5, 1.15, "ระบบการกระจายพลังงานไฟฟ้าและการป้องกันความปลอดภัย (Power Distribution & Isolation: PDB)",
        fontsize=10.5, fontweight='bold', ha='center', color="#263238")
pdb_desc = (
    "• แหล่งจ่ายไฟ 12V DC (5A): เลี้ยงมอเตอร์ปั๊มไดอะแฟรม 3 ตัว, ปั๊มรีดสาย 3 ตัว, โซลินอยด์วาล์ว โดยต่อ Flyback Diode (1N4007) ป้องกัน Back EMF\n"
    "• รางจ่ายไฟ 5V DC (3A): สเต็ปดาวน์ผ่าน Buck Converter (XL4015) จ่ายเลี้ยงบอร์ด ESP32-S3 และบอร์ดกล้อง พร้อมคาปาซิเตอร์ฟิลเตอร์ 1000 µF\n"
    "• การแยกรางกราวด์: แยก Power Ground ออกจาก Analog Signal Ground เพื่อขจัดสัญญาณรบกวนในวงจรแปลงแอนะล็อกเป็นดิจิทัล (ADC)"
)
ax.text(7.5, 0.65, pdb_desc, fontsize=8.5, ha='center', va='center', color="#37474F")

plt.tight_layout()
out_path = out_dir / "diagram_2_electronic_wiring.png"
plt.savefig(out_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Successfully generated {out_path} ({os.path.getsize(out_path):,} bytes)")
