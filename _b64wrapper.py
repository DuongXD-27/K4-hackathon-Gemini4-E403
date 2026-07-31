import base64, sys
b64_data = sys.stdin.read().strip()
decoded = base64.b64decode(b64_data).decode('utf-8')
out_path = r'f:\K4-hackathon-Gemini4-E403\_fix.py'
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(decoded)
print('Written %d chars to %s' % (len(decoded), out_path))
