# Reflection — Nguyễn Tuấn Phong

## MSSV
2A202601038

## Vai trò
Validation + demo script

---

## 1. Phần mình trực tiếp làm

- Phụ trách validation CP5: liên hệ 3 học viên K3/K4 để test prototype
- Ghi nhận feedback từ vòng user test: Trương Minh Hoàng, Đỗ Nhật Minh, Trần Đức Thiện
- Viết validation/README.md: tổng hợp feedback, điểm mạnh, điểm cần cải thiện
- Chuẩn bị demo script cho CP6: chuẩn bị flow demo, slide 6 trang

---

## 2. AI đã hỗ trợ như thế nào

- Dùng AI để viết script hỏi validation (3 câu hỏi chuẩn sau khi test)
- AI hỗ trợ tổng hợp feedback từ 3 người thành 1 báo cáo ngắn gọn
- Nhờ AI gợi ý cách trình bày demo 6 trang theo guide §5.1

---

## 3. Một case fail của nhóm và bài học rút ra

- Case fail: Khi hỏi Đỗ Nhật Minh về câu hỏi out-of-scope, mình ghi nhận feedback "hơi tiếc là phần câu hỏi kiểm tra nhanh hơi ngắn" nhưng không truyền lại ngay cho Công để fix prompt
- Bài học: feedback từ validation cần được chuyển thành action items cụ thể ngay, không nên chờ tổng hợp cuối cùng
- Cách khắc phục: đã bổ sung action items vào validation/README.md và thông báo lại cho nhóm

---

## 4. Liên kết với spec/eval/validation

- validation/: toàn bộ feedback CP5 từ 3 người test
- spec.md §8: kế hoạch validation CP5 đã được thực hiện đúng theo kế hoạch
- eval/: kết quả validation bổ sung 2 insights mới cho golden set (selection ngắn, nút xóa selection)
- feedback đã chuyển thành: cần bổ sung case R05 cho selection 1 từ vào golden set

---

## 5. Ghi chép kiểm thử

- Validation với 3 học viên: Trương Minh Hoàng, Đỗ Nhật Minh, Trần Đức Thiện
- Insight chính: AI phát hiện misconception đúng + có citation [trang X], từ chối out-of-scope lịch sự
- Điểm cần cải thiện: câu hỏi kiểm tra hơi ngắn, nút xóa selection chưa rõ, AI cố trả lời khi selection quá ngắn
- Tỷ lệ user sẽ dùng thật: 3/3 học viên cho biết sẽ dùng khi làm lab
