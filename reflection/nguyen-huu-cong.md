# Reflection — Nguyễn Hữu Công

## MSSV
2A202601732

## Vai trò
Prompt engineering + golden set (eval/)

---

## 1. Phần mình trực tiếp làm

- Phụ trách prompt engineering: viết và tinh chỉnh system prompt cho Gemini API để phát hiện misconception và sinh check-question
- Xây dựng golden set 22 cases: 8 hard cases (lớp 1-4), 10 normal cases, 4 rare cases
- Thiết kế cấu trúc evaluation: định nghĩa 4 chiều quality (Accuracy, Grounding, Refusal, Check-question)
- Chạy và ghi kết quả các lượt evaluation vào spec.md §7

---

## 2. AI đã hỗ trợ như thế nào

- Nhờ AI (Claude) gợi ý các edge cases cho golden set dựa trên chatlog thật
- Dùng AI để tạo các case test từ khóa ngắn, câu hỏi lai Anh-Việt, câu hỏi có lỗi chính tả
- AI hỗ trợ debug prompt khi gặp false positive: phân tích tại sao model flag nhầm ở case N05

---

## 3. Một case fail của nhóm và bài học rút ra

- Case fail: Lượt đầu chạy golden set, case N05 (Agile là gì?) bị false positive — AI flag là misconception trong khi đây là câu hỏi thường không có trong tài liệu, không nên flag
- Bài học: prompt cần rõ ràng hơn về việc KHÔNG flag khi câu hỏi không có trong tài liệu và học viên không claim gì sai
- Cách khắc phục: thêm instruction "Chỉ flag khi student claim something WRONG, không flag khi student hỏi thông thường"

---

## 4. Liên kết với spec/eval/validation

- eval/: toàn bộ golden set.csv và kết quả chạy do mình quản lý
- spec.md §7: kết quả evaluation 90.9% pass, quality bar được chốt
- validation/: phản hồi từ Trần Đức Thiện (về nút xóa selection) giúp mình bổ sung case hiếm cho selection ngắn/vô nghĩa

---

## 5. Ghi chép kiểm thử

- Lượt 1: 90.9% pass (20/22 cases)
- 1 false positive ở case N05 (đã fix)
- 1 false negative ở case G03 (nhầm RAG với fine-tuning — model bỏ sót)
- 0 case bịa citation
- Vượt quality bar: >= 70% và <= 2 false positives
