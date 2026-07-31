from __future__ import annotations

import json
import mimetypes
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse


HOST = "127.0.0.1"
PORT = int(os.environ.get("PORT", "8000"))
ROOT = Path(__file__).resolve().parents[1]
CODEBASE = ROOT / "codebase"
SLIDES_DIR = ROOT / "data" / "vlearn-pack" / "slides"


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


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        print("%s - - [%s] %s" % (self.client_address[0], self.log_date_time_string(), format % args))

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, path: Path, content_type: str | None = None) -> None:
        if not path.exists() or not path.is_file():
            self.send_error(404, "File not found")
            return
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type or mimetypes.guess_type(path.name)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = unquote(parsed.path)

        # Main app
        if path in ("/", "/index.html", "/codebase/index.html"):
            self.send_file(CODEBASE / "index.html", "text/html; charset=utf-8")
            return

        # Route /.env removed for security

        # Serve HTML slide files (e.g. /slides/ai_in_action_slides.html)
        if path.startswith("/slides/") and path.endswith(".html"):
            name = Path(path.removeprefix("/slides/")).name
            html_path = SLIDES_DIR / name
            if not html_path.exists():
                self.send_error(404, f"HTML slide not found: {name}")
                return
            self.send_file(html_path, "text/html; charset=utf-8")
            return

        self.send_error(404)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = unquote(parsed.path)

        if path == "/api/chat":
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length == 0:
                self.send_error(400, "Empty body")
                return
            body = self.rfile.read(content_length)
            data = json.loads(body.decode("utf-8"))
            
            provider = data.get("provider")
            userText = data.get("userText")
            systemPrompt = data.get("systemPrompt")
            
            import urllib.request
            import urllib.error
            
            try:
                if provider == "gemini":
                    key = ENV.get("GEMINI_API_KEY")
                    if not key: raise Exception("Missing GEMINI_API_KEY")
                    model = ENV.get("GEMINI_MODEL", "gemini-2.0-flash")
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
                    payload = {
                        "systemInstruction": { "parts": [{ "text": systemPrompt }] },
                        "contents": [{ "role": "user", "parts": [{ "text": userText }] }]
                    }
                    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
                    
                elif provider == "openai":
                    key = ENV.get("OPENAI_API_KEY")
                    if not key: raise Exception("Missing OPENAI_API_KEY")
                    model = ENV.get("OPENAI_MODEL", "gpt-4o-mini")
                    url = "https://api.openai.com/v1/chat/completions"
                    payload = {
                        "model": model,
                        "messages": [
                            { "role": "system", "content": systemPrompt },
                            { "role": "user", "content": userText }
                        ]
                    }
                    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
                    
                elif provider == "anthropic":
                    key = ENV.get("ANTHROPIC_API_KEY")
                    if not key: raise Exception("Missing ANTHROPIC_API_KEY")
                    model = ENV.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
                    url = "https://api.anthropic.com/v1/messages"
                    payload = {
                        "model": model,
                        "max_tokens": 1024,
                        "system": systemPrompt,
                        "messages": [{ "role": "user", "content": userText }]
                    }
                    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json", "x-api-key": key, "anthropic-version": "2023-06-01"})
                    
                elif provider == "openrouter":
                    key = ENV.get("OPENROUTER_API_KEY")
                    if not key: raise Exception("Missing OPENROUTER_API_KEY")
                    model = ENV.get("OPENROUTER_MODEL", "google/gemma-4-31b-it:free")
                    url = "https://openrouter.ai/api/v1/chat/completions"
                    payload = {
                        "model": model,
                        "messages": [
                            { "role": "system", "content": systemPrompt },
                            { "role": "user", "content": userText }
                        ]
                    }
                    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
                
                else:
                    self.send_error(400, "Unknown provider")
                    return

                with urllib.request.urlopen(req, timeout=30) as response:
                    res_body = response.read()
                    res_json = json.loads(res_body.decode("utf-8"))
                    
                    if provider == "gemini":
                        raw_answer = res_json["candidates"][0]["content"]["parts"][0]["text"]
                    elif provider in ("openai", "openrouter"):
                        raw_answer = res_json["choices"][0]["message"]["content"]
                    elif provider == "anthropic":
                        raw_answer = res_json["content"][0]["text"]
                    else:
                        raw_answer = "{}"
                    
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(raw_answer.encode("utf-8"))
                    
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(str(e).encode("utf-8"))
            return
            
        self.send_error(404)


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Serving Comprehension Gap Detector at http://{HOST}:{PORT}/")
    server.serve_forever()
