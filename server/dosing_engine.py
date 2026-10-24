"""
dosing_engine.py — Two-Factor Precision AI Nutrient Dosing & Priming Compensation Engine
Architecture:
  - Factor 1 (Total Volume V_total): Calculated from EC deficit (ΔEC = max(0, EC_target - EC_current))
    and tank volume (V_tank), ensuring total ionic concentration precisely meets target without overdose.
  - Factor 2 (Nutrient Ratio r1, r2, r3): AI Multimodal classification determines proportion (sums to 100%):
      * Healthy/Control: 33.33% : 33.33% : 33.33%
      * Early Warning: 45.0% (deficient) : 27.5% : 27.5%
      * Confirmed Deficiency: 55.0% (deficient) : 22.5% : 22.5%
  - Priming Latency Compensation (t_prime): Offsets tubing fill delay so net liquid delivered equals V_i.
      t_pump = t_prime + (V_i / Q * 1000 ms)  (if V_i > 0)
"""

from typing import Dict, Any

# Safety limits & default constants
DEFAULT_TARGET_EC = 1.85      # mS/cm (Optimal for water spinach 1.6 - 2.0)
DEFAULT_TANK_VOLUME = 23.3    # Liters (Standard DWC foam box 34x49 cm)
DEFAULT_FLOW_RATE = 1.5       # ml/sec (Standard 12V peristaltic pump)
DEFAULT_PRIMING_DELAY = 2.0   # seconds (Delay to draw liquid to nozzle tip)
K_EC_SLOPE = 0.38             # mS/cm per (ml of concentrated stock / L of water)
HARD_MAX_EC = 3.2             # Above this, total nutrient lockout
HARD_MIN_PH = 4.2             # Below this, extreme acidity lockout
MAX_PUMP_DURATION_MS = 25000  # 25 seconds hardware cutoff safety limit


class TwoTierDosingEngine:
    def __init__(
        self,
        tank_volume_liters: float = DEFAULT_TANK_VOLUME,
        target_ec: float = DEFAULT_TARGET_EC,
        pump_flow_rate_ml_s: float = DEFAULT_FLOW_RATE,
        priming_delay_s: float = DEFAULT_PRIMING_DELAY,
        k_ec_slope: float = K_EC_SLOPE,
    ):
        self.tank_volume = float(tank_volume_liters)
        self.target_ec = float(target_ec)
        self.pump_flow_rate = float(pump_flow_rate_ml_s)
        self.priming_delay_s = float(priming_delay_s)
        self.k_ec_slope = float(k_ec_slope)

    def update_calibration(
        self,
        target_ec: float = None,
        tank_volume: float = None,
        pump_flow_rate_ml_s: float = None,
        priming_delay_s: float = None,
    ) -> Dict[str, Any]:
        if target_ec is not None and target_ec > 0:
            self.target_ec = float(target_ec)
        if tank_volume is not None and tank_volume > 0:
            self.tank_volume = float(tank_volume)
        if pump_flow_rate_ml_s is not None and pump_flow_rate_ml_s > 0:
            self.pump_flow_rate = float(pump_flow_rate_ml_s)
        if priming_delay_s is not None and priming_delay_s >= 0:
            self.priming_delay_s = float(priming_delay_s)

        return self.get_calibration()

    def get_calibration(self) -> Dict[str, Any]:
        return {
            "target_ec": round(self.target_ec, 2),
            "tank_volume_liters": round(self.tank_volume, 1),
            "pump_flow_rate_ml_s": round(self.pump_flow_rate, 2),
            "priming_delay_s": round(self.priming_delay_s, 2),
            "k_ec_slope": round(self.k_ec_slope, 3),
        }

    def calibrate_from_test_run(
        self,
        collected_ml: float,
        test_duration_s: float = 10.0,
        observed_prime_s: float = 2.0,
    ) -> Dict[str, Any]:
        """
        Calculates net flow rate Q = collected_ml / (test_duration_s - observed_prime_s)
        and automatically updates the engine.
        """
        effective_time = max(0.5, test_duration_s - observed_prime_s)
        calculated_q = max(0.1, round(collected_ml / effective_time, 3))
        self.pump_flow_rate = calculated_q
        self.priming_delay_s = max(0.0, round(observed_prime_s, 2))
        return {
            "calculated_flow_rate_ml_s": calculated_q,
            "priming_delay_s": self.priming_delay_s,
            "test_duration_s": test_duration_s,
            "collected_ml": collected_ml,
            "status": "success",
            "message": f"Calibrated: Flow Rate = {calculated_q} ml/s (Priming Delay = {self.priming_delay_s}s)",
        }

    def compute_dosing(
        self,
        ec: float,
        ph: float,
        temp: float = 26.0,
        ai_class: str = "Control",
        ai_confidence: float = 0.95,
        ai_stage: str = "HEALTHY_NORMAL",
    ) -> Dict[str, Any]:
        # 1. Hard Safety Lockout Checks
        if ec >= HARD_MAX_EC:
            return {
                "deficiency_class": ai_class,
                "confidence": ai_confidence,
                "stage": ai_stage,
                "dosing_plan": {"pump1_ms": 0, "pump2_ms": 0, "pump3_ms": 0, "total_volume_ml": 0.0},
                "ratios": {"r1_pct": 33.3, "r2_pct": 33.3, "r3_pct": 33.3},
                "volumes_ml": {"pump1_ml": 0.0, "pump2_ml": 0.0, "pump3_ml": 0.0, "total_volume_ml": 0.0},
                "tier1_status": "HIGH_EC_LOCKOUT",
                "tier1_reason": f"EC สูงเกินเกณฑ์ปลอดภัย ({ec:.2f} mS/cm > {HARD_MAX_EC}) ระงับการเติมปุ๋ยทุกสูตร แนะนำให้เจือจางด้วยน้ำเปล่า",
                "tier2_reason": "ถูกระงับการทำงานโดยระบบความปลอดภัยขั้นวิกฤต",
                "ai_reason": "ตัดการทำงานของปั๊มทุกตัวเพื่อป้องกันปุ๋ยเกินเกณฑ์ (Nutrient Burn)",
                "safety_status": "LOCKED_OUT",
            }

        if ph <= HARD_MIN_PH:
            return {
                "deficiency_class": ai_class,
                "confidence": ai_confidence,
                "stage": ai_stage,
                "dosing_plan": {"pump1_ms": 0, "pump2_ms": 0, "pump3_ms": 0, "total_volume_ml": 0.0},
                "ratios": {"r1_pct": 33.3, "r2_pct": 33.3, "r3_pct": 33.3},
                "volumes_ml": {"pump1_ml": 0.0, "pump2_ml": 0.0, "pump3_ml": 0.0, "total_volume_ml": 0.0},
                "tier1_status": "LOW_PH_LOCKOUT",
                "tier1_reason": f"pH เป็นกรดจัดรุนแรง ({ph:.2f} < {HARD_MIN_PH}) ห้ามเติมสารละลายปุ๋ยเคมี",
                "tier2_reason": "ระงับการเติมปุ๋ยจนกว่าจะปรับสมดุลกรด-ด่าง",
                "ai_reason": "หยุดการทำงานเพื่อความปลอดภัยของรากพืชจากภาวะ Acid Shock",
                "safety_status": "LOCKED_OUT",
            }

        # ----------------------------------------------------------------------
        # Step 1: Nutrient Ratios (r1, r2, r3) based on AI Diagnosis
        # ----------------------------------------------------------------------
        norm_class = ai_class.upper().strip()
        is_early_warning = "EARLY" in ai_stage.upper() or "PRE" in ai_stage.upper()
        is_symptomatic = ("CONFIRMED" in ai_stage.upper() or "SYMPTOMATIC" in ai_stage.upper()) and not is_early_warning

        if norm_class in ["-N", "NITROGEN"]:
            r1 = 0.55 if is_symptomatic else 0.45
            r2 = (1.0 - r1) / 2.0
            r3 = (1.0 - r1) / 2.0
            tier2_reason = f"AI วินิจฉัย: ขาดไนโตรเจน (-N) จัดสรรสัดส่วนปุ๋ย N {r1*100:.1f}% (P={r2*100:.1f}%, K={r3*100:.1f}%)"
            has_deficiency = True
        elif norm_class in ["-P", "PHOSPHORUS"]:
            r2 = 0.55 if is_symptomatic else 0.45
            r1 = (1.0 - r2) / 2.0
            r3 = (1.0 - r2) / 2.0
            tier2_reason = f"AI วินิจฉัย: ขาดฟอสฟอรัส (-P) จัดสรรสัดส่วนปุ๋ย P {r2*100:.1f}% (N={r1*100:.1f}%, K={r3*100:.1f}%)"
            has_deficiency = True
        elif norm_class in ["-K", "POTASSIUM"]:
            r3 = 0.55 if is_symptomatic else 0.45
            r1 = (1.0 - r3) / 2.0
            r2 = (1.0 - r3) / 2.0
            tier2_reason = f"AI วินิจฉัย: ขาดโพแทสเซียม (-K) จัดสรรสัดส่วนปุ๋ย K {r3*100:.1f}% (N={r1*100:.1f}%, P={r2*100:.1f}%)"
            has_deficiency = True
        else:
            r1 = 1.0 / 3.0
            r2 = 1.0 / 3.0
            r3 = 1.0 / 3.0
            tier2_reason = "สารอาหารสมดุล (Healthy / Control) จัดสรรสัดส่วนปุ๋ยเท่ากัน 33.3% ทุกสูตร"
            has_deficiency = False

        # ----------------------------------------------------------------------
        # Step 2: Total Volume Needed (V_total) from EC Deficit
        # ----------------------------------------------------------------------
        raw_deficit = self.target_ec - ec

        if ec < 0.9:
            tier1_status = "FRESH_WATER_DETECTED"
            ec_deficit = max(0.1, raw_deficit)
            tier1_reason = f"ตรวจพบน้ำเปล่า/EC ต่ำมาก ({ec:.2f} mS/cm, พร่อง {ec_deficit:.2f} mS/cm)"
        elif raw_deficit > 0.05:
            tier1_status = "MILD_DEPLETION"
            ec_deficit = raw_deficit
            tier1_reason = f"EC เริ่มลดลง ({ec:.2f} mS/cm, พร่อง {ec_deficit:.2f} mS/cm)"
        else:
            if has_deficiency and ec < 2.3:
                # Targeted nutrient enrichment pulse to alleviate deficiency
                tier1_status = "DEFICIENCY_PULSE"
                ec_deficit = 0.20 if is_symptomatic else 0.12
                tier1_reason = f"EC ปกติ ({ec:.2f} mS/cm) แต่ตรวจพบอาการขาดธาตุ จ่ายปุ๋ยเสริมเฉพาะทาง (Pulse {ec_deficit:.2f} mS/cm)"
            else:
                tier1_status = "NORMAL_EC"
                ec_deficit = 0.0
                tier1_reason = f"ค่า EC รวมอยู่ในเกณฑ์ที่เหมาะสม ({ec:.2f} mS/cm, เป้าหมาย {self.target_ec:.2f} mS/cm)"

        if ec_deficit <= 0.01:
            v_total = 0.0
        else:
            # V_total (ml) = (ΔEC * V_tank) / k_ec_slope
            v_total = (ec_deficit * self.tank_volume) / self.k_ec_slope
            # Cap maximum single-dose total volume (based on max runtime)
            max_allowable_vol = ((MAX_PUMP_DURATION_MS - self.priming_delay_s * 1000) / 1000.0) * self.pump_flow_rate * 3.0
            v_total = max(3.0, min(v_total, max_allowable_vol))

        # ----------------------------------------------------------------------
        # Step 3: Individual Volumes (ml) & Priming Latency Runtime (ms)
        # ----------------------------------------------------------------------
        if v_total > 0:
            v1 = round(v_total * r1, 2)
            v2 = round(v_total * r2, 2)
            v3 = round(v_total * r3, 2)
            prime_ms = int(self.priming_delay_s * 1000)

            t1 = int(round(prime_ms + (v1 / self.pump_flow_rate) * 1000)) if v1 > 0 else 0
            t2 = int(round(prime_ms + (v2 / self.pump_flow_rate) * 1000)) if v2 > 0 else 0
            t3 = int(round(prime_ms + (v3 / self.pump_flow_rate) * 1000)) if v3 > 0 else 0

            t1 = min(t1, MAX_PUMP_DURATION_MS)
            t2 = min(t2, MAX_PUMP_DURATION_MS)
            t3 = min(t3, MAX_PUMP_DURATION_MS)
        else:
            v1 = v2 = v3 = 0.0
            t1 = t2 = t3 = 0
            prime_ms = int(self.priming_delay_s * 1000)

        combined_reason = f"{tier1_reason} | {tier2_reason}"

        return {
            "deficiency_class": ai_class,
            "confidence": round(ai_confidence, 3),
            "stage": ai_stage,
            "dosing_plan": {
                "pump1_ms": t1,
                "pump2_ms": t2,
                "pump3_ms": t3,
                "total_volume_ml": round(v1 + v2 + v3, 2),
            },
            "ratios": {
                "r1_pct": round(r1 * 100, 1),
                "r2_pct": round(r2 * 100, 1),
                "r3_pct": round(r3 * 100, 1),
            },
            "volumes_ml": {
                "pump1_ml": v1,
                "pump2_ml": v2,
                "pump3_ml": v3,
                "total_volume_ml": round(v1 + v2 + v3, 2),
            },
            "priming_delay_ms": prime_ms,
            "flow_rate_ml_s": round(self.pump_flow_rate, 2),
            "tank_volume_liters": round(self.tank_volume, 1),
            "target_ec": round(self.target_ec, 2),
            "tier1_status": tier1_status,
            "tier1_reason": tier1_reason,
            "tier2_reason": tier2_reason,
            "ai_reason": combined_reason,
            "safety_status": "NORMAL",
        }


# Global singleton instance
dosing_engine = TwoTierDosingEngine()
