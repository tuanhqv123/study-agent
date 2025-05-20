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
