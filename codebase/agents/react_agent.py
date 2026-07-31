from core.config import settings
from prompts.system_prompts import PromptManager
from tools.registry import tool_registry

class ReActAgent:
    """
    Placeholder cho ReAct Agent sẽ được implement trong tương lai.
    Agent này sẽ:
    1. Nhận câu hỏi từ user.
    2. Đưa ra Thought -> Action (Tool Calling) -> Observation vòng lặp.
    3. Trả về Final Answer.
    """
    
    def __init__(self, llm_service):
        self.llm_service = llm_service
        self.tools = tool_registry
        
    def run(self, user_input: str, base_system_prompt: str, provider: str) -> str:
        # Hiện tại, do chưa implement loop, ta fallback về việc gọi LLM bình thường
        # Trong tương lai, chỗ này sẽ là vòng lặp ReAct
        
        # Ví dụ chuẩn bị ReAct prompt
        # react_prompt = PromptManager.get_react_agent_prompt(self.tools.get_tool_descriptions())
        # full_system_prompt = base_system_prompt + "\n" + react_prompt
        
        full_system_prompt = base_system_prompt
        
        return self.llm_service.generate_response(
            provider, 
            full_system_prompt, 
            user_input
        )
