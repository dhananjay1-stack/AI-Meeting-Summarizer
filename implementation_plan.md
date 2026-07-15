# AI Meeting Summarizer — Completion & Self-Verification Plan

## Background

The previous session built the full 12-phase architecture of the AI Meeting Summarizer:
- **Backend**: FastAPI with 22 routes, JWT auth, SQLAlchemy models (9 tables), rate limiting, AI provider abstraction, export service — **all 19 tests passing, 0 lint errors, health check confirmed live**
- **Frontend**: React + Vite + TypeScript with 5 pages (Login, Dashboard, Upload, MeetingDetail, Settings), premium dark-mode CSS design system with glassmorphism — **builds cleanly**
- **DevOps**: Docker Compose, GitHub Actions CI, Dockerfiles, documentation

However, the project was **never run end-to-end** (frontend + backend together), and several integration gaps remain. Additionally, the user requests an **autonomous self-verification loop** where the agent validates its own web application.

---

## Phase 1: Backend Critical Fixes

### [MODIFY] [settings.py](file:///c:/Users/DELL/Meeting_Summarizer/backend/config/settings.py)
- Add `UPLOAD_DIR` setting with default `./uploads`
- Ensure `ALLOWED_ORIGINS` includes `http://localhost:5173` (Vite dev server)

### [MODIFY] [main.py](file:///c:/Users/DELL/Meeting_Summarizer/backend/main.py)
- Create `uploads/` directory on startup if it doesn't exist
- Add static file serving for uploaded files

### [MODIFY] [meeting_service.py](file:///c:/Users/DELL/Meeting_Summarizer/backend/services/meeting_service.py)
- Add proper background task support using FastAPI's `BackgroundTasks`
- Ensure meeting processing doesn't block the upload response

### [MODIFY] [meetings.py](file:///c:/Users/DELL/Meeting_Summarizer/backend/api/meetings.py)
- Wire up `BackgroundTasks` for async processing
- Add proper file validation with fallback if `python-magic` fails
- Add export download endpoints that actually serve files

---

## Phase 2: Frontend — Global Navigation & Layout Shell

> [!IMPORTANT]
> Currently there is **no navigation component**. Users cannot move between pages without manually typing URLs. This is the #1 UX blocker.

### [NEW] [Sidebar.tsx](file:///c:/Users/DELL/Meeting_Summarizer/frontend/src/components/Sidebar.tsx)
- Premium glassmorphic sidebar with:
  - App logo/branding with gradient text
  - Navigation links: Dashboard, Upload, Settings
  - Active route indicator with animated pill
  - User avatar + email display
  - Logout button
  - Collapsible on mobile (hamburger trigger)
  - Smooth slide-in animation

### [NEW] [Layout.tsx](file:///c:/Users/DELL/Meeting_Summarizer/frontend/src/components/Layout.tsx)
- Wraps protected pages in Sidebar + main content area
- Responsive: sidebar collapses to overlay on mobile
- Animated page transitions

### [MODIFY] [App.tsx](file:///c:/Users/DELL/Meeting_Summarizer/frontend/src/App.tsx)
- Wrap all `ProtectedRoute` pages in `<Layout>` component

### [MODIFY] [index.css](file:///c:/Users/DELL/Meeting_Summarizer/frontend/src/index.css)
- Add sidebar styles, layout grid, mobile overlay, skeleton loaders
- Add shimmer animation for loading skeletons

---

## Phase 3: Frontend — Page Enhancements

### [MODIFY] [DashboardPage.tsx](file:///c:/Users/DELL/Meeting_Summarizer/frontend/src/pages/DashboardPage.tsx)
- Add search bar with real-time filtering
- Add meeting cards with status badges (uploaded → transcribing → summarizing → completed)
- Add skeleton loading states
- Add empty state illustration
- Add stats header (total meetings, total hours, action items)

### [MODIFY] [UploadPage.tsx](file:///c:/Users/DELL/Meeting_Summarizer/frontend/src/pages/UploadPage.tsx)
- Fix drag-and-drop to properly upload to backend
- Add upload progress bar with percentage
- Add file type validation (visual feedback)
- Add success redirect to meeting detail page

### [MODIFY] [MeetingDetailPage.tsx](file:///c:/Users/DELL/Meeting_Summarizer/frontend/src/pages/MeetingDetailPage.tsx)
- Add tabbed view: Transcript | Summary | Action Items
- Add export buttons (PDF, DOCX, TXT) that call backend export API
- Add copy-to-clipboard functionality
- Add processing status with animated progress

### [MODIFY] [SettingsPage.tsx](file:///c:/Users/DELL/Meeting_Summarizer/frontend/src/pages/SettingsPage.tsx)
- Add working theme toggle (dark/light) with persistence in localStorage
- Add AI provider selection dropdown
- Add profile update form

### [MODIFY] [LoginPage.tsx](file:///c:/Users/DELL/Meeting_Summarizer/frontend/src/pages/LoginPage.tsx)
- Polish with animated background particles/gradient
- Add form validation feedback
- Add password strength indicator for registration

---

## Phase 4: Frontend — API Integration & Vite Proxy

### [MODIFY] [vite.config.ts](file:///c:/Users/DELL/Meeting_Summarizer/frontend/vite.config.ts)
- Add proxy configuration: `/api` → `http://localhost:8000`

### [MODIFY] [api.ts](file:///c:/Users/DELL/Meeting_Summarizer/frontend/src/lib/api.ts)
- Update base URL to use relative paths (works with Vite proxy)
- Add API functions for: search, export, meeting status polling
- Add proper error handling with toast-like feedback

### [MODIFY] [auth.ts](file:///c:/Users/DELL/Meeting_Summarizer/frontend/src/lib/auth.ts)
- Ensure token refresh logic works
- Add proper logout cleanup

---

## Phase 5: Expanded Testing

### [MODIFY] [test_meetings.py](file:///c:/Users/DELL/Meeting_Summarizer/backend/tests/test_meetings.py)
- Add upload tests with real file fixtures
- Add export endpoint tests
- Add search/filter tests
- Add pagination tests

### [NEW] [test_export.py](file:///c:/Users/DELL/Meeting_Summarizer/backend/tests/test_export.py)
- Test PDF, DOCX, TXT generation
- Test unauthorized access prevention

### [NEW] [test_integration.py](file:///c:/Users/DELL/Meeting_Summarizer/backend/tests/test_integration.py)
- Full end-to-end: register → login → upload → check status → view summary → export

---

## Phase 6: Autonomous Self-Verification Loop

> [!IMPORTANT]
> This phase goes beyond the original SRS. The agent will:
> 1. Start the backend server (`uvicorn`)
> 2. Start the frontend dev server (`npm run dev`)
> 3. Programmatically test every route and interaction
> 4. Report pass/fail with details

### Verification Steps

| # | Test | Method | Expected |
|---|------|--------|----------|
| 1 | Backend health | `GET /api/health` | `{"status":"healthy"}` |
| 2 | Swagger docs | `GET /api/docs` | HTTP 200 |
| 3 | Register user | `POST /api/auth/register` | HTTP 201 + token |
| 4 | Login user | `POST /api/auth/login` | HTTP 200 + token |
| 5 | Create meeting | `POST /api/meetings` with file | HTTP 201 |
| 6 | List meetings | `GET /api/meetings` | HTTP 200 + array |
| 7 | Get meeting detail | `GET /api/meetings/{id}` | HTTP 200 + data |
| 8 | Search meetings | `GET /api/meetings?search=test` | HTTP 200 |
| 9 | Export TXT | `GET /api/meetings/{id}/export?format=txt` | HTTP 200 + file |
| 10 | Settings GET | `GET /api/settings` | HTTP 200 |
| 11 | Settings UPDATE | `PUT /api/settings` | HTTP 200 |
| 12 | Frontend loads | `GET http://localhost:5173` | HTTP 200 + HTML |
| 13 | Frontend login page | `GET http://localhost:5173/login` | HTTP 200 |
| 14 | TypeScript build | `npm run build` | Exit code 0 |
| 15 | All pytest pass | `pytest backend/tests/ -v` | All green |

### [NEW] [verify.py](file:///c:/Users/DELL/Meeting_Summarizer/backend/tests/verify.py)
- Automated verification script that hits all endpoints
- Reports pass/fail with response details
- Can be run standalone: `python -m backend.tests.verify`

---

## Verification Plan

### Automated Tests
```bash
python -m pytest backend/tests/ -v --tb=short
cd frontend && npm run build
python -m backend.tests.verify
```

### Manual Verification (Agent Self-Test)
- Start backend: `uvicorn backend.main:app --host 127.0.0.1 --port 8000`
- Start frontend: `cd frontend && npm run dev`
- Hit every API endpoint via PowerShell `Invoke-WebRequest`
- Verify frontend serves HTML
- Verify full register → login → upload → view flow

---

## Open Questions

> [!NOTE]
> **Ollama requirement**: The AI summarization pipeline requires Ollama running locally with a model pulled. For the self-verification, should I:
> - Skip AI processing tests if Ollama isn't available (graceful fallback)?
> - Mock the AI responses for testing?
> 
> **Recommendation**: Mock AI for automated tests; skip gracefully in self-verification if Ollama isn't running.

> [!NOTE]
> **Faster-Whisper**: The transcription service requires `faster-whisper` which needs a C++ build toolchain. Should I:
> - Install it (may fail on Windows without Visual C++ Build Tools)?
> - Add a mock/fallback transcription mode for testing?
>
> **Recommendation**: Add fallback mode that creates a placeholder transcript, allowing the full flow to be tested without GPU/native deps.
