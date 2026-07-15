# API Guide

## Base URL

```
http://localhost:8000/api
```

Interactive Swagger docs: `http://localhost:8000/api/docs`  
ReDoc: `http://localhost:8000/api/redoc`

---

## Authentication

All protected endpoints require a Bearer token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

### POST `/auth/register`

Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "StrongPass1!"
}
```

**Password requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character

**Response (201):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "johndoe",
  "role": "user",
  "is_active": true,
  "created_at": "2026-01-01T00:00:00Z"
}
```

### POST `/auth/login`

**Request:**
```json
{
  "email": "user@example.com",
  "password": "StrongPass1!"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOi...",
  "refresh_token": "eyJhbGciOi...",
  "token_type": "bearer"
}
```

### POST `/auth/refresh`

Refresh an expired access token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOi..."
}
```

### GET `/auth/me`

Get the current authenticated user's profile.

**Response (200):** Same as register response.

### POST `/auth/logout`

Log out the current user (server-side audit only, client must discard tokens).

---

## Meetings

### POST `/meetings/`

Create a new meeting record.

**Request:**
```json
{
  "title": "Sprint Planning",
  "description": "Weekly sprint planning meeting",
  "meeting_date": "2026-01-15T10:00:00Z",
  "participant_count": 8
}
```

### GET `/meetings/?page=1&page_size=20&status_filter=completed`

List meetings with pagination and optional status filter.

**Response (200):**
```json
{
  "meetings": [...],
  "total": 42,
  "page": 1,
  "page_size": 20,
  "total_pages": 3
}
```

### GET `/meetings/{id}`

Get full meeting details including transcript, summary, action items, and keywords.

**Response (200):**
```json
{
  "meeting": { "id": "...", "title": "...", "status": "completed", ... },
  "audio_file": { "original_filename": "meeting.mp3", "file_size": 15000000, ... },
  "transcript": { "full_text": "...", "segments": [...], "language": "en", ... },
  "summary": { "executive_summary": "...", "key_points": [...], "decisions": [...], ... },
  "action_items": [{ "description": "...", "assignee": "John", "priority": "high", ... }],
  "keywords": [{ "keyword": "sprint", "frequency": 5 }]
}
```

### POST `/meetings/{id}/upload`

Upload an audio file for a meeting. Triggers background processing (transcribe → summarize → extract).

**Request:** `multipart/form-data` with field `file` (max 500MB).

**Supported formats:** MP3, WAV, M4A, OGG, FLAC, WEBM, MP4, WMA

### POST `/meetings/{id}/export`

Export meeting data as PDF, DOCX, or TXT.

**Request:**
```json
{
  "format": "pdf"
}
```

**Response:** Binary file download.

### GET `/meetings/search?query=sprint&page=1&page_size=20`

Search meetings by title, description, or transcript content.

### GET `/meetings/stats`

Get aggregated statistics for the current user.

**Response (200):**
```json
{
  "total_meetings": 42,
  "completed_meetings": 38,
  "total_duration_seconds": 86400
}
```

### PATCH `/meetings/{id}/action-items/{item_id}`

Update an action item's status, priority, or assignee.

**Request:**
```json
{
  "status": "completed",
  "priority": "high",
  "assignee": "Jane Doe"
}
```

---

## Settings

### GET `/settings/`

Get the current user's preferences.

**Response (200):**
```json
{
  "default_ai_provider": "ollama",
  "default_whisper_model": "base",
  "enable_diarization": false,
  "default_export_format": "pdf",
  "theme": "dark"
}
```

### PATCH `/settings/`

Update user preferences (partial update).

---

## Health

### GET `/health`

**Response (200):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development"
}
```

---

## Error Responses

All errors follow a consistent format:

```json
{
  "error": true,
  "message": "Human-readable error description",
  "details": {}
}
```

| Status Code | Meaning |
|-------------|---------|
| 400 | Bad request / validation error |
| 401 | Invalid or expired token |
| 403 | Insufficient permissions |
| 404 | Resource not found |
| 409 | Conflict (duplicate resource) |
| 422 | Validation error |
| 429 | Rate limit exceeded |
| 500 | Internal server error |
