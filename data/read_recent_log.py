import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

log_path = r'C:\Users\Admin\.gemini\antigravity\brain\3db8a5a7-963d-4d8f-a985-fe689ed088ef\.system_generated\logs\transcript_full.jsonl'
with open(log_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx in range(286, min(308, len(lines))):
    obj = json.loads(lines[idx])
    src = obj.get('source')
    typ = obj.get('type')
    content = obj.get('content', '')
    if content:
        content_preview = str(content)[:300].replace('\n', ' ')
    else:
        content_preview = f"tool_calls: {[tc.get('name') for tc in obj.get('tool_calls', [])]}"
    print(f"[{idx}] {src} | {typ} | {content_preview}")
