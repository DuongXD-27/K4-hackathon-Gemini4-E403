import re
from providers import call_llm
from tools import TOOLS
from prompts import REACT_SYSTEM_PROMPT

class ReActAgent:
    def __init__(self):
        self.system_prompt = REACT_SYSTEM_PROMPT
        self.max_iterations = 4

    def run(self, user_query: str, slide_id: str) -> str:
        prompt = self.system_prompt + f"\n\nNgữ cảnh hiện tại: Học viên đang xem slide có ID: '{slide_id}'.\nCâu hỏi của học viên: {user_query}\n"
        
        for i in range(self.max_iterations):
            print(f"--- ReAct Iteration {i+1} ---")
            try:
                response = call_llm(prompt)
            except Exception as e:
                print(f"LLM Error: {e}")
                return '```json\n{"answer": "Lỗi kết nối LLM trên backend.", "has_misconception": false, "misconception": "", "check_question": ""}\n```'
            
            print(f"LLM Response:\n{response}\n")
            
            # Check for Final Answer first
            final_answer_match = re.search(r"Final Answer:\s*(.*)", response, re.DOTALL | re.IGNORECASE)
            if final_answer_match:
                return final_answer_match.group(1).strip()
            
            # Check for Action
            action_match = re.search(r"Action:\s*([a-zA-Z0-9_]+)", response, re.IGNORECASE)
            action_input_match = re.search(r"Action Input:\s*(.+)", response, re.IGNORECASE)
            
            if action_match and action_input_match:
                action = action_match.group(1).strip()
                action_input = action_input_match.group(1).strip().strip("\"'")
                
                if action in TOOLS:
                    print(f"Agent gọi công cụ: {action}({action_input})")
                    try:
                        observation = TOOLS[action](action_input)
                    except Exception as e:
                        observation = f"Lỗi khi chạy công cụ {action}: {type(e).__name__} - {str(e)}"
                else:
                    observation = f"Công cụ {action} không tồn tại."
                
                print(f"Observation: {observation}")
                prompt += f"\n{response}\nObservation: {observation}\n"
            else:
                # Ép agent ra Final Answer nếu quên xuất ra Action/Final Answer
                prompt += f"\n{response}\nLỗi: Không tìm thấy 'Action' và 'Action Input', cũng không có 'Final Answer:'. Hãy cung cấp 'Final Answer:' hoặc 'Action:'.\n"
                
        return '```json\n{"answer": "Xin lỗi, tôi không thể xử lý câu hỏi sau nhiều bước suy nghĩ.", "has_misconception": false, "misconception": "", "check_question": ""}\n```'
