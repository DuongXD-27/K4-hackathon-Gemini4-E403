# Reflection — Nguyễn Tuấn Dương

## MSSV
2A202601966

## Vai trò
spec.md + evidence + mining data

---

## 1. Phần mình trực tiếp làm

- Phụ trách spec.md: viết toàn bộ AI Spec theo template, định nghĩa sản phẩm Comprehension Gap Detector
- Mining data từ chatlog thật: phân tích 1.261 turns để tìm bằng chứng về pain point
- Khảo sát đường A: thiết kế và thu kết quả Google Form từ 23 học viên
- Điền evidence vào spec.md: tỷ lệ tutor không bao giờ hỏi check-question (0.24%), tỷ lệ từ chối (23.9%)

---

## 2. AI đã hỗ trợ như thế nào

- Nhờ AI đọc file CSV chatlog lớn và đếm các field cụ thể (asked_check_question, misconceptions, follow_ups)
- Dùng AI để viết script analyze_chatlog.py xử lý 1.261 turns
- AI hỗ trợ viết lại các observation thành ngôn ngữ spec chuẩn

---

## 3. Một case fail của nhóm và bài học rút ra

- Case fail: Lượt đầu tiên khi mining data, mình đếm sai tỷ lệ tutor trả lời không có citation (41.7%) — con số đúng nhưng interpretation sai, lúc đầu tưởng đây là vấn đề lớn cần fix trước
- Bài học: cần đọc kỹ từng case trong golden set trước khi viết spec, không nên suy diễn từ số liệu thống kê một mình
- Cách khắc phục: khi phát hiện Công gặp vấn đề với golden set, đã trao đổi lại và điều chỉnh spec cho phù hợp

---

## 4. Liên kết với spec/eval/validation

- spec.md §1-§2: toàn bộ evidence và impact do mình viết
- spec.md §8: phân công có tên để cả nhóm biết ai làm gì
- eval/: phối hợp với Công để golden set phản ánh đúng pain point đã mine
- validation/: kết quả feedback 3 người test giúp xác nhận spec đúng hướng

---

## 5. Ghi chép kiểm thử

- Đã review golden set 22 cases (20 case gốc + 2 case thêm từ chatlog thật)
- Đã chạy lượt đầu: 90.9% pass, vượt quality bar 70%
- Cần bổ sung thêm case cho lớp 2 (ambiguous) do feedback từ Đỗ Nhật Minh cho thấy AI chưa hỏi lại đủ rõ ràng
