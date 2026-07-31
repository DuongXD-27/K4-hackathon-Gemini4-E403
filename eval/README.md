# Evaluation Log

## Kết quả các lượt chạy

| Lượt | Ngày | % pass | Ghi chú |
|---|---|---|---|
| Lượt 1 | 31/07/2026 | 90.9% | 20/22 pass. Bị 1 false positive (báo nhầm) ở case N05 và 1 false negative (bỏ sót) ở case G03. Đã có 0 case bịa citation. Vượt quality bar (>= 70%, <= 2 false positives). |

## Chi tiết các lượt

### Lượt 1 (31/07/2026)

- Tổng cases: 22
- Pass: 20
- Fail: 2

**False positives:**
- N05 (Agile là gì?): AI flag là misconception trong khi đây là câu hỏi thường, không có claim sai từ học viên

**False negatives:**
- G03 (nhầm RAG với fine-tuning): AI không phát hiện ra misconception

**Chất lượng citation:**
- 0 case bịa citation — tất cả citation đều trace được về transcript

## Quality Bar

> "Đạt khi >= 70% case qua bộ (đúng theo định nghĩa từng chiều), VÀ 0 case nào bịa citation, VÀ <=2 false positive misconception flag trong bộ 20 case"

**Kết luận:** Vượt quality bar
