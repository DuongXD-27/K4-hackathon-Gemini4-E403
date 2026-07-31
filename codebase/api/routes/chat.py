import json
import re
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agents.react_agent import ReActAgent
from services.llm_service import llm_service

router = APIRouter()

# Khởi tạo ReAct Agent với LLM Service
agent = ReActAgent(llm_service=llm_service)

class ChatRequest(BaseModel):
    provider: str
    userText: str
    selectedText: str = ""
    fullSlideText: str = ""

from typing import Optional

class TutorResponse(BaseModel):
    answer: str
    misconception_detected: bool = False
    misconception_confidence: Optional[str] = "low"
    misconception_evidence: Optional[str] = ""
    check_question: Optional[str] = ""

def clean_json_string(raw_text: str) -> str:
    """Loại bỏ markdown code block (nếu có) để lấy JSON hợp lệ."""
    text = raw_text.strip()
    if text.startswith("```"):
        match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            return match.group(1)
    return text

@router.post("/chat", response_model=TutorResponse)
def chat_api(request: ChatRequest):
    try:
        from prompts.system_prompts import PromptManager
        
        system_prompt = PromptManager.build_tutor_prompt(
            selected_text=request.selectedText,
            full_slide_text=request.fullSlideText
        )
        
        raw_answer = agent.run(
            user_input=request.userText,
            base_system_prompt=system_prompt,
            provider=request.provider
        )
        
        # Tiền xử lý raw_answer để đảm bảo nó là JSON hợp lệ
        cleaned_json = clean_json_string(raw_answer)
        
        try:
            parsed_data = json.loads(cleaned_json)
            # Pydantic sẽ tự động validate dữ liệu khi parse vào TutorResponse
            return TutorResponse(**parsed_data)
        except json.JSONDecodeError:
            print(f"Failed to parse JSON: {raw_answer}")
            raise ValueError("LLM did not return a valid JSON format.")
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
