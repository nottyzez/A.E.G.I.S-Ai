import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('d:/Code มหาปลัย/data/drive_items.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# The items are in data[0]
items = data[0]
print(f"Total items in folder: {len(items)}")

for i, item in enumerate(items):
    file_id = item[0]
    raw_name = item[2]
    # fix mojibake: latin1 -> utf-8
    try:
        name = raw_name.encode('latin1').decode('utf-8')
    except Exception:
        name = raw_name
    mime_type = item[3]
    print(f"[{i}] Name: {name} | Type: {mime_type} | ID: {file_id}")
