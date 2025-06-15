# StudyAssistant - AI Study Companion

## 📋 Overview
AI-powered study assistant with document search, PTIT schedule integration, and intelligent Q&A using local LLM models.

## ✨ Features
- 📄 Document Upload & Search (PDF, DOCX, TXT)
- 🤖 AI Chat with Thinking Mode  
- 📅 PTIT Schedule Integration
- 🔍 Vector-based Semantic Search
- 🌐 Web Search Integration

## 🛠️ Requirements
- **Python 3.10+**
- **Node.js 16+** 
- **Docker** (for Redis)
- **LM Studio** (for AI models)

## 🚀 Installation & Setup
- **LM Studio**
- **Git**

### 1. Clone Repository

```bash
git clone https://github.com/tuanhqv123/study-agent.git
cd study-agent
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Build for production
npm run build
```

### 4. Redis Setup with Docker

```bash
# Start Redis container
docker run -d \
  --name studyassistant-redis \
  -p 6379:6379 \
  --restart unless-stopped \
  redis:7.2-alpine

# Verify Redis is running
docker ps | grep redis
```

### 5. LM Studio Configuration

#### Download LM Studio

1. Visit [LM Studio](https://lmstudio.ai/)
2. Download and install for your OS

#### Download Models

Search and download in LM Studio:

**Primary Model (Recommended):**

```
Publisher: lmstudio-community
Model: qwen3-4b
Purpose: Enhanced reasoning with thinking mode
Size: ~4GB
```

**Alternative Model (Lightweight):**

```
Publisher: lmstudio-community
Model: qwen3-1.7b
Purpose: Fast responses, lower memory usage
Size: ~1.7GB
```

#### Start LM Studio Server

1. Open LM Studio
2. Go to **"Local Server"** tab
3. Load your downloaded model
4. Configure settings:
   - Port: 1234 (default)
   - Context Length: 4096
   - Temperature: 0.7
5. Click **"Start Server"**

### 6. Environment Configuration

Create `.env` file in `/backend/`:

```env
# Database Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# LM Studio Configuration
LM_STUDIO_URL=http://localhost:1234/v1/chat/completions
LM_STUDIO_MODEL=qwen3-4b
LM_STUDIO_API_KEY=lm-studio

# PTIT Integration
PTIT_BASE_URL=https://qldt.ptit.edu.vn/api
PTIT_USERNAME=your_ptit_username
PTIT_PASSWORD=your_ptit_password

# Application Settings
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your_secret_key_here

# File Upload Settings
MAX_FILE_SIZE=52428800
UPLOAD_FOLDER=uploads
SUPPORTED_EXTENSIONS=pdf,docx,txt

# Google APIs
GOOGLE_SEARCH_API_KEY=your_google_api_key
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
```

### 7. Google APIs Setup

#### Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project or select existing one
3. Enable required APIs:
   - **Custom Search JSON API**
   - **Drive API** (for Google Drive integration)

#### Setup Custom Search Engine

1. Go to [Programmable Search Engine](https://programmablesearchengine.google.com/)
2. Click **"Add"** to create new search engine
3. Configure search engine:
   - **Sites to search**: Leave empty for entire web
   - **Name**: StudyAssistant Search
   - **Language**: English
4. Click **"Create"**
5. Copy **Search Engine ID**

#### Get API Credentials

1. Go to [Google Cloud Console - Credentials](https://console.cloud.google.com/apis/credentials)
2. Click **"Create Credentials"** → **"API Key"**
3. Copy the **API Key**
4. (Optional) Restrict API key:
   - Click on API key to edit
   - Under **"API restrictions"**, select:
     - Custom Search JSON API
     - Google Drive API

#### Update Environment Variables

Add to your `.env` file:

```env
# Google APIs
GOOGLE_SEARCH_API_KEY=your_google_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
GOOGLE_DRIVE_CLIENT_ID=your_drive_client_id_here
GOOGLE_DRIVE_CLIENT_SECRET=your_drive_client_secret_here
```

### 8. Supabase Database Setup

#### Create Supabase Project

1. Go to [Supabase](https://supabase.com/)
2. Create new project
3. Copy URL and anon key to `.env`

#### Create Database Tables

Run in Supabase SQL Editor:

```sql
-- Enable vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Spaces table for organizing conversations
CREATE TABLE public.spaces (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  created_at timestamp with time zone DEFAULT now(),
  user_id uuid NOT NULL,
  name text NOT NULL,
  description text,
  prompt text CHECK (char_length(prompt) <= 1000),
  CONSTRAINT spaces_pkey PRIMARY KEY (id),
  CONSTRAINT spaces_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
);

-- Chat sessions table
CREATE TABLE public.chat_sessions (
  agent_id text,
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL DEFAULT gen_random_uuid(),
  created_at timestamp with time zone DEFAULT now(),
  name text,
  space_id uuid,
  CONSTRAINT chat_sessions_pkey PRIMARY KEY (id),
  CONSTRAINT chat_sessions_space_id_fkey FOREIGN KEY (space_id) REFERENCES public.spaces(id),
  CONSTRAINT chat_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
);

-- Messages table for chat history
CREATE TABLE public.messages (
  role text,
  content text,
  sources jsonb,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  chat_id uuid DEFAULT gen_random_uuid(),
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  CONSTRAINT messages_pkey PRIMARY KEY (id),
  CONSTRAINT messages_chat_id_fkey FOREIGN KEY (chat_id) REFERENCES public.chat_sessions(id)
);

-- User files table
CREATE TABLE public.user_files (
  space_id uuid,
  user_id uuid NOT NULL,
  filename text NOT NULL,
  content_type text,
  file_size_bytes bigint,
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  status text DEFAULT 'processing'::text,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT user_files_pkey PRIMARY KEY (id),
  CONSTRAINT user_files_space_id_fkey FOREIGN KEY (space_id) REFERENCES public.spaces(id),
  CONSTRAINT user_files_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
);

-- File chunks table for vector storage
CREATE TABLE public.file_chunks (
  file_id uuid NOT NULL,
  chunk_index integer NOT NULL,
  content text NOT NULL,
  embedding vector(384), -- 384-dimensional vectors
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT file_chunks_pkey PRIMARY KEY (id),
  CONSTRAINT file_chunks_file_id_fkey FOREIGN KEY (file_id) REFERENCES public.user_files(id)
);

-- University credentials table for PTIT integration
CREATE TABLE public.university_credentials (
  user_id uuid NOT NULL,
  university_username character varying NOT NULL,
  university_password character varying NOT NULL,
  access_token text,
  token_expiry timestamp with time zone,
  name character varying,
  refresh_token text,
  CONSTRAINT university_credentials_pkey PRIMARY KEY (user_id),
  CONSTRAINT university_credentials_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
);

-- Create indexes for performance
CREATE INDEX idx_spaces_user_id ON public.spaces(user_id);
CREATE INDEX idx_chat_sessions_user_id ON public.chat_sessions(user_id);
CREATE INDEX idx_chat_sessions_space_id ON public.chat_sessions(space_id);
CREATE INDEX idx_messages_chat_id ON public.messages(chat_id);
CREATE INDEX idx_user_files_user_id ON public.user_files(user_id);
CREATE INDEX idx_user_files_space_id ON public.user_files(space_id);
CREATE INDEX idx_file_chunks_file_id ON public.file_chunks(file_id);
CREATE INDEX idx_file_chunks_embedding ON public.file_chunks
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

## 🏃‍♂️ Running the Application

### Start Services
```bash
# 1. Start Redis
docker start studyassistant-redis

# 2. Start LM Studio (load model and start server)

# 3. Start Backend
cd backend
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows
python run.py

# 4. Start Frontend (optional - for development)
cd frontend
npm run dev
```

### Access Application
- **Main App**: http://localhost:5000
- **Development Frontend**: http://localhost:3000
- **Health Check**: http://localhost:5000/health

---

## 🎉 Quick Start Guide

1. **Upload a document** (PDF/DOCX/TXT)
2. **Ask questions** about your content  
3. **Use thinking mode** with `/no_thinking` toggle
4. **Check PTIT schedule** (if you're a student)

**Happy studying with AI! 📚✨**
