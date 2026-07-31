"""
Reads index.html as binary, finds replacement points, writes back.
Strategy: use Python to do the heavy string manipulation to avoid
the JSON encoding issue with backticks and unicode in tool args.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

HTML = r'f:\K4-hackathon-Gemini4-E403\codebase\index.html'
with open(HTML, 'r', encoding='utf-8') as f:
    c = f.read()

print(f"Loaded {len(c)} chars")
print("OK")
