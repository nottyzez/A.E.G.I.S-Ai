import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches

os.environ['MPLCONFIGDIR'] = str(Path.cwd() / '.matplotlib_cache')

out_dir = Path("docs/figures")
out_dir.mkdir(parents=True, exist_ok=True)

plt.rcParams['font.sans-serif'] = ['Leelawadee UI', 'TH Sarabun New', 'Tahoma', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(figsize=(15.0, 9.5), dpi=300)
ax.set_xlim(0, 15.0)
ax.set_ylim(0, 9.5)
ax.axis('off')

# Title (International IEEE Engineering Format)
fig.text(0.5, 0.95, 'ELECTRICAL SCHEMATIC & MICROCONTROLLER PINOUT DIAGRAM',
         fontsize=15, fontweight='bold', ha='center', color='#000000')
fig.text(0.5, 0.91, 'ESP32-S3 N16R8 Embedded Controller with Sensor Array, 8-Ch Opto-Isolated Relays, and Power Rails',
         fontsize=11, ha='center', color='#333333', style='italic')

# 1. Microcontroller Block (U-1: ESP32-S3 N16R8)
esp_rect = patches.Rectangle((5.6, 2.5), 3.8, 5.8, ec="#000000", fc="#FAFAFA", lw=2.5)
ax.add_patch(esp_rect)
ax.text(7.5, 8.0, "U-1: ESP32-S3 N16R8\nDual-Core Xtensa LX7 @ 160MHz\nFlash 16MB / PSRAM 8MB",
        fontsize=10.5, fontweight='bold', ha='center', va='center')

# Pin lists on ESP32
left_pins = [
    (7.4, "GPIO 1 (ADC1_CH0)", "pH IN"),
    (5.8, "GPIO 2 (ADC1_CH1)", "EC IN"),
    (4.2, "GPIO 4 (OneWire)", "TEMP IN"),
    (2.8, "Wi-Fi 802.11 b/g/n", "TCP/IP")
]
for py, pnum, pdesc in left_pins:
    ax.plot([5.6, 5.2], [py, py], color="#000000", lw=2)
    ax.text(5.75, py, pnum, fontsize=8, fontweight='bold', va='center')

right_pins = [
    (7.4, "GPIO 5", "RELAY 1 (Sample In)"),
    (6.6, "GPIO 6", "RELAY 2 (Sample Return)"),
    (5.8, "GPIO 7", "RELAY 3 (Probe Rinse)"),
    (5.0, "GPIO 8", "RELAY 4 (Drain Valve)"),
    (4.2, "GPIO 9", "RELAY 5 (Nutrient A)"),
    (3.4, "GPIO 10", "RELAY 6 (Nutrient B)"),
    (2.6, "GPIO 11", "RELAY 7 (Nutrient C)")
]
for py, pnum, pdesc in right_pins:
    ax.plot([9.4, 9.8], [py, py], color="#000000", lw=2)
    ax.text(9.25, py, pnum, fontsize=8, fontweight='bold', ha='right', va='center')

# Left Column: Sensors & Inputs
ax.text(2.6, 8.4, "SENSOR TRANSDUCERS (INPUTS)", fontsize=11.5, fontweight='bold', ha='center')

# S1: pH
s_ph = patches.Rectangle((0.6, 6.8), 4.0, 1.2, ec="#000000", fc="#FFFFFF", lw=1.8)
ax.add_patch(s_ph)
ax.text(2.6, 7.5, "SEN-01: Analog pH Sensor Kit\n0 - 3.3V Output (Calibrated Response)", fontsize=8.5, fontweight='bold', ha='center', va='center')
ax.text(2.6, 7.05, "pH = -8.487 x V + 29.59", fontsize=8, ha='center', style='italic')
ax.plot([4.6, 5.2], [7.4, 7.4], color="#000000", lw=1.8)

# S2: EC
s_ec = patches.Rectangle((0.6, 5.2), 4.0, 1.2, ec="#000000", fc="#FFFFFF", lw=1.8)
ax.add_patch(s_ec)
ax.text(2.6, 5.9, "SEN-02: Analog EC/TDS Probe Kit\n0 - 3.3V Output (Standardized to 25°C)", fontsize=8.5, fontweight='bold', ha='center', va='center')
ax.text(2.6, 5.45, "Moving Median 15 Samples Filter", fontsize=8, ha='center', style='italic')
ax.plot([4.6, 5.2], [5.8, 5.8], color="#000000", lw=1.8)

# S3: Temp
s_temp = patches.Rectangle((0.6, 3.6), 4.0, 1.2, ec="#000000", fc="#FFFFFF", lw=1.8)
ax.add_patch(s_temp)
ax.text(2.6, 4.3, "SEN-03: DS18B20 Digital Temp Probe\nStainless Waterproof Probe (Dallas OneWire)", fontsize=8.5, fontweight='bold', ha='center', va='center')
ax.text(2.6, 3.85, "Pull-up Resistor R1 = 4.7 kOhm to 3.3V", fontsize=8, ha='center', style='italic')
ax.plot([4.6, 5.2], [4.2, 4.2], color="#000000", lw=1.8)

# S4: Camera
s_cam = patches.Rectangle((0.6, 2.0), 4.0, 1.2, ec="#000000", fc="#FFFFFF", lw=1.8)
ax.add_patch(s_cam)
ax.text(2.6, 2.7, "CAM-01: ESP32-S3 CAM (OV5640 5MP)\nTop-down Nadir Canopy Imaging (90°)", fontsize=8.5, fontweight='bold', ha='center', va='center')
ax.text(2.6, 2.25, "JPEG UXGA -> HTTP POST via 2.4GHz Wi-Fi", fontsize=8, ha='center', style='italic')
ax.plot([4.6, 5.2], [2.8, 2.8], color="#000000", lw=1.8, linestyle="--")

# Right Column: Actuator Relay Channels
ax.text(12.3, 8.4, "8-CH RELAY MODULE (OPTO-ISOLATED)", fontsize=11.5, fontweight='bold', ha='center')

relay_items = [
    (7.4, "ACT-01: Diaphragm Pump 1 (Inflow)\n12V DC, 1.5A | Sample to Cell (6s)"),
    (6.6, "ACT-02: Diaphragm Pump 2 (Return)\n12V DC, 1.5A | Cell to Tank (7s)"),
    (5.8, "ACT-03: Diaphragm Pump 3 (Rinse)\n12V DC, 1.2A | Probe Wash (5s)"),
    (5.0, "ACT-04: Solenoid Drain Valve\n12V DC Normally-Closed (NC) (6s)"),
    (4.2, "ACT-05: Peristaltic Pump 1 (Stock A)\n12V DC | High-N Calcium Nitrate"),
    (3.4, "ACT-06: Peristaltic Pump 2 (Stock B)\n12V DC | High-P Phosphoric Acid"),
    (2.6, "ACT-07: Peristaltic Pump 3 (Stock C)\n12V DC | High-K Potassium Sulfate"),
]

for ry, rlabel in relay_items:
    r_box = patches.Rectangle((10.2, ry - 0.3), 4.2, 0.65, ec="#000000", fc="#FFFFFF", lw=1.5)
    ax.add_patch(r_box)
    ax.text(12.3, ry, rlabel, fontsize=7.6, ha='center', va='center', fontweight='bold')
    ax.plot([9.8, 10.2], [ry, ry], color="#000000", lw=1.8)

# Bottom Box: Power Distribution & Ground Topology (PDB)
pdb_rect = patches.Rectangle((0.6, 0.4), 13.8, 1.3, ec="#000000", fc="#FAFAFA", lw=2)
ax.add_patch(pdb_rect)
ax.text(7.5, 1.4, "POWER DISTRIBUTION & ISOLATION TOPOLOGY (PDB)", fontsize=10.5, fontweight='bold', ha='center')
pdb_specs = (
    "• 12V DC Heavy Load Rail (5.0A): Feeds 3x Diaphragms, 3x Peristaltics, 1x Solenoid Valve; Snubber Diodes D1-D7 (1N4007) suppress back EMF.\n"
    "• 5V DC Logic Rail (3.0A): XL4015 DC-DC Buck Converter (Ripple < 30mV); Powers ESP32-S3 VIN, ESP32-S3 CAM, and Relay Optocouplers.\n"
    "• Star Grounding Scheme: Dedicated Analog Ground (AGND) return path isolated from Inductive Load Ground (PGND) to prevent ADC quantization jitter."
)
ax.text(7.5, 0.85, pdb_specs, fontsize=7.8, ha='center', va='center')

plt.tight_layout()
out_path = out_dir / "diagram_2_electronic_wiring_mono.png"
plt.savefig(out_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Successfully generated {out_path} ({os.path.getsize(out_path):,} bytes)")
