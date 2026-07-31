import base64, sys
b64 = sys.stdin.read().strip()
decoded = base64.b64decode(b64).decode('utf-8')
path = r'f:\K4-hackathon-Gemini4-E403\_fix_index.py'
with open(path, 'w', encoding='utf-8') as f:
    f.write(decoded)
print(f"Written {len(decoded)} bytes to {path}")
