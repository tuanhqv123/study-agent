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

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL** with pgvector extension
- **LM Studio** or **Ollama** for local AI models

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/tuanhqv123/study-agent.git
   cd study-agent
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env  # Configure your environment variables
   python run.py
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **AI Model Setup**
   - Install [LM Studio](https://lmstudio.ai/) or [Ollama](https://ollama.ai/)
   - Download recommended model: `Qwen/Qwen2.5-7B-Instruct-GGUF`
   - Start local server on port 1234

### Environment Configuration

Create `.env` files in both `backend/` and `frontend/` directories:

**Backend (.env)**:
```env
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
LM_STUDIO_URL=http://localhost:1234
BRAVE_API_KEY=your-brave-api-key
SECRET_KEY=your-secret-key
```

**Frontend (.env)**:
```env
VITE_API_URL=http://localhost:5000/api/v1
VITE_SUPABASE_URL=your-supabase-url
VITE_SUPABASE_ANON_KEY=your-supabase-anon-key
```

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Documentation Index](./docs/README.md)** - Navigation guide
- **[Backend Architecture](./docs/backend-architecture.md)** - System design and patterns
- **[API Documentation](./docs/api-documentation.md)** - Complete API reference
- **[Database Design](./docs/database-design.md)** - Schema and optimization
- **[Security Report](./docs/security-report.md)** - Security measures
- **[Performance Report](./docs/performance-report.md)** - Optimization strategies

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

## 🔧 Development

### Running Tests
```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality
```bash
# Python linting
flake8 backend/
black backend/

# JavaScript linting
cd frontend
npm run lint
npm run format
```

## 🚀 Deployment

The application supports multiple deployment options:

- **Railway**: Recommended for quick deployment
- **Docker**: Full containerization support
- **Traditional VPS**: Manual deployment guide available

See [Deployment Documentation](./docs/deployment-guide.md) for detailed instructions.

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

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **PTIT** - Posts and Telecommunications Institute of Technology
- **Hugging Face** - AI model hosting and transformers library
- **Supabase** - Backend-as-a-Service platform
- **LM Studio** - Local LLM inference platform

## 📞 Contact

- **Author**: Tuan Tran
- **Email**: tuanhqv123@gmail.com
- **GitHub**: [@tuanhqv123](https://github.com/tuanhqv123)

---

**Study Assistant for PTITer** - Empowering PTIT students with AI-driven academic support.
