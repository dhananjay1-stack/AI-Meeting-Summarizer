"""
Application-wide constants.
"""

# ── Audio MIME types allowed for upload ──────────────────────────
ALLOWED_MIME_TYPES: set[str] = {
    "audio/mpeg",          # .mp3
    "audio/wav",           # .wav
    "audio/x-wav",         # .wav (alt)
    "audio/mp4",           # .m4a
    "audio/x-m4a",         # .m4a (alt)
    "audio/ogg",           # .ogg
    "audio/flac",          # .flac
    "audio/x-flac",        # .flac (alt)
    "audio/webm",          # .webm
    "video/mp4",           # .mp4 (video with audio)
    "audio/x-ms-wma",      # .wma
    "video/webm",          # .webm (video with audio)
}

# ── Meeting processing statuses ──────────────────────────────────
class MeetingStatus:
    UPLOADED = "uploaded"
    VALIDATING = "validating"
    TRANSCRIBING = "transcribing"
    CLEANING = "cleaning"
    SUMMARIZING = "summarizing"
    EXTRACTING = "extracting"
    COMPLETED = "completed"
    FAILED = "failed"

    ALL = [
        UPLOADED, VALIDATING, TRANSCRIBING, CLEANING,
        SUMMARIZING, EXTRACTING, COMPLETED, FAILED,
    ]


# ── User roles ───────────────────────────────────────────────────
class UserRole:
    USER = "user"
    ADMIN = "admin"

    ALL = [USER, ADMIN]


# ── Action item priorities ───────────────────────────────────────
class ActionItemPriority:
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    ALL = [HIGH, MEDIUM, LOW]


# ── Action item statuses ─────────────────────────────────────────
class ActionItemStatus:
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

    ALL = [PENDING, IN_PROGRESS, COMPLETED]


# ── Export formats ────────────────────────────────────────────────
class ExportFormat:
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"

    ALL = [PDF, DOCX, TXT]


# ── Token types ───────────────────────────────────────────────────
class TokenType:
    ACCESS = "access"
    REFRESH = "refresh"


# ── Pagination defaults ──────────────────────────────────────────
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# ── Password policy ──────────────────────────────────────────────
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128

# ── Audit log actions ────────────────────────────────────────────
class AuditAction:
    USER_REGISTERED = "user_registered"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    MEETING_CREATED = "meeting_created"
    MEETING_DELETED = "meeting_deleted"
    MEETING_EXPORTED = "meeting_exported"
    FILE_UPLOADED = "file_uploaded"
    SETTINGS_UPDATED = "settings_updated"
    PASSWORD_CHANGED = "password_changed"
