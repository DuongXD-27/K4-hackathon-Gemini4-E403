import os
import sys
import json
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import shutil

# Đảm bảo import được các module cùng thư mục
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ReAct_agent import ReActAgent

app = FastAPI(title="Comprehension Gap Detector API")

data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
if os.path.exists(data_path):
    app.mount("/data", StaticFiles(directory=data_path), name="data")

@app.get("/")
def read_root():
    """Trang chủ API."""
    from fastapi.responses import HTMLResponse
    import os
    index_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    from fastapi.responses import Response
    return Response(content=b"", media_type="image/x-icon", status_code=204)

@app.get("/api/slides")
def get_slides():
    """Đọc slide_manifest.json để trả về danh sách slide thực tế."""
    manifest_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "slide_manifest.json")
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        
        for day in manifest.get("days", []):
            if "slides" not in day:
                day["slides"] = []
                # Tạo mục lục slide cho mỗi trang
                for i in range(1, day.get("page_count", 29) + 1):
                    day["slides"].append({
                        "id": f"{day['id']}_p{i}",
                        "title": f"{day.get('slide_title_prefix', 'Trang')} {i}",
                        "file": day.get("pdf"),
                        "page": i,
                        "page_count": day.get("page_count"),
                        "day_id": day["id"],
                        "day_title": day["title"],
                        "pdf": day.get("pdf"),
                        "badge": day.get("badge")
                    })
        return manifest
    except Exception as e:
        return {"days": [], "error": str(e)}



@app.post("/api/upload_file")
async def upload_file(file: UploadFile = File(...)):
    """Lưu file người dùng upload và trả về đường dẫn."""
    temp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "temp")
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"file_path": os.path.join("data", "temp", file.filename)}



@app.post("/api/chat")
async def chat(request: Request):
    """Xử lý chat bằng ReAct Agent thay vì gọi trực tiếp từ frontend."""
    data = await request.json()
    user_message = data.get("question", "")
    slide_id = data.get("slide_id", "slide_1")
    provider = data.get("provider")
    
    if provider:
        os.environ["ACTIVE_PROVIDER"] = provider
        
    agent = ReActAgent()
    final_answer = agent.run(user_message, slide_id)
    
    # Parse JSON từ câu trả lời của agent
    try:
        json_str = final_answer.replace("```json", "").replace("```", "").strip()
        result = json.loads(json_str)
    except Exception as e:
        result = {
            "answer": f"Lỗi parse JSON từ LLM: {str(e)}\nRaw Answer:\n{final_answer}",
            "has_misconception": False,
            "misconception": "",
            "check_question": ""
        }
        
    return JSONResponse(content=result)

if __name__ == "__main__":
    # Để chạy: uv run uvicorn codebase.app:app --reload
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
