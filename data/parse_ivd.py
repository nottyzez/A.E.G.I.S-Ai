import urllib.request
import re
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

folder_id = '1Cj2VfcmbuHjlRr3AJWjLuLzE5WE3IEhK'
url = f'https://drive.google.com/drive/folders/{folder_id}?usp=sharing'

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
with urllib.request.urlopen(req) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

# Match window['_DRIVE_ivd'] = '...';
match = re.search(r"window\['_DRIVE_ivd'\]\s*=\s*'([^']+)'", html)
if match:
    encoded_str = match.group(1)
    # Decode string escape sequences
    decoded_str = encoded_str.encode().decode('unicode_escape')
    print("Decoded length:", len(decoded_str))
    data = json.loads(decoded_str)
    
    # Save formatted json to file to inspect
    with open('d:/Code มหาปลัย/data/drive_items.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Saved to d:/Code มหาปลัย/data/drive_items.json")

    # Let's inspect the items in data
    # Recursively find file IDs, names, and mimeTypes
    def extract_items(obj, items=None):
        if items is None:
            items = []
        if isinstance(obj, list):
            # Often [id, name, mimeType, ...] or similar
            if len(obj) >= 2 and isinstance(obj[0], str) and isinstance(obj[1], str):
                if len(obj[0]) > 20 and not obj[0].startswith('http'):
                    items.append((obj[0], obj[1]))
            for item in obj:
                extract_items(item, items)
        elif isinstance(obj, dict):
            for v in obj.values():
                extract_items(v, items)
        return items

    extracted = extract_items(data)
    print(f"Total extracted potential files/folders: {len(extracted)}")
    for file_id, name in extracted:
        print(f"  ID: {file_id} | Name: {name}")

else:
    print("Not found window['_DRIVE_ivd']")
