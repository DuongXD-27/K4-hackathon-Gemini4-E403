MOCK_SLIDES_OCR = {
    "slide_1": "Few-shot prompting cung cấp ví dụ trong prompt lúc inference — model không học gì thêm, trọng số không thay đổi. Fine-tuning thì cập nhật trọng số model bằng cách huấn luyện lại trên tập dữ liệu mới.",
    "slide_2": "Retrieval-Augmented Generation (RAG) kết hợp LLM với một cơ sở tri thức bên ngoài để giảm hallucination bằng cách truy xuất thông tin liên quan trước khi sinh văn bản."
}

def get_slide_ocr(slide_id: str) -> str:
    """
    Lấy nội dung OCR của một slide cụ thể.
    """
    return MOCK_SLIDES_OCR.get(slide_id, f"Không tìm thấy nội dung OCR cho slide ID: {slide_id}")

TOOLS = {
    "get_slide_ocr": get_slide_ocr
}
