import sys
sys.stdout.reconfigure(encoding='utf-8')
with open(r'f:/K4-hackathon-Gemini4-E403/codebase/index.html','r',encoding='utf-8') as f:
    c=f.read()
# Show last 50 chars of function
s = c.find('function buildSystemPrompt(selectedText) {')
sel = c.find('Selection capture')
func_end = c.rfind('}', s, sel)
last50 = c[func_end-20:func_end+30]
print(repr(last50))
# Count lines
lines_after = c[func_end:sel].split('\n')
print('Lines between func_end and sel:', len(lines_after))
for i,l in enumerate(lines_after):
    print(f'  line {i}: {repr(l)}')
