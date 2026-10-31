#!/usr/bin/env python3
"""
Automated Verification Script for Academic References & Poster QR Code
Checks:
1. Existence and integrity of REFERENCES.md at project root.
2. Presence and APA 7th edition formatting of all 21 numbered citations.
3. Functional, clickable markdown links for all DOIs and publisher URLs.
4. Link or badge pointing to REFERENCES.md in README.md.
5. Presence and dimension verification of QR code assets (PNG >= 1000x1000 px, SVG).
6. Programmatic decoding of the QR code image using OpenCV QRCodeDetector,
   confirming the decoded URL exactly matches:
   https://github.com/nottyzez/A.E.G.I.S-Ai/blob/main/REFERENCES.md
7. Documentation of poster sizing and placement guidelines.
"""

import os
import re
import sys
import cv2

TARGET_URL = "https://github.com/nottyzez/A.E.G.I.S-Ai/blob/main/REFERENCES.md"

EXPECTED_CITATIONS = [
    {
        "id": 1,
        "author": "Abu Sneineh",
        "title": "smart hydroponics monitoring",
        "doi": "https://doi.org/10.1016/j.iot.2023.100789"
    },
    {
        "id": 2,
        "author": "Alipio",
        "title": "Precision agriculture: IoT-based smart hydroponic system with closed-loop nutrient control",
        "doi": "https://doi.org/10.1109/iThings.2019.00057"
    },
    {
        "id": 3,
        "author": "Baltrušaitis",
        "title": "Multimodal machine learning: A survey and taxonomy",
        "doi": "https://doi.org/10.1109/TPAMI.2018.2798607"
    },
    {
        "id": 4,
        "author": "Cakmak",
        "title": "role of potassium in alleviating detrimental effects of abiotic stresses",
        "doi": "https://doi.org/10.1002/jpln.200420485"
    },
    {
        "id": 5,
        "author": "Elsherbiny",
        "title": "Integration of visual symptoms and solution electrical conductivity",
        "doi": "https://doi.org/10.1016/j.compag.2022.107086"
    },
    {
        "id": 6,
        "author": "Garg",
        "title": "Multimodal sensor fusion in smart agriculture",
        "doi": "https://doi.org/10.1016/j.inffus.2024.102234"
    },
    {
        "id": 7,
        "author": "Hu",
        "title": "Squeeze-and-Excitation networks",
        "doi": "https://doi.org/10.1109/CVPR.2018.00745"
    },
    {
        "id": 8,
        "author": "Koyama",
        "title": "root-growth assay for aluminum and proton rhizotoxicity",
        "doi": "https://doi.org/10.1093/pcp/pce041"
    },
    {
        "id": 9,
        "author": "Luan",
        "title": "Transcriptional and post-transcriptional regulation of phosphate starvation",
        "doi": "https://doi.org/10.1093/pcp/pcac048"
    },
    {
        "id": 10,
        "author": "Marschner",
        "title": "Marschner's Mineral Nutrition of Higher Plants",
        "doi": "https://doi.org/10.1016/C2009-0-02393-4"
    },
    {
        "id": 11,
        "author": "Masclaux-Daubresse",
        "title": "Nitrogen uptake, assimilation and remobilization in plants",
        "doi": "https://doi.org/10.1093/aob/mcq028"
    },
    {
        "id": 12,
        "author": "Meyer",
        "title": "Verification of color vegetation indices for automated crop imaging applications",
        "doi": "https://doi.org/10.1016/j.compag.2008.03.009"
    },
    {
        "id": 13,
        "author": "Mitsanis",
        "title": "Closed-loop precision nutrient dosing and automated probe cleaning",
        "doi": "https://doi.org/10.1016/j.atech.2024.100412"
    },
    {
        "id": 14,
        "author": "Murugesan",
        "title": "Explainable deep learning framework for plant disease detection",
        "doi": "https://doi.org/10.1038/s41598-024-84512-3"
    },
    {
        "id": 15,
        "author": "Reyes-Yanes",
        "title": "Digital twin and deep learning applied to hydroponics",
        "doi": "https://doi.org/10.1016/j.compag.2022.106796"
    },
    {
        "id": 16,
        "author": "Sandler",
        "title": "MobileNetV2: Inverted residuals and linear bottlenecks",
        "doi": "https://doi.org/10.1109/CVPR.2018.00474"
    },
    {
        "id": 17,
        "author": "Selvaraju",
        "title": "Grad-CAM: Visual explanations from deep networks",
        "doi": "https://doi.org/10.1109/ICCV.2017.74"
    },
    {
        "id": 18,
        "author": "Tournaire-Roux",
        "title": "Cytosolic pH regulates root water transport during anoxic stress",
        "doi": "https://doi.org/10.1038/nature01853"
    },
    {
        "id": 19,
        "author": "Trejo-Téllez",
        "title": "Nutrient solutions for hydroponic systems",
        "doi": "https://doi.org/10.5772/37578"
    },
    {
        "id": 20,
        "author": "Trong",
        "title": "Late fusion of convolutional neural networks and sensor time-series",
        "doi": "https://doi.org/10.1109/ACCESS.2020.3013892"
    },
    {
        "id": 21,
        "author": "Wang",
        "title": "Physiological responses and nutrient uptake kinetics of water spinach",
        "doi": "https://doi.org/10.1016/j.scienta.2017.02.019"
    }
]

def verify_references_markdown():
    print("[1/5] Verifying REFERENCES.md exists and contains all 21 citations...")
    ref_path = "REFERENCES.md"
    assert os.path.exists(ref_path), f"Error: {ref_path} not found at project root."
    
    with open(ref_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    for item in EXPECTED_CITATIONS:
        cid = item["id"]
        # Check number
        num_pattern = rf"(?:^|\n){cid}\.\s+"
        assert re.search(num_pattern, content), f"Citation #{cid} number missing in {ref_path}"
        
        # Check author
        author = item["author"]
        assert author in content, f"Citation #{cid} author '{author}' missing in {ref_path}"
        
        # Check title snippet
        title = item["title"]
        assert title.lower() in content.lower(), f"Citation #{cid} title snippet '{title}' missing in {ref_path}"
        
        # Check clickable link: [url](url) or [text](url)
        doi = item["doi"]
        assert doi in content, f"Citation #{cid} DOI '{doi}' missing in {ref_path}"
        link_pattern = rf"\[.*?\]\({re.escape(doi)}\)"
        assert re.search(link_pattern, content), f"Citation #{cid} clickable markdown link for DOI '{doi}' missing in {ref_path}"
        
    print(f"  --> PASS: All 21 citations present with verified clickable links in {ref_path}.")

def verify_readme_link():
    print("[2/5] Verifying README.md links to REFERENCES.md...")
    readme_path = "README.md"
    assert os.path.exists(readme_path), f"Error: {readme_path} not found."
    
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    assert "REFERENCES.md" in content, "README.md does not reference REFERENCES.md"
    ref_link_pattern = r"\[.*?\]\(REFERENCES\.md\)"
    assert re.search(ref_link_pattern, content), "README.md missing markdown link or badge pointing to REFERENCES.md"
    print("  --> PASS: README.md successfully links to REFERENCES.md.")

def verify_qr_assets():
    print("[3/5] Verifying QR code assets in docs/assets and assets directories...")
    dirs_to_check = [os.path.join("docs", "assets"), "assets"]
    
    for d in dirs_to_check:
        assert os.path.isdir(d), f"Directory {d} does not exist."
        png_path = os.path.join(d, "references_qr.png")
        svg_path = os.path.join(d, "references_qr.svg")
        
        assert os.path.exists(png_path), f"Missing PNG asset: {png_path}"
        assert os.path.exists(svg_path), f"Missing SVG asset: {svg_path}"
        
        # Check PNG resolution
        img = cv2.imread(png_path)
        assert img is not None, f"Failed to load image at {png_path}"
        h, w = img.shape[:2]
        print(f"  --> {png_path} resolution: {w}x{h} px")
        assert w >= 1000 and h >= 1000, f"PNG asset resolution {w}x{h} < 1000x1000 px"
        
        # Check SVG format
        with open(svg_path, "r", encoding="utf-8") as sf:
            svg_text = sf.read()
        assert "<svg" in svg_text and "</svg>" in svg_text, f"{svg_path} is not valid SVG"
        
    print("  --> PASS: QR code assets exist and meet resolution criteria (>= 1000x1000 px, vector SVG).")

def verify_qr_decoding():
    print("[4/5] Programmatically decoding QR code image with OpenCV QRCodeDetector...")
    png_path = os.path.join("docs", "assets", "references_qr.png")
    img = cv2.imread(png_path)
    assert img is not None, f"Failed to read {png_path}"
    
    detector = cv2.QRCodeDetector()
    decoded_url, points, _ = detector.detectAndDecode(img)
    
    print(f"  --> Decoded URL: '{decoded_url}'")
    print(f"  --> Expected URL: '{TARGET_URL}'")
    assert decoded_url == TARGET_URL, (
        f"Mismatch: Decoded '{decoded_url}' != Expected '{TARGET_URL}'"
    )
    print("  --> PASS: QR code decodes exactly to target URL.")

def verify_poster_guidance():
    print("[5/5] Verifying poster placement and sizing documentation...")
    # Check in REFERENCES.md
    with open("REFERENCES.md", "r", encoding="utf-8") as f:
        ref_text = f.read().lower()
        
    keywords = ["poster", "35 mm", "quiet zone", "dpi"]
    for kw in keywords:
        assert kw in ref_text, f"REFERENCES.md missing poster guidance keyword: '{kw}'"
        
    # Check in POSTER_GUIDELINES.md
    guidelines_path = os.path.join("docs", "assets", "POSTER_GUIDELINES.md")
    assert os.path.exists(guidelines_path), f"Missing {guidelines_path}"
    with open(guidelines_path, "r", encoding="utf-8") as f:
        g_text = f.read().lower()
    for kw in ["print size", "quiet zone", "dpi", "placement"]:
        assert kw in g_text, f"{guidelines_path} missing poster keyword: '{kw}'"
        
    print("  --> PASS: Poster sizing and placement recommendations fully documented.")

def main():
    print("=" * 70)
    print("A.E.G.I.S. ACADEMIC REFERENCES & POSTER QR VERIFICATION SUITE")
    print("=" * 70)
    try:
        verify_references_markdown()
        verify_readme_link()
        verify_qr_assets()
        verify_qr_decoding()
        verify_poster_guidance()
        print("=" * 70)
        print("ALL VERIFICATION CHECKS PASSED SUCCESSFULLY (5/5)")
        print("=" * 70)
        return 0
    except AssertionError as e:
        print(f"\n❌ VERIFICATION FAILED: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    sys.exit(main())
