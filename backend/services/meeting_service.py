"""
Meeting service — orchestrates the full meeting processing pipeline.
"""

import logging

from fastapi import BackgroundTasks, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config.constants import MeetingStatus
from backend.models.meeting import Meeting
from backend.repositories.meeting_repo import MeetingRepository
from backend.services.export_service import export_service
from backend.services.upload_service import UploadService

logger = logging.getLogger(__name__)


class MeetingService:
    """Orchestrates meeting upload, transcription, and summarization."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = MeetingRepository(db)
        self.upload_service = UploadService()

    async def upload_and_process(
        self,
        meeting: Meeting,
        file: UploadFile,
        background_tasks: BackgroundTasks,
    ) -> Meeting:
        """Upload audio file and schedule background processing."""
        # Validate and store the file
        file_meta = await self.upload_service.validate_and_store(file)

        # Create audio file record
        await self.repo.create_audio_file(meeting_id=meeting.id, **file_meta)

        # Update meeting status
        meeting = await self.repo.update(meeting, status=MeetingStatus.UPLOADED)

        # Schedule background processing
        background_tasks.add_task(
            self._process_meeting,
            meeting_id=meeting.id,
            file_path=file_meta["file_path"],
        )

        return meeting

    async def _process_meeting(self, meeting_id: str, file_path: str) -> None:
        """
        Background task: transcribe → clean → summarize → extract.
        Uses a new DB session since this runs outside the request lifecycle.
        """
        from backend.database.session import async_session_factory

        async with async_session_factory() as db:
            repo = MeetingRepository(db)

            try:
                meeting = await repo.get_by_id(meeting_id)
                if not meeting:
                    logger.error(f"Meeting {meeting_id} not found for processing")
                    return

                # ── Step 1: Transcribe ──────────────────────────
                await repo.update(meeting, status=MeetingStatus.TRANSCRIBING)
                await db.commit()

                from backend.services.transcription_service import transcription_service

                transcription_result = await transcription_service.transcribe(file_path)

                # ── Step 2: Clean transcript ────────────────────
                await repo.update(meeting, status=MeetingStatus.CLEANING)
                await db.commit()

                from backend.services.transcript_cleaner import transcript_cleaner

                cleaned_text = transcript_cleaner.clean(transcription_result["full_text"])

                # Save transcript
                await repo.create_transcript(
                    meeting_id=meeting_id,
                    full_text=cleaned_text,
                    segments=transcription_result["segments"],
                    language=transcription_result["language"],
                    confidence=transcription_result["confidence"],
                    has_diarization=False,
                )

                # Update meeting duration
                await repo.update(
                    meeting,
                    duration_seconds=transcription_result.get("duration_seconds"),
                )
                await db.commit()

                # ── Step 3: Summarize ───────────────────────────
                await repo.update(meeting, status=MeetingStatus.SUMMARIZING)
                await db.commit()

                from backend.services.summarization_service import SummarizationService

                summarizer = SummarizationService()
                summary_result = await summarizer.summarize(cleaned_text)

                # Save summary
                await repo.create_summary(
                    meeting_id=meeting_id,
                    executive_summary=summary_result["executive_summary"],
                    key_points=summary_result["key_points"],
                    decisions=summary_result["decisions"],
                    ai_model=summary_result["ai_model"],
                    ai_provider=summary_result["ai_provider"],
                    processing_time=summary_result["processing_time"],
                )

                # ── Step 4: Extract action items & keywords ─────
                await repo.update(meeting, status=MeetingStatus.EXTRACTING)
                await db.commit()

                if summary_result.get("action_items"):
                    action_items_data = []
                    for item in summary_result["action_items"]:
                        action_items_data.append({
                            "description": item.get("description", ""),
                            "assignee": item.get("assignee"),
                            "priority": item.get("priority", "medium"),
                        })
                    await repo.create_action_items(meeting_id, action_items_data)

                if summary_result.get("keywords"):
                    keywords_data = [
                        {"keyword": kw, "frequency": 1}
                        for kw in summary_result["keywords"]
                    ]
                    await repo.create_keywords(meeting_id, keywords_data)

                # ── Done ────────────────────────────────────────
                await repo.update(meeting, status=MeetingStatus.COMPLETED)
                await db.commit()

                logger.info(f"Meeting {meeting_id} processing completed successfully.")

            except Exception as e:
                logger.error(f"Meeting {meeting_id} processing failed: {e}", exc_info=True)
                try:
                    meeting = await repo.get_by_id(meeting_id)
                    if meeting:
                        await repo.update(
                            meeting,
                            status=MeetingStatus.FAILED,
                            error_message=str(e)[:500],
                        )
                        await db.commit()
                except Exception as db_err:
                    logger.error(f"Failed to update meeting status: {db_err}")

    async def export_meeting(self, meeting: Meeting, format: str):
        """Export a completed meeting in the specified format."""
        transcript = meeting.transcript
        summary = meeting.summary
        action_items = meeting.action_items or []

        if format == "txt":
            return export_service.export_txt(meeting, transcript, summary, action_items)
        elif format == "docx":
            return export_service.export_docx(meeting, transcript, summary, action_items)
        elif format == "pdf":
            return export_service.export_pdf(meeting, transcript, summary, action_items)
        else:
            raise ValueError(f"Unsupported export format: {format}")
