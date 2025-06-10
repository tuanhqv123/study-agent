# Google Custom Search API Setup Guide

## Bước 1: Tạo Google Cloud Project và API Key

1. Truy cập [Google Cloud Console](https://console.cloud.google.com/)
2. Tạo project mới hoặc chọn project có sẵn
3. Vào **APIs & Services** > **Library**
4. Tìm và enable **Custom Search API**
5. Vào **APIs & Services** > **Credentials**
6. Click **Create Credentials** > **API Key**
7. Copy API Key (đây là `GOOGLE_API_KEY`)

## Bước 2: Tạo Custom Search Engine

1. Truy cập [Programmable Search Engine](https://programmablesearchengine.google.com/)
2. Click **Get Started** và đăng nhập Google
3. Click **Add** để tạo search engine mới
4. **Sites to search**: Để trống hoặc nhập `*` để search toàn web
5. **Name**: Đặt tên cho search engine
6. Click **Create**

## Bước 3: Cấu hình Search Engine

1. Trong control panel của search engine vừa tạo
2. Vào tab **Setup**
3. Copy **Search engine ID** (đây là `GOOGLE_SEARCH_ENGINE_ID`)
4. Vào tab **Features**
5. Bật **Search the entire web** nếu muốn search toàn web

## Bước 4: Cập nhật credentials trong code

Sửa file `backend/app/services/web_search_service.py`:

```python
self.GOOGLE_API_KEY = "YOUR_ACTUAL_API_KEY_HERE"
self.GOOGLE_SEARCH_ENGINE_ID = "YOUR_ACTUAL_SEARCH_ENGINE_ID_HERE"
```

## Giới hạn sử dụng

- **Free tier**: 100 queries/ngày
- **Paid tier**: $5 cho 1000 queries đầu tiên, sau đó $0.50/1000 queries

## So sánh với Brave Search

| Feature          | Brave Search               | Google Custom Search                   |
| ---------------- | -------------------------- | -------------------------------------- |
| Free queries     | Không rõ                   | 100/ngày                               |
| Paid plan        | Không rõ                   | $5/1000 queries                        |
| Setup complexity | Đơn giản (chỉ cần API key) | Phức tạp hơn (API key + Search Engine) |
| Search quality   | Tốt                        | Rất tốt (Google)                       |
| Language support | Tốt                        | Excellent                              |

## Output thay đổi

Response structure khác nhau:

**Brave Search:**

```json
{
  "web": {
    "results": [
      {
        "title": "...",
        "url": "...",
        "description": "..."
      }
    ]
  }
}
```

**Google Custom Search:**

```json
{
  "items": [
    {
      "title": "...",
      "link": "...",
      "snippet": "..."
    }
  ]
}
```

**Về chất lượng kết quả:**

- Google có thể cho kết quả chính xác và relevant hơn
- Google có better ranking algorithm
- Google hỗ trợ nhiều tính năng advanced hơn (safe search, language restriction, etc.)
