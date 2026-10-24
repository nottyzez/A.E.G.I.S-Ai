import urllib.request
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

folder_id = '1Cj2VfcmbuHjlRr3AJWjLuLzE5WE3IEhK'
url = f'https://drive.google.com/drive/folders/{folder_id}?usp=sharing'

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
with urllib.request.urlopen(req) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
print(f"Total script tags: {len(scripts)}")
for i, s in enumerate(scripts):
    s_clean = s.strip()
    if s_clean:
        prefix = s_clean[:80].replace('\n', ' ')
        print(f"  [{i}] len={len(s_clean)} | {prefix}")
