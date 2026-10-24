import urllib.request
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

folder_id = '1Cj2VfcmbuHjlRr3AJWjLuLzE5WE3IEhK'
url = f'https://drive.google.com/drive/folders/{folder_id}?usp=sharing'

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

# Search for AF_initDataCallback
callbacks = re.findall(r'AF_initDataCallback\s*\(\s*\{.*?data:\s*function\(\)\{return\s*(.*?)\}\s*\}\s*\);', html, re.DOTALL)
print("Callbacks found:", len(callbacks))

for i, cb in enumerate(callbacks):
    print(f"\n--- Callback {i} (len {len(cb)}) ---")
    # Search for strings inside callback
    strings = re.findall(r'"([^"\\]{4,})"', cb)
    # Filter interesting strings
    interesting = [s for s in strings if any(ext in s.lower() for ext in ['.jpg', '.png', '.zip', '.rar', 'control', 'ขาด', 'dataset', 'แก้ว'])]
    print("Interesting strings:", interesting[:20])
