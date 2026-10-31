# Hardware Pinout Synchronization & Sensor Calibration Specs Plan

**Date:** 2026-10-31  
**Goal:** Synchronize all pinouts, relay mappings, and sensor calibration formulas across `main.py`, `server/static/index.html`, and test suites according to the official hardware specification table:
- **Sensors:**
  - `GPIO 1`: Analog pH Kit (ADC1_CH0, `pH = -8.487V + 29.59`)
  - `GPIO 2`: Analog EC/TDS Probe (ADC1_CH1, Temp compensated to 25°C)
  - `GPIO 4`: DS18B20 Temp Probe (OneWire, Pull-up 4.7kΩ)
- **Fluidic Control (Relays 1–4):**
  - `R1`: Diaphragm Pump 1 (Inflow, GPIO 5, 6s)
  - `R2`: Diaphragm Pump 2 (Return, GPIO 6, 7s)
  - `R3`: Diaphragm Pump 3 (Rinse, GPIO 7, 5s)
  - `R4`: Solenoid Valve (Drain, GPIO 8, 6s)
- **Dosing Pumps (Relays 5–7):**
  - `R5`: Peristaltic 1 (Stock A: High-N / Calcium Nitrate, GPIO 9)
  - `R6`: Peristaltic 2 (Stock B: High-P / Phosphoric Acid, GPIO 10)
  - `R7`: Peristaltic 3 (Stock C: High-K / Potassium Sulfate, GPIO 11)

### Tasks:
1. Update `main.py`:
   - Map `MANUAL_DOSE` active pumps to `[5, 6, 7]` instead of `[1, 2, 3]`.
   - Update `PHASE_LABELS` and command logging descriptions.
2. Update `server/static/index.html`:
   - Update `relays` array in `ElectronicControlTabView` with the exact names, pins `GPIO 5–11`, roles, and spec default durations (`6s, 7s, 5s, 6s, 10s, 10s, 10s`).
   - Add "สเปกฮาร์ดแวร์ (Spec Defaults)" preset button to the pulse selector.
   - Add "ESP32-S3 Hardware Pinout & Calibration Specifications" card displaying GPIO 1, 2, 4 with the linear pH formula `pH = -8.487V + 29.59`.
   - Update phase jump relay highlights for the 6-phase pipeline.
3. Update `tests/test_presentation_override.py` and run full regression suite (`verify_figma_implementation.py`, `test_dashboard_e2e.py`).
