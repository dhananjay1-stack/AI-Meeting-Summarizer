# Deployment Guide

## Development Setup

### Prerequisites

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.11+ | Backend runtime |
| Node.js | 20+ | Frontend build |
| Ollama | Latest | Local LLM for summarization |
| Git | Latest | Version control |

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/meeting-summarizer.git
cd meeting-summarizer
```

### 2. Backend Setup

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings (generate a real JWT_SECRET_KEY!)

# Start the development server
uvicorn backend.main:app --reload --port 8000
```

> **Note:** On first startup in development mode, SQLite tables are created automatically.

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

### 4. AI Setup (Ollama)

```bash
# Install Ollama: https://ollama.com/download
# Pull a model
ollama pull gemma3

# Verify it's running
curl http://localhost:11434/api/tags
```

---

## Docker Deployment

### Quick Start

```bash
# Build and start all services
docker-compose up --build -d

# Pull an Ollama model (first time only)
docker exec meeting-summarizer-ollama ollama pull gemma3

# Check logs
docker-compose logs -f backend
```

**Services:**
| Service | URL | Container |
|---------|-----|-----------|
| Frontend | `http://localhost:3000` | meeting-summarizer-frontend |
| Backend API | `http://localhost:8000` | meeting-summarizer-backend |
| Ollama | `http://localhost:11434` | meeting-summarizer-ollama |
| Swagger Docs | `http://localhost:8000/api/docs` | — |

### Environment Variables

Generate a secure JWT secret for production:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Set it in your `.env` or Docker Compose environment:

```yaml
environment:
  - JWT_SECRET_KEY=your-generated-secret
```

---

## Production Deployment

### Option A: Render + Vercel (Free / Low-Cost)

#### Backend on Render

1. Create a new **Web Service** on [Render](https://render.com)
2. Connect your GitHub repository
3. Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables in the Render dashboard
5. Use **Render PostgreSQL** for the database:
   ```
   DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname
   ```

#### Frontend on Vercel

1. Import the `frontend/` directory on [Vercel](https://vercel.com)
2. Set the environment variable:
   ```
   VITE_API_URL=https://your-backend.onrender.com
   ```
3. Deploy

### Option B: VPS with Docker Compose

```bash
# On your server
git clone https://github.com/yourusername/meeting-summarizer.git
cd meeting-summarizer

# Set production environment
cp .env.example .env
# Edit .env with production values

# Start services
docker-compose up -d

# Pull Ollama model
docker exec meeting-summarizer-ollama ollama pull gemma3
```

### Option C: PostgreSQL Production Database

Switch from SQLite to PostgreSQL:

1. Install PostgreSQL or use a managed service
2. Update `.env`:
   ```
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/meeting_summarizer
   ```
3. Install the async PostgreSQL driver (already in requirements.txt):
   ```
   pip install asyncpg
   ```

---

## Troubleshooting

### Backend won't start

```bash
# Check Python version
python --version  # Must be 3.11+

# Check if port is in use
netstat -tlnp | grep 8000

# Check logs
uvicorn backend.main:app --reload --log-level debug
```

### Ollama not connecting

```bash
# Verify Ollama is running
curl http://localhost:11434/api/tags

# Check model is downloaded
ollama list

# If using Docker, ensure container name matches OLLAMA_BASE_URL
docker exec meeting-summarizer-ollama ollama list
```

### Upload fails

- Check `MAX_UPLOAD_SIZE_MB` in `.env` (default: 500MB)
- Verify the file is a supported audio format
- Check `uploads/` directory has write permissions

### Slow transcription

- Use a smaller Whisper model: set `WHISPER_MODEL_SIZE=tiny` in `.env`
- Use GPU if available: set `WHISPER_DEVICE=cuda`
- Use float16 compute: set `WHISPER_COMPUTE_TYPE=float16`

### Database reset

```bash
# Delete SQLite database
rm meeting_summarizer.db

# Restart server (tables auto-create in development)
uvicorn backend.main:app --reload
```
