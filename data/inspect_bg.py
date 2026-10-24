import shutil
import sys, io
from pathlib import Path
from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

src = Path(r"C:/Users/Admin/.gemini/antigravity/brain/3db8a5a7-963d-4d8f-a985-fe689ed088ef/.user_uploaded/media_1792577188404_6b8b6946.png")
dst = Path(r"d:/Code มหาปลัย/server/static/images_real/forest_bg.png")
dst.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(src, dst)
print("Copied to:", dst, "size:", dst.stat().st_size)

im = Image.open(src).convert("RGB")
print("Dimensions:", im.size)
w, h = im.size
for name, (x, y) in [
    ("Top sky", (w//2, int(h*0.08))),
    ("Mountain peak", (int(w*0.35), int(h*0.30))),
    ("Center mist", (w//2, int(h*0.50))),
    ("Mid pine", (int(w*0.20), int(h*0.65))),
    ("Deep forest bottom", (w//2, int(h*0.88))),
]:
    r, g, b = im.getpixel((x, y))
    print(f"  {name}: RGB({r},{g},{b}) #{r:02x}{g:02x}{b:02x}")
