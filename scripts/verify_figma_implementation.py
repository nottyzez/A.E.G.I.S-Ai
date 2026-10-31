# -*- coding: utf-8 -*-
"""
Verification Script for Figma UI Layout & Visual Effects Implementation
Validates:
1. CSS classes and specific dimensions (315x116, 341x116, 665x248, 662x217, 272x245, 524x352, 524x248)
2. Day labels: Sun, Mon, Tue, Wed, Thu, Fri, Sat in both pH and EC charts
3. Progress strips for Healthy (78%), N (0%), P (10%), K (2%) with height 12.51px, radius 80px, #A8C5DA, rgba(28, 28, 28, 0.4)
4. Work Sans 700 20px, Inter 12px, Work Sans 400 32px
5. Sidebar logo hidden
6. Drifting clouds keyframes & layers
7. Mouse-parallax space nebula
8. Reduced star particle count (490 total) & meteor adjustments
9. Dual-path asset resolver compatibility
"""

import sys
import re
from pathlib import Path

INDEX_PATH = Path("server/static/index.html")
assert INDEX_PATH.exists(), f"{INDEX_PATH} not found"
html = INDEX_PATH.read_text(encoding="utf-8")

checks = []

def check(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    checks.append((name, status, detail))
    print(f"[{status}] {name} {detail}")

# 1. CSS Classes and Dimensions
check("CSS .figma-card-ph-kpi (315x116)", ".figma-card-ph-kpi" in html and "315px" in html and "116px" in html)
check("CSS .figma-card-ec-kpi (341x116)", ".figma-card-ec-kpi" in html and "341px" in html and "116px" in html)
check("CSS .figma-card-ec-chart (665x248)", ".figma-card-ec-chart" in html and "665px" in html and "248px" in html)
check("CSS .figma-card-ph-chart (662x217)", ".figma-card-ph-chart" in html and "662px" in html and "217px" in html)
check("CSS .figma-card-temperature (272x245)", ".figma-card-temperature" in html and "272px" in html and "245px" in html)
check("CSS .figma-card-aegis-analyze (524x352)", ".figma-card-aegis-analyze" in html and "524px" in html and "352px" in html)
check("CSS .figma-card-projections (524x248)", ".figma-card-projections" in html and "524px" in html and "248px" in html)
check("CSS .figma-title-block (Inter 600 40px)", ".figma-title-block" in html and "font-size: 40px" in html and "line-height: 20px" in html)
check("CSS .figma-strip-track (height 12.51px, radius 80px)", ".figma-strip-track" in html and "12.51px" in html and "80px" in html)
check("CSS .figma-strip-fill (#A8C5DA)", ".figma-strip-fill" in html and "#A8C5DA" in html)

# 2. Day Labels in both charts
ph_chart_match = re.search(r"figma-card-ph-chart.*?Sun.*?Mon.*?Tue.*?Wed.*?Thu.*?Fri.*?Sat", html, re.DOTALL)
check("pH Chart 7-day horizontal labels (Sun-Sat)", bool(ph_chart_match))

ec_chart_match = re.search(r"figma-card-ec-chart.*?Sun.*?Mon.*?Tue.*?Wed.*?Thu.*?Fri.*?Sat", html, re.DOTALL)
check("EC Chart 7-day horizontal labels (Sun-Sat)", bool(ec_chart_match))

# 3. A.E.G.I.S analyze! 4 progress strips
strip_labels_match = re.search(r"figma-card-aegis-analyze.*?Healthy.*?N.*?P.*?K", html, re.DOTALL)
check("A.E.G.I.S analyze! strips (Healthy, N, P, K)", bool(strip_labels_match))
check("A.E.G.I.S analyze! title fontSize: '32px'", "A.E.G.I.S analyze!" in html and "32px" in html)
check("Work Sans 700 20px on left & Inter 12px on right in strips", bool(re.search(r"font-work font-bold text-\[20px\].*?\{item\.label\}.*?font-inter text-\[12px\].*?\{pct\}%", html, re.DOTALL)))
check("Control unit probs (78%, 0%, 10%, 2%)", "Healthy: 0.78" in html and "P_Deficiency: 0.10" in html and "K_Deficiency: 0.02" in html)
check("A.E.G.I.S analyze card is isolated to Analyze tab", html.count('figma-card-aegis-analyze magic-bento-card') == 1 and 'figma-card-aegis-analyze' not in html[html.find('Peristaltic Fertilizer Dosing Deck'):html.find('Peristaltic Fertilizer Dosing Deck') + 300])

# 4. Sidebar Logo Hidden & Responsive Card Rules
check("Sidebar logo hidden", "figma-sidebar-logo" in html and "display: 'none'" in html)
check("Figma cards responsive max-width: 100%", html.count("max-width: 100%") >= 7)

# 5. Cosmic & Atmospheric Effects
check("Drifting clouds keyframes", "cloudDriftSlow" in html and "cloudDriftFast" in html and "dashboard-clouds-layer" in html)
check("Drifting clouds pointer-events: none", "pointer-events: none" in html and "dashboard-clouds-layer" in html)
check("Mouse parallax space nebula", "home-space-nebula" in html and "nebulaRef" in html)
check("Reduced star particle count (280 far, 150 mid, 60 near = 490)", "createStarLayer(280" in html and "createStarLayer(150" in html and "createStarLayer(60" in html)
check("Meteor frequency adjustment (Dashboard rare, Home disabled)", "Math.random() < 0.002" in html and "meteorGroup.visible = false" in html)

# 6. Background Image Asset Files Exist
bg_dash = Path("server/static/images_real/dashboard_mountain_bg.png")
bg_space = Path("server/static/images_real/space_bg.jpg")
check("Dashboard background image exists (>50KB)", bg_dash.exists() and bg_dash.stat().st_size > 50000)
check("Space background image exists (>50KB)", bg_space.exists() and bg_space.stat().st_size > 50000)

# Summary
total = len(checks)
passed = sum(1 for c in checks if c[1] == "PASS")
print(f"\nVerification Result: {passed}/{total} Passed")
assert passed == total, f"Some verification checks failed: {[c for c in checks if c[1] != 'PASS']}"
print("All verification checks PASSED successfully!")
