"""
Pydantic schemas for request/response validation.
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from backend.config.constants import (
    ActionItemPriority,
    ActionItemStatus,
    ExportFormat,
    MIN_PASSWORD_LENGTH,
)


# ═══════════════════════════════════════════════════════════════
# Authentication Schemas
# ═══════════════════════════════════════════════════════════════


class UserRegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=64, pattern=r"^[a-zA-Z0-9_-]+$")
    password: str = Field(..., min_length=MIN_PASSWORD_LENGTH, max_length=128)


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════
# Meeting Schemas
# ═══════════════════════════════════════════════════════════════


class MeetingCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=256)
    description: Optional[str] = Field(None, max_length=2000)
    meeting_date: Optional[datetime] = None
    participant_count: Optional[int] = Field(None, ge=1, le=1000)


class MeetingUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=256)
    description: Optional[str] = Field(None, max_length=2000)
    meeting_date: Optional[datetime] = None
    participant_count: Optional[int] = Field(None, ge=1, le=1000)


class MeetingResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    status: str
    duration_seconds: Optional[int]
    participant_count: Optional[int]
    meeting_date: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    has_transcript: bool = False
    has_summary: bool = False
    action_item_count: int = 0

    model_config = {"from_attributes": True}


class MeetingListResponse(BaseModel):
    meetings: list[MeetingResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ═══════════════════════════════════════════════════════════════
# Audio File Schema
# ═══════════════════════════════════════════════════════════════


class AudioFileResponse(BaseModel):
    id: str
    original_filename: str
    mime_type: str
    file_size: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════
# Transcript Schemas
# ═══════════════════════════════════════════════════════════════


class TranscriptSegment(BaseModel):
    start: float
    end: float
    text: str
    speaker: Optional[str] = None


class TranscriptResponse(BaseModel):
    id: str
    full_text: str
    segments: Optional[list[dict]] = None
    language: Optional[str]
    confidence: Optional[float]
    has_diarization: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════
# Summary Schemas
# ═══════════════════════════════════════════════════════════════


class SummaryResponse(BaseModel):
    id: str
    executive_summary: str
    key_points: Optional[list[str]] = None
    decisions: Optional[list[str]] = None
    ai_model: str
    ai_provider: str
    processing_time: Optional[float]
    created_at: datetime

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════
# Action Item Schemas
# ═══════════════════════════════════════════════════════════════


class ActionItemResponse(BaseModel):
    id: str
    description: str
    assignee: Optional[str]
    priority: str
    status: str
    due_date: Optional[date]
    created_at: datetime

    model_config = {"from_attributes": True}


class ActionItemUpdateRequest(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee: Optional[str] = None
    due_date: Optional[date] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        if v is not None and v not in ActionItemStatus.ALL:
            raise ValueError(f"Status must be one of: {ActionItemStatus.ALL}")
        return v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str | None) -> str | None:
        if v is not None and v not in ActionItemPriority.ALL:
            raise ValueError(f"Priority must be one of: {ActionItemPriority.ALL}")
        return v


# ═══════════════════════════════════════════════════════════════
# Keyword Schema
# ═══════════════════════════════════════════════════════════════


class KeywordResponse(BaseModel):
    keyword: str
    frequency: int

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════
# Meeting Detail (combined response)
# ═══════════════════════════════════════════════════════════════


class MeetingDetailResponse(BaseModel):
    meeting: MeetingResponse
    audio_file: Optional[AudioFileResponse] = None
    transcript: Optional[TranscriptResponse] = None
    summary: Optional[SummaryResponse] = None
    action_items: list[ActionItemResponse] = []
    keywords: list[KeywordResponse] = []


# ═══════════════════════════════════════════════════════════════
# Export Schema
# ═══════════════════════════════════════════════════════════════


class ExportRequest(BaseModel):
    format: str = Field(default="pdf")

    @field_validator("format")
    @classmethod
    def validate_format(cls, v: str) -> str:
        if v not in ExportFormat.ALL:
            raise ValueError(f"Format must be one of: {ExportFormat.ALL}")
        return v


# ═══════════════════════════════════════════════════════════════
# User Settings Schemas
# ═══════════════════════════════════════════════════════════════


class UserSettingsResponse(BaseModel):
    default_ai_provider: str
    default_whisper_model: str
    enable_diarization: bool
    default_export_format: str
    theme: str

    model_config = {"from_attributes": True}


class UserSettingsUpdateRequest(BaseModel):
    default_ai_provider: Optional[str] = None
    default_whisper_model: Optional[str] = None
    enable_diarization: Optional[bool] = None
    default_export_format: Optional[str] = None
    theme: Optional[str] = None


# ═══════════════════════════════════════════════════════════════
# Search Schema
# ═══════════════════════════════════════════════════════════════


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


# ═══════════════════════════════════════════════════════════════
# Generic Responses
# ═══════════════════════════════════════════════════════════════


class MessageResponse(BaseModel):
    message: str


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
