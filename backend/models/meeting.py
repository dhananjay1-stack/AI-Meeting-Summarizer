"""
Meeting-related models: Meeting, AudioFile, Transcript, Summary, ActionItem, Keyword.
"""

from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base, TimestampMixin, UUIDMixin, utc_now


class Meeting(UUIDMixin, TimestampMixin, Base):
    """A meeting record owned by a user."""

    __tablename__ = "meetings"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="uploaded", nullable=False, index=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    participant_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    meeting_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="meetings")
    audio_file = relationship(
        "AudioFile", back_populates="meeting", uselist=False, cascade="all, delete-orphan"
    )
    transcript = relationship(
        "Transcript", back_populates="meeting", uselist=False, cascade="all, delete-orphan"
    )
    summary = relationship(
        "Summary", back_populates="meeting", uselist=False, cascade="all, delete-orphan"
    )
    action_items = relationship(
        "ActionItem", back_populates="meeting", cascade="all, delete-orphan"
    )
    keywords = relationship("Keyword", back_populates="meeting", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Meeting {self.title} [{self.status}]>"


class AudioFile(UUIDMixin, Base):
    """Uploaded audio file metadata."""

    __tablename__ = "audio_files"

    meeting_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("meetings.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    original_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(256), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA-256
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    # Relationship
    meeting = relationship("Meeting", back_populates="audio_file")

    def __repr__(self) -> str:
        return f"<AudioFile {self.original_filename}>"


class Transcript(UUIDMixin, Base):
    """Transcription result for a meeting."""

    __tablename__ = "transcripts"

    meeting_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("meetings.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    full_text: Mapped[str] = mapped_column(Text, nullable=False)
    segments: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # Timestamped segments
    language: Mapped[str | None] = mapped_column(String(10), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    has_diarization: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    # Relationship
    meeting = relationship("Meeting", back_populates="transcript")

    def __repr__(self) -> str:
        return f"<Transcript meeting={self.meeting_id} lang={self.language}>"


class Summary(UUIDMixin, Base):
    """AI-generated summary for a meeting."""

    __tablename__ = "summaries"

    meeting_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("meetings.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    executive_summary: Mapped[str] = mapped_column(Text, nullable=False)
    key_points: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    decisions: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ai_model: Mapped[str] = mapped_column(String(100), nullable=False)
    ai_provider: Mapped[str] = mapped_column(String(50), nullable=False)
    processing_time: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    # Relationship
    meeting = relationship("Meeting", back_populates="summary")

    def __repr__(self) -> str:
        return f"<Summary meeting={self.meeting_id} provider={self.ai_provider}>"


class ActionItem(UUIDMixin, Base):
    """Extracted action item from a meeting."""

    __tablename__ = "action_items"

    meeting_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    assignee: Mapped[str | None] = mapped_column(String(128), nullable=True)
    priority: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    # Relationship
    meeting = relationship("Meeting", back_populates="action_items")

    def __repr__(self) -> str:
        return f"<ActionItem {self.description[:50]}>"


class Keyword(UUIDMixin, Base):
    """Extracted keyword/topic from a meeting."""

    __tablename__ = "keywords"

    meeting_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True
    )
    keyword: Mapped[str] = mapped_column(String(100), nullable=False)
    frequency: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Relationship
    meeting = relationship("Meeting", back_populates="keywords")

    def __repr__(self) -> str:
        return f"<Keyword {self.keyword} (x{self.frequency})>"
