# Developer Guide

## Getting Started

This guide covers the codebase structure, conventions, and how to extend the application.

## Project Architecture

The application follows a **layered architecture**:

```
Request → API Routes → Services → Repositories → Database
                  ↓
             AI Pipeline (Whisper → Ollama)
```

### Layer Responsibilities

| Layer | Directory | Purpose |
|-------|-----------|---------|
| **API** | `backend/api/` | HTTP endpoints, request parsing, response formatting |
| **Core** | `backend/core/` | Pydantic schemas, exception classes |
| **Services** | `backend/services/` | Business logic, pipeline orchestration |
| **Repositories** | `backend/repositories/` | Database queries (data access layer) |
| **Models** | `backend/models/` | SQLAlchemy ORM models |
| **Security** | `backend/security/` | JWT, password hashing, auth guards |
| **Config** | `backend/config/` | Settings and constants |

### Key Design Decisions

1. **Async everywhere** — The entire stack is async (FastAPI, SQLAlchemy async, aiosqlite/asyncpg)
2. **Repository pattern** — Database access is isolated from business logic
3. **Provider abstraction** — AI providers are swappable via the `AIProvider` interface
4. **Background processing** — Audio processing runs in `BackgroundTasks` to avoid blocking requests
5. **UUID primary keys** — All models use UUID4 strings for IDs

---

## Adding a New API Endpoint

1. Define Pydantic schemas in `backend/core/schemas.py`
2. Add repository methods in `backend/repositories/`
3. Implement business logic in `backend/services/`
4. Create the route handler in `backend/api/`
5. Register the router in `backend/main.py`

---

## Adding a New AI Provider

1. Create a new class in `backend/services/ai_provider.py`:

```python
class MyProvider(AIProvider):
    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        # Your implementation
        ...

    def get_model_name(self) -> str:
        return "my-model"

    def get_provider_name(self) -> str:
        return "myprovider"
```

2. Register it in `get_ai_provider()` in the same file.
3. Add config settings in `backend/config/settings.py`.
4. Update the frontend settings selector in `SettingsPage.tsx`.

---

## Database Migrations

For development, tables auto-create on startup. For production, use Alembic:

```bash
# Initialize Alembic (one-time)
alembic init backend/database/migrations

# Generate a migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

---

## Testing

```bash
# Run all tests
python -m pytest backend/tests/ -v

# Run with coverage
python -m pytest backend/tests/ -v --cov=backend --cov-report=term-missing

# Run specific test file
python -m pytest backend/tests/test_auth.py -v

# Run specific test class
python -m pytest backend/tests/test_auth.py::TestLogin -v
```

### Test Conventions

- Tests use an **in-memory SQLite** database (auto-reset per test)
- `client` fixture: unauthenticated HTTP client
- `auth_client` fixture: pre-registered + logged-in client
- Async tests decorated with `@pytest.mark.asyncio`

---

## Code Style

- **Formatter:** Black (100 char line length)
- **Linter:** Ruff
- **Type hints:** Required on all function signatures

```bash
# Format
black backend/

# Lint
ruff check backend/

# Fix lint issues
ruff check backend/ --fix
```

---

## Frontend Development

```bash
cd frontend
npm run dev        # Start dev server with HMR
npm run build      # Production build
npm run preview    # Preview production build
```

### Component Structure

- **Pages** (`src/pages/`): Full page components with their own CSS
- **Components** (`src/components/`): Reusable UI components
- **Lib** (`src/lib/`): API client, auth context, utilities

### Design System

The design system is defined in `src/index.css` using CSS custom properties:
- Colors, typography, spacing, shadows are all tokenized
- Dark/light mode via `[data-theme="light"]` selector
- Use `glass-card`, `btn-primary`, `btn-secondary`, `input-field` utility classes
