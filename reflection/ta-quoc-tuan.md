# Reflection — Tạ Quốc Tuấn

## MSSV
2A202601114

## Vai trò
Build prototype (UI + API call)

---

## 1. Phần mình trực tiếp làm

- Xây dựng codebase/prototype: giao diện cho phép bôi đen text và nhập câu hỏi
- Tích hợp Gemini API call: gọi API với system prompt đã viết, xử lý response
- Mock phần bôi đen slide: dùng text input thay vì integrate thật vào VLearn
- Xử lý các trạng thái UI: loading, error, success, out-of-scope

---

## 2. AI đã hỗ trợ như thế nào

- Dùng AI để viết UI component với Tailwind CSS cho phần bôi đen text và hiển thị kết quả
- AI gợi ý cách xử lý response từ Gemini API (parse JSON, xử lý error)
- Nhờ AI viết code mock data để test UI khi chưa có API thật

---

## 3. Một case fail của nhóm và bài học rút ra

- Case fail: Khi test prototype với input rất ngắn (1 từ), AI vẫn cố trả lời thay vì hỏi lại — không đúng spec §5 case 3
- Bài học: cần thêm validation ở frontend để check độ dài input trước khi gọi API, không nên phó thác hoàn toàn cho prompt
- Cách khắc phục: thêm check độ dài selected_text >= 10 ký tự trước khi submit

---

## 4. Liên kết với spec/eval/validation

- spec.md §4: đảm bảo prototype implement đúng thiết kế, đặc biệt phần conditional automation
- spec.md §5: xử lý đúng 4 lớp edge cases
- validation/: phản hồi từ Trần Đức Thiện về nút xóa selection chưa rõ giúp cải thiện UI
- eval/: prototype phải chạy được với golden set để đo quality

---

## 5. Ghi chép kiểm thử

- Đã test prototype với 5 cases mẫu từ golden set
- UI loading state: hoạt động tốt, hiển thị spinner khi đang gọi API
- UI out-of-scope: đúng khi từ chối với câu hỏi tóm tắt toàn bộ
- Cần cải thiện: nút xóa selection chưa đủ nổi bật
