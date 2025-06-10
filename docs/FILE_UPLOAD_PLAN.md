# File Upload Feature Plan

## Tổng quan

Hệ thống hỗ trợ người dùng upload file để làm nguồn tri thức (knowledge) cho từng space. Có 2 kiểu upload file chính:

- **Upload file từ máy tính (Local File Upload)**
- **Upload file từ Google Drive (Google Drive File Upload)**

Tất cả file upload (dù từ local hay Google Drive) đều được xử lý embedding (tách chunk, tạo vector) để phục vụ search và trả lời trong từng space.

### Cải tiến UI/UX: Dropdown cho nút Upload File

- Khi người dùng click vào biểu tượng `Paperclip` (kẹp giấy), một dropdown menu sẽ xuất hiện.
- Menu này sẽ cung cấp 2 tùy chọn:
  1. **Upload từ máy tính (Local File Upload)**: Kích hoạt input file `type="file"` hiện có.
  2. **Chọn từ Google Drive (Google Drive File Upload)**: Bắt đầu luồng tích hợp Google Picker.
- Mục tiêu: Gom nhóm các tùy chọn upload, cải thiện trải nghiệm người dùng.

---

## 1. Upload file từ máy tính (Local File Upload)

### Luồng hoạt động

1. User click "New Space" hoặc "Upload File" trong một space.
2. User click vào biểu tượng `Paperclip` và chọn "Upload từ máy tính" từ dropdown.
3. User chọn file qua `<input type="file" />` (có thể chọn nhiều file).
4. File được lưu vào state (chỉ là reference, chưa upload).
5. Khi user nhấn "Create Space" (hoặc xác nhận upload):
   - Frontend upload file lên backend.
   - Backend đọc nội dung file, tách chunk, embedding.
   - Lưu vector embedding vào database, gắn với space_id.
   - (Không lưu file gốc nếu không cần, chỉ lưu embedding và metadata.)
6. Nếu user cancel, không upload, không embedding, không sinh rác.

### Lưu ý

- Giới hạn số lượng và dung lượng file upload.
- Chỉ upload và embedding khi user xác nhận.
- Có thể hiển thị trạng thái "Đang xử lý..." khi embedding.

---

## 2. Upload file từ Google Drive (Google Drive File Upload)

### Luồng hoạt động

1. User click "Chọn file từ Google Drive" trong dialog tạo space hoặc upload file.
2. User click vào biểu tượng `Paperclip` và chọn "Chọn từ Google Drive" từ dropdown.
3. App mở Google Picker API để user chọn file trên Google Drive.
4. Khi user chọn file, frontend lưu fileId (và metadata) vào state (chưa tải file).
5. Khi user nhấn "Create Space" (hoặc xác nhận upload):
   - Frontend gửi fileId và access token Google lên backend.
   - Backend dùng Google Drive API tải nội dung file về.
   - Backend tách chunk, embedding nội dung file.
   - Lưu vector embedding vào database, gắn với space_id.
   - (Không lưu file gốc nếu không cần, chỉ lưu embedding và metadata.)
6. Nếu user cancel, không tải file, không embedding, không sinh rác.

### Lưu ý

- Cần xin quyền Google Drive (OAuth, scope: drive.readonly).
- Chỉ tải file và embedding khi user xác nhận.
- Có thể hiển thị trạng thái "Đang xử lý..." khi embedding.

---

## 3. Tính năng upload file hiện tại

- Hiện tại chỉ hỗ trợ upload file từ local.
- File được upload lên backend, xử lý embedding, lưu vector vào DB.
- Không lưu file gốc nếu không cần.
- Không hỗ trợ upload từ Google Drive.

---

## 4. Tổng kết

- **Tất cả tính năng upload file** sẽ có 2 kiểu:
  1. Upload file từ máy tính (local)
  2. Upload file từ Google Drive
- Cả hai đều chỉ lưu embedding (vector) và metadata, không lưu file gốc nếu không cần.
- Chỉ upload/embedding khi user xác nhận tạo space hoặc upload file.
- Nếu user cancel, không sinh rác trong hệ thống.
