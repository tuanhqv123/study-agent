# Embedding & Vector Monitoring TODO

## 1. Logging & Data Collection

- [ ] Log mỗi lần truy vấn embedding (user_id, query, top_k, chunk/file trả về, điểm similarity, timestamp)
- [ ] Log số lượng embedding mới sinh ra mỗi ngày/tháng
- [ ] Log tỉ lệ truy vấn không có kết quả (no hit)

## 2. Supabase/Postgres Views

- [ ] View: Số lượng embedding mới theo ngày
- [ ] View: Top chunk/file được trả về nhiều nhất trong top K
- [ ] View: Phân phối điểm similarity (histogram)
- [ ] View: Tỉ lệ truy vấn không có kết quả
- [ ] View: Thống kê embedding theo loại dữ liệu (file, web, note, ...)

## 3. Dashboard/Frontend

- [ ] Biểu đồ số lượng embedding mới theo ngày
- [ ] Bảng top chunk được trả về nhiều nhất (kèm file, nội dung, số lần xuất hiện)
- [ ] Biểu đồ histogram/phân phối điểm similarity
- [ ] Card hiển thị tỉ lệ truy vấn không có kết quả
- [ ] Trang chi tiết: cho phép admin search lại truy vấn và xem chunk thực tế trả về

## 4. Cảnh báo & Giám sát

- [ ] Cảnh báo khi tỉ lệ no hit tăng bất thường
- [ ] Cảnh báo khi điểm similarity trung bình giảm mạnh
- [ ] Cảnh báo khi một chunk/file bị truy vấn quá nhiều (dấu hiệu bias/spam)

---

**Ghi chú:**

- Cần bổ sung log truy vấn embedding nếu backend chưa có.
- Ưu tiên log: user_id, query, top_k, chunk/file trả về, similarity, timestamp.
- Có thể mở rộng để log cả loại dữ liệu, nguồn embedding, v.v.
