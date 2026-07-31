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
    systemPrompt: str

@router.post("/chat", response_class=PlainTextResponse)
def chat_api(request: ChatRequest):
    try:
        # Gọi Agent thay vì gọi trực tiếp LLM Service. 
        # Tương lai agent.run() sẽ xử lý tool calling loop.
        raw_answer = agent.run(
            user_input=request.userText,
            base_system_prompt=request.systemPrompt,
            provider=request.provider
        )
        return raw_answer
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
