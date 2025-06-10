# Study Assistant for PTITer — Project Context

## 1. Mục tiêu dự án

Dự án **Study Assistant for PTITer** ra đời nhằm hỗ trợ sinh viên PTIT quản lý, tra cứu lịch học, lịch thi, hỏi đáp học thuật, và tra cứu thông tin nhanh chóng bằng AI. Ứng dụng giúp sinh viên tiết kiệm thời gian,giảm tương tác với trên web, chủ động hơn trong việc học tập và chuẩn bị cho các kỳ thi.

---

## 2. Đối tượng sử dụng

- **Sinh viên PTIT**: Người dùng chính, cần tra cứu lịch học, lịch thi, hỏi đáp học thuật, tìm kiếm tài liệu nhanh.

---

## 3. Bối cảnh sử dụng

- **Trước khi đến trường**: Sinh viên kiểm tra lịch học, lịch thi trong tuần/ngày.
- **Khi đến trường không rõ lịch đã thay đổi**: Sử dụng chatbot đã đăng nhập liên kết với tài khoản cá nhân để có thể hỏi lịch học tức thì, không cần đăng nhập lại.
- **Khi cần hỏi đáp nhanh**: Sinh viên hỏi AI về kiến thức, bài tập, hoặc các vấn đề học thuật.
- **Khi cần tra cứu thông tin ngoài trường**: Bật web search để AI trả lời dựa trên nguồn web mới nhất.
- **Khi cần tham khảo tài liệu**: Upload file PDF, AI sẽ trả lời dựa trên nội dung file.

---

## 4. Các tính năng chính

- **Chat AI đa mô hình**: Chọn Qwen, Gemma, ... để hỏi đáp học thuật.
- **Tra cứu lịch học/lịch thi**: Tự động phân tích câu hỏi, lấy dữ liệu từ API trường, trả về chi tiết từng buổi học/thi.
- **Web search**: Tích hợp Brave Search, trả về kết quả kèm nguồn tham khảo.
- **Upload file**: Hỏi đáp dựa trên nội dung file PDF/tài liệu.
- **Quản lý phiên chat, lưu lịch sử**: Dễ dàng xem lại các cuộc hội thoại cũ.

---

## 5. Phạm vi & ràng buộc

- **Chỉ hỗ trợ sinh viên PTIT** (có thể mở rộng).
- **Dữ liệu lịch học/lịch thi** lấy từ API trường, cần tài khoản sinh viên.
- **AI chỉ trả lời trong phạm vi học thuật, không hỗ trợ các chủ đề ngoài lề.**
- **Bảo mật thông tin đăng nhập**: Không lưu mật khẩu thô, chỉ lưu token truy cập.

---

## 6. Định hướng phát triển

- **Tích hợp thêm nhiều mô hình AI mới, hỗ trợ tiếng Việt tốt hơn.**
- **Thêm tính năng nhắc nhở lịch học, lịch thi qua email/Zalo.**
- **Mở rộng cho giảng viên, hỗ trợ quản lý lớp học.**
- **Tích hợp thêm các nguồn web search khác, hỗ trợ tìm kiếm tài liệu học thuật.**
- **Cải thiện UI/UX, hỗ trợ mobile.**

---

## 7. Tech stack & Hạ tầng triển khai

- **Frontend:** ReactJS (Vite), TailwindCSS, sử dụng các component hiện đại, responsive.
- **Backend:** Python (Flask), tổ chức dạng REST API, dễ mở rộng, dễ tích hợp với các AI model cục bộ.
- **AI Model:** Tích hợp các mô hình local (Qwen, Gemma, ...), giao tiếp qua LM Studio, có thể mở rộng thêm model mới dễ dàng.
- **Web Search:** Brave Search API, trả về kết quả kèm nguồn, giúp AI trả lời sát thực tế.
- **File Storage:** Hỗ trợ upload file, lưu trữ và truy vấn nội dung file để AI trả lời theo ngữ cảnh tài liệu.
- **Database & Auth:**
  - **Supabase** được sử dụng như một Backend as a Service (BaaS):
    - Cung cấp sẵn hệ thống xác thực (auth), lưu trữ dữ liệu (PostgreSQL), API realtime, file storage, ...
    - Giúp triển khai hệ thống nhanh, không cần tự dựng backend phức tạp.
    - Có thể **self-host** Supabase trên server riêng nếu muốn kiểm soát dữ liệu tuyệt đối (Supabase là mã nguồn mở, có thể cài đặt trên hạ tầng của bạn).
    - **PostgreSQL** là hệ quản trị cơ sở dữ liệu chính, mạnh mẽ, mở rộng tốt, hỗ trợ truy vấn phức tạp, realtime, trigger, ...
    - Dữ liệu lịch sử chat, user, file, ... đều lưu trong PostgreSQL của Supabase.

**Lợi ích khi dùng Supabase:**

- Đăng ký tài khoản, xác thực, lưu trữ dữ liệu, file, ... chỉ cần cấu hình, không cần code backend thủ công.
- Có dashboard quản lý dữ liệu, user, truy vấn, ... rất tiện lợi cho dev và admin.
- Dễ dàng tích hợp với các dịch vụ khác, mở rộng quy mô khi cần.
- Có thể chuyển sang self-host bất cứ lúc nào nếu muốn kiểm soát toàn bộ dữ liệu và bảo mật.

---

## 8. Technical Reports & Architecture Overview

### 8.1 Data Flow & Persistence

- **Ingestion Pipelines**: Web scraper gathers raw HTML/text → passed to parsing service (`web_scraper_service`) → cleaned and chunked.
- **Embedding**: Chunks sent to embedding model (Sentence Transformer) → vectors written to `embeddings` table in Supabase (PostgreSQL + pgvector).
- **Chat Logging**: User queries and AI responses persisted in `chat_messages` and `sessions` tables via `ai_service` and `file_service`.
- **Schedule Data**: `ptit_auth_service` fetches token, `schedule_service` & `exam_schedule_service` call PTIT API → results cached in `schedules` and `exam_schedules` tables.
- **File Storage**: Uploaded PDFs processed by `file_service`, text extracted via `trafilatura`, embeddings stored alongside metadata in `files` and `embeddings` tables.

### 8.2 Backend Features

- **Routes Layer** (`app/routes`): REST endpoints for authentication, chat (`/chat`), file operations (`/file`), PTIT data (`/ptit/schedule`, `/ptit/exams`), and web search (`/web-search`).
- **Services Layer** (`app/services`): Business logic divided into:
  - `query_classifier`: keyword + LMStudio classification.
  - `ai_service` / `lmstudio_service`: local model orchestration for chat & classification.
  - `web_search_service`: calls Brave Search API, aggregates results.
  - `web_scraper_service`: performs scraping and immediate vector embedding.
  - `schedule_service` & `exam_schedule_service`: fetch and normalize PTIT calendar.
  - `file_service`: handles upload, parsing, chunking, embedding.
  - `ptit_auth_service`: Supabase auth integration for PTIT credentials.
- **Data Layer** (`app/lib/supabase.py`): Single Supabase client for all DB/Storage operations, environment-based configuration.
- **Utilities**: Logging, error handling, and configuration management (`app/utils/logger.py`, `app/config`).

### 8.3 Frontend Features & UI Analysis

- **Framework & Styling**: React (Vite) + TailwindCSS for rapid, responsive UI.
- **Component Structure** (`src/components`):
  - `ChatInterface`: orchestrates message list and input.
  - `ChatInput`: handles user text entry, file attachments.
  - `AgentSelector`: switch between Qwen, Gemma, etc.
  - `MessageItem`: renders user vs AI messages, supports markdown.
  - `Settings`: model selection, preferences.
  - `Login` / `Signup` / `ProtectedRoute`: auth flow.
- **State & Data Fetching**: Uses Supabase JS client in `src/lib/supabase.js` and custom hooks for realtime chat updates and file lists.
- **UX Considerations**: Loading states, error feedback, mobile-first layout.

### 8.4 API Calls & Integration

- **Authentication**:
  - POST `/auth/signup`, `/auth/login` → returns JWT, stored in browser storage.
  - GET `/auth/refresh` → refresh token flow.
- **Chat**:
  - POST `/chat` with `{ message, agent, contextIds }` → streamed response via Server-Sent Events / polling.
- **File Operations**:
  - POST `/file/upload` (multipart) → returns `fileId`.
  - GET `/file/:id/embeddings` → retrieve embeddings for context.
- **PTIT Schedule**:
  - GET `/ptit/schedule?date=YYYY-MM-DD` → returns class timetable.
  - GET `/ptit/exams?week=this|next|last` → returns exam schedule.
- **Web Search & Scraping**:
  - GET `/web-search?query=...` → returns top-k search results + embedded context.

### 8.5 Maintainability & Future Development

- **Modular Design**: Clear separation of concerns (routes → services → data lib) simplifies adding new features or AI models.
- **Config-Driven Agents**: `config/agents.py` allows registering new local models (e.g., Qwen3) without code changes.
- **Scalability**: Leverage Supabase for autoscaling DB and storage; swap in self-hosted Supabase if needed.
- **Testing Strategy**: Unit tests for services (`test/`), integration tests for API routes; CI pipelines to run `pytest` and linting.
- **Extensibility**: Adding new scraping sources, embedding models, or UI themes is straightforward by following existing service/component patterns.
- **Documentation & Versioning**: Maintained docs in `/docs`, version controlled; future API changes tracked via OpenAPI spec and changelogs.

---

## 9. Chi tiết hoạt động từng tính năng (User/Dev Friendly)

### 9.1 Upload file PDF/tài liệu

- **Bước 1:** Người dùng chọn file PDF trên giao diện (component `ChatInput` hoặc `FileUpload`).
- **Bước 2:** Frontend gửi file qua API `POST /file/upload` (dạng multipart/form-data).
- **Bước 3:** Backend nhận file, lưu vào Supabase Storage, đồng thời:
  - Trích xuất text từ PDF (dùng `trafilatura` hoặc `pdfplumber`).
  - Chia nhỏ nội dung thành các đoạn (chunk) hợp lý.
  - Tạo vector embedding cho từng đoạn (dùng Sentence Transformer).
  - Lưu metadata file vào bảng `files`, lưu vector vào bảng `embeddings` (liên kết với fileId).
- **Bước 4:** Khi người dùng hỏi về nội dung file, hệ thống sẽ:
  - Embed câu hỏi thành vector.
  - Tìm các đoạn tài liệu liên quan nhất (vector search trong DB).
  - Đưa các đoạn này vào prompt cho AI model trả lời.
- **Ví dụ:**
  - User upload file "Bai_giang_ML.pdf".
  - Hỏi: "Giải thích thuật toán KNN trong tài liệu vừa upload?"
  - Hệ thống tìm đoạn nói về KNN trong file, trả lời dựa trên nội dung đó.

### 9.2 Web Search & Scraping

- **Bước 1:** User bật/tắt chế độ web search trên UI (nút toggle hoặc trong Settings).
- **Bước 2:** Khi hỏi, nếu bật web search, backend gọi Brave Search API lấy top kết quả.
- **Bước 3:** Backend scrape nội dung từng link, trích xuất text, chunk, tạo embedding và lưu vào DB.
- **Bước 4:** Embed câu hỏi, tìm các đoạn web liên quan nhất, đưa vào prompt cho AI trả lời.
- **Ví dụ:**
  - User hỏi: "Cập nhật mới nhất về lịch thi PTIT năm nay?"
  - Hệ thống search web, scrape các trang trường, lấy đoạn liên quan, trả lời dựa trên nguồn mới nhất.

### 9.3 Chat AI đa mô hình

- **Bước 1:** User chọn model (Qwen, Gemma, ...), nhập câu hỏi.
- **Bước 2:** Frontend gửi API `POST /chat` với `{message, agent, contextIds}`.
- **Bước 3:** Backend lấy context (từ file, web, lịch học...), tạo prompt, gửi sang model local (qua LM Studio API hoặc trực tiếp).
- **Bước 4:** Model trả về câu trả lời, lưu vào DB, trả về frontend hiển thị.
- **Ví dụ:**
  - User chọn Qwen, hỏi: "Lịch học tuần này của mình thế nào?"
  - Hệ thống lấy lịch từ API trường, đưa vào prompt, Qwen trả lời chi tiết.

### 9.4 Tra cứu lịch học/lịch thi

- **Bước 1:** User hỏi về lịch học/lịch thi ("Lịch học ngày mai?", "Khi nào thi Toán?").
- **Bước 2:** Backend phân loại câu hỏi (`query_classifier`), xác định là truy vấn lịch.
- **Bước 3:** Gọi API trường (qua `schedule_service` hoặc `exam_schedule_service`), lấy dữ liệu.
- **Bước 4:** Trả về thông tin chi tiết từng buổi học/thi, kèm thời gian, địa điểm.
- **Ví dụ:**
  - User hỏi: "Lịch thi tuần sau của mình?"
  - Hệ thống trả về danh sách môn, ngày, giờ, phòng thi tuần sau.

### 9.5 Quản lý phiên chat, lưu lịch sử

- **Bước 1:** Mỗi cuộc chat được gán sessionId, lưu vào bảng `sessions`.
- **Bước 2:** Mỗi message (user/AI) lưu vào `chat_messages` (liên kết sessionId, userId).
- **Bước 3:** User có thể xem lại lịch sử chat, tìm kiếm theo từ khóa, tải về nếu muốn.

### 9.6 Đăng nhập, xác thực, bảo mật

- **Bước 1:** User đăng ký/đăng nhập qua Supabase Auth (email/password hoặc OAuth).
- **Bước 2:** Nhận JWT, lưu ở localStorage frontend, gửi kèm mỗi API call.
- **Bước 3:** Backend xác thực token, phân quyền truy cập dữ liệu.
- **Bước 4:** Không lưu mật khẩu thô, chỉ lưu token truy cập, bảo mật tối đa.

---

## 10. Tổng kết logic hoạt động (Minh họa tổng quan)

1. **User upload file → Backend xử lý, tạo vector → Lưu DB → Khi hỏi sẽ tìm đoạn liên quan trong file để trả lời.**
2. **User hỏi có bật web search → Backend search, scrape, embed, lưu DB → Tìm đoạn web liên quan để trả lời.**
3. **User hỏi về lịch học/thi → Backend lấy dữ liệu từ API trường → Trả về chi tiết.**
4. **Mọi câu hỏi đều được phân loại, chọn model phù hợp, lấy context (file/web/lịch) → Đưa vào prompt cho AI trả lời → Lưu lịch sử.**

Các flow này đều có thể mở rộng, thay đổi model, thêm nguồn dữ liệu, hoặc tích hợp thêm tính năng mới mà không ảnh hưởng hệ thống cũ nhờ thiết kế module rõ ràng.

---

## 11. Chi tiết kỹ thuật xử lý và lưu trữ dữ liệu

### 11.1 Xử lý và lưu trữ File PDF

#### A. Quá trình xử lý file PDF sau khi upload

1. **Thu nhận file từ frontend**:

   ```python
   # Trong file file_routes.py
   @file_routes.route('/upload', methods=['POST'])
   def upload_file():
       if 'file' not in request.files:
           return jsonify({'error': 'No file part'}), 400
       file = request.files['file']
       # Gọi file_service xử lý tiếp
       result = file_service.process_uploaded_file(file, current_user.id)
       return jsonify(result)
   ```

2. **Trích xuất text từ PDF (file_service.py)**:

   ```python
   def process_uploaded_file(self, file, user_id):
       # 1. Lưu file tạm lên filesystem
       temp_path = os.path.join(TEMP_DIR, secure_filename(file.filename))
       file.save(temp_path)

       # 2. Trích xuất text
       if file.filename.endswith('.pdf'):
           text_content = self.extract_text_from_pdf(temp_path)
       else:
           # Xử lý các loại file khác (docx, txt, etc.)
           text_content = self.extract_text_from_other(temp_path)

       # 3. Chia chunk văn bản
       chunks = self.chunk_text(text_content, chunk_size=1000, overlap=200)

       # 4. Upload file lên Supabase Storage
       file_path = f"files/{user_id}/{uuid.uuid4()}_{secure_filename(file.filename)}"
       storage_result = supabase_client.storage.from_('documents').upload(
           file_path,
           open(temp_path, 'rb'),
           file_options={'content-type': mimetypes.guess_type(file.filename)[0]}
       )

       # 5. Tạo record trong bảng 'files'
       file_record = {
           'user_id': user_id,
           'filename': file.filename,
           'storage_path': file_path,
           'file_type': os.path.splitext(file.filename)[1],
           'size_bytes': os.path.getsize(temp_path),
           'text_content': text_content[:1000],  # Lưu preview text
           'chunk_count': len(chunks)
       }
       file_insert = supabase_client.table('files').insert(file_record).execute()
       file_id = file_insert.data[0]['id']

       # 6. Tạo embeddings và lưu vào DB
       self.create_and_store_embeddings(chunks, file_id, user_id)

       # 7. Xóa file tạm
       os.remove(temp_path)

       return {'file_id': file_id, 'filename': file.filename}
   ```

3. **Trích xuất text chi tiết**:

   ```python
   def extract_text_from_pdf(self, file_path):
       text = ""
       # Sử dụng pdfplumber để trích xuất text
       with pdfplumber.open(file_path) as pdf:
           for page in pdf.pages:
               page_text = page.extract_text() or ""
               text += page_text + "\n\n"

               # Trích xuất text từ bảng
               tables = page.extract_tables()
               for table in tables:
                   for row in table:
                       row_text = " | ".join([cell or "" for cell in row])
                       text += row_text + "\n"
                   text += "\n"

       # Làm sạch text
       text = re.sub(r'\n{3,}', '\n\n', text)  # Giảm dòng trống thừa
       text = re.sub(r'\s{2,}', ' ', text)     # Giảm khoảng trắng thừa

       return text
   ```

4. **Chia đoạn (chunking) cho hiệu quả embedding**:

   ```python
   def chunk_text(self, text, chunk_size=1000, overlap=200):
       """Chia text thành các chunk nhỏ để embedding hiệu quả"""
       chunks = []
       # Chia theo đoạn văn, giữ nguyên văn khi có thể
       paragraphs = [p for p in text.split('\n\n') if p.strip()]

       current_chunk = ""
       for para in paragraphs:
           # Nếu đoạn văn quá dài, cần chia nhỏ theo câu
           if len(para) > chunk_size:
               sentences = nltk.sent_tokenize(para)
               for sentence in sentences:
                   if len(current_chunk) + len(sentence) <= chunk_size:
                       current_chunk += sentence + " "
                   else:
                       chunks.append(current_chunk.strip())
                       # Tạo overlap để giữ nguyên ngữ cảnh
                       current_chunk = current_chunk[-overlap:] if overlap > 0 else ""
                       current_chunk += sentence + " "
           else:
               # Thêm đoạn vào chunk hiện tại nếu không vượt quá kích thước
               if len(current_chunk) + len(para) <= chunk_size:
                   current_chunk += para + "\n\n"
               else:
                   chunks.append(current_chunk.strip())
                   current_chunk = para + "\n\n"

       # Thêm phần chunk cuối nếu có
       if current_chunk:
           chunks.append(current_chunk.strip())

       return chunks
   ```

5. **Tạo vector embedding và lưu vào database**:

   ```python
   def create_and_store_embeddings(self, chunks, file_id, user_id):
       """Tạo và lưu vector embedding cho các chunks"""
       # Khởi tạo Sentence Transformer model
       embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

       # Batch embedding để tối ưu hiệu năng
       chunk_vectors = embedding_model.encode(chunks, batch_size=8, show_progress_bar=True)

       # Chuẩn bị dữ liệu để insert vào DB
       embeddings_data = []
       for i, (chunk, vector) in enumerate(zip(chunks, chunk_vectors)):
           embeddings_data.append({
               'file_id': file_id,
               'user_id': user_id,
               'chunk_index': i,
               'content': chunk,
               'embedding': vector.tolist(),  # Chuyển numpy array thành list để lưu vào JSON
               'embedding_model': 'all-MiniLM-L6-v2'
           })

       # Insert vào Supabase DB (bảng embeddings sử dụng pgvector extension)
       for batch in chunks_by_size(embeddings_data, 20):  # Insert theo batches 20 records
           supabase_client.table('embeddings').insert(batch).execute()

       logger.info(f"Created {len(chunks)} embeddings for file {file_id}")
       return len(chunks)
   ```

#### B. Cấu trúc DB và truy vấn vector similarity

1. **Cấu trúc bảng trong Supabase**:

   ```sql
   -- Schema cho bảng files
   CREATE TABLE files (
     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
     user_id UUID REFERENCES auth.users(id) NOT NULL,
     filename TEXT NOT NULL,
     storage_path TEXT NOT NULL,
     file_type TEXT,
     size_bytes INTEGER,
     text_content TEXT,  -- Preview/summary text
     chunk_count INTEGER,
     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
     updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );

   -- Schema cho bảng embeddings (yêu cầu pgvector extension)
   CREATE EXTENSION IF NOT EXISTS vector;

   CREATE TABLE embeddings (
     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
     file_id UUID REFERENCES files(id) ON DELETE CASCADE,
     user_id UUID REFERENCES auth.users(id),
     chunk_index INTEGER,
     content TEXT NOT NULL,
     embedding vector(384),  -- Dimension phụ thuộc vào model (384 cho all-MiniLM-L6-v2)
     embedding_model TEXT,
     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );

   -- Index vector để tìm kiếm nhanh với cosine similarity
   CREATE INDEX embeddings_vector_idx ON embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
   ```

2. **Truy vấn vector similarity khi người dùng hỏi về nội dung file**:

   ```python
   def get_relevant_context(self, query, file_ids, top_k=5):
       """Lấy các đoạn văn liên quan nhất dựa trên vector similarity"""
       # Embed câu hỏi của user
       embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
       query_vector = embedding_model.encode(query).tolist()

       # Truy vấn Supabase với hàm vector_cosine_similarity() của pgvector
       query_result = supabase_client.rpc(
           'match_embeddings',  # Function đã tạo trong Supabase
           {
               'query_embedding': query_vector,
               'match_file_ids': file_ids,  # List các file_id để filter
               'match_threshold': 0.7,      # Cosine similarity threshold
               'match_count': top_k         # Số lượng kết quả trả về
           }
       ).execute()

       # Kết quả chứa content và similarity score
       results = query_result.data

       # Format context từ các đoạn liên quan
       context_parts = []
       for item in results:
           context_parts.append({
               'content': item['content'],
               'similarity': item['similarity'],
               'file_id': item['file_id'],
               'filename': item['filename']
           })

       return context_parts
   ```

3. **SQL Function trong Supabase để tìm kiếm vector:**
   ```sql
   CREATE OR REPLACE FUNCTION match_embeddings(
       query_embedding vector(384),
       match_file_ids uuid[],
       match_threshold float DEFAULT 0.7,
       match_count int DEFAULT 5
   ) RETURNS TABLE (
       id uuid,
       file_id uuid,
       filename text,
       content text,
       similarity float
   )
   LANGUAGE plpgsql
   AS $$
   BEGIN
       RETURN QUERY
       SELECT
           e.id,
           e.file_id,
           f.filename,
           e.content,
           1 - (e.embedding <=> query_embedding) as similarity
       FROM
           embeddings e
       JOIN
           files f ON e.file_id = f.id
       WHERE
           e.file_id = ANY(match_file_ids)
           AND 1 - (e.embedding <=> query_embedding) > match_threshold
       ORDER BY
           similarity DESC
       LIMIT
           match_count;
   END;
   $$;
   ```

### 11.2 Web Search & Scraping - Xử lý & Lưu trữ chi tiết

#### A. Quy trình Web Search & Scraping

1. **Gọi Brave Search API để lấy kết quả tìm kiếm**:

   ```python
   # web_search_service.py
   def search_web(self, query, num_results=5):
       """Tìm kiếm web qua Brave Search API"""
       headers = {
           'Accept': 'application/json',
           'Accept-Encoding': 'gzip',
           'X-Subscription-Token': BRAVE_API_KEY
       }

       params = {
           'q': query,
           'count': num_results,
           'freshness': 'month',  # Chỉ lấy kết quả trong vòng 1 tháng
           'textDecorations': 'false',
           'textFormat': 'raw'
       }

       response = requests.get(
           'https://api.search.brave.com/res/v1/web/search',
           headers=headers,
           params=params
       )

       if response.status_code != 200:
           logger.error(f"Brave Search API error: {response.status_code} {response.text}")
           return []

       results = response.json().get('web', {}).get('results', [])
       return [
           {
               'title': result.get('title', ''),
               'url': result.get('url', ''),
               'description': result.get('description', '')
           }
           for result in results
       ]
   ```

2. **Scrape từng URL và xử lý nội dung**:

   ```python
   # web_scraper_service.py
   def scrape_and_process_urls(self, search_results):
       """Scrape và xử lý từng URL từ kết quả tìm kiếm"""
       processed_results = []

       for result in search_results:
           url = result['url']
           try:
               # Sử dụng trafilatura để extract web content chất lượng cao
               downloaded = trafilatura.fetch_url(url)
               if downloaded:
                   # Extract text và clean HTML/boilerplate
                   extracted_text = trafilatura.extract(
                       downloaded,
                       include_links=True,
                       include_images=False,
                       include_tables=True,
                       output_format='text',
                       with_metadata=False
                   )

                   if extracted_text:
                       # Chia text thành chunks để embedding
                       chunks = self.chunk_text(extracted_text)

                       # Thêm thông tin URL vào mỗi chunk để tracking nguồn
                       processed_chunks = [
                           {
                               'url': url,
                               'title': result['title'],
                               'content': chunk,
                               'search_snippet': result.get('description', '')
                           }
                           for chunk in chunks
                       ]

                       # Ngay lập tức tạo embeddings và lưu vào DB
                       self.create_and_store_web_embeddings(processed_chunks)

                       processed_results.extend(processed_chunks)
           except Exception as e:
               logger.error(f"Error scraping {url}: {str(e)}")

       return processed_results
   ```

3. **Tạo embeddings và lưu vào bảng web_embeddings**:

   ```python
   def create_and_store_web_embeddings(self, processed_chunks):
       """Tạo và lưu embeddings cho web content"""
       if not processed_chunks:
           return []

       # Extract content từ chunks để batch encode
       contents = [chunk['content'] for chunk in processed_chunks]

       # Sử dụng cùng model với file để nhất quán
       embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
       chunk_vectors = embedding_model.encode(contents, batch_size=8)

       # Chuẩn bị dữ liệu để insert vào DB
       web_embeddings = []
       for i, (chunk, vector) in enumerate(zip(processed_chunks, chunk_vectors)):
           web_embeddings.append({
               'url': chunk['url'],
               'title': chunk['title'],
               'content': chunk['content'],
               'search_snippet': chunk['search_snippet'],
               'embedding': vector.tolist(),
               'embedding_model': 'all-MiniLM-L6-v2',
               'timestamp': datetime.utcnow().isoformat()
           })

       # Insert vào Supabase DB (web_embeddings table)
       supabase_client.table('web_embeddings').insert(web_embeddings).execute()

       return len(web_embeddings)
   ```

#### B. Cấu trúc bảng web_embeddings và truy vấn

1. **Schema cho bảng web_embeddings**:

   ```sql
   CREATE TABLE web_embeddings (
     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
     url TEXT NOT NULL,
     title TEXT,
     content TEXT NOT NULL,
     search_snippet TEXT,
     embedding VECTOR(384),  -- Cùng dimension với file embeddings
     embedding_model TEXT,
     timestamp TIMESTAMP WITH TIME ZONE,
     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );

   -- Index vector cho cosine similarity
   CREATE INDEX web_embeddings_vector_idx ON web_embeddings
     USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

   -- Index timestamp để easily purge old entries
   CREATE INDEX web_embeddings_timestamp_idx ON web_embeddings(timestamp);
   ```

2. **Truy vấn tìm web content liên quan đến câu hỏi**:

   ```python
   def get_relevant_web_context(self, query, top_k=5):
       """Lấy web content liên quan đến query của user"""
       # Embed câu hỏi
       embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
       query_vector = embedding_model.encode(query).tolist()

       # Truy vấn Supabase với pgvector similarity
       query_result = supabase_client.rpc(
           'match_web_embeddings',
           {
               'query_embedding': query_vector,
               'match_threshold': 0.7,
               'match_count': top_k
           }
       ).execute()

       results = query_result.data

       # Format kết quả và thêm nguồn trích dẫn
       context_with_sources = []
       for item in results:
           context_with_sources.append({
               'content': item['content'],
               'url': item['url'],
               'title': item['title'],
               'similarity': item['similarity']
           })

       return context_with_sources
   ```

3. **SQL Function để truy vấn web_embeddings**:
   ```sql
   CREATE OR REPLACE FUNCTION match_web_embeddings(
       query_embedding VECTOR(384),
       match_threshold FLOAT DEFAULT 0.7,
       match_count INT DEFAULT 5
   ) RETURNS TABLE (
       id UUID,
       url TEXT,
       title TEXT,
       content TEXT,
       similarity FLOAT
   )
   LANGUAGE plpgsql
   AS $$
   BEGIN
       RETURN QUERY
       SELECT
           we.id,
           we.url,
           we.title,
           we.content,
           1 - (we.embedding <=> query_embedding) as similarity
       FROM
           web_embeddings we
       WHERE
           1 - (we.embedding <=> query_embedding) > match_threshold
       ORDER BY
           similarity DESC,
           we.timestamp DESC  -- Ưu tiên nội dung mới hơn
       LIMIT
           match_count;
   END;
   $$;
   ```

### 11.3 Cách AI trả lời truy vấn dựa trên vector contexts

1. **Quy trình hoàn chỉnh để trả lời truy vấn**:

   ```python
   # ai_service.py
   def answer_with_context(self, query, agent_name, file_ids=None, use_web_search=False):
       """Trả lời câu hỏi với context từ file và/hoặc web search"""
       contexts = []
       sources = []

       # 1. Lấy context từ file nếu có
       if file_ids:
           file_contexts = file_service.get_relevant_context(query, file_ids)
           contexts.extend([ctx['content'] for ctx in file_contexts])
           sources.extend([
               {'type': 'file', 'filename': ctx['filename'], 'similarity': ctx['similarity']}
               for ctx in file_contexts
           ])

       # 2. Lấy context từ web nếu bật chế độ web search
       if use_web_search:
           # Tìm kiếm web
           search_results = web_search_service.search_web(query)

           # Scrape và tạo embeddings nếu cần
           web_scraper_service.scrape_and_process_urls(search_results)

           # Lấy context liên quan
           web_contexts = web_search_service.get_relevant_web_context(query)
           contexts.extend([ctx['content'] for ctx in web_contexts])
           sources.extend([
               {'type': 'web', 'url': ctx['url'], 'title': ctx['title'], 'similarity': ctx['similarity']}
               for ctx in web_contexts
           ])

       # 3. Xây dựng prompt với context
       system_prompt = """Bạn là trợ lý học tập thông minh cho sinh viên PTIT.
       Sử dụng thông tin trong ngữ cảnh sau đây để trả lời câu hỏi của người dùng.
       Nếu thông tin không có trong ngữ cảnh, hãy nói rằng bạn không có đủ thông tin để trả lời.

       Ngữ cảnh:
       {context}
       """

       # Join tất cả context với separator
       context_text = "\n\n---\n\n".join(contexts)
       formatted_prompt = system_prompt.format(context=context_text)

       # 4. Gọi model trả lời (qua LM Studio nếu dùng local, hoặc trực tiếp)
       if agent_name == "lmstudio":
           response = self.call_lmstudio_api(formatted_prompt, query)
       else:
           # Xử lý theo từng loại agent khác
           response = self.call_specific_agent(agent_name, formatted_prompt, query)

       # 5. Trả về kết quả với sources để citation
       return {
           'answer': response,
           'sources': sources
       }
   ```

2. **Gọi LM Studio API (local model)**:

   ```python
   def call_lmstudio_api(self, system_prompt, user_query):
       """Gọi model qua LM Studio API"""
       api_url = "http://localhost:1234/v1/chat/completions"

       headers = {
           "Content-Type": "application/json"
       }

       data = {
           "messages": [
               {"role": "system", "content": system_prompt},
               {"role": "user", "content": user_query}
           ],
           "temperature": 0.7,
           "max_tokens": 1024
       }

       response = requests.post(api_url, headers=headers, json=data)

       if response.status_code == 200:
           return response.json()['choices'][0]['message']['content']
       else:
           logger.error(f"LM Studio API error: {response.status_code} {response.text}")
           return "Xin lỗi, tôi không thể trả lời ngay lúc này. Vui lòng thử lại sau."
   ```

3. **Truy vấn trực tiếp với Qwen3 local**:

   ```python
   # Local inference với Qwen3 trên macOS
   def query_qwen3_local(self, system_prompt, user_query):
       """Truy vấn Qwen3 local trực tiếp không qua LM Studio"""
       # Load tokenizer và model nếu chưa có
       if not hasattr(self, 'qwen_model') or not hasattr(self, 'qwen_tokenizer'):
           from transformers import AutoModelForCausalLM, AutoTokenizer
           import torch

           self.qwen_tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen-3B-Chat", trust_remote_code=True)

           # Sử dụng MPS (Metal Performance Shaders) backend trên macOS M-series
           self.qwen_model = AutoModelForCausalLM.from_pretrained(
               "Qwen/Qwen-3B-Chat",
               device_map="auto",  # Auto-detect MPS
               torch_dtype=torch.float16,  # Sử dụng float16 để tiết kiệm bộ nhớ
               trust_remote_code=True
           )

       # Format messages cho Qwen
       messages = [
           {"role": "system", "content": system_prompt},
           {"role": "user", "content": user_query}
       ]

       # Tokenize và generate
       response, history = self.qwen_model.chat(
           self.qwen_tokenizer,
           messages,
           history=[]
       )

       return response
   ```

Như vậy, toàn bộ quy trình xử lý vector và database đã được mô tả chi tiết, từ lúc upload file, xử lý, tạo embedding, lưu trữ, đến lúc truy vấn dữ liệu và gọi model để trả lời. Đây là flow kỹ thuật đầy đủ của tính năng semantic search dựa trên vector similarity.

---

## 12. Backend Architecture & Technical Implementation (English Documentation)

### 12.1 System Overview & Technology Stack

The Study Assistant for PTITer is built with a modern, scalable architecture that combines Flask backend with React frontend. The system leverages multiple AI models, vector databases, and external APIs to provide comprehensive educational assistance.

**Core Technologies:**

- **Backend Framework**: Flask (Python) with Blueprint-based modular routing
- **Database**: Supabase (PostgreSQL) with pgvector extension for vector operations
- **AI/ML Stack**: LM Studio for local model serving, multiple models (Qwen, Gemma, Claude)
- **Text Processing**: Sentence Transformers for embeddings, PyPDF2 for PDF extraction
- **External APIs**: Brave Search for web search, PTIT APIs for academic data
- **Authentication**: Supabase Auth with JWT tokens
- **File Storage**: Supabase Storage for uploaded documents

### 12.2 Backend Architecture & Flow Processing

#### 12.2.1 Application Structure

The Flask application follows a clean, modular architecture:

```
backend/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── routes/              # API endpoints
│   │   ├── auth.py          # Authentication routes
│   │   ├── chat.py          # Chat & AI interaction
│   │   ├── file_routes.py   # File upload/management
│   │   └── ptit_routes.py   # PTIT academic data
│   ├── services/            # Business logic layer
│   │   ├── ai_service.py    # AI model interactions
│   │   ├── file_service.py  # File processing & embeddings
│   │   ├── web_search_service.py   # Web search integration
│   │   ├── web_scraper_service.py  # Content scraping
│   │   ├── schedule_service.py     # Class schedule processing
│   │   ├── exam_schedule_service.py # Exam schedule processing
│   │   ├── ptit_auth_service.py    # PTIT authentication
│   │   └── query_classifier.py     # Query categorization
│   ├── config/              # Configuration
│   │   └── agents.py        # AI model configurations
│   ├── lib/                 # External integrations
│   │   └── supabase.py      # Database client
│   └── utils/               # Utilities
│       └── logger.py        # Logging system
└── run.py                   # Application entry point
```

#### 12.2.2 Request Processing Flow

**1. Authentication Flow:**

- User credentials are validated through Supabase Auth
- JWT tokens are issued and verified for subsequent requests
- PTIT university credentials are separately validated through institutional APIs

**2. Chat Message Processing:**

```
User Input → Query Classification → Context Retrieval → AI Processing → Response
```

**Detailed Flow:**

1. **Request Reception**: Chat endpoint receives message with metadata (agent, file context, web search flags)
2. **Query Classification**: `QueryClassifier` categorizes the query:
   - `education`: General academic questions
   - `schedule`: Class schedule queries
   - `examschedule`: Exam schedule queries
   - `date_query`: Date-specific queries
   - `uml`: UML diagram requests
   - `other`: Non-academic topics (filtered out)
3. **Context Gathering**: Based on classification:
   - File context: Retrieve relevant document chunks via vector similarity
   - Web search: Scrape and embed real-time web content
   - Academic data: Fetch schedule/exam data from PTIT APIs
4. **AI Processing**: Selected model processes query with context
5. **Response Delivery**: Formatted response with metadata returned to frontend

### 12.3 Database Design & Data Models

#### 12.3.1 Core Tables

**Users & Authentication:**

```sql
-- Managed by Supabase Auth
users (
  id UUID PRIMARY KEY,
  email TEXT,
  encrypted_password TEXT,
  created_at TIMESTAMP
)

-- User preferences and settings
user_preferences (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  preferred_agent TEXT,
  web_search_enabled BOOLEAN,
  created_at TIMESTAMP
)
```

**File Management & Vector Storage:**

```sql
-- File metadata
user_files (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  filename TEXT,
  content_type TEXT,
  file_size INTEGER,
  storage_path TEXT,
  created_at TIMESTAMP
)

-- Text chunks for semantic search
file_chunks (
  id UUID PRIMARY KEY,
  file_id UUID REFERENCES user_files(id) ON DELETE CASCADE,
  chunk_index INTEGER,
  content TEXT,
  embedding VECTOR(384),  -- pgvector extension
  created_at TIMESTAMP
)

-- Web search result storage
web_embeddings (
  id UUID PRIMARY KEY,
  chat_id UUID,
  source_url TEXT,
  title TEXT,
  content TEXT,
  embedding VECTOR(384),
  search_query TEXT,
  created_at TIMESTAMP
)
```

**Chat & Message Management:**

```sql
-- Chat sessions
chat_sessions (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  title TEXT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)

-- Individual messages
messages (
  id UUID PRIMARY KEY,
  chat_id UUID REFERENCES chat_sessions(id),
  role TEXT, -- 'user' or 'assistant'
  content TEXT,
  sources JSONB, -- Web search sources
  agent_id TEXT,
  created_at TIMESTAMP
)
```

#### 12.3.2 Vector Search Implementation

The system uses PostgreSQL's pgvector extension for efficient similarity search:

```sql
-- Create index for fast similarity search
CREATE INDEX file_chunks_embedding_idx
ON file_chunks USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Similarity search query
SELECT content, 1 - (embedding <=> $query_vector) as similarity
FROM file_chunks
WHERE file_id = $file_id
ORDER BY embedding <=> $query_vector
LIMIT 5;
```

### 12.4 AI Service Architecture

#### 12.4.1 Multi-Model Support

The `AiService` provides a unified interface for multiple AI models:

**Supported Models:**

- **Qwen (3B/7B)**: Optimized for Vietnamese and technical content
- **Gemma**: Google's efficient language model
- **Claude (via API)**: For complex reasoning tasks
- **Local Models**: Served through LM Studio

**Model Configuration:**

```python
# config/agents.py
AGENTS = {
    "qwen-3b": {
        "display_name": "Qwen 3B",
        "model": "Qwen/Qwen-3B-Chat",
        "temperature": 0.7,
        "max_tokens": 2048,
        "endpoint": "local"
    }
}
```

#### 12.4.2 Context Injection Strategies

**1. File Context Processing:**

- PDF text extraction using PyPDF2
- Chunking with semantic boundaries (sentences, paragraphs)
- Vector embedding using Sentence Transformers
- Retrieval-Augmented Generation (RAG) implementation

**2. Web Search Context:**

- Real-time web search via Brave API
- Content scraping with BeautifulSoup
- Dynamic embedding and relevance scoring
- Source attribution for transparency

**3. Academic Data Context:**

- Live integration with PTIT APIs
- Schedule/exam data formatting
- Date parsing and intelligent filtering

### 12.5 API Endpoints & Integration

#### 12.5.1 Authentication Endpoints

**POST** `/auth/verify-university-credentials`

- Validates PTIT university credentials
- Returns current semester information
- Required for schedule/exam features

**POST** `/auth/ptit-login`

- Raw PTIT authentication
- Returns detailed login response data

#### 12.5.2 Chat & AI Endpoints

**GET** `/chat/agents`

- Returns list of available AI models
- Includes model capabilities and configurations

**POST** `/chat`

- Main chat interface
- Supports multiple query types and contexts
- Request body:

```json
{
  "message": "User query",
  "agent_id": "qwen-3b",
  "web_search_enabled": true,
  "file_id": "uuid-if-file-context",
  "conversation_history": [],
  "university_credentials": {
    "username": "student_id",
    "password": "encrypted_password"
  }
}
```

**GET** `/chat/messages`

- Retrieves chat history for a session
- Supports pagination and filtering

#### 12.5.3 File Management Endpoints

**POST** `/file/upload`

- Handles multipart file upload
- Processes PDF/text files
- Creates vector embeddings
- Returns file ID for future reference

**GET** `/file/list`

- Lists user's uploaded files
- Returns metadata and upload timestamps

**DELETE** `/file/<file_id>`

- Removes file and associated embeddings
- Cascading deletion for data consistency

#### 12.5.4 Academic Data Endpoints

**GET** `/ptit/schedule`

- Retrieves class schedule for current semester
- Supports date filtering and course filtering
- Returns structured schedule data with time, location, course details

**GET** `/ptit/exam-schedule`

- Fetches exam schedule information
- Includes exam dates, times, locations, and course codes
- Supports filtering by date range

**GET** `/ptit/student-info`

- Returns authenticated student information
- Includes student ID, major, current semester

### 12.6 Security & Performance Considerations

#### 12.6.1 Authentication & Authorization

**JWT Token Management:**

- Tokens expire after 24 hours for security
- Refresh token mechanism for seamless user experience
- Secure token storage in HTTP-only cookies (production)

**Data Isolation:**

- All user data is strictly isolated by user_id
- File access controlled through user ownership verification
- Chat sessions are private and encrypted in transit

**API Rate Limiting:**

- File upload: 10 files per hour per user
- Chat messages: 60 requests per minute per user
- Web search: 20 searches per hour per user

#### 12.6.2 Performance Optimization

**Vector Search Optimization:**

- pgvector indexes for sub-second similarity search
- Batch embedding creation for efficiency
- Smart chunking strategies to balance context and speed

**Caching Strategy:**

- Academic schedule data cached for 1 hour
- Web search results cached for 30 minutes
- Model responses cached based on identical queries

**Memory Management:**

- Local AI models loaded on-demand
- Automatic cleanup of temporary files
- Connection pooling for database operations

### 12.7 Monitoring & Error Handling

#### 12.7.1 Logging System

Comprehensive logging across all components:

- Request/response logging for API debugging
- Model inference timing and performance metrics
- Error tracking with stack traces and context
- Security event logging (failed authentication, suspicious activity)

#### 12.7.2 Error Recovery

**Graceful Degradation:**

- If local AI models fail, fallback to cloud APIs
- Web search failures don't break chat functionality
- Academic API downtime handled with cached data

**User-Friendly Error Messages:**

- Technical errors translated to understandable language
- Retry mechanisms for transient failures
- Clear feedback on system limitations

### 12.8 Deployment Architecture

#### 12.8.1 Development Environment

**Local Development Stack:**

- Flask development server with hot reload
- Local Supabase instance or cloud development project
- LM Studio for local AI model serving
- Docker containers for service isolation

#### 12.8.2 Production Environment

**Infrastructure:**

- **Backend**: Containerized Flask application on cloud platform
- **Database**: Managed Supabase PostgreSQL with pgvector
- **File Storage**: Supabase Storage with CDN distribution
- **AI Models**: Mix of local GPU servers and cloud APIs

**Scaling Considerations:**

- Horizontal scaling for stateless API servers
- Load balancing for chat endpoints
- Database read replicas for query performance
- Vector search optimization with index tuning

### 12.9 Future Enhancement Roadmap

#### 12.9.1 Technical Improvements

**Advanced AI Features:**

- Multi-modal support (image, audio processing)
- Custom fine-tuned models for PTIT-specific content
- Federated learning for personalized responses

**Performance Enhancements:**

- Real-time embedding updates with streaming
- Advanced caching with Redis
- GraphQL API for flexible data fetching

#### 12.9.2 Integration Expansions

**Educational Platform Integration:**

- Learning Management System (LMS) connections
- Grade tracking and analysis
- Assignment submission assistance

**Social Features:**

- Study group formation
- Peer-to-peer knowledge sharing
- Collaborative document annotation

---

This concludes the comprehensive backend architecture documentation. The system is designed for scalability, maintainability, and extensibility while providing robust educational assistance through advanced AI and data processing capabilities.

- Retrieves class schedule for specific dates
- Supports date ranges and semester filtering

**GET** `/ptit/exam-schedule`

- Fetches exam schedules
- Supports midterm/final exam filtering

### 12.6 External Service Integrations

#### 12.6.1 PTIT API Integration

The system integrates with PTIT's internal APIs for academic data:

**Authentication Flow:**

1. Student credentials validation
2. Session token acquisition
3. API access with bearer authentication
4. Data retrieval and caching

**Data Processing:**

- Schedule parsing with Vietnamese date handling
- Exam schedule formatting and filtering
- Semester detection and management

#### 12.6.2 Web Search Integration

**Brave Search API:**

- Real-time web search capabilities
- Configurable result limits and filtering
- Source metadata preservation

**Content Scraping:**

- Intelligent content extraction
- HTML parsing and cleaning
- Text chunking for embedding

### 12.7 Performance & Scalability

#### 12.7.1 Optimization Strategies

**Database Optimization:**

- Vector indexes for fast similarity search
- Connection pooling for concurrent requests
- Query optimization for large datasets

**Caching:**

- Academic data caching to reduce API calls
- Embedding caching for repeated queries
- Session management for user context

**Async Processing:**

- Asynchronous web scraping
- Concurrent embedding generation
- Background file processing

#### 12.7.2 Error Handling & Monitoring

**Comprehensive Logging:**

- Request/response logging with timestamps
- Error tracking with stack traces
- Performance monitoring with execution times

**Graceful Degradation:**

- Fallback responses when external APIs fail
- Alternative model routing when primary model unavailable
- User-friendly error messages

### 12.8 Security & Data Privacy

#### 12.8.1 Authentication & Authorization

**Multi-layer Security:**

- Supabase Auth for user management
- JWT token validation for API access
- University credential encryption
- Session timeout management

#### 12.8.2 Data Protection

**Privacy Measures:**

- User data isolation in database
- Secure file storage with access controls
- No persistent storage of university passwords
- GDPR-compliant data handling

### 12.9 Development & Deployment

#### 12.9.1 Local Development

**Environment Setup:**

- Python virtual environment with requirements.txt
- Supabase local development setup
- LM Studio for model serving
- Environment variable configuration

**Testing Strategy:**

- Unit tests for service layers
- Integration tests for API endpoints
- Mock external dependencies for testing

#### 12.9.2 Production Deployment

**Infrastructure:**

- Cloud deployment with container orchestration
- Supabase hosted database and storage
- Load balancing for high availability
- Monitoring and alerting systems

This architecture provides a robust, scalable foundation for educational AI assistance with clear separation of concerns, comprehensive error handling, and extensible design for future enhancements.

---
