# Deployment Guide

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Development Environment Setup](#2-development-environment-setup)
3. [Production Deployment](#3-production-deployment)
4. [Configuration Management](#4-configuration-management)
5. [Database Setup](#5-database-setup)
6. [AI Model Configuration](#6-ai-model-configuration)
7. [Monitoring & Maintenance](#7-monitoring--maintenance)
8. [Troubleshooting](#8-troubleshooting)

## 1. Prerequisites

### 1.1 System Requirements

**Development Environment:**

- **Operating System**: macOS 12+, Ubuntu 20.04+, or Windows 10+ (WSL2 recommended)
- **Python**: 3.11 or higher
- **Node.js**: 18.x or higher
- **Memory**: 8GB RAM minimum (16GB recommended for local AI models)
- **Storage**: 20GB free space (additional space for AI models)

**Production Environment:**

- **CPU**: 4+ cores recommended
- **Memory**: 16GB RAM minimum (32GB for optimal AI performance)
- **Storage**: 100GB+ SSD storage
- **Network**: Stable internet connection for external APIs

### 1.2 External Service Accounts

**Required Services:**

1. **Supabase Account** - Database and authentication
2. **Brave Search API** - Web search functionality
3. **PTIT Portal Access** - Academic integration (if available)

**Optional Services:** 4. **OpenAI API** - Fallback AI model (if not using local models) 5. **Sentry** - Error tracking and monitoring 6. **Cloudflare** - CDN and security (production)

## 2. Development Environment Setup

### 2.1 Clone Repository

```bash
# Clone the repository
git clone https://github.com/your-org/study-assistant-ptit.git
cd study-assistant-ptit

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..
```

### 2.2 Environment Configuration

**Create backend environment file:**

```bash
# Create backend/.env
cp backend/.env.example backend/.env
```

**Configure backend/.env:**

```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key

# Database URL (if connecting directly)
DATABASE_URL=postgresql://user:password@localhost:5432/study_assistant

# AI Configuration
LM_STUDIO_URL=http://localhost:1234
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2

# External APIs
BRAVE_API_KEY=your-brave-api-key

# File Upload
MAX_FILE_SIZE=10485760  # 10MB
UPLOAD_FOLDER=./uploads

# PTIT Integration (if available)
PTIT_API_URL=https://ptit-api-endpoint.edu.vn
PTIT_CLIENT_ID=your-ptit-client-id
PTIT_CLIENT_SECRET=your-ptit-client-secret

# Development Settings
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

**Create frontend environment file:**

```bash
# Create frontend/.env
cp frontend/.env.example frontend/.env
```

**Configure frontend/.env:**

```env
# API Configuration
VITE_API_URL=http://localhost:5000/api/v1
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key

# Development Settings
VITE_APP_ENV=development
VITE_DEBUG=true

# Feature Flags
VITE_ENABLE_PTIT_INTEGRATION=true
VITE_ENABLE_WEB_SEARCH=true
```

### 2.3 Database Setup (Development)

**Option A: Using Supabase Cloud**

1. Create a new Supabase project
2. Run database migrations:

```bash
cd backend
python setup_database.py
```

**Option B: Local PostgreSQL**

```bash
# Install PostgreSQL and pgvector
# Ubuntu/Debian:
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo apt install postgresql-15-pgvector

# macOS:
brew install postgresql
brew install pgvector

# Start PostgreSQL service
sudo systemctl start postgresql  # Linux
brew services start postgresql   # macOS

# Create database
createdb study_assistant

# Run migrations
cd backend
python -c "from app import create_app; from app.models import db; app = create_app(); app.app_context().push(); db.create_all()"
```

### 2.4 AI Model Setup

**Install LM Studio:**

1. Download from [https://lmstudio.ai/](https://lmstudio.ai/)
2. Install and launch LM Studio
3. Download recommended model: `Qwen/Qwen2.5-7B-Instruct-GGUF`
4. Load model and start local server on port 1234

**Alternative: Ollama Setup**

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull recommended model
ollama pull qwen2.5:7b-instruct

# Start Ollama server
ollama serve
```

### 2.5 Start Development Servers

**Terminal 1 - Backend:**

```bash
cd backend
python run.py
# Server runs on http://localhost:5000
```

**Terminal 2 - Frontend:**

```bash
cd frontend
npm run dev
# Server runs on http://localhost:3000
```

**Terminal 3 - AI Model (if using LM Studio):**

```bash
# Start LM Studio and load model
# Ensure server is running on http://localhost:1234
```

### 2.6 Verify Installation

**Check backend health:**

```bash
curl http://localhost:5000/api/v1/health
```

**Expected response:**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "database": "connected",
    "ai_model": "available",
    "storage": "ready"
  }
}
```

## 3. Production Deployment

### 3.1 Platform Options

**Recommended Platforms:**

1. **Railway** (Recommended for beginners)

   - Automatic deployments from Git
   - Built-in PostgreSQL with pgvector
   - Simple environment variable management

2. **DigitalOcean App Platform**

   - Managed containers
   - Database clustering
   - CDN integration

3. **AWS/GCP/Azure**
   - Maximum flexibility
   - Requires more configuration
   - Suitable for enterprise deployment

### 3.2 Railway Deployment

**Step 1: Prepare Repository**

```bash
# Create production branch
git checkout -b production

# Add Procfile for Railway
echo "web: gunicorn --bind 0.0.0.0:$PORT app:app" > backend/Procfile

# Add requirements.txt if not exists
pip freeze > backend/requirements.txt

# Commit changes
git add .
git commit -m "Prepare for production deployment"
git push origin production
```

**Step 2: Railway Configuration**

1. Connect GitHub repository to Railway
2. Create new project from repository
3. Add PostgreSQL service with pgvector
4. Configure environment variables (see Production Environment Variables below)

**Step 3: Database Migration**

```bash
# Connect to Railway database and run migrations
railway run python setup_database.py
```

### 3.3 Docker Deployment

**Create Dockerfile for backend:**

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
```

**Create docker-compose.yml:**

```yaml
version: "3.8"

services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/study_assistant
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
    depends_on:
      - db
    volumes:
      - ./uploads:/app/uploads

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:5000/api/v1

  db:
    image: pgvector/pgvector:pg15
    environment:
      - POSTGRES_DB=study_assistant
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

**Deploy with Docker:**

```bash
# Build and start services
docker-compose up -d

# Run database migrations
docker-compose exec backend python setup_database.py
```

## 4. Configuration Management

### 4.1 Production Environment Variables

**Backend Configuration:**

```env
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-production-secret-key-here

# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Supabase (Production)
SUPABASE_URL=https://your-prod-project.supabase.co
SUPABASE_KEY=your-prod-anon-key
SUPABASE_SERVICE_KEY=your-prod-service-key

# AI Configuration
LM_STUDIO_URL=http://ai-server:1234
OPENAI_API_KEY=your-openai-key-fallback

# External APIs
BRAVE_API_KEY=your-brave-api-key

# Security
CORS_ORIGINS=https://your-domain.com
JWT_SECRET_KEY=your-jwt-secret

# File Storage
MAX_FILE_SIZE=10485760
UPLOAD_FOLDER=/app/uploads

# Monitoring
SENTRY_DSN=your-sentry-dsn
LOG_LEVEL=INFO

# Rate Limiting
REDIS_URL=redis://redis:6379/0
```

**Frontend Configuration:**

```env
# API Configuration
VITE_API_URL=https://api.your-domain.com/api/v1
VITE_SUPABASE_URL=https://your-prod-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-prod-anon-key

# Production Settings
VITE_APP_ENV=production
VITE_DEBUG=false

# Feature Flags
VITE_ENABLE_PTIT_INTEGRATION=true
VITE_ENABLE_WEB_SEARCH=true
VITE_ENABLE_ANALYTICS=true

# Analytics (if using)
VITE_GA_MEASUREMENT_ID=GA-MEASUREMENT-ID
```

### 4.2 Security Configuration

**SSL/TLS Setup:**

```nginx
# nginx configuration for HTTPS
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Environment Security:**

```bash
# Set proper file permissions
chmod 600 .env
chown root:root .env

# Use secrets management (production)
export SECRET_KEY=$(cat /run/secrets/secret_key)
export DATABASE_URL=$(cat /run/secrets/database_url)
```

## 5. Database Setup

### 5.1 Supabase Production Setup

**Create Production Database:**

1. Create new Supabase organization/project
2. Configure database with appropriate instance size
3. Enable pgvector extension:

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify extension
SELECT * FROM pg_extension WHERE extname = 'vector';
```

**Configure Row Level Security:**

```sql
-- Enable RLS on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE files ENABLE ROW LEVEL SECURITY;
ALTER TABLE embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (see database-design.md for complete policies)
```

### 5.2 Database Migration Script

**Create setup_database.py:**

```python
#!/usr/bin/env python3
"""
Database setup and migration script
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def setup_database():
    """Setup database with all required tables and extensions"""

    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        sys.exit(1)

    try:
        engine = create_engine(database_url)

        with engine.connect() as conn:
            # Enable extensions
            print("Enabling pgvector extension...")
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS uuid_ossp;"))

            # Create tables (implement based on database-design.md)
            print("Creating tables...")
            create_tables(conn)

            # Create indexes
            print("Creating indexes...")
            create_indexes(conn)

            # Create functions
            print("Creating functions...")
            create_functions(conn)

            conn.commit()
            print("Database setup completed successfully!")

    except SQLAlchemyError as e:
        print(f"Database setup failed: {e}")
        sys.exit(1)

def create_tables(conn):
    """Create all application tables"""
    # Implementation based on database-design.md schemas
    pass

def create_indexes(conn):
    """Create all required indexes"""
    # Implementation based on database-design.md indexes
    pass

def create_functions(conn):
    """Create database functions"""
    # Implementation based on database-design.md functions
    pass

if __name__ == "__main__":
    setup_database()
```

## 6. AI Model Configuration

### 6.1 Local AI Model Deployment

**LM Studio Production Setup:**

```bash
# Install LM Studio on server
wget https://releases.lmstudio.ai/linux/latest/lmstudio-linux.tar.gz
tar -xzf lmstudio-linux.tar.gz
cd lmstudio

# Download and configure model
./lmstudio-cli download Qwen/Qwen2.5-7B-Instruct-GGUF
./lmstudio-cli load Qwen/Qwen2.5-7B-Instruct-GGUF

# Start server with production settings
./lmstudio-cli serve --port 1234 --host 0.0.0.0 --threads 4
```

**Ollama Production Setup:**

```bash
# Install Ollama on Ubuntu
curl -fsSL https://ollama.ai/install.sh | sh

# Configure systemd service
sudo systemctl enable ollama
sudo systemctl start ollama

# Pull models
ollama pull qwen2.5:7b-instruct
ollama pull nomic-embed-text:latest  # For embeddings
```

**GPU Configuration (NVIDIA):**

```bash
# Install NVIDIA drivers and CUDA
sudo apt update
sudo apt install nvidia-driver-525
sudo apt install nvidia-cuda-toolkit

# Verify GPU availability
nvidia-smi

# Configure Ollama for GPU
sudo systemctl edit ollama
```

Add to service file:

```ini
[Service]
Environment="CUDA_VISIBLE_DEVICES=0"
Environment="OLLAMA_HOST=0.0.0.0"
```

### 6.2 Cloud AI Fallback

**OpenAI Integration:**

```python
# backend/app/services/ai_service.py
class AIService:
    def __init__(self):
        self.local_model_url = os.getenv('LM_STUDIO_URL')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')

    async def generate_response(self, prompt):
        try:
            # Try local model first
            return await self.call_local_model(prompt)
        except Exception as e:
            logging.warning(f"Local model failed: {e}")
            # Fallback to OpenAI
            return await self.call_openai(prompt)
```

## 7. Monitoring & Maintenance

### 7.1 Health Checks

**Create health check endpoint:**

```python
# backend/app/routes/health.py
@bp.route('/health')
def health_check():
    """System health check endpoint"""
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'services': {}
    }

    # Check database
    try:
        db.session.execute(text('SELECT 1'))
        health_status['services']['database'] = 'healthy'
    except Exception:
        health_status['services']['database'] = 'unhealthy'
        health_status['status'] = 'unhealthy'

    # Check AI model
    try:
        response = requests.get(f"{LM_STUDIO_URL}/health", timeout=5)
        health_status['services']['ai_model'] = 'healthy' if response.ok else 'unhealthy'
    except Exception:
        health_status['services']['ai_model'] = 'unhealthy'

    return jsonify(health_status)
```

### 7.2 Logging Configuration

**Configure logging:**

```python
# backend/app/config.py
import logging
from logging.handlers import RotatingFileHandler

def configure_logging(app):
    if not app.debug:
        # File logging
        if not os.path.exists('logs'):
            os.mkdir('logs')

        file_handler = RotatingFileHandler(
            'logs/study_assistant.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )

        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Study Assistant startup')
```

### 7.3 Backup Strategy

**Database Backup Script:**

```bash
#!/bin/bash
# backup_database.sh

BACKUP_DIR="/backups/study_assistant"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="study_assistant_backup_${TIMESTAMP}.sql"

# Create backup directory
mkdir -p $BACKUP_DIR

# Perform backup
pg_dump $DATABASE_URL > $BACKUP_DIR/$BACKUP_FILE

# Compress backup
gzip $BACKUP_DIR/$BACKUP_FILE

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/${BACKUP_FILE}.gz"
```

**Schedule backups with cron:**

```bash
# Add to crontab
0 2 * * * /path/to/backup_database.sh
```

## 8. Troubleshooting

### 8.1 Common Issues

**Database Connection Issues:**

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check pgvector extension
psql -d study_assistant -c "SELECT * FROM pg_extension WHERE extname = 'vector';"

# Test connection
psql $DATABASE_URL -c "SELECT version();"
```

**AI Model Issues:**

```bash
# Check LM Studio server
curl http://localhost:1234/v1/models

# Check Ollama
ollama list
ollama ps

# Check GPU usage
nvidia-smi
```

**File Upload Issues:**

```bash
# Check disk space
df -h

# Check upload directory permissions
ls -la uploads/

# Check file size limits
grep MAX_FILE_SIZE .env
```

### 8.2 Performance Issues

**Database Performance:**

```sql
-- Check slow queries
SELECT query, total_time, calls, mean_time
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;

-- Check index usage
SELECT indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan = 0;

-- Check table sizes
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size(tablename::regclass)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(tablename::regclass) DESC;
```

**Memory Usage:**

```bash
# Check Python memory usage
ps aux | grep python | head -5

# Check system memory
free -h

# Monitor in real-time
htop
```

### 8.3 Error Recovery

**Database Recovery:**

```bash
# Restore from backup
gunzip study_assistant_backup_20241215_020000.sql.gz
psql $DATABASE_URL < study_assistant_backup_20241215_020000.sql
```

**Service Recovery:**

```bash
# Restart services
sudo systemctl restart study-assistant
sudo systemctl restart nginx

# Check service logs
journalctl -u study-assistant -f
tail -f /var/log/nginx/error.log
```

---

## Conclusion

This deployment guide provides comprehensive instructions for setting up the Study Assistant in both development and production environments. Key considerations:

**For Development:**

- Local setup with LM Studio or Ollama
- Supabase cloud database for ease
- Hot reload for rapid iteration

**For Production:**

- Managed hosting platforms recommended
- Proper security configuration essential
- Monitoring and backup strategies critical
- GPU acceleration for AI models when possible

**Next Steps:**

- Set up monitoring dashboard
- Implement automated testing pipeline
- Configure CI/CD deployment
- Plan scaling strategy

→ **Related Documentation:**

- [Backend Architecture](./backend-architecture.md) - Understanding the system design
- [Database Design](./database-design.md) - Database setup details
- [Security Report](./security-report.md) - Security configuration
- [Performance Report](./performance-report.md) - Optimization strategies
