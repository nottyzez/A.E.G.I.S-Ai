import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Set MPLCONFIGDIR to avoid warning
os.environ['MPLCONFIGDIR'] = str(Path.cwd() / '.matplotlib_cache')

out_dir = Path("docs/figures")
out_dir.mkdir(parents=True, exist_ok=True)

plt.rcParams['font.sans-serif'] = ['Leelawadee UI', 'TH Sarabun New', 'Tahoma', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(figsize=(14, 8.5), dpi=300)
ax.set_xlim(0, 14)
ax.set_ylim(0, 8.5)
ax.axis('off')

# Title
fig.text(0.5, 0.94, 'ผังกลศาสตร์ของไหลและระบบท่อควบคุมการจ่ายธาตุอาหาร (Fluidic P&ID Diagram)',
         fontsize=16, fontweight='bold', ha='center', color='#1A237E')
fig.text(0.5, 0.90, 'ระบบ A.E.G.I.S. ไฮโดรโปนิกส์ผักบุ้งจีนแบบน้ำลึก (Deep Water Culture: DWC 23.3 ลิตร)',
         fontsize=12, ha='center', color='#455A64')

# 1. Main Tank DWC
main_tank = patches.FancyBboxPatch((0.8, 4.5), 4.5, 3.2, boxstyle="round,pad=0.15",
                                   ec="#0288D1", fc="#E1F5FE", lw=2.5)
ax.add_patch(main_tank)
ax.text(3.05, 7.3, "ถังปลูกหลัก DWC (Culture Tank)\nความจุ 23.3 ลิตร", fontsize=12,
        fontweight='bold', ha='center', va='center', color="#01579B")

# Plants in DWC
for x_pos in [1.6, 2.6, 3.6, 4.5]:
    ax.plot([x_pos, x_pos], [6.2, 6.7], color="#388E3C", lw=3)
    ax.scatter([x_pos], [6.8], s=250, color="#4CAF50", zorder=4)
ax.plot([1.0, 5.1], [6.2, 6.2], color="#795548", lw=3.5, label="แผ่นโฟมปลูกพืช")
ax.text(3.05, 5.2, "สารละลายธาตุอาหารสมบูรณ์\n(หรือน้ำเปล่าในระยะเริ่มต้น)",
        fontsize=10, ha='center', color="#0277BD", style='italic')

# 2. Measuring Cup (Sampling Cell)
measuring_cell = patches.FancyBboxPatch((8.8, 4.5), 4.4, 3.2, boxstyle="round,pad=0.15",
                                        ec="#7B1FA2", fc="#F3E5F5", lw=2.5)
ax.add_patch(measuring_cell)
ax.text(11.0, 7.3, "กระบอกตรวจวัดสารละลาย (Sampling Cell)\nแยกอิสระจากถังปลูก",
        fontsize=12, fontweight='bold', ha='center', va='center', color="#4A148C")

# Probes inside measuring cell
probes = [
    (9.4, "pH Probe\n(GPIO 1)", "#E91E63"),
    (11.0, "EC/TDS Probe\n(GPIO 2)", "#009688"),
    (12.6, "DS18B20 Temp\n(GPIO 4)", "#FF9800")
]
for px, plabel, pcol in probes:
    probe_rect = patches.Rectangle((px - 0.45, 5.0), 0.9, 1.6, ec=pcol, fc="#FFFFFF", lw=1.8, zorder=3)
    ax.add_patch(probe_rect)
    ax.text(px, 5.8, plabel, fontsize=8.5, fontweight='bold', ha='center', va='center', color=pcol)

# 3. Rinse Water Reservoir
clean_tank = patches.FancyBboxPatch((8.8, 1.2), 2.0, 1.8, boxstyle="round,pad=0.1",
                                    ec="#00ACC1", fc="#E0F7FA", lw=2)
ax.add_patch(clean_tank)
ax.text(9.8, 2.1, "ถังน้ำสะอาดสำรอง\n(Clean Rinse Water)", fontsize=9.5, fontweight='bold',
        ha='center', va='center', color="#006064")

# 4. Wastewater Drain Tank
waste_tank = patches.FancyBboxPatch((11.4, 1.2), 1.8, 1.8, boxstyle="round,pad=0.1",
                                    ec="#757575", fc="#EEEEEE", lw=2)
ax.add_patch(waste_tank)
ax.text(12.3, 2.1, "ถังระบายน้ำทิ้ง\n(Drain Waste)", fontsize=9.5, fontweight='bold',
        ha='center', va='center', color="#424242")

# 5. Dosing Bottles (3 Bottles Assembly)
dosing_box = patches.FancyBboxPatch((0.8, 0.8), 5.5, 2.4, boxstyle="round,pad=0.15",
                                    ec="#E65100", fc="#FFF3E0", lw=2.5)
ax.add_patch(dosing_box)
ax.text(3.55, 2.8, "ชุดขวดแม่ปุ๋ยดัดแปลง 3 ขวด (3-Stock Fertilizer Assembly)",
        fontsize=11, fontweight='bold', ha='center', color="#BF360C")

bottles = [
    (1.7, "ขวดที่ 1 (GPIO 9)\nStock A (Ca+N)\n800mL A + 200mL RO", "#D32F2F"),
    (3.55, "ขวดที่ 2 (GPIO 10)\nHigh-P Formula\n500mL B + H3PO4", "#388E3C"),
    (5.4, "ขวดที่ 3 (GPIO 11)\nHigh-K Formula\n300mL B + K2SO4", "#1976D2")
]
for bx, blabel, bcol in bottles:
    b_patch = patches.FancyBboxPatch((bx - 0.75, 1.0), 1.5, 1.5, boxstyle="round,pad=0.08",
                                     ec=bcol, fc="#FFFFFF", lw=1.5)
    ax.add_patch(b_patch)
    ax.text(bx, 1.75, blabel, fontsize=8, ha='center', va='center', color=bcol, fontweight='bold')

# PIPING & PUMPS (Arrows & Annotations)

# Line 1: Sampling Inflow (Tank -> Measuring Cup)
ax.annotate("", xy=(8.8, 6.7), xytext=(5.3, 6.7),
            arrowprops=dict(arrowstyle="->", color="#1565C0", lw=3))
pump1_box = patches.Circle((7.0, 6.7), 0.45, ec="#1565C0", fc="#BBDEFB", lw=2, zorder=5)
ax.add_patch(pump1_box)
ax.text(7.0, 6.7, "P1", fontsize=10, fontweight='bold', ha='center', va='center', color="#0D47A1", zorder=6)
ax.text(7.0, 7.35, "ปั๊มไดอะแฟรม 1 (GPIO 5)\nดึงน้ำเข้าวัด (6 วินาที)", fontsize=8.5,
        ha='center', color="#0D47A1", fontweight='bold')

# Line 2: Sample Return (Measuring Cup -> Tank)
ax.annotate("", xy=(5.3, 5.5), xytext=(8.8, 5.5),
            arrowprops=dict(arrowstyle="->", color="#2E7D32", lw=3))
pump2_box = patches.Circle((7.0, 5.5), 0.45, ec="#2E7D32", fc="#C8E6C9", lw=2, zorder=5)
ax.add_patch(pump2_box)
ax.text(7.0, 5.5, "P2", fontsize=10, fontweight='bold', ha='center', va='center', color="#1B5E20", zorder=6)
ax.text(7.0, 4.85, "ปั๊มไดอะแฟรม 2 (GPIO 6)\nสูบน้ำคืนถัง 100% (7 วินาที)", fontsize=8.5,
        ha='center', color="#1B5E20", fontweight='bold')

# Line 3: Clean Rinse Inflow (Clean Tank -> Measuring Cup)
ax.annotate("", xy=(10.0, 4.5), xytext=(10.0, 3.0),
            arrowprops=dict(arrowstyle="->", color="#00838F", lw=2.5))
pump3_box = patches.Circle((10.0, 3.75), 0.35, ec="#00838F", fc="#B2EBF2", lw=1.8, zorder=5)
ax.add_patch(pump3_box)
ax.text(10.0, 3.75, "P3", fontsize=9, fontweight='bold', ha='center', va='center', color="#006064", zorder=6)
ax.text(8.9, 3.75, "ปั๊ม 3 (GPIO 7)\nฉีดล้างโพรบ", fontsize=8, ha='right', va='center', color="#006064")

# Line 4: Wastewater Drain (Measuring Cup -> Waste Tank)
ax.annotate("", xy=(12.3, 3.0), xytext=(12.3, 4.5),
            arrowprops=dict(arrowstyle="->", color="#D32F2F", lw=2.5))
valve_box = patches.Rectangle((11.95, 3.5), 0.7, 0.5, ec="#D32F2F", fc="#FFCDD2", lw=1.8, zorder=5)
ax.add_patch(valve_box)
ax.text(12.3, 3.75, "VALVE", fontsize=7.5, fontweight='bold', ha='center', va='center', color="#B71C1C", zorder=6)
ax.text(13.4, 3.75, "โซลินอยด์วาล์ว\n(GPIO 8 - Drain)", fontsize=8, ha='left', va='center', color="#B71C1C")

# Line 5: Fertilizer Dosing lines (Dosing box -> DWC Tank)
ax.annotate("", xy=(3.05, 4.5), xytext=(3.55, 3.2),
            arrowprops=dict(arrowstyle="->", color="#E65100", lw=3, connectionstyle="arc3,rad=-0.2"))
ax.text(2.3, 3.7, "ปั๊มรีดสาย 1, 2, 3 จ่ายปุ๋ย\nตามการวินิจฉัยของ AI (3-5 วินาที)",
        fontsize=9, fontweight='bold', ha='right', color="#E65100")

# Legend / Note at bottom
legend_text = (
    "• ระบบควบคุมแบบวงปิดสองระดับ (Two-Tier Closed-Loop Actuation): "
    "Tier 1 เติมปุ๋ยพื้นฐานเมื่อ EC < 0.8 mS/cm | Tier 2 AI A.E.G.I.S. เติมปุ๋ยจำเพาะ (-N, -P, -K)\n"
    "• กลไกความปลอดภัยระดับฮาร์ดแวร์: Watchdog Cutoff ปั๊มปุ๋ยสูงสุดไม่เกิน 25 วินาที | ล็อกระบบทันทีหาก EC > 2.5 mS/cm หรือ pH < 4.0"
)
ax.text(7.0, 0.3, legend_text, fontsize=9, ha='center', va='center',
        bbox=dict(boxstyle="square,pad=0.4", fc="#FAFAFA", ec="#BDBDBD", lw=1))

plt.tight_layout()
out_path = out_dir / "diagram_1_fluidic_pid.png"
plt.savefig(out_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Successfully generated {out_path} ({os.path.getsize(out_path):,} bytes)")
