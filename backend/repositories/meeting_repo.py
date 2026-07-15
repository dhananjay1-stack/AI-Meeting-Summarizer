"""
Meeting repository — data access layer for Meeting and related models.
"""

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.models.meeting import ActionItem, AudioFile, Keyword, Meeting, Summary, Transcript


class MeetingRepository:
    """CRUD operations for Meeting and related models."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Meeting CRUD ─────────────────────────────────────────────

    async def create(self, user_id: str, title: str, **kwargs) -> Meeting:
        meeting = Meeting(user_id=user_id, title=title, **kwargs)
        self.db.add(meeting)
        await self.db.flush()
        return meeting

    async def get_by_id(self, meeting_id: str, user_id: str | None = None) -> Meeting | None:
        query = (
            select(Meeting)
            .options(
                selectinload(Meeting.audio_file),
                selectinload(Meeting.transcript),
                selectinload(Meeting.summary),
                selectinload(Meeting.action_items),
                selectinload(Meeting.keywords),
            )
            .where(Meeting.id == meeting_id)
        )
        if user_id:
            query = query.where(Meeting.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_by_user(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
    ) -> tuple[list[Meeting], int]:
        """Return paginated meetings for a user and total count."""
        query = select(Meeting).where(Meeting.user_id == user_id)

        if status:
            query = query.where(Meeting.status == status)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginate
        query = (
            query.options(
                selectinload(Meeting.transcript),
                selectinload(Meeting.summary),
                selectinload(Meeting.action_items),
            )
            .order_by(Meeting.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        result = await self.db.execute(query)
        meetings = list(result.scalars().all())
        return meetings, total

    async def search(
        self,
        user_id: str,
        query_text: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Meeting], int]:
        """Full-text search across meeting titles, descriptions, and transcripts."""
        search_pattern = f"%{query_text}%"

        query = (
            select(Meeting)
            .outerjoin(Transcript)
            .where(
                Meeting.user_id == user_id,
                or_(
                    Meeting.title.ilike(search_pattern),
                    Meeting.description.ilike(search_pattern),
                    Transcript.full_text.ilike(search_pattern),
                ),
            )
        )

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginate
        query = (
            query.options(
                selectinload(Meeting.transcript),
                selectinload(Meeting.summary),
                selectinload(Meeting.action_items),
            )
            .order_by(Meeting.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        result = await self.db.execute(query)
        meetings = list(result.scalars().unique().all())
        return meetings, total

    async def update(self, meeting: Meeting, **kwargs) -> Meeting:
        for key, value in kwargs.items():
            if hasattr(meeting, key) and value is not None:
                setattr(meeting, key, value)
        await self.db.flush()
        return meeting

    async def delete(self, meeting: Meeting) -> None:
        await self.db.delete(meeting)
        await self.db.flush()

    # ── Audio File ───────────────────────────────────────────────

    async def create_audio_file(self, meeting_id: str, **kwargs) -> AudioFile:
        audio = AudioFile(meeting_id=meeting_id, **kwargs)
        self.db.add(audio)
        await self.db.flush()
        return audio

    # ── Transcript ───────────────────────────────────────────────

    async def create_transcript(self, meeting_id: str, **kwargs) -> Transcript:
        transcript = Transcript(meeting_id=meeting_id, **kwargs)
        self.db.add(transcript)
        await self.db.flush()
        return transcript

    # ── Summary ──────────────────────────────────────────────────

    async def create_summary(self, meeting_id: str, **kwargs) -> Summary:
        summary = Summary(meeting_id=meeting_id, **kwargs)
        self.db.add(summary)
        await self.db.flush()
        return summary

    # ── Action Items ─────────────────────────────────────────────

    async def create_action_items(
        self, meeting_id: str, items: list[dict]
    ) -> list[ActionItem]:
        action_items = []
        for item_data in items:
            item = ActionItem(meeting_id=meeting_id, **item_data)
            self.db.add(item)
            action_items.append(item)
        await self.db.flush()
        return action_items

    async def get_action_item(self, item_id: str) -> ActionItem | None:
        result = await self.db.execute(select(ActionItem).where(ActionItem.id == item_id))
        return result.scalar_one_or_none()

    async def update_action_item(self, item: ActionItem, **kwargs) -> ActionItem:
        for key, value in kwargs.items():
            if hasattr(item, key) and value is not None:
                setattr(item, key, value)
        await self.db.flush()
        return item

    # ── Keywords ─────────────────────────────────────────────────

    async def create_keywords(self, meeting_id: str, keywords: list[dict]) -> list[Keyword]:
        keyword_objects = []
        for kw_data in keywords:
            kw = Keyword(meeting_id=meeting_id, **kw_data)
            self.db.add(kw)
            keyword_objects.append(kw)
        await self.db.flush()
        return keyword_objects

    # ── Stats ────────────────────────────────────────────────────

    async def get_user_stats(self, user_id: str) -> dict:
        """Get summary statistics for a user's meetings."""
        total = await self.db.execute(
            select(func.count()).where(Meeting.user_id == user_id)
        )
        completed = await self.db.execute(
            select(func.count()).where(
                Meeting.user_id == user_id, Meeting.status == "completed"
            )
        )
        total_duration = await self.db.execute(
            select(func.sum(Meeting.duration_seconds)).where(Meeting.user_id == user_id)
        )

        return {
            "total_meetings": total.scalar() or 0,
            "completed_meetings": completed.scalar() or 0,
            "total_duration_seconds": total_duration.scalar() or 0,
        }
