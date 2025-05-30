# Study Assistant for PTITer

An AI-powered educational platform designed specifically for students at Posts and Telecommunications Institute of Technology (PTIT). This intelligent study assistant combines local AI models with comprehensive document processing to provide personalized academic support.

## 🎯 Key Features

- **AI-Powered Chat Assistant**: Intelligent conversational AI using local LLM models
- **Document Processing**: Upload and analyze academic documents with vector embeddings
- **PTIT Integration**: Direct integration with PTIT academic systems and schedules
- **Multi-language Support**: Vietnamese and English language support
- **Real-time Web Search**: Enhanced responses with current information
- **Secure Authentication**: User authentication and data protection

## 🏗️ Architecture

### Backend (Python/Flask)
- **AI Service**: Local LLM integration with LM Studio/Ollama
- **Document Processing**: Text extraction and vector embeddings
- **PTIT Services**: Academic schedule and authentication integration
- **Database**: PostgreSQL with pgvector for similarity search

### Frontend (React/Vite)
- **Modern UI**: Responsive design with Tailwind CSS
- **Real-time Chat**: WebSocket-based messaging
- **File Management**: Document upload and processing interface
- **Agent Selection**: Multiple AI assistant personalities

## 📁 Project Structure

```
study-assistant/
├── backend/                 # Python Flask API
│   ├── app/
│   │   ├── routes/         # API endpoints
│   │   ├── services/       # Business logic
│   │   ├── config/         # Configuration files
│   │   └── utils/          # Utility functions
│   ├── requirements.txt    # Python dependencies
│   └── run.py             # Application entry point
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── lib/          # Utilities and configurations
│   │   └── assets/       # Static assets
│   ├── package.json      # Node.js dependencies
│   └── vite.config.js    # Vite configuration
└── docs/                 # Comprehensive documentation
    ├── README.md         # Documentation index
    ├── backend-architecture.md
    ├── api-documentation.md
    ├── database-design.md
    └── ... (more technical docs)
```
## 🛠️ Technology Stack

### Backend
- **Framework**: Flask with Blueprint architecture
- **Database**: PostgreSQL with pgvector for vector similarity
- **AI Integration**: LM Studio, Ollama, Transformers
- **Authentication**: Supabase Auth
- **File Processing**: PyPDF2, python-docx, Markdown

### Frontend
- **Framework**: React 18 with Vite
- **Styling**: Tailwind CSS
- **State Management**: React hooks and context
- **UI Components**: Custom components with Radix UI
- **Build Tool**: Vite with optimized bundling

### AI & ML
- **Local LLMs**: Qwen 2.5, Llama, Mistral models
- **Embeddings**: Sentence Transformers (multilingual)
- **Vector Search**: pgvector with cosine similarity
- **Text Processing**: NLTK, spaCy for Vietnamese

## 📝 API Reference

### Core Endpoints

- `POST /api/v1/chat/send` - Send chat message
- `GET /api/v1/chat/sessions` - Get chat history
- `POST /api/v1/files/upload` - Upload documents
- `GET /api/v1/ptit/schedule` - Get PTIT schedule
- `POST /api/v1/search/web` - Web search integration

Full API documentation: [API Docs](./docs/api-documentation.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request



---

**Study Assistant for PTITer** - Empowering PTIT students with AI-driven academic support.
