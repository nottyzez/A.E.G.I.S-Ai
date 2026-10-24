import urllib.request
import sys
import io
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

test_file_id = "11ZuMeC8fioEbE1eDE8vjNpadERtXBOME"
download_url = f"https://drive.usercontent.google.com/download?id={test_file_id}&export=download"

out_path = r"d:\Code มหาปลัย\data\test_download.jpg"

try:
    req = urllib.request.Request(download_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp:
        content = resp.read()
        print(f"Downloaded bytes: {len(content)}")
        with open(out_path, "wb") as f:
            f.write(content)
        print(f"Saved to {out_path}, size={os.path.getsize(out_path)}")
except Exception as e:
    print("Download error:", e)
