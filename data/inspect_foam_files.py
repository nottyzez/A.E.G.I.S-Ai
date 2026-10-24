import urllib.request
import re
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def get_folder_items(folder_id):
    url = f'https://drive.google.com/drive/folders/{folder_id}?usp=sharing'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return []

    match = re.search(r"window\['_DRIVE_ivd'\]\s*=\s*'([^']+)'", html)
    if not match:
        return []
    
    encoded_str = match.group(1)
    decoded_str = encoded_str.encode().decode('unicode_escape')
    data = json.loads(decoded_str)
    
    items = []
    if data and len(data) > 0 and data[0]:
        for item in data[0]:
            file_id = item[0]
            raw_name = item[2]
            try:
                name = raw_name.encode('latin1').decode('utf-8')
            except Exception:
                name = raw_name
            mime_type = item[3]
            items.append({
                "id": file_id,
                "name": name,
                "mime": mime_type,
            })
    return items

foam_folders = [
    ("Control", "1l2we6toFKY0YFRWHuWtqm-oSgw-5kiom"),
    ("N", "1JjYOOh0ukU2c-_2v47Fy9idTTm7BL2hr"),
    ("P", "1oB7ZFk8AqJ01v0mF2KpU-EoZeAEP8dLX"),
    ("K", "11Ut8gaROcAfxiKlPPGFZe8v2DjCl4wP0")
]

for name, fid in foam_folders:
    items = get_folder_items(fid)
    print(f"\n📦 Foam Box Tank {name}: found {len(items)} items")
    for it in items:
        print(f"   - {it['name']} ({it['mime']}) [ID: {it['id']}]")
