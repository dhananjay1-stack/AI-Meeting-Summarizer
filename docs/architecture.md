# Architecture Overview

## System Architecture

```mermaid
graph TB
    subgraph Client["Client Layer"]
        Browser["Browser (React SPA)"]
    end

    subgraph API["API Gateway Layer"]
        CORS["CORS Middleware"]
        RateLimit["Rate Limiter"]
        AuthMiddleware["JWT Auth"]
        CORS --> RateLimit --> AuthMiddleware
    end

    subgraph Routes["Route Layer"]
        AuthRoutes["/api/auth/*"]
        MeetingRoutes["/api/meetings/*"]
        SettingsRoutes["/api/settings/*"]
        HealthRoute["/api/health"]
    end

    subgraph Services["Service Layer"]
        MeetingService["Meeting Service"]
        UploadService["Upload Service"]
        TranscriptionService["Transcription Service"]
        SummarizationService["Summarization Service"]
        ExportService["Export Service"]
    end

    subgraph AI["AI Layer"]
        Whisper["Faster-Whisper"]
        OllamaProvider["Ollama Provider"]
        OpenAIProvider["OpenAI Provider"]
        ClaudeProvider["Claude Provider"]
        GeminiProvider["Gemini Provider"]
    end

    subgraph Data["Data Layer"]
        Repositories["Repositories"]
        SQLAlchemy["SQLAlchemy ORM"]
        DB[(SQLite / PostgreSQL)]
        FileStorage["File Storage"]
    end

    Browser --> CORS
    AuthMiddleware --> Routes
    Routes --> Services
    MeetingService --> UploadService
    MeetingService --> TranscriptionService
    MeetingService --> SummarizationService
    MeetingService --> ExportService
    TranscriptionService --> Whisper
    SummarizationService --> OllamaProvider
    SummarizationService --> OpenAIProvider
    SummarizationService --> ClaudeProvider
    SummarizationService --> GeminiProvider
    Services --> Repositories
    Repositories --> SQLAlchemy --> DB
    UploadService --> FileStorage
```

## Processing Pipeline

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend
    participant API as FastAPI
    participant BG as Background Task
    participant W as Faster-Whisper
    participant LLM as Ollama LLM
    participant DB as Database

    U->>FE: Upload audio file
    FE->>API: POST /api/meetings/{id}/upload
    API->>API: Validate MIME type & size
    API->>DB: Store file metadata
    API-->>FE: 200 OK (status: uploaded)
    API->>BG: Start background processing

    Note over BG: Async Pipeline

    BG->>DB: Update status → transcribing
    BG->>W: Transcribe audio
    W-->>BG: Segments + full text

    BG->>DB: Update status → cleaning
    BG->>BG: Clean transcript (filler removal)

    BG->>DB: Store transcript
    BG->>DB: Update status → summarizing
    BG->>LLM: Generate summary from transcript
    LLM-->>BG: JSON (summary, key points, decisions, actions)

    BG->>DB: Store summary
    BG->>DB: Update status → extracting
    BG->>DB: Store action items & keywords
    BG->>DB: Update status → completed

    FE->>API: GET /api/meetings/{id} (polling)
    API-->>FE: Full meeting details
    FE->>U: Display summary, transcript, actions
```

## Database Entity Relationship

```mermaid
erDiagram
    Users ||--o{ Meetings : creates
    Users ||--o{ AuditLogs : generates
    Users ||--|| UserSettings : has
    Meetings ||--|| AudioFiles : has
    Meetings ||--|| Transcripts : has
    Meetings ||--|| Summaries : has
    Meetings ||--o{ ActionItems : contains
    Meetings ||--o{ Keywords : tagged_with

    Users {
        uuid id PK
        string email UK
        string username UK
        string hashed_password
        string role
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    Meetings {
        uuid id PK
        uuid user_id FK
        string title
        text description
        string status
        int duration_seconds
        int participant_count
        datetime meeting_date
        text error_message
        datetime created_at
        datetime updated_at
    }

    AudioFiles {
        uuid id PK
        uuid meeting_id FK
        string original_filename
        string stored_filename
        string file_path
        string mime_type
        bigint file_size
        string checksum
        datetime created_at
    }

    Transcripts {
        uuid id PK
        uuid meeting_id FK
        text full_text
        json segments
        string language
        float confidence
        boolean has_diarization
        datetime created_at
    }

    Summaries {
        uuid id PK
        uuid meeting_id FK
        text executive_summary
        json key_points
        json decisions
        string ai_model
        string ai_provider
        float processing_time
        datetime created_at
    }

    ActionItems {
        uuid id PK
        uuid meeting_id FK
        text description
        string assignee
        string priority
        string status
        date due_date
        datetime created_at
    }

    Keywords {
        uuid id PK
        uuid meeting_id FK
        string keyword
        int frequency
    }

    AuditLogs {
        uuid id PK
        uuid user_id FK
        string action
        string resource_type
        uuid resource_id
        json details
        string ip_address
        datetime created_at
    }

    UserSettings {
        uuid id PK
        uuid user_id FK
        string default_ai_provider
        string default_whisper_model
        boolean enable_diarization
        string default_export_format
        string theme
        datetime updated_at
    }
```

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | React 19 + TypeScript | SPA with type safety |
| Bundler | Vite 8 | Fast HMR and builds |
| Styling | Vanilla CSS | Custom design system with glassmorphism |
| Icons | Lucide React | Consistent icon set |
| Backend | FastAPI | Async Python REST API |
| ORM | SQLAlchemy 2.0 | Async database operations |
| Auth | JWT (python-jose) + bcrypt | Stateless authentication |
| Transcription | Faster-Whisper | Local, fast, privacy-preserving STT |
| Summarization | Ollama | Local LLM (Gemma 3 / Llama / Mistral) |
| Export | ReportLab + python-docx | PDF and DOCX generation |
| Database | SQLite (dev) / PostgreSQL (prod) | Relational data storage |
| Deployment | Docker + Docker Compose | Container orchestration |
| CI/CD | GitHub Actions | Automated testing and building |

## Security Architecture

```mermaid
graph LR
    subgraph Request
        R[Incoming Request]
    end

    subgraph Middleware
        CORS[CORS Check]
        Rate[Rate Limiter]
        JWT[JWT Validation]
        RBAC[Role Check]
    end

    subgraph Validation
        MIME[MIME Verification]
        Size[File Size Check]
        Schema[Pydantic Schema]
        SQL[SQLAlchemy ORM]
    end

    subgraph Logging
        Audit[Audit Log]
    end

    R --> CORS --> Rate --> JWT --> RBAC
    RBAC --> Schema --> SQL
    RBAC --> MIME --> Size
    SQL --> Audit
```

### Security measures implemented:
- **Authentication**: JWT access + refresh tokens (HS256)
- **Password Hashing**: bcrypt with strength validation (uppercase, lowercase, digit, special char)
- **Rate Limiting**: slowapi with per-endpoint limits (10/min for auth, 60/min default)
- **File Upload Security**: MIME magic-byte verification, size limits, UUID filenames, SHA-256 checksums
- **SQL Injection**: Prevented via SQLAlchemy ORM (parameterized queries)
- **XSS Prevention**: React auto-escaping + security headers (X-XSS-Protection, X-Content-Type-Options)
- **CORS**: Configured allow-list
- **Audit Logging**: All security-relevant actions logged with user ID and IP
- **RBAC**: Role-based access control ready (user/admin roles)
- **Secret Management**: All secrets in .env, never hardcoded
