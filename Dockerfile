# ═══════════════════════════════════════════════════════════════
# AI Meeting Summarizer — Unified Production Dockerfile
# Builds the React frontend, then serves everything from FastAPI
# ═══════════════════════════════════════════════════════════════

# ── Stage 1: Build Frontend ──────────────────────────────────
FROM node:20-slim AS frontend-build

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

# ── Stage 2: Python Backend + Frontend dist ──────────────────
FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies (production only)
COPY requirements-prod.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ backend/

# Copy frontend build from stage 1
COPY --from=frontend-build /app/frontend/dist frontend/dist

# Create directories
RUN mkdir -p uploads

# Environment
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

EXPOSE ${PORT}

CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT}"]
