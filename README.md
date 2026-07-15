# 🎯 AI Meeting Summarizer

> Transform your meetings into actionable insights with AI-powered transcription and summarization.

[![Live Demo](https://img.shields.io/badge/🌐_Live_Demo-Visit_App-00C853?style=for-the-badge)](https://ai-meeting-summarizer-7d6f.onrender.com)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev)
[![Deployed on Render](https://img.shields.io/badge/Deployed_on-Render-46E3B7.svg)](https://render.com)

---

## 🌐 Live Demo

**👉 [https://ai-meeting-summarizer-7d6f.onrender.com](https://ai-meeting-summarizer-7d6f.onrender.com)**

> **Note:** The app is hosted on Render's free tier. The first request may take ~50 seconds as the instance spins up from sleep.

---

## ✨ Features

- **🎤 Audio Transcription** — Powered by Groq Whisper-large-v3 API (cloud) with local Faster-Whisper fallback
- **🤖 AI Summarization** — Executive summaries, key points, and decisions via Groq / Ollama / OpenAI / Claude / Gemini
- **✅ Action Item Extraction** — Automatically identified with assignees and priorities
- **🔍 Full-Text Search** — Search across meeting titles, descriptions, and transcripts
- **📄 Export** — Download summaries as PDF, DOCX, or TXT
- **🔐 Secure Authentication** — JWT-based auth with refresh tokens and password policy
- **🌓 Dark/Light Mode** — Beautiful responsive dashboard with glassmorphism design
- **📱 Responsive Sidebar** — Premium navigation with collapsible sidebar and mobile support
- **🐳 Docker Ready** — One-command deployment with Docker Compose
- **☁️ Cloud Deployed** — Live on Render with automatic deployments from GitHub

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────────┐     ┌──────────────────┐
│  React Frontend │────▶│   FastAPI Backend    │────▶│   Groq API       │
│  (Vite + TS)    │     │   (Python 3.11)      │     │  (Whisper + LLM) │
└─────────────────┘     └─────────────────────┘     └──────────────────┘
                              │                           │
                        ┌─────┴─────┐              ┌─────┴──────┐
                        │  SQLite   │              │  Fallback: │
                        │  Database │              │  Ollama /  │
                        └───────────┘              │  OpenAI /  │
                                                   │  Claude /  │
                                                   │  Gemini    │
                                                   └────────────┘
```

### AI Provider Support

| Provider | Transcription | Summarization | API Key Required |
|----------|:------------:|:-------------:|:----------------:|
| **Groq** (default for cloud) | ✅ Whisper-large-v3 | ✅ Llama 3.1 | ✅ Free at [console.groq.com](https://console.groq.com) |
| **Ollama** (default for local) | ❌ | ✅ Any local model | ❌ |
| **OpenAI** | ❌ | ✅ GPT-4o-mini | ✅ |
| **Claude** | ❌ | ✅ Claude Sonnet | ✅ |
| **Gemini** | ❌ | ✅ Gemini 2.0 Flash | ✅ |
| **Faster-Whisper** (local) | ✅ | ❌ | ❌ |

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- A Groq API key (free) **OR** [Ollama](https://ollama.com) installed locally

### 1. Clone & Setup

```bash
git clone https://github.com/dhananjay1-stack/AI-Meeting-Summarizer.git
cd AI-Meeting-Summarizer

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

**Option A: Groq (recommended for cloud / free tier)**

```bash
# Get a free API key at https://console.groq.com
# Add to your .env file:
AI_PROVIDER=groq
GROQ_API_KEY=gsk_your_key_here
```

**Option B: Ollama (local, no API key needed)**

```bash
# Install Ollama and pull a model
ollama pull gemma3
ollama serve

# In your .env file:
AI_PROVIDER=ollama
```

### 5. Docker (Alternative)

```bash
docker-compose up --build
```

## ☁️ Deploy to Render

This app is deployed on [Render](https://render.com) with a single `render.yaml` blueprint.

### One-Click Deploy

1. Fork this repository
2. Go to [Render Dashboard](https://dashboard.render.com) → **New** → **Blueprint**
3. Connect your GitHub repo and select `render.yaml`
4. Add `GROQ_API_KEY` in the environment variables
5. Deploy! 🚀

### Required Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `AI_PROVIDER` | `groq` | AI provider for summarization |
| `GROQ_API_KEY` | `gsk_...` | Free from [console.groq.com](https://console.groq.com) |
| `ENVIRONMENT` | `production` | App environment |
| `DATABASE_URL` | `sqlite+aiosqlite:///./meeting_summarizer.db` | Database connection |
| `ALLOWED_ORIGINS` | `*` | CORS origins |
| `PORT` | `10000` | Server port (Render default) |

## 📁 Project Structure

```
AI-Meeting-Summarizer/
├── backend/
│   ├── api/            # FastAPI route handlers (auth, meetings, settings)
│   ├── config/         # Settings and constants
│   ├── core/           # Schemas and exceptions
│   ├── database/       # Async session management
│   ├── models/         # SQLAlchemy models (User, Meeting, Summary, etc.)
│   ├── prompts/        # AI prompt templates
│   ├── repositories/   # Data access layer
│   ├── security/       # JWT, bcrypt, rate limiting
│   ├── services/       # Business logic (transcription, summarization, export)
│   ├── storage/        # File storage abstraction
│   ├── tests/          # Test suite (22 tests)
│   └── main.py         # FastAPI application + SPA serving
├── frontend/
│   └── src/
│       ├── components/ # Sidebar, Layout, Navbar
│       ├── lib/        # API client, auth context
│       └── pages/      # Login, Dashboard, Upload, MeetingDetail, Settings
├── render.yaml         # Render deployment blueprint
├── docker-compose.yml
├── Dockerfile          # Multi-stage build (Node + Python)
├── requirements.txt    # Development dependencies
├── requirements-prod.txt # Production dependencies (optimized)
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
| GET | `/api/health` | Health check |

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
- Real-time password strength indicator on registration
- MIME-type verification using magic bytes (with extension fallback)
- Rate limiting on auth endpoints
- CORS configuration
- SQL injection prevention (SQLAlchemy ORM)
- XSS prevention (React escaping + security headers)
- Random filenames for uploads (UUID-based)
- SHA-256 file checksums
- Audit logging for security events

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 19, TypeScript, Vite, React Router |
| **Backend** | FastAPI, Python 3.11, SQLAlchemy 2.0, Pydantic v2 |
| **Database** | SQLite (async via aiosqlite) |
| **AI - Transcription** | Groq Whisper API / Faster-Whisper (local) |
| **AI - Summarization** | Groq / Ollama / OpenAI / Claude / Gemini |
| **Auth** | JWT (python-jose) + bcrypt |
| **Export** | ReportLab (PDF), python-docx (DOCX) |
| **Deployment** | Docker, Render |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

---

<p align="center">
  Built with ❤️ by <a href="https://github.com/dhananjay1-stack">dhananjay1-stack</a>
</p>
