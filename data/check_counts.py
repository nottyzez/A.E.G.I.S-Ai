import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

img_dir = r"D:\Code มหาปลัย\Ai มหาปลัย\dataset_real\images"
if os.path.exists(img_dir):
    for d in sorted(os.listdir(img_dir)):
        p = os.path.join(img_dir, d)
        if os.path.isdir(p):
            print(f"  {d}: {len(os.listdir(p))} files")
