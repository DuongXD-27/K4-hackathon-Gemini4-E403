import json
import urllib.request
import urllib.error

from core.config import settings

class LLMService:
    def _call_gemini(self, system_prompt: str, user_text: str) -> str:
        key = settings.GEMINI_API_KEY
        if not key:
            raise Exception("Missing GEMINI_API_KEY")
        model = settings.GEMINI_MODEL
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        payload = {
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": user_text}]}]
        }
        req = urllib.request.Request(
            url, 
            data=json.dumps(payload).encode("utf-8"), 
            headers={"Content-Type": "application/json"}
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            res_json = json.loads(response.read().decode("utf-8"))
            return res_json["candidates"][0]["content"]["parts"][0]["text"]

    def _call_openai(self, system_prompt: str, user_text: str) -> str:
        key = settings.OPENAI_API_KEY
        if not key:
            raise Exception("Missing OPENAI_API_KEY")
        model = settings.OPENAI_MODEL
        url = "https://api.openai.com/v1/chat/completions"
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ]
        }
        req = urllib.request.Request(
            url, 
            data=json.dumps(payload).encode("utf-8"), 
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"}
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            res_json = json.loads(response.read().decode("utf-8"))
            return res_json["choices"][0]["message"]["content"]

    def _call_anthropic(self, system_prompt: str, user_text: str) -> str:
        key = settings.ANTHROPIC_API_KEY
        if not key:
            raise Exception("Missing ANTHROPIC_API_KEY")
        model = settings.ANTHROPIC_MODEL
        url = "https://api.anthropic.com/v1/messages"
        payload = {
            "model": model,
            "max_tokens": 1024,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_text}]
        }
        req = urllib.request.Request(
            url, 
            data=json.dumps(payload).encode("utf-8"), 
            headers={
                "Content-Type": "application/json", 
                "x-api-key": key, 
                "anthropic-version": "2023-06-01"
            }
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            res_json = json.loads(response.read().decode("utf-8"))
            return res_json["content"][0]["text"]

    def _call_openrouter(self, system_prompt: str, user_text: str) -> str:
        key = settings.OPENROUTER_API_KEY
        if not key:
            raise Exception("Missing OPENROUTER_API_KEY")
        model = settings.OPENROUTER_MODEL
        url = "https://openrouter.ai/api/v1/chat/completions"
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ]
        }
        req = urllib.request.Request(
            url, 
            data=json.dumps(payload).encode("utf-8"), 
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"}
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            res_json = json.loads(response.read().decode("utf-8"))
            return res_json["choices"][0]["message"]["content"]

    def generate_response(self, provider: str, system_prompt: str, user_text: str) -> str:
        if provider == "gemini":
            return self._call_gemini(system_prompt, user_text)
        elif provider == "openai":
            return self._call_openai(system_prompt, user_text)
        elif provider == "anthropic":
            return self._call_anthropic(system_prompt, user_text)
        elif provider == "openrouter":
            return self._call_openrouter(system_prompt, user_text)
        else:
            raise ValueError(f"Unknown provider: {provider}")

llm_service = LLMService()
