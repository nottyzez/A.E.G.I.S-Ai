import urllib.request

url = 'https://docs.google.com/spreadsheets/d/12u0Cj5Fv_BBpGKucgqgouCgzeJjAluhZSRFmv4gLT7Y/edit?usp=sharing'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    resp = urllib.request.urlopen(req)
    print("Status:", resp.status)
    print("Final URL:", resp.url)
except Exception as e:
    print("Error:", e)
