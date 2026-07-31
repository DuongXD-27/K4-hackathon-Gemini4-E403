# Comprehension Gap Detector — Gemini4 · Zone 4 E403

## Thành viên nhóm


| MSSV        | Họ và tên          |
| ----------- | --------------------- |
| 2A202601966 | Nguyễn Tuấn Dương |
| 2A202601732 | Nguyễn Hữu Công    |
| 2A202601114 | Tạ Quốc Tuấn       |
| 2A202601038 | Nguyễn Tuấn Phong   |

## Phân công có tên


| Phần                                   | Người phụ trách   |
| --------------------------------------- | --------------------- |
| spec.md + evidence + mining data        | Nguyễn Tuấn Dương |
| Prompt engineering + golden set (eval/) | Nguyễn Hữu Công    |
| Build prototype (UI + API call)         | Tạ Quốc Tuấn       |
| Validation + demo script                | Nguyễn Tuấn Phong   |

## Cấu trúc repo

```
repo/
├── README.md          ← thành viên (mã HV + tên) + phân công có tên từng phần
├── spec.md            ← AI Spec theo 03-template-ai-spec.md
├── demo-slides.pdf    ← slide 6 trang theo 02-guide.md §5.1
├── codebase/          ← prototype (ghi rõ phần nào mock)
├── eval/              ← golden set + bảng kết quả các lượt chạy
├── validation/        ← feedback log từ vòng user test
└── reflection/       ← mỗi người 1 file
```

## Sản phẩm

Comprehension Gap Detector — AI tutor phát hiện hiểu lầm (misconception) của học viên khoá AI Thực Chiến khi đang đọc slide trên VLearn, đồng thời sinh câu hỏi kiểm tra (check-question) để xác nhận lại kiến thức đúng.
