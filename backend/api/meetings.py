"""
Meeting API endpoints: CRUD, upload, process, search, export.
"""

import math

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config.constants import AuditAction, MeetingStatus
from backend.core.schemas import (
    ActionItemResponse,
    ActionItemUpdateRequest,
    ExportRequest,
    MeetingCreateRequest,
    MeetingDetailResponse,
    MeetingListResponse,
    MeetingResponse,
    MeetingUpdateRequest,
    MessageResponse,
    AudioFileResponse,
    TranscriptResponse,
    SummaryResponse,
    KeywordResponse,
)
from backend.database.session import get_db
from backend.models.audit import AuditLog
from backend.models.user import User
from backend.repositories.meeting_repo import MeetingRepository
from backend.security.dependencies import get_current_active_user
from backend.services.meeting_service import MeetingService

router = APIRouter(prefix="/api/meetings", tags=["Meetings"])


def _build_meeting_response(meeting) -> MeetingResponse:
    """Convert a Meeting ORM object to a MeetingResponse.

    Safe for both eagerly-loaded and freshly-created meetings
    (where relationships may not have been loaded yet).
    """
    from sqlalchemy.orm import attributes

    def _is_loaded(obj, attr_name: str) -> bool:
        """Check if a relationship attribute has been eagerly loaded."""
        try:
            state = attributes.instance_state(obj)
            return attr_name not in state.unloaded
        except Exception:
            return False

    has_transcript = meeting.transcript is not None if _is_loaded(meeting, "transcript") else False
    has_summary = meeting.summary is not None if _is_loaded(meeting, "summary") else False
    action_count = (
        len(meeting.action_items) if _is_loaded(meeting, "action_items") and meeting.action_items else 0
    )

    return MeetingResponse(
        id=meeting.id,
        title=meeting.title,
        description=meeting.description,
        status=meeting.status,
        duration_seconds=meeting.duration_seconds,
        participant_count=meeting.participant_count,
        meeting_date=meeting.meeting_date,
        error_message=meeting.error_message,
        created_at=meeting.created_at,
        updated_at=meeting.updated_at,
        has_transcript=has_transcript,
        has_summary=has_summary,
        action_item_count=action_count,
    )


@router.post("/", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
async def create_meeting(
    body: MeetingCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new meeting record."""
    repo = MeetingRepository(db)
    meeting = await repo.create(
        user_id=current_user.id,
        title=body.title,
        description=body.description,
        meeting_date=body.meeting_date,
        participant_count=body.participant_count,
    )
    return _build_meeting_response(meeting)


@router.get("/", response_model=MeetingListResponse)
async def list_meetings(
    page: int = 1,
    page_size: int = 20,
    status_filter: str | None = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List the current user's meetings with pagination."""
    repo = MeetingRepository(db)
    meetings, total = await repo.list_by_user(
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        status=status_filter,
    )

    return MeetingListResponse(
        meetings=[_build_meeting_response(m) for m in meetings],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total > 0 else 1,
    )


@router.get("/search", response_model=MeetingListResponse)
async def search_meetings(
    query: str,
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Search meetings by title, description, or transcript content."""
    repo = MeetingRepository(db)
    meetings, total = await repo.search(
        user_id=current_user.id,
        query_text=query,
        page=page,
        page_size=page_size,
    )

    return MeetingListResponse(
        meetings=[_build_meeting_response(m) for m in meetings],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total > 0 else 1,
    )


@router.get("/stats")
async def get_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get meeting statistics for the current user."""
    repo = MeetingRepository(db)
    stats = await repo.get_user_stats(current_user.id)
    return stats


@router.get("/{meeting_id}", response_model=MeetingDetailResponse)
async def get_meeting(
    meeting_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a meeting's full details including transcript, summary, and action items."""
    repo = MeetingRepository(db)
    meeting = await repo.get_by_id(meeting_id, user_id=current_user.id)

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found.")

    return MeetingDetailResponse(
        meeting=_build_meeting_response(meeting),
        audio_file=AudioFileResponse.model_validate(meeting.audio_file)
        if meeting.audio_file
        else None,
        transcript=TranscriptResponse.model_validate(meeting.transcript)
        if meeting.transcript
        else None,
        summary=SummaryResponse.model_validate(meeting.summary)
        if meeting.summary
        else None,
        action_items=[
            ActionItemResponse.model_validate(item)
            for item in (meeting.action_items or [])
        ],
        keywords=[
            KeywordResponse.model_validate(kw)
            for kw in (meeting.keywords or [])
        ],
    )


@router.patch("/{meeting_id}", response_model=MeetingResponse)
async def update_meeting(
    meeting_id: str,
    body: MeetingUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a meeting's metadata."""
    repo = MeetingRepository(db)
    meeting = await repo.get_by_id(meeting_id, user_id=current_user.id)

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found.")

    update_data = body.model_dump(exclude_unset=True)
    if update_data:
        meeting = await repo.update(meeting, **update_data)

    return _build_meeting_response(meeting)


@router.delete("/{meeting_id}", response_model=MessageResponse)
async def delete_meeting(
    meeting_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a meeting and all associated data."""
    repo = MeetingRepository(db)
    meeting = await repo.get_by_id(meeting_id, user_id=current_user.id)

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found.")

    await repo.delete(meeting)

    # Audit
    audit = AuditLog(
        user_id=current_user.id,
        action=AuditAction.MEETING_DELETED,
        resource_type="meeting",
        resource_id=meeting_id,
        ip_address=request.client.host if request.client else None,
    )
    db.add(audit)

    return MessageResponse(message="Meeting deleted successfully.")


@router.post("/{meeting_id}/upload", response_model=MeetingResponse)
async def upload_audio(
    meeting_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload an audio file for a meeting and start processing."""
    repo = MeetingRepository(db)
    meeting = await repo.get_by_id(meeting_id, user_id=current_user.id)

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found.")

    if meeting.audio_file:
        raise HTTPException(status_code=400, detail="Audio file already uploaded for this meeting.")

    # Use the meeting service for upload + background processing
    service = MeetingService(db)
    meeting = await service.upload_and_process(
        meeting=meeting,
        file=file,
        background_tasks=background_tasks,
    )

    # Audit
    audit = AuditLog(
        user_id=current_user.id,
        action=AuditAction.FILE_UPLOADED,
        resource_type="meeting",
        resource_id=meeting_id,
        ip_address=request.client.host if request.client else None,
        details={"filename": file.filename},
    )
    db.add(audit)

    return _build_meeting_response(meeting)


@router.post("/{meeting_id}/export")
async def export_meeting(
    meeting_id: str,
    body: ExportRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Export meeting data as PDF, DOCX, or TXT."""
    repo = MeetingRepository(db)
    meeting = await repo.get_by_id(meeting_id, user_id=current_user.id)

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found.")

    if meeting.status != MeetingStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Meeting processing not complete.")

    service = MeetingService(db)
    file_response = await service.export_meeting(meeting, body.format)

    # Audit
    audit = AuditLog(
        user_id=current_user.id,
        action=AuditAction.MEETING_EXPORTED,
        resource_type="meeting",
        resource_id=meeting_id,
        ip_address=request.client.host if request.client else None,
        details={"format": body.format},
    )
    db.add(audit)

    return file_response


@router.patch("/{meeting_id}/action-items/{item_id}", response_model=ActionItemResponse)
async def update_action_item(
    meeting_id: str,
    item_id: str,
    body: ActionItemUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an action item's status, priority, or assignee."""
    repo = MeetingRepository(db)
    meeting = await repo.get_by_id(meeting_id, user_id=current_user.id)

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found.")

    item = await repo.get_action_item(item_id)
    if not item or item.meeting_id != meeting_id:
        raise HTTPException(status_code=404, detail="Action item not found.")

    update_data = body.model_dump(exclude_unset=True)
    if update_data:
        item = await repo.update_action_item(item, **update_data)

    return ActionItemResponse.model_validate(item)
