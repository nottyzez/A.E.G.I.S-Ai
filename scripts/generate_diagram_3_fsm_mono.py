import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches

os.environ['MPLCONFIGDIR'] = str(Path.cwd() / '.matplotlib_cache')

out_dir = Path("docs/figures")
out_dir.mkdir(parents=True, exist_ok=True)

plt.rcParams['font.sans-serif'] = ['Leelawadee UI', 'TH Sarabun New', 'Tahoma', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(figsize=(14.5, 9.2), dpi=300)
ax.set_xlim(0, 14.5)
ax.set_ylim(0, 9.2)
ax.axis('off')

# Title (IEEE/Elsevier Standard Flowchart)
fig.text(0.5, 0.95, 'FINITE STATE MACHINE (FSM) OPERATIONAL FLOWCHART',
         fontsize=15, fontweight='bold', ha='center', color='#000000')
fig.text(0.5, 0.91, '6-Phase Sequential Fluidic Control, Multimodal AI Decision, and Hardware Safety Interlocks',
         fontsize=11, ha='center', color='#333333', style='italic')

# Helper function to draw ANSI/IEEE decision diamond
def draw_diamond(ax, cx, cy, w, h, text, subtext=""):
    pts = [[cx, cy + h/2], [cx + w/2, cy], [cx, cy - h/2], [cx - w/2, cy]]
    poly = patches.Polygon(pts, closed=True, ec="#000000", fc="#FAFAFA", lw=2.2, zorder=4)
    ax.add_patch(poly)
    ax.text(cx, cy + 0.15, text, fontsize=9.2, fontweight='bold', ha='center', va='center', zorder=5)
    if subtext:
        ax.text(cx, cy - 0.28, subtext, fontsize=7.5, ha='center', va='center', style='italic', color="#333333", zorder=5)

# FSM Phase blocks
# Row 1 (Top): P1 -> P2 -> P3
p1 = patches.Rectangle((1.0, 7.0), 3.5, 1.4, ec="#000000", fc="#FAFAFA", lw=2.2)
ax.add_patch(p1)
ax.text(2.75, 7.95, "PHASE 1: SAMPLING INFLOW", fontsize=10, fontweight='bold', ha='center')
ax.text(2.75, 7.65, "T_normal = 6,000 ms | Watchdog = 15,000 ms", fontsize=7.5, ha='center', style='italic')
ax.text(2.75, 7.3, "Diaphragm Pump 1 (GPIO 5) active\nDraws sample from 23.3L tank to cell", fontsize=8, ha='center')

p2 = patches.Rectangle((5.5, 7.0), 3.5, 1.4, ec="#000000", fc="#FAFAFA", lw=2.2)
ax.add_patch(p2)
ax.text(7.25, 7.95, "PHASE 2: SETTLING & SENSING", fontsize=10, fontweight='bold', ha='center')
ax.text(7.25, 7.65, "Settling Delay = 3,000 ms (Bubble dissipation)", fontsize=7.5, ha='center', style='italic')
ax.text(7.25, 7.3, "ESP32 reads 15 ADC samples via Median Filter\nComputes EC25 and calibrated pH", fontsize=8, ha='center')

p3 = patches.Rectangle((10.0, 7.0), 3.5, 1.4, ec="#000000", fc="#FAFAFA", lw=2.2)
ax.add_patch(p3)
ax.text(11.75, 7.95, "PHASE 3: SAMPLE RECOVERY", fontsize=10, fontweight='bold', ha='center')
ax.text(11.75, 7.65, "T_normal = 7,000 ms | Watchdog = 15,000 ms", fontsize=7.5, ha='center', style='italic')
ax.text(11.75, 7.3, "Diaphragm Pump 2 (GPIO 6) active\nReturns 100% of tested liquid to tank", fontsize=8, ha='center')

# Connectors Row 1
ax.annotate("", xy=(5.5, 7.7), xytext=(4.5, 7.7), arrowprops=dict(arrowstyle="->", color="#000000", lw=2.5))
ax.annotate("", xy=(10.0, 7.7), xytext=(9.0, 7.7), arrowprops=dict(arrowstyle="->", color="#000000", lw=2.5))
ax.annotate("", xy=(11.75, 6.0), xytext=(11.75, 7.0), arrowprops=dict(arrowstyle="->", color="#000000", lw=2.5))

# Decision Node: AI Diagnosis
draw_diamond(ax, 11.75, 4.8, 3.8, 1.8, "A.E.G.I.S. EVALUATION\nLate-Fusion Prediction", "P_fused = 0.45*P_vis + 0.55*P_sen")

# Row 2 (Middle): P4 Dosing -> P5 Clean Rinse
p4 = patches.Rectangle((5.5, 4.1), 3.5, 1.4, ec="#000000", fc="#FAFAFA", lw=2.2)
ax.add_patch(p4)
ax.text(7.25, 5.05, "PHASE 4: TWO-TIER DOSING", fontsize=10, fontweight='bold', ha='center')
ax.text(7.25, 4.75, "Pulse Duration = 3,000 - 5,000 ms", fontsize=7.5, ha='center', style='italic')
ax.text(7.25, 4.4, "• Tier 1: Priming if EC < 0.8 mS/cm\n• Tier 2: AI doses Pump 1 (-N), 2 (-P), 3 (-K)", fontsize=7.8, ha='center')

p5 = patches.Rectangle((1.0, 4.1), 3.5, 1.4, ec="#000000", fc="#FAFAFA", lw=2.2)
ax.add_patch(p5)
ax.text(2.75, 5.05, "PHASE 5: CLEAN PROBE RINSE", fontsize=10, fontweight='bold', ha='center')
ax.text(2.75, 4.75, "T_normal = 5,000 ms | Watchdog = 10,000 ms", fontsize=7.5, ha='center', style='italic')
ax.text(2.75, 4.4, "Diaphragm Pump 3 (GPIO 7) active\nRinses glass & metal probe residues", fontsize=8, ha='center')

# Connectors Middle
ax.annotate("", xy=(9.0, 4.8), xytext=(9.85, 4.8), arrowprops=dict(arrowstyle="->", color="#000000", lw=2.5))
ax.text(9.4, 5.05, "Deficient / Low EC", fontsize=7.5, fontweight='bold', ha='center')

ax.annotate("", xy=(4.5, 4.8), xytext=(5.5, 4.8), arrowprops=dict(arrowstyle="->", color="#000000", lw=2.5))

# Branch for Healthy (Skip dosing)
ax.plot([11.75, 11.75, 7.25, 7.25], [3.9, 3.4, 3.4, 4.1], color="#000000", lw=1.8, linestyle="--")
ax.text(10.5, 3.55, "Healthy / Balanced -> Bypass Dosing", fontsize=7.5, ha='center', style='italic')

# Row 3 (Bottom): P6 Drain -> Standby Cooldown
p6 = patches.Rectangle((1.0, 1.8), 3.5, 1.4, ec="#000000", fc="#FAFAFA", lw=2.2)
ax.add_patch(p6)
ax.text(2.75, 2.75, "PHASE 6: WASTE DRAIN", fontsize=10, fontweight='bold', ha='center')
ax.text(2.75, 2.45, "T_normal = 6,000 ms | Watchdog = 12,000 ms", fontsize=7.5, ha='center', style='italic')
ax.text(2.75, 2.1, "Solenoid Valve SV-101 (GPIO 8) opens\nDischarges rinse wastewater to receptor", fontsize=8, ha='center')

p_standby = patches.Rectangle((5.5, 1.8), 8.0, 1.4, ec="#000000", fc="#F5F5F5", lw=2.2)
ax.add_patch(p_standby)
ax.text(9.5, 2.75, "SYSTEM STANDBY & COOLDOWN (6 - 12 HOURS)", fontsize=10.5, fontweight='bold', ha='center')
ax.text(9.5, 2.45, "Continuous Aeration Active | Telemetry Upload to DigitalOcean VPS", fontsize=8, ha='center', style='italic')
ax.text(9.5, 2.1, "Allows biological nutrient assimilation; Prevents chemical over-saturation.\nSystem polls for next scheduled cycle or remote operator command.", fontsize=8, ha='center')

# Connectors Bottom
ax.annotate("", xy=(2.75, 3.2), xytext=(2.75, 4.1), arrowprops=dict(arrowstyle="->", color="#000000", lw=2.5))
ax.annotate("", xy=(5.5, 2.5), xytext=(4.5, 2.5), arrowprops=dict(arrowstyle="->", color="#000000", lw=2.5))

# Loop back to Phase 1
ax.annotate("", xy=(1.0, 7.7), xytext=(9.5, 1.8),
            arrowprops=dict(arrowstyle="->", color="#000000", lw=1.8, linestyle="dotted",
                            connectionstyle="arc3,rad=-0.42"))
ax.text(7.5, 0.95, "CYCLE RECURRENCE: Re-initiates automated sampling every 12 hours",
        fontsize=8.5, fontweight='bold', ha='center')

# Safety Guard Legend
guard_box = patches.Rectangle((1.0, 0.25), 12.5, 0.55, ec="#000000", fc="#FFFFFF", lw=1.2)
ax.add_patch(guard_box)
guard_str = (
    "HARDWARE SAFETY GUARDS: 1) MAX_SAFETY_DOSING_MS = 25,000 ms (Hard Watchdog Cutoff); "
    "2) HARD_MAX_EC = 2.5 mS/cm & HARD_MIN_PH = 4.0 (Emergency Abort);\n"
    "3) Non-blocking Finite State Machine (millis() architecture) prevents CPU hangup; "
    "4) Boot-Glitch Lockout on all relay GPIOs."
)
ax.text(7.25, 0.52, guard_str, fontsize=7.8, ha='center', va='center')

plt.tight_layout()
out_path = out_dir / "diagram_3_fsm_flowchart_mono.png"
plt.savefig(out_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Successfully generated {out_path} ({os.path.getsize(out_path):,} bytes)")
