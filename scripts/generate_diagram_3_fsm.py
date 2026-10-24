import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches

os.environ['MPLCONFIGDIR'] = str(Path.cwd() / '.matplotlib_cache')

out_dir = Path("docs/figures")
out_dir.mkdir(parents=True, exist_ok=True)

plt.rcParams['font.sans-serif'] = ['Leelawadee UI', 'TH Sarabun New', 'Tahoma', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(figsize=(14, 9.0), dpi=300)
ax.set_xlim(0, 14)
ax.set_ylim(0, 9.0)
ax.axis('off')

# Title
fig.text(0.5, 0.95, 'ผังลำดับขั้นตอนการทำงานเครื่องจักรสถานะจำกัด 6 ขั้นตอน (6-Phase Operational FSM)',
         fontsize=16, fontweight='bold', ha='center', color='#1A237E')
fig.text(0.5, 0.91, 'กลไกควบคุมของไหล การตรวจวัดสารละลาย และการจ่ายแม่ปุ๋ยอัตโนมัติแบบวงปิดสองระดับ (Two-Tier Closed-Loop)',
         fontsize=12, ha='center', color='#455A64')

# Nodes coordinates & definitions
# Flow: P1 -> P2 -> P3 -> AI Decision -> P4 Dosing -> P5 Rinse -> P6 Drain -> Cooldown
phases = [
    # (x, y, w, h, title, time_info, desc, color_border, color_bg)
    (1.5, 7.3, 3.2, 1.2, "Phase 1: สุ่มตัวอย่างน้ำเข้า\n(Sampling Inflow)", "เวลาปกติ: 6 วินาที | Watchdog: 15 วินาที",
     "ปั๊มไดอะแฟรม 1 (GPIO 5) ดูดสารละลาย\nจากถังปลูก 23.3L เข้าสู่กระบอกวัด", "#1565C0", "#E3F2FD"),
    
    (5.4, 7.3, 3.2, 1.2, "Phase 2: หน่วงเวลาน้ำนิ่ง & วัดผล\n(Settling & Measurement)", "เวลาปกติ: 3 วินาที (รอฟองอากาศสลาย)",
     "ESP32 อ่านค่า ADC ผ่าน Moving Median\nคำนวณ pH Calibrated และ EC ชดเชย 25°C", "#7B1FA2", "#F3E5F5"),
     
    (9.3, 7.3, 3.2, 1.2, "Phase 3: ดูดน้ำคืนถังปลูก\n(Sample Return)", "เวลาปกติ: 7 วินาที | Watchdog: 15 วินาที",
     "ปั๊มไดอะแฟรม 2 (GPIO 6) สูบสารละลาย\nกลับคืนถังปลูก 100% ไม่สูญเสียปุ๋ย", "#2E7D32", "#E8F5E9"),
     
    (9.3, 4.8, 3.2, 1.4, "AI Decision: การวินิจฉัยธาตุอาหาร\n(A.E.G.I.S. Multimodal Late-Fusion)", "ความแม่นยำ 100% (Alpha 0.45, Beta 0.55)",
     "วิเคราะห์ภาพพุ่มใบ (Stream A: 95.12%)\nร่วมกับแนวโน้มไอออนเซนเซอร์ (Stream B: 97.56%)", "#E65100", "#FFF3E0"),
     
    (5.4, 4.8, 3.2, 1.4, "Phase 4: จ่ายปุ๋ยชดเชยสองระดับ\n(Two-Tier Nutrient Dosing)", "เวลาปกติ: 3 – 5 วินาที | Max Guard: 25 วินาที",
     "• Tier 1: ปูพื้นฐานสารละลาย (EC < 0.8)\n• Tier 2: สั่งปั๊มรีดสาย 1, 2, 3 (-N, -P, -K)", "#C2185B", "#FCE4EC"),
     
    (1.5, 4.8, 3.2, 1.4, "Phase 5: ฉีดน้ำสะอาดล้างโพรบ\n(Clean Probe Rinse)", "เวลาปกติ: 5 วินาที | Watchdog: 10 วินาที",
     "ปั๊มไดอะแฟรม 3 (GPIO 7) ดูดน้ำสะอาด\nชะล้างคราบเกลือตกผลึกบนโพรบวัด", "#00838F", "#E0F7FA"),
     
    (1.5, 2.2, 3.2, 1.3, "Phase 6: ระบายน้ำล้างทิ้ง\n(Wastewater Drain)", "เวลาปกติ: 6 วินาที | Watchdog: 12 วินาที",
     "โซลินอยด์วาล์ว 12V (GPIO 8) เปิดปล่อย\nน้ำล้างทิ้งลงถังน้ำเสีย ไม่ให้เจือจางถังปลูก", "#D32F2F", "#FFEBEE"),
     
    (5.4, 2.2, 7.1, 1.3, "Phase Ready: เข้าสู่ระยะพักตัวและติดตามผล\n(Standby & Cooldown)", "ระยะหน่วงเวลา Cooldown: 6 – 12 ชั่วโมง",
     "เปิดปั๊มลมเติมออกซิเจนตลอด 24 ชม. ให้พืชดูดซึมธาตุอาหารจนเต็มที่\nและส่งข้อมูลโทรมาตรขึ้นระบบ Cloud Dashboard / 3D Digital Twin แบบเรียลไทม์", "#37474F", "#ECEFF1")
]

# Draw boxes
for px, py, pw, ph, ptitle, psub, pdesc, bcolor, bgcolor in phases:
    box = patches.FancyBboxPatch((px, py), pw, ph, boxstyle="round,pad=0.12",
                                ec=bcolor, fc=bgcolor, lw=2.2)
    ax.add_patch(box)
    ax.text(px + pw/2, py + ph - 0.28, ptitle, fontsize=10, fontweight='bold', ha='center', color=bcolor)
    ax.text(px + pw/2, py + ph - 0.65, psub, fontsize=8, ha='center', color="#424242", style='italic')
    ax.text(px + pw/2, py + 0.25, pdesc, fontsize=8.5, ha='center', va='center', color="#212121")

# Connecting Arrows
# P1 -> P2
ax.annotate("", xy=(5.4, 7.9), xytext=(4.7, 7.9), arrowprops=dict(arrowstyle="->", color="#1565C0", lw=3))
# P2 -> P3
ax.annotate("", xy=(9.3, 7.9), xytext=(8.6, 7.9), arrowprops=dict(arrowstyle="->", color="#7B1FA2", lw=3))
# P3 -> AI Decision
ax.annotate("", xy=(10.9, 6.2), xytext=(10.9, 7.3), arrowprops=dict(arrowstyle="->", color="#2E7D32", lw=3))
# AI Decision -> P4 Dosing
ax.annotate("", xy=(8.6, 5.5), xytext=(9.3, 5.5), arrowprops=dict(arrowstyle="->", color="#E65100", lw=3))
# P4 Dosing -> P5 Rinse
ax.annotate("", xy=(4.7, 5.5), xytext=(5.4, 5.5), arrowprops=dict(arrowstyle="->", color="#C2185B", lw=3))
# P5 Rinse -> P6 Drain
ax.annotate("", xy=(3.1, 3.5), xytext=(3.1, 4.8), arrowprops=dict(arrowstyle="->", color="#00838F", lw=3))
# P6 Drain -> Standby
ax.annotate("", xy=(5.4, 2.85), xytext=(4.7, 2.85), arrowprops=dict(arrowstyle="->", color="#D32F2F", lw=3))
# Standby loop back to P1
ax.annotate("", xy=(1.5, 7.9), xytext=(8.95, 2.2),
            arrowprops=dict(arrowstyle="->", color="#37474F", lw=2, linestyle="dashed",
                            connectionstyle="arc3,rad=-0.45"))
ax.text(7.5, 0.95, "[CYCLE] เริ่มรอบการทำงานอัตโนมัติรอบถัดไป (Scheduled Cycle ทุก 12 ชั่วโมง)",
        fontsize=9, fontweight='bold', ha='center', color="#37474F")

# Safety Interlock Guard Banner
guard_text = (
    "[SAFETY] HARDWARE SAFETY INTERLOCK GUARDRAILS:\n"
    "• Hard Max Dosing Watchdog: ตัดไฟปั๊มปุ๋ยทุกตัวทันทีหากทำงานเกิน 25 วินาที (`MAX_SAFETY_DOSING_MS = 25000`)\n"
    "• Emergency Acid/Osmotic Cutoff: ล็อกระบบทันทีหากตรวจพบ `EC > 2.5 mS/cm` หรือ `pH < 4.0`\n"
    "• Boot-Glitch Lockout: กำหนดสถานะ LOW ก่อนเปิดใช้โหมด Output เพื่อป้องกันไฟกระชากสั่งงานรีเลย์ขณะเปิดสวิตช์"
)
ax.text(7.0, 0.45, guard_text, fontsize=8.5, ha='center', va='center',
        bbox=dict(boxstyle="round,pad=0.4", fc="#FFFDE7", ec="#FBC02D", lw=1.5))

plt.tight_layout()
out_path = out_dir / "diagram_3_fsm_flowchart.png"
plt.savefig(out_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Successfully generated {out_path} ({os.path.getsize(out_path):,} bytes)")
