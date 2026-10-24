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

cup_folders = [
    ("Cup Control", "1GcSP8ktStIIErPuNIXN-vmMPuyFvhPl9"),
    ("Cup N", "1w7gwMh2YQ-d5Fcby6bM_sQrUJ7LoMpDS"),
    ("Cup P", "1n3odwv3TxMe3vibzZjk4pLjTuMMVViCP"),
    ("Cup K", "1RzUXHQ2vh8Ne0G_7aHoo4cUUfu60oz7n")
]

for name, fid in cup_folders:
    items = get_folder_items(fid)
    print(f"\n📸 {name}: found {len(items)} files")
    for it in items[:10]:
        print(f"   - {it['name']} ({it['mime']}) [ID: {it['id']}]")
