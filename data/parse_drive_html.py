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

# Search for filenames or common file extensions: .jpg, .png, .zip, .csv, .xlsx, etc.
matches = re.findall(r'([a-zA-Z0-9_\- \(\)\.\u0E00-\u0E7F]+\.(?:jpg|jpeg|png|zip|rar|csv|xlsx|json|txt))', html, re.IGNORECASE)
print("Filename matches:", list(set(matches))[:30])

# Look for drive items data structures (e.g., _DRIVE_BOOTSTRAP_DATA or similar)
bootstrap = re.findall(r'_DRIVE_BOOTSTRAP_DATA\s*=\s*(.*?);</script>', html)
if bootstrap:
    print("Found _DRIVE_BOOTSTRAP_DATA, length:", len(bootstrap[0]))
    with open('d:/Code มหาปลัย/data/drive_bootstrap.txt', 'w', encoding='utf-8') as f:
        f.write(bootstrap[0][:10000])

# Look for folder or subfolder names
folder_matches = re.findall(r'\[\"([a-zA-Z0-9_-]{20,})\",\[\"([^\"]+)\"\]', html)
print("Folder matches:", folder_matches[:10])
