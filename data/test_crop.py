"""
test_crop.py — Automatic plant segmentation and cropping using Excess Green Index (ExG).
Handles Windows Unicode path encoding.
"""

import sys
import io
import os
import cv2
import numpy as np

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def imread_unicode(path):
    with open(path, 'rb') as f:
        bytes_data = np.frombuffer(f.read(), np.uint8)
    return cv2.imdecode(bytes_data, cv2.IMREAD_COLOR)

def imwrite_unicode(path, img):
    ext = os.path.splitext(str(path))[1]
    is_success, buffer = cv2.imencode(ext, img)
    if is_success:
        with open(path, 'wb') as f:
            f.write(buffer)
        return True
    return False

def crop_plant(img_path, output_path, padding_pct=0.08):
    img = imread_unicode(img_path)
    if img is None:
        print(f"Error reading image: {img_path}")
        return False

    h, w, _ = img.shape
    
    # 1. Convert to float RGB for ExG calculation
    b = img[:, :, 0].astype(np.float32)
    g = img[:, :, 1].astype(np.float32)
    r = img[:, :, 2].astype(np.float32)
    
    # Excess Green Index (ExG): 2*G - R - B
    exg = 2 * g - r - b
    
    # Normalize ExG to 0-255 uint8
    exg_norm = cv2.normalize(exg, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    
    # 2. Otsu thresholding + Gaussian Blur
    blurred = cv2.GaussianBlur(exg_norm, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # 3. Morphological opening & closing to remove noise
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    # 4. Find all green contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        print(f"No plant detected in {img_path}")
        return False
        
    # Filter small noise contours (keep contours > 0.5% of total image area)
    min_area = (h * w) * 0.005
    plant_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]
    
    if not plant_contours:
        # Fallback to largest contour
        plant_contours = [max(contours, key=cv2.contourArea)]
        
    # 5. Combined bounding box covering all plant foliage
    x_min, y_min = w, h
    x_max, y_max = 0, 0
    for cnt in plant_contours:
        x, y, cw, ch = cv2.boundingRect(cnt)
        x_min = min(x_min, x)
        y_min = min(y_min, y)
        x_max = max(x_max, x + cw)
        y_max = max(y_max, y + ch)
        
    # Add padding
    pad_x = int((x_max - x_min) * padding_pct)
    pad_y = int((y_max - y_min) * padding_pct)
    x1 = max(0, x_min - pad_x)
    y1 = max(0, y_min - pad_y)
    x2 = min(w, x_max + pad_x)
    y2 = min(h, y_max + pad_y)
    
    # 6. Crop and save
    cropped = img[y1:y2, x1:x2]
    imwrite_unicode(output_path, cropped)
    print(f"✅ Successfully cropped: ({w}x{h}) -> ({x2-x1}x{y2-y1}) saved to {output_path}")
    return True

if __name__ == "__main__":
    test_img = r"d:\Code มหาปลัย\data\test_download.jpg"
    test_out = r"d:\Code มหาปลัย\data\test_cropped.jpg"
    if os.path.exists(test_img):
        crop_plant(test_img, test_out)
    else:
        print(f"File not found: {test_img}")
