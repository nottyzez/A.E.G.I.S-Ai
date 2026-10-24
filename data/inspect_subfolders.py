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
        print(f"Error fetching {folder_id}: {e}")
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
            size = item[4] if len(item) > 4 else None
            items.append({
                "id": file_id,
                "name": name,
                "mime": mime_type,
                "size": size,
            })
    return items

subfolders = [
    ("กล่องโฟม 23 L น้ำบาดาล", "1sqcPWleiOUZ9g1g_KB7mjYRqKxUpyyrM"),
    ("แก้ว 650 ml น้ำดื่ม", "1EH-C8dcFXYH0jpDoM5ZFfnt3ugyUF9Wt")
]

all_data = {}
for name, fid in subfolders:
    print(f"\n📁 Checking folder: {name} ({fid}) ...")
    items = get_folder_items(fid)
    print(f"  Found {len(items)} items:")
    for it in items[:25]:
        print(f"    - {it['name']} ({it['mime']}) [ID: {it['id']}]")
    all_data[name] = items

with open('d:/Code มหาปลัย/data/drive_subfolders.json', 'w', encoding='utf-8') as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)
