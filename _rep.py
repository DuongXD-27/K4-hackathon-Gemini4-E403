import sys
sys.stdout.reconfigure(encoding='utf-8')
with open(r'f:/K4-hackathon-Gemini4-E403/codebase/index.html','r',encoding='utf-8') as f:
    c=f.read()
func_start = c.find('function buildSystemPrompt(selectedText) {')
sel_pos = c.find('Selection capture')
func_end = c.rfind('}',func_start,sel_pos)
snippet = c[func_start:func_start+100]
print('func_start',func_start)
print('func_end',func_end)
print(snippet[:80])
