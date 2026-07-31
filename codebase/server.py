import sys
from pathlib import Path
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Ensure codebase is in sys.path
ROOT = Path(__file__).resolve().parents[1]
CODEBASE = ROOT / "codebase"
if str(CODEBASE) not in sys.path:
    sys.path.insert(0, str(CODEBASE))

from core.config import settings
from api.routes import chat

app = FastAPI(title="Comprehension Gap Detector (ReAct Ready)")

# API Routes
app.include_router(chat.router, prefix="/api")

# Static / Frontend Routes
@app.get("/slides/{slide_name}")
async def serve_slide(slide_name: str):
    html_path = settings.SLIDES_DIR / slide_name
    if not html_path.exists():
        raise HTTPException(status_code=404, detail=f"HTML slide not found: {slide_name}")
    return FileResponse(html_path)

@app.get("/")
@app.get("/index.html")
@app.get("/codebase/index.html")
async def root():
    return FileResponse(settings.STATIC_DIR / "index.html")

app.mount("/", StaticFiles(directory=settings.STATIC_DIR), name="static")

if __name__ == "__main__":
    print(f"Serving at http://{settings.HOST}:{settings.PORT}/")
    uvicorn.run("server:app", host=settings.HOST, port=settings.PORT, reload=True)
