# Validation Log — CP5

## Người thực hiện validation

Nguyễn Tuấn Phong — 2A202601038

## Phương pháp validation

- Task giao: "Dùng cái này để hiểu đoạn slide sau" (giao đoạn slide thật từ data pack)
- 3 câu hỏi sau khi dùng: (1) Điều gì khó hiểu nhất? (2) Kết quả AI bạn có tin không — vì sao? (3) Bạn có dùng thật không — vì sao/vì sao chưa?

## Feedback từ vòng user test

### [1] Trương Minh Hoàng — học viên K3

> "Lúc đầu mình cứ tưởng AI chỉ trả lời như ChatGPT thôi, nhưng bôi đen đoạn về RAG trong slide day01 rồi hỏi 'RAG có cần train lại model không', nó trả lời đúng kèm [trang 14] luôn. Đặc biệt cái phần 'Có thể bạn đang nhầm' hiện ra đúng chỗ mình đang lẫn lộn giữa RAG và fine-tuning, đọc xong hiểu ngay. Mình sẽ xài thật khi làm lab."

- Diem manh: phat hien dung misconception, co citation [trang 14]
- Diem can thieu: chua co

### [2] Đỗ Nhật Minh — học viên K3

> "Mình thử hỏi câu ngoài scope kiểu 'Tóm tắt toàn bộ day01 cho tôi' thì nó từ chối nhẹ nhàng, hướng dẫn mình bôi đen đoạn cụ thể thay vì kiểu máy móc 'không thể'. Cảm giác như hỏi thầy chứ không phải hỏi chatbot. Hơi tiếc là phần câu hỏi kiểm tra nhanh hơi ngắn, đôi khi mình muốn AI giải thích kỹ hơn chỗ mình đang nhầm."

- Diem manh: tu choi lich suu + huong dan, cam giac nhu hoi thay
- Diem can thieu: cau hoi kiem tra ngan, muon giai thich ky hon

### [3] Trần Đức Thiện — học viên K3

> "Mình bôi đen đoạn về top_p rồi hỏi 'top_p với temperature khác nhau chỗ nào' thì AI sinh câu hỏi kiểm tra ngay 'Nếu muốn output đa dạng mà vẫn đúng trọng tâm thì dùng cái nào?' — đúng chỗ mình đang lấn cấn. Cái này hơn hẳn tutor cũ chỉ trả lời xong là hết. Nhưng khi bôi đen nhầm 1 từ thì AI vẫn cố trả lời, hơi vô duyên — nên có nút xóa selection rõ hơn."

- Diem manh: check-question dung trong tam, tot hon tutor cu
- Diem can thieu: nut xoa selection chua ro, AI van co tra loi khi selection nham

## Tổng hợp điểm cần cải thiện

1. Câu hỏi kiểm tra hơi ngắn, cần giải thích kỹ hơn chỗ học viên đang nhầm
2. Nút xóa selection chưa rõ ràng, cần nổi bật hơn
3. AI nên từ chối hoặc cảnh báo khi selection quá ngắn/vô nghĩa thay vì cố trả lời
