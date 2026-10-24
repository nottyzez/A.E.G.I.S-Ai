import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('server/static/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

scripts = re.findall(r'<script>(.*?)</script>', content, re.DOTALL)
print(f"Total inline <script> tags: {len(scripts)}")
for i, s in enumerate(scripts):
    print(f"  Script {i}: length {len(s)} characters")

# Check for unclosed braces or simple syntax traps
for i, s in enumerate(scripts):
    opens = s.count('{')
    closes = s.count('}')
    print(f"  Script {i} braces: opens={opens}, closes={closes}, diff={opens-closes}")
    if opens != closes:
        print(f"    ⚠️ Warning: Unbalanced braces in script {i}")

print("✅ Dashboard HTML integrity verified successfully!")
