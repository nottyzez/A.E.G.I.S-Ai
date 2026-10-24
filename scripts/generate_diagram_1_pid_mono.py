import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches

os.environ['MPLCONFIGDIR'] = str(Path.cwd() / '.matplotlib_cache')

out_dir = Path("docs/figures")
out_dir.mkdir(parents=True, exist_ok=True)

plt.rcParams['font.sans-serif'] = ['Leelawadee UI', 'TH Sarabun New', 'Tahoma', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(figsize=(14.5, 8.8), dpi=300)
ax.set_xlim(0, 14.5)
ax.set_ylim(0, 8.8)
ax.axis('off')

# Title (International IEEE/Elsevier Format)
fig.text(0.5, 0.95, 'PROCESS & INSTRUMENTATION DIAGRAM (P&ID)',
         fontsize=15, fontweight='bold', ha='center', color='#000000')
fig.text(0.5, 0.91, 'Automated Closed-Loop Nutrient Dosing & Sampling Architecture (ISA-5.1 Standard)',
         fontsize=11, ha='center', color='#333333', style='italic')

# Helper function for ISA-5.1 Solenoid Valve symbol (Two triangles with square actuator)
def draw_solenoid_valve(ax, x, y, width=0.6, height=0.4, tag="SV-101"):
    # Left triangle
    tri_left = patches.Polygon([[x - width/2, y - height/2], [x, y], [x - width/2, y + height/2]],
                               closed=True, ec="#000000", fc="#FFFFFF", lw=1.8, zorder=5)
    # Right triangle
    tri_right = patches.Polygon([[x + width/2, y - height/2], [x, y], [x + width/2, y + height/2]],
                                closed=True, ec="#000000", fc="#FFFFFF", lw=1.8, zorder=5)
    ax.add_patch(tri_left)
    ax.add_patch(tri_right)
    # Solenoid actuator box on top
    act_box = patches.Rectangle((x - 0.18, y + height/2), 0.36, 0.28, ec="#000000", fc="#FFFFFF", lw=1.5, zorder=5)
    ax.add_patch(act_box)
    ax.text(x, y + height/2 + 0.14, "S", fontsize=7.5, fontweight='bold', ha='center', va='center')
    ax.plot([x, x], [y, y + height/2], color="#000000", lw=1.5, zorder=5)
    # Tag
    ax.text(x, y - height/2 - 0.2, tag, fontsize=8, fontweight='bold', ha='center')

# Helper function for ISA-5.1 Pump symbol (Circle with internal triangle)
def draw_isa_pump(ax, x, y, radius=0.4, direction='right', tag="P-101"):
    circle = patches.Circle((x, y), radius, ec="#000000", fc="#FFFFFF", lw=2, zorder=5)
    ax.add_patch(circle)
    # Directional triangle
    r = radius * 0.75
    if direction == 'right':
        pts = [[x - r/2, y - r], [x + r, y], [x - r/2, y + r]]
    elif direction == 'left':
        pts = [[x + r/2, y - r], [x - r, y], [x + r/2, y + r]]
    elif direction == 'up':
        pts = [[x - r, y - r/2], [x, y + r], [x + r, y - r/2]]
    else: # down
        pts = [[x - r, y + r/2], [x, y - r], [x + r, y + r/2]]
    tri = patches.Polygon(pts, closed=True, ec="#000000", fc="#000000", lw=1, zorder=6)
    ax.add_patch(tri)
    ax.text(x, y + radius + 0.22, tag, fontsize=8.5, fontweight='bold', ha='center')

# 1. Main Cultivation Tank DWC (TK-101)
tk_dwc = patches.Rectangle((0.8, 4.3), 4.5, 3.4, ec="#000000", fc="#FAFAFA", lw=2.5)
ax.add_patch(tk_dwc)
ax.text(3.05, 7.35, "TK-101: CULTURE TANK (DWC)\nถังปลูกผักบุ้งจีนระบบน้ำลึก (23.3 L)",
        fontsize=10.5, fontweight='bold', ha='center', va='center')

# Planting Raft (Hatched line)
raft = patches.Rectangle((1.0, 6.2), 4.1, 0.25, ec="#000000", fc="#E0E0E0", lw=1.5, hatch="///")
ax.add_patch(raft)
ax.text(3.05, 6.32, "Floating Styrofoam Raft / แผ่นโฟมปลูกพืช", fontsize=7.5, ha='center', va='center')

# Aeration Stone at bottom
aero = patches.Rectangle((1.5, 4.5), 3.1, 0.25, ec="#000000", fc="#CCCCCC", lw=1.2, hatch="...")
ax.add_patch(aero)
ax.text(3.05, 4.62, "Continuous Air Diffuser / หัวทรายเติมอากาศ (O2)", fontsize=7.5, ha='center', va='center')

# Water Level Line
ax.plot([1.0, 5.1], [5.9, 5.9], color="#000000", lw=1.2, linestyle="-.")
ax.text(4.8, 5.65, "Liquid Level\n23.3 L", fontsize=7.5, ha='right')

# 2. Measuring Cell / Sampling Vessel (V-102)
tk_sample = patches.Rectangle((8.8, 4.3), 4.8, 3.4, ec="#000000", fc="#FAFAFA", lw=2.5)
ax.add_patch(tk_sample)
ax.text(11.2, 7.35, "V-102: SAMPLING & MEASUREMENT CELL\nกระบอกตรวจวัดสารละลายแยกอิสระ",
        fontsize=10.5, fontweight='bold', ha='center', va='center')

# Instrument Bubbles inside Measuring Cell (ISA-5.1 Standards)
probes = [
    (9.6, "pHT\n101", "pH Transmitter\n(GPIO 1 / ADC1_CH0)"),
    (11.2, "AIT\n101", "Conductivity/EC\n(GPIO 2 / ADC1_CH1)"),
    (12.8, "TT\n101", "Temperature DS18B20\n(GPIO 4 / OneWire)")
]
for px, ptag, pdesc in probes:
    p_circ = patches.Circle((px, 5.8), 0.48, ec="#000000", fc="#FFFFFF", lw=1.8, zorder=4)
    ax.add_patch(p_circ)
    ax.plot([px - 0.48, px + 0.48], [5.8, 5.8], color="#000000", lw=1.2, zorder=5) # Division line for bubble
    ax.text(px, 6.0, ptag.split('\n')[0], fontsize=8, fontweight='bold', ha='center', va='center', zorder=6)
    ax.text(px, 5.6, ptag.split('\n')[1], fontsize=7.5, fontweight='bold', ha='center', va='center', zorder=6)
    ax.plot([px, px], [5.32, 4.7], color="#000000", lw=2.5, zorder=4) # Sensor probe stem
    ax.scatter([px], [4.7], s=60, color="#000000", zorder=5) # Probe tip
    ax.text(px, 5.0, pdesc, fontsize=6.8, ha='center', va='top', bbox=dict(boxstyle="square,pad=0.1", fc="#FFFFFF", ec="none"))

# 3. Clean Water Reservoir (TK-103)
tk_clean = patches.Rectangle((8.8, 1.2), 2.2, 1.8, ec="#000000", fc="#FAFAFA", lw=2)
ax.add_patch(tk_clean)
ax.text(9.9, 2.1, "TK-103: CLEAN WATER\nถังน้ำสะอาดล้างโพรบ", fontsize=8.5, fontweight='bold', ha='center', va='center')

# 4. Wastewater Drain Receptor (DR-104)
tk_drain = patches.Rectangle((11.4, 1.2), 2.2, 1.8, ec="#000000", fc="#F5F5F5", lw=2, hatch="//")
ax.add_patch(tk_drain)
ax.text(12.5, 2.1, "DR-104: WASTE RECEPTOR\nถังระบายน้ำทิ้งแยกอิสระ", fontsize=8.5, fontweight='bold', ha='center', va='center')

# 5. Dosing Assembly (TK-105A, B, C)
tk_dosing = patches.Rectangle((0.8, 0.8), 5.8, 2.4, ec="#000000", fc="#FAFAFA", lw=2.2)
ax.add_patch(tk_dosing)
ax.text(3.7, 2.9, "3-STOCK FERTILIZER ASSEMBLY / ชุดจ่ายแม่ปุ๋ยดัดแปลง 3 ขวด",
        fontsize=9.5, fontweight='bold', ha='center')

dosing_bottles = [
    (1.7, "TK-105A (N)\nStock A (Ca+N)\n800mL A + 200mL RO", "DP-101 (GPIO 9)"),
    (3.7, "TK-105B (P)\nHigh-P Formula\n500mL B + H3PO4", "DP-102 (GPIO 10)"),
    (5.7, "TK-105C (K)\nHigh-K Formula\n300mL B + K2SO4", "DP-103 (GPIO 11)")
]
for bx, blabel, bpump in dosing_bottles:
    b_box = patches.Rectangle((bx - 0.85, 1.0), 1.7, 1.6, ec="#000000", fc="#FFFFFF", lw=1.5)
    ax.add_patch(b_box)
    ax.text(bx, 1.9, blabel, fontsize=7.2, ha='center', va='center', fontweight='bold')
    ax.text(bx, 1.25, bpump, fontsize=7, ha='center', va='center', style='italic')

# --- PIPING CONNECTIONS & ACTUATORS (ISA-5.1 FLOW) ---

# Line 1: Inflow Line (TK-101 -> V-102)
ax.plot([5.3, 8.8], [6.6, 6.6], color="#000000", lw=2.5) # Pipe line
draw_isa_pump(ax, 7.05, 6.6, radius=0.38, direction='right', tag="P-101 (Inflow)")
ax.text(7.05, 5.95, "Diaphragm Pump 1 (GPIO 5)\n6,000 ms Active", fontsize=7.5, ha='center', style='italic')

# Line 2: Return Line (V-102 -> TK-101)
ax.plot([8.8, 5.3], [5.2, 5.2], color="#000000", lw=2.5) # Pipe line
draw_isa_pump(ax, 7.05, 5.2, radius=0.38, direction='left', tag="P-102 (Return)")
ax.text(7.05, 4.55, "Diaphragm Pump 2 (GPIO 6)\n7,000 ms Active (100% Recovery)", fontsize=7.5, ha='center', style='italic')

# Line 3: Rinse Line (TK-103 -> V-102)
ax.plot([9.9, 9.9], [3.0, 4.3], color="#000000", lw=2.2)
draw_isa_pump(ax, 9.9, 3.65, radius=0.34, direction='up', tag="P-103 (Rinse)")
ax.text(9.0, 3.65, "GPIO 7\n5,000 ms", fontsize=7.5, ha='right', va='center')

# Line 4: Drain Line (V-102 -> DR-104)
ax.plot([12.5, 12.5], [4.3, 3.0], color="#000000", lw=2.2)
draw_solenoid_valve(ax, 12.5, 3.65, width=0.6, height=0.35, tag="SV-101 (Drain)")
ax.text(13.4, 3.65, "GPIO 8\n6,000 ms", fontsize=7.5, ha='left', va='center')

# Line 5: Dosing Injection Line (Assembly -> TK-101)
ax.plot([3.7, 3.7, 3.05, 3.05], [3.2, 3.7, 3.7, 4.3], color="#000000", lw=2.5)
ax.annotate("", xy=(3.05, 4.3), xytext=(3.05, 3.7),
            arrowprops=dict(arrowstyle="->", color="#000000", lw=2.5))
ax.text(4.4, 3.9, "Peristaltic Dosing Line (Tier 1 & 2 Dosing: 3,000-5,000 ms)", fontsize=8, fontweight='bold')

# Footnote Table / Legend (IEEE Technical Box)
legend_box = patches.Rectangle((0.8, 0.15), 12.8, 0.55, ec="#000000", fc="#FFFFFF", lw=1.2)
ax.add_patch(legend_box)
note_text = (
    "STANDARDS & INTERLOCKS: P&ID conforms to ISA-5.1 / ISO 10628. "
    "Solid Lines = Process Liquid Piping; Dashed Lines = Electrical Signals.\n"
    "CRITICAL SAFETY GUARDS: Maximum Dosing Watchdog = 25,000 ms; "
    "Emergency Cutoff at EC > 2.5 mS/cm or pH < 4.0; Isolated Ca(2+) prevents phosphate precipitation."
)
ax.text(7.2, 0.42, note_text, fontsize=7.8, ha='center', va='center')

plt.tight_layout()
out_path = out_dir / "diagram_1_fluidic_pid_mono.png"
plt.savefig(out_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Successfully generated {out_path} ({os.path.getsize(out_path):,} bytes)")
