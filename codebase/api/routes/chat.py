from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
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

@router.post("/chat", response_class=PlainTextResponse)
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
        return raw_answer
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
