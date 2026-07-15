# 🎯 AI Meeting Summarizer

> Transform your meetings into actionable insights with AI-powered transcription and summarization.

[![CI](https://github.com/yourusername/meeting-summarizer/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/meeting-summarizer/actions)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev)

---

## ✨ Features

- **🎤 Audio Transcription** — Powered by Faster-Whisper with language detection and timestamps
- **🤖 AI Summarization** — Executive summaries, key points, and decisions via Ollama (local LLM)
- **✅ Action Item Extraction** — Automatically identified with assignees and priorities
- **🔍 Full-Text Search** — Search across meeting titles, descriptions, and transcripts
- **📄 Export** — Download summaries as PDF, DOCX, or TXT
- **🔐 Secure Authentication** — JWT-based auth with refresh tokens and password policy
- **🌓 Dark/Light Mode** — Beautiful responsive dashboard with glassmorphism design
- **🐳 Docker Ready** — One-command deployment with Docker Compose

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────────┐     ┌──────────────┐
│  React Frontend │────▶│   FastAPI Backend    │────▶│   Ollama     │
│  (Vite + TS)    │     │   (Python 3.11)      │     │   (Local AI) │
└─────────────────┘     └─────────────────────┘     └──────────────┘
                              │                          │
                        ┌─────┴─────┐              ┌────┴────┐
                        │ SQLite/   │              │ Faster- │
                        │ PostgreSQL│              │ Whisper │
                        └───────────┘              └─────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- [Ollama](https://ollama.com) (for AI summarization)

### 1. Clone & Setup

```bash
git clone https://github.com/yourusername/meeting-summarizer.git
cd meeting-summarizer

# Copy environment file
cp .env.example .env
```

### 2. Backend

```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the API server
uvicorn backend.main:app --reload
```

The API will be available at `http://localhost:8000`  
Swagger docs: `http://localhost:8000/api/docs`

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

The dashboard will be available at `http://localhost:5173`

### 4. AI Setup

```bash
# Install Ollama and pull a model
ollama pull gemma3
ollama serve
```

### 5. Docker (Alternative)

```bash
docker-compose up --build
```

## 📁 Project Structure

```
Meeting_Summarizer/
├── backend/
│   ├── api/            # FastAPI route handlers
│   ├── config/         # Settings and constants
│   ├── core/           # Schemas and exceptions
│   ├── database/       # Session management
│   ├── models/         # SQLAlchemy models
│   ├── prompts/        # AI prompt templates
│   ├── repositories/   # Data access layer
│   ├── security/       # JWT, bcrypt, rate limiting
│   ├── services/       # Business logic
│   ├── storage/        # File storage abstraction
│   ├── tests/          # Test suite
│   └── main.py         # FastAPI application
├── frontend/
│   └── src/
│       ├── components/ # Reusable UI components
│       ├── lib/        # API client, auth context
│       └── pages/      # Application pages
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login and get tokens |
| POST | `/api/auth/refresh` | Refresh access token |
| GET | `/api/auth/me` | Get current user |
| GET | `/api/meetings/` | List meetings (paginated) |
| POST | `/api/meetings/` | Create a meeting |
| GET | `/api/meetings/{id}` | Get meeting details |
| POST | `/api/meetings/{id}/upload` | Upload audio file |
| GET | `/api/meetings/search` | Search meetings |
| POST | `/api/meetings/{id}/export` | Export meeting |
| GET | `/api/settings/` | Get user settings |
| PATCH | `/api/settings/` | Update settings |

## 🧪 Testing

```bash
# Run backend tests
python -m pytest backend/tests/ -v

# Run with coverage
python -m pytest backend/tests/ -v --cov=backend --cov-report=term-missing
```

## 🛡️ Security

- JWT authentication with access + refresh tokens
- bcrypt password hashing with strength validation
- MIME-type verification using magic bytes
- Rate limiting on auth endpoints
- CORS configuration
- SQL injection prevention (SQLAlchemy ORM)
- XSS prevention (React escaping + security headers)
- Random filenames for uploads (UUID-based)
- SHA-256 file checksums
- Audit logging for security events

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.
