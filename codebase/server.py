from __future__ import annotations

import base64
import json
import mimetypes
import os
import re
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse


HOST = "127.0.0.1"
PORT = int(os.environ.get("PORT", "8000"))
ROOT = Path(__file__).resolve().parents[1]
CODEBASE = ROOT / "codebase"
SLIDES_DIR = ROOT / "data" / "vlearn-pack" / "slides"
MANIFEST_PATH = ROOT / "data" / "slide_manifest.json"
OCR_CACHE_DIR = ROOT / "data" / "ocr-cache"


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


def estimate_pdf_page_count(pdf_path: Path) -> int:
    data = pdf_path.read_bytes()
    counts = [int(item) for item in re.findall(rb"/Count\s+(\d+)", data)]
    return max(counts) if counts else len(re.findall(rb"/Type\s*/Page\b", data))


def load_manifest() -> dict:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    for day in manifest.get("days", []):
        pdf_path = SLIDES_DIR / day["pdf"]
        if pdf_path.exists() and not day.get("page_count"):
            day["page_count"] = estimate_pdf_page_count(pdf_path)
    return manifest


MANIFEST = load_manifest()


def build_slide_index() -> tuple[dict[str, dict], set[str]]:
    slides: dict[str, dict] = {}
    allowed_pdfs: set[str] = set()
    for day in MANIFEST.get("days", []):
        pdf = day["pdf"]
        allowed_pdfs.add(pdf)
        page_count = int(day.get("page_count") or estimate_pdf_page_count(SLIDES_DIR / pdf))
        day["page_count"] = page_count
        day_slides = []
        for page in range(1, page_count + 1):
            slide_id = f"{day['id']}-p{page}"
            slide = {
                "id": slide_id,
                "day_id": day["id"],
                "day_title": day["title"],
                "badge": day.get("badge", day["title"]),
                "title": f"{day.get('slide_title_prefix', day['title'] + ' — Slide')} {page}",
                "pdf": pdf,
                "page": page,
                "page_count": page_count,
            }
            slides[slide_id] = slide
            day_slides.append(slide)
        day["slides"] = day_slides
    return slides, allowed_pdfs


SLIDES, ALLOWED_PDFS = build_slide_index()


def cache_path(slide_id: str) -> Path:
    return OCR_CACHE_DIR / f"{slide_id}.json"


def read_cached_ocr(slide_id: str) -> tuple[str, str] | None:
    path = cache_path(slide_id)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        text = str(data.get("text", "")).strip()
        source = str(data.get("source", "cache"))
        return (text, source) if text else None
    except Exception:
        return None


def write_cached_ocr(slide_id: str, text: str, source: str) -> None:
    OCR_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path(slide_id).write_text(
        json.dumps({"text": text, "source": source}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def extract_page_with_pypdf(pdf_path: Path, page_number: int) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        from PyPDF2 import PdfReader  # type: ignore

    reader = PdfReader(str(pdf_path))
    index = max(0, page_number - 1)
    if index >= len(reader.pages):
        return ""
    return reader.pages[index].extract_text() or ""


def extract_with_markitdown(pdf_path: Path, page_number: int) -> str:
    from markitdown import MarkItDown

    result = MarkItDown().convert(str(pdf_path))
    text = getattr(result, "text_content", "") or ""
    # MarkItDown usually returns the whole PDF. Keep the result useful even if page slicing is unavailable.
    return f"[PDF: {pdf_path.name}, page target: {page_number}]\n{text}".strip()


def extract_with_gemini(pdf_path: Path, page_number: int) -> str:
    if ENV.get("GEMINI_OCR_ENABLED") != "1":
        return ""
    api_key = ENV.get("GEMINI_API_KEY")
    if not api_key:
        return ""

    model = ENV.get("GEMINI_OCR_MODEL") or ENV.get("GEMINI_MODEL") or "gemini-2.0-flash"
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    pdf_data = base64.b64encode(pdf_path.read_bytes()).decode("ascii")
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            "Trích xuất text OCR sạch từ trang "
                            f"{page_number} của file PDF này. Chỉ trả về nội dung của trang đó, "
                            "giữ tiếng Việt, bỏ header/footer lặp lại nếu không cần thiết."
                        )
                    },
                    {"inline_data": {"mime_type": "application/pdf", "data": pdf_data}},
                ]
            }
        ]
    }
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=12) as response:
        data = json.loads(response.read().decode("utf-8"))
    return data["candidates"][0]["content"]["parts"][0]["text"]


def extract_slide_text(slide_id: str) -> tuple[str, str]:
    cached = read_cached_ocr(slide_id)
    if cached:
        return cached[0], f"cache/{cached[1]}"

    slide = SLIDES[slide_id]
    pdf_path = SLIDES_DIR / slide["pdf"]
    page_number = int(slide["page"])

    extractors = (
        ("pypdf", lambda: extract_page_with_pypdf(pdf_path, page_number)),
        ("markitdown", lambda: extract_with_markitdown(pdf_path, page_number)),
        ("gemini", lambda: extract_with_gemini(pdf_path, page_number)),
    )
    for source, extractor in extractors:
        try:
            text = extractor().strip()
            if text:
                write_cached_ocr(slide_id, text, source)
                return text, source
        except Exception:
            continue

    fallback = (
        f"Không trích xuất được text OCR cho {slide['day_title']} — trang {page_number}.\n"
        f"PDF: {slide['pdf']}\n"
        "Vui lòng kiểm tra nội dung trực tiếp trong viewer phía trên hoặc cài pypdf/markitdown để OCR cục bộ."
    )
    return fallback, "fallback"


def public_manifest() -> dict:
    return {
        "days": [
            {
                "id": day["id"],
                "title": day["title"],
                "badge": day.get("badge", day["title"]),
                "pdf": day["pdf"],
                "page_count": day["page_count"],
                "slides": day["slides"],
            }
            for day in MANIFEST.get("days", [])
        ]
    }


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

    def do_HEAD(self) -> None:
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        if path.startswith("/data/vlearn-pack/slides/"):
            name = Path(path.removeprefix("/data/vlearn-pack/slides/")).name
            if name in ALLOWED_PDFS:
                pdf_path = SLIDES_DIR / name
                self.send_response(200)
                self.send_header("Content-Type", "application/pdf")
                self.send_header("Content-Length", str(pdf_path.stat().st_size))
                self.end_headers()
                return
        self.send_error(404)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = unquote(parsed.path)

        if path in ("/", "/index.html", "/codebase/index.html"):
            self.send_file(CODEBASE / "index.html", "text/html; charset=utf-8")
            return

        if path == "/.env":
            env_path = ROOT / ".env"
            self.send_file(env_path, "text/plain; charset=utf-8")
            return

        if path == "/api/slides":
            self.send_json(public_manifest())
            return

        if path == "/api/ocr":
            slide_id = parse_qs(parsed.query).get("slide", [""])[0]
            if slide_id not in SLIDES:
                self.send_json({"error": "Unknown slide id"}, 404)
                return
            text, source = extract_slide_text(slide_id)
            slide = SLIDES[slide_id]
            self.send_json({
                "slide": slide_id,
                "page": slide["page"],
                "page_count": slide["page_count"],
                "pdf": slide["pdf"],
                "text": text,
                "source": source,
            })
            return

        if path.startswith("/slides/"):
            name = Path(path.removeprefix("/slides/")).name
            if name not in ALLOWED_PDFS:
                self.send_error(404, "Unknown slide PDF")
                return
            self.send_file(SLIDES_DIR / name, "application/pdf")
            return

        if path.startswith("/data/vlearn-pack/slides/"):
            name = Path(path.removeprefix("/data/vlearn-pack/slides/")).name
            if name not in ALLOWED_PDFS:
                self.send_error(404, "Unknown slide PDF")
                return
            self.send_file(SLIDES_DIR / name, "application/pdf")
            return

        self.send_error(404)


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Serving Comprehension Gap Detector at http://{HOST}:{PORT}/")
    print("Slide metadata:", MANIFEST_PATH)
    print("Optional OCR packages: pip install pypdf markitdown")
    server.serve_forever()
