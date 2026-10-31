"""
A.E.G.I.S. High-Resolution Poster QR Code Generator
Generates print-quality PNG (>= 1000x1000 px) and vector SVG assets.
Target URL: https://github.com/nottyzez/A.E.G.I.S-Ai/blob/main/REFERENCES.md
"""

import os
import cv2
import numpy as np

TARGET_URL = "https://github.com/nottyzez/A.E.G.I.S-Ai/blob/main/REFERENCES.md"

def generate_qr_assets():
    # 1. Initialize OpenCV QR encoder
    encoder = cv2.QRCodeEncoder.create()
    qr_matrix = encoder.encode(TARGET_URL)
    
    if qr_matrix is None or qr_matrix.size == 0:
        raise RuntimeError("Failed to encode target URL into QR code matrix.")
        
    print(f"Raw QR matrix size: {qr_matrix.shape}")
    
    # 2. Add standard quiet zone (4 modules on all sides)
    quiet_zone = 4
    padded = np.pad(qr_matrix, quiet_zone, mode="constant", constant_values=255)
    total_modules = padded.shape[0]
    print(f"Padded QR matrix size: {padded.shape} (Quiet zone: {quiet_zone} modules)")
    
    # 3. Scale up for print-quality PNG (>= 1000x1000 px)
    # Using module scale of 32 -> 45 * 32 = 1440 x 1440 px
    scale = 32
    png_img = np.repeat(np.repeat(padded, scale, axis=0), scale, axis=1)
    print(f"Generated PNG dimensions: {png_img.shape[1]}x{png_img.shape[0]} px")
    assert png_img.shape[0] >= 1000 and png_img.shape[1] >= 1000
    
    # 4. Generate SVG vector format
    h, w = padded.shape
    path_commands = []
    for r in range(h):
        for c in range(w):
            if padded[r, c] == 0:  # Black module
                path_commands.append(f"M{c},{r}h1v1h-1z")
                
    svg_content = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="1440" height="1440" shape-rendering="crispEdges">\n'
        f'  <title>A.E.G.I.S References QR Code</title>\n'
        f'  <desc>QR code linking to {TARGET_URL}</desc>\n'
        f'  <rect width="100%" height="100%" fill="#FFFFFF"/>\n'
        f'  <path d="{" ".join(path_commands)}" fill="#000000"/>\n'
        '</svg>\n'
    )
    
    # 5. Output directories: docs/assets and assets
    output_dirs = [
        os.path.join("docs", "assets"),
        os.path.join("assets")
    ]
    
    for out_dir in output_dirs:
        os.makedirs(out_dir, exist_ok=True)
        
        # Save PNG
        png_path = os.path.join(out_dir, "references_qr.png")
        cv2.imwrite(png_path, png_img)
        print(f"Saved PNG to: {png_path}")
        
        # Also save alias qr_code.png
        png_alias = os.path.join(out_dir, "qr_code.png")
        cv2.imwrite(png_alias, png_img)
        
        # Save SVG
        svg_path = os.path.join(out_dir, "references_qr.svg")
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
        print(f"Saved SVG to: {svg_path}")
        
        # Also save alias qr_code.svg
        svg_alias = os.path.join(out_dir, "qr_code.svg")
        with open(svg_alias, "w", encoding="utf-8") as f:
            f.write(svg_content)

    # 6. Verify PNG decoding with OpenCV QRCodeDetector
    test_img = cv2.imread(os.path.join("docs", "assets", "references_qr.png"))
    detector = cv2.QRCodeDetector()
    decoded_text, points, _ = detector.detectAndDecode(test_img)
    print(f"Decoded QR code text: {decoded_text}")
    assert decoded_text == TARGET_URL, f"Decoded text '{decoded_text}' != expected '{TARGET_URL}'"
    print("Verification SUCCESS: Decoded URL matches TARGET_URL exactly.")

if __name__ == "__main__":
    generate_qr_assets()
