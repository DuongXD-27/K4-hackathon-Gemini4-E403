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

        # .env for API keys
        if path == "/.env":
            self.send_file(ROOT / ".env", "text/plain; charset=utf-8")
            return

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


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Serving Comprehension Gap Detector at http://{HOST}:{PORT}/")
    server.serve_forever()
