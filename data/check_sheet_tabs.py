import urllib.request
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
url = 'https://docs.google.com/spreadsheets/d/12u0Cj5Fv_BBpGKucgqgouCgzeJjAluhZSRFmv4gLT7Y/htmlview'

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8')

# Search for any gid references
gids = re.findall(r'gid=([0-9]+)', html)
print('Unique gids:', list(set(gids)))

# Search for sheet names
titles = re.findall(r'name: "([^"]+)"', html)
print('Titles:', titles)

# Search for tab labels in html
sheet_labels = re.findall(r'<li[^>]*id="sheets-button-[^"]*"[^>]*>(.*?)</li>', html)
print('Sheet labels count:', len(sheet_labels))
for l in sheet_labels:
    print('Label:', l)
