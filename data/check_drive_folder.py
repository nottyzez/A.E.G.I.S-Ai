import urllib.request
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

folder_id = '1Cj2VfcmbuHjlRr3AJWjLuLzE5WE3IEhK'
url = f'https://drive.google.com/drive/folders/{folder_id}?usp=sharing'

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print(f"Status: {resp.status}, HTML length: {len(html)}")
        # Look for file names or folder names in the HTML
        title_match = re.search(r'<title>(.*?)</title>', html)
        if title_match:
            print("Title:", title_match.group(1))
        
        # Search for file items
        # Google Drive embeds items in JS objects
        items = re.findall(r'\[\"([a-zA-Z0-9_-]{25,})\",\[\"(.*?)\"', html)
        print("Found items count:", len(items))
        for item in items[:10]:
            print("Item:", item)
            
except Exception as e:
    print("Error:", e)
