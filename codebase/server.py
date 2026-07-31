import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import sys
import uvicorn

ROOT = Path(__file__).resolve().parents[1]
CODEBASE = ROOT / "codebase"
STATIC_DIR = CODEBASE / "static"
SLIDES_DIR = ROOT / "data" / "vlearn-pack" / "slides"

if str(CODEBASE) not in sys.path:
    sys.path.insert(0, str(CODEBASE))

from llm_service import LLMService

def load_dotenv() -> dict[str, str]:
    env_path = ROOT / ".env"
    env: dict[str, str] = {}
    if env_path.exists():
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            env[key.strip()] = value.strip().strip('"').strip("'")
    return {**env, **os.environ}

ENV = load_dotenv()
llm_service = LLMService(ENV)

app = FastAPI(title="Comprehension Gap Detector")

class ChatRequest(BaseModel):
    provider: str
    userText: str
    systemPrompt: str

# Do không dùng async/await ở LLMService, ta định nghĩa hàm đồng bộ (def) 
# để FastAPI tự động chạy trong threadpool, tránh block event loop.
@app.post("/api/chat", response_class=PlainTextResponse)
def chat_api(request: ChatRequest):
    try:
        raw_answer = llm_service.generate_response(
            request.provider, 
            request.systemPrompt, 
            request.userText
        )
        return raw_answer
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/slides/{slide_name}")
async def serve_slide(slide_name: str):
    html_path = SLIDES_DIR / slide_name
    if not html_path.exists():
        raise HTTPException(status_code=404, detail=f"HTML slide not found: {slide_name}")
    return FileResponse(html_path)

@app.get("/")
@app.get("/index.html")
@app.get("/codebase/index.html")
async def root():
    return FileResponse(STATIC_DIR / "index.html")

# Phục vụ các file tĩnh khác (css, js, images...)
app.mount("/", StaticFiles(directory=STATIC_DIR), name="static")

if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = int(os.environ.get("PORT", "8000"))
    print(f"Serving Comprehension Gap Detector at http://{HOST}:{PORT}/")
    # Khi chạy file trực tiếp, dùng uvicorn.run
    uvicorn.run("server:app", host=HOST, port=PORT, reload=True)
