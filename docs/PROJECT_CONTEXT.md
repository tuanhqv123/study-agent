# Project Context: Study Assistant for PTIT

## 1. Overview

The **Study Assistant for PTIT** is a chat-based application that helps students manage schedules, look up exam timetables, ask academic questions, and perform document QA using local AI models.

## 2. Target Users

- **PTIT students** seeking quick access to class and exam schedules.
- **Users** needing AI-driven academic support (Q&A, summaries).
- **Developers/Admins** who want a modular, self-hosted solution.

## 3. Key Features

- **Multi-model AI chat**: Qwen, Gemma, etc., via LM Studio API.
- **Schedule lookup**: Retrieve class/exam calendars from PTIT API.
- **File upload & QA**: Extract, chunk, embed PDF/DOCX and answer questions.
- **Web search integration**: Brave Search scraping + vector search.
- **Real-time streaming**: Server-Sent Events or OpenAI-style streaming.

## 4. Architecture & Tech Stack

- **Backend**: Python, Flask, LM Studio HTTP API.
- **Frontend**: React (Vite), TailwindCSS, Radix UI, Supabase Auth.
- **Database & Storage**: Supabase (PostgreSQL + pgvector), Supabase Storage.

## 5. Data Flow

1. **User request** → Frontend sends to Flask `/chat` endpoint.
2. **Classification** → LM Studio classifies into schedule, exam, date, general, etc.
3. **Context gathering** → Call relevant services (schedule, exam, file, web).
4. **Embedding** → Generate vectors for question + context chunks.
5. **Vector search** → Retrieve top-k chunks via Supabase RPC.
6. **Prompt assembly** → Build system + user messages.
7. **Model call** → LM Studio `/v1/chat/completions` with streaming.
8. **Response & Logging** → Stream back to UI and save in DB.

## 6. AI Model Integration

### Vector Embedding

```python
from sentence_transformers import SentenceTransformer

# Initialize embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')
# Encode chunks or query
vectors = model.encode(chunks, batch_size=8)
# Store/query with Supabase pgvector
```

### Supabase RPC for Similarity Search

```python
# Query top-k relevant chunks
query_result = supabase_client.rpc(
    'match_embeddings',
    {
        'query_embedding': query_vector,
        'match_file_ids': file_ids,
        'match_threshold': 0.7,
        'match_count': top_k
    }
).execute()
results = query_result.data
```

### LM Studio HTTP Calls

```python
import httpx

def classify_query_lmstudio(query: str) -> str:
    url = 'http://localhost:1234/v1/chat/completions'
    payload = {
        'messages': [
            {'role': 'system', 'content': 'Classify the user query.'},
            {'role': 'user', 'content': query}
        ],
        'temperature': 0.0,
        'max_tokens': 16
    }
    resp = httpx.post(url, json=payload)
    return resp.json()['choices'][0]['message']['content']
```

### Prompt Template

```python
SYSTEM_PROMPT = """
You are a Study Assistant for PTIT students.
Use the context below to answer the question.
{context}
"""
# Format with joined context chunks
formatted_prompt = SYSTEM_PROMPT.format(context=context_text)
```

## 7. Authentication & Storage

- **Supabase Auth** for user signup/login (JWT).
- **Supabase Storage** for file uploads.
- **PostgreSQL + pgvector** for embedding storage and vector search.

## 8. Deployment & Environment

- **Local LM Studio** server hosting Qwen/Gemma models.
- Flask app with environment variables for Supabase and LM Studio.
- Frontend served via Vite or static build behind CDN.

## 9. Next Steps

- Add **streaming support** (`stream=True`) for `/v1/chat/completions`.
- Improve **time parsing** with combined regex & LM Studio.
- Enhance **UI/UX** for mobile responsiveness and accessibility.
