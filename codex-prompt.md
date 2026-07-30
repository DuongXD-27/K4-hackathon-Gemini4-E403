# Prompt cho Codex sửa hệ thống slide OCR / demo

Bạn là một lập trình viên đang sửa ứng dụng demo trong repo này để làm cho hệ thống hiển thị nội dung slide đúng, tự động OCR từ slide PDF và cho phép người dùng chọn slide theo Day/lesson một cách trực quan.

## Vấn đề hiện tại

Hiện tại hệ thống có 3 vấn đề chính:

1. Khi chạy chương trình, nội dung slide có thể bị ghi đè hoặc fallback sai, dẫn tới slide bị trống hoặc hiển thị sai nội dung, ví dụ slide 1 bị trống khi demo.
2. Tất cả nội dung hiện tại được lưu trữ như một "database" tĩnh bên trong file server.py, điều này không phù hợp. Hệ thống nên lấy nội dung slide từ quy trình OCR thực tế, không phụ thuộc hoàn toàn vào dữ liệu hardcode.
3. Danh sách slide hiện tại quá ngắn và chỉ hiển thị dạng Day 1 - Slide 8. Cần thay đổi UI để người dùng có thể scroll down và chọn Day 1 hoặc Day 2, sau đó chọn slide tương ứng trong day đó.

## Mục tiêu chính

Hãy sửa hệ thống để:

- Khi server chạy, phần text hiển thị bên dưới slide phải là kết quả OCR trực tiếp từ slide PDF (hoặc từ một quy trình OCR/VLM hỗ trợ như Gemini).
- Không dùng dữ liệu nội dung slide chỉ để giả lập trong server.py như một cơ sở dữ liệu tĩnh.
- Hệ thống phải có cấu trúc dữ liệu slide rõ ràng, có thể mở rộng cho nhiều day và nhiều slide.
- UI phải cho phép chọn theo Day và Slide, ví dụ: chọn Day 1 hoặc Day 2 rồi chọn slide trong day đó.
- Khi đổi slide, hệ thống phải load đúng PDF và text OCR tương ứng.
- Nếu OCR không thành công, hệ thống nên có fallback hợp lý nhưng không làm mất toàn bộ nội dung hoặc hiển thị trống một cách sai lệch.

## Nhiệm vụ cần thực hiện

### 1) Sửa lỗi hiện tại về slide và OCR

- Kiểm tra logic hiện tại trong file server.py và giao diện index.html.
- Đảm bảo khi tải một slide, hệ thống không bị thay đổi sang một slide khác hoặc nội dung bị fallback sai.
- Fix bug khiến slide bị trống hoặc hiển thị nội dung không đúng với slide đang chọn.
- Đảm bảo mỗi slide ID được ánh xạ đúng với đúng file PDF và đúng page số.

### 2) Tách dữ liệu slide ra khỏi server.py

- Không nên giữ toàn bộ metadata slide trong một dict hardcoded trực tiếp bên trong server.py.
- Thay vào đó, hãy tạo một nguồn dữ liệu riêng cho metadata slide, ví dụ:
  - một file JSON trong thư mục data/ để lưu thông tin các day, slide và mapping tới file PDF/page tương ứng
  - hoặc một cấu trúc dữ liệu được load từ file riêng thay vì hardcode ở trong server.py
- Server phải đọc metadata từ file này khi khởi động.
- Nếu cần, có thể thêm một cache file cho OCR output để tránh phải OCR lại mỗi lần.

### 3) Cải tiến quy trình OCR

- Giữ logic OCR hiện tại bằng pypdf hoặc markitdown làm phương án đầu tiên.
- Nếu có biến môi trường như GEMINI_API_KEY, hãy tích hợp kết nối tới Gemini (VLM/LLM) để hỗ trợ OCR hoặc làm sạch text từ trang PDF.
- Nếu không có API key hoặc kết nối thất bại, hệ thống phải fallback về phương pháp OCR cục bộ.
- Không lưu API key trực tiếp vào mã nguồn; chỉ đọc từ biến môi trường.
- Chỉ dùng dữ liệu hợp lệ từ file PDF hoặc OCR thực tế. Không dùng nội dung giả lập nếu có thể tránh.

### 4) Cải thiện giao diện chọn slide

- UI hiện tại nên được đổi sao cho có vùng chọn slide rõ ràng, ví dụ:
  - một dropdown cho Day (Day 1 / Day 2 / Day 3 nếu có)
  - một dropdown hoặc list cho Slide trong day đó
  - khi người dùng chọn Day, danh sách slide tương ứng sẽ thay đổi
  - khi chọn slide, hệ thống sẽ load đúng PDF và nội dung OCR tương ứng
- Có thể dùng layout dạng sidebar left hoặc top selector, nhưng phải dễ dùng khi scroll.
- Khi người dùng cuộn xuống, vẫn có thể thay đổi slide mà không làm mất bố cục.

### 5) Tối ưu trải nghiệm demo

- Khi mở app, nên mặc định hiển thị slide đầu tiên có sẵn.
- Phần text OCR nên được render dưới khung slide, rõ ràng, có thể đọc được.
- Nếu OCR chưa có dữ liệu, hiển thị thông báo trạng thái như "Đang OCR..." hoặc "Không tìm thấy text" thay vì trống trắng.

## Yêu cầu kỹ thuật cụ thể

### Backend

- Sửa server.py để:
  - load metadata slide từ file bên ngoài thay vì hardcode toàn bộ trong dict
  - hỗ trợ endpoint GET /api/slides để trả về danh sách day và slide theo cấu trúc rõ ràng
  - hỗ trợ endpoint GET /api/ocr?slide=... để trả về text OCR cho slide đó
  - nếu có Gemini API key, gọi Gemini để trích xuất hoặc làm sạch text OCR
  - có cơ chế cache / fallback để tránh lỗi khi OCR thất bại

### Frontend

- Sửa index.html để:
  - hiển thị PDF slide trong viewer
  - hiển thị text OCR dưới viewer
  - có UI chọn Day và Slide
  - gọi đúng API khi người dùng đổi lựa chọn
  - không dùng dữ liệu cứng trong JS khi có thể tránh

### Cấu trúc dữ liệu đề xuất

Bạn có thể dùng cấu trúc JSON như sau:

```json
{
  "days": [
    {
      "id": "day1",
      "title": "Day 1",
      "slides": [
        {
          "id": "d1p1",
          "title": "Slide 1",
          "pdf": "d1-slide-hackathon.pdf",
          "page": 1
        }
      ]
    }
  ]
}
```

Nếu dữ liệu thật trong repo đã có nhiều slide, hãy tự động đọc từ thư mục data/vlearn-pack/slides hoặc các file PDF có sẵn để tạo danh sách slide. Nếu không thể tự động phát hiện đầy đủ, hãy tạo metadata tối thiểu nhưng hợp lý và có thể mở rộng.

## Tiêu chí chấp nhận

Hệ thống được xem là hoàn thành khi:

- Khi chạy server, app không còn phụ thuộc vào dữ liệu hardcoded tĩnh trong server.py để hiển thị slide nội dung.
- Người dùng có thể chọn Day 1 hoặc Day 2 và chọn slide tương ứng.
- Nội dung bên dưới slide được tạo từ OCR thực tế từ PDF, không phải từ một string giả lập cố định.
- Nếu có Gemini API, hệ thống sử dụng nó để hỗ trợ OCR; nếu không có, vẫn chạy được bằng phương pháp cục bộ.
- Không còn bug khiến slide bị rỗng hoặc hiển thị nội dung sai khi demo.

## Lưu ý quan trọng

- Hãy sửa ít nhất các file chính sau: server.py, index.html.
- Nếu cần, có thể thêm file cấu hình JSON mới hoặc file helper mới.
- Đừng hardcode API key hoặc secret vào repo.
- Hãy viết code sạch, dễ mở rộng, và có fallback phù hợp.
- Nếu một số slide không có text OCR rõ ràng, hãy giữ fallback nhưng vẫn hiển thị thông tin hữu ích thay vì blank.

## Kết quả mong muốn

Sau khi sửa, demo nên có trải nghiệm như sau:

1. Mở trang web.
2. Chọn Day 1 hoặc Day 2 từ dropdown.
3. Chọn một slide trong day đó.
4. Trên giao diện, hình ảnh slide sẽ đổi theo lựa chọn.
5. Bên dưới slide, phần text sẽ hiển thị nội dung OCR hoặc text được làm sạch từ slide đó.
6. Hệ thống có thể hoạt động tốt trong demo mà không bị lỗi slide trống hoặc nội dung sai.
