"""
User settings API endpoints.
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config.constants import AuditAction
from backend.core.schemas import UserSettingsResponse, UserSettingsUpdateRequest
from backend.database.session import get_db
from backend.models.audit import AuditLog
from backend.models.settings import UserSettings
from backend.models.user import User
from backend.security.dependencies import get_current_active_user

router = APIRouter(prefix="/api/settings", tags=["Settings"])


@router.get("/", response_model=UserSettingsResponse)
async def get_settings(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the current user's settings."""
    result = await db.execute(
        select(UserSettings).where(UserSettings.user_id == current_user.id)
    )
    user_settings = result.scalar_one_or_none()

    if not user_settings:
        # Create default settings if missing
        user_settings = UserSettings(user_id=current_user.id)
        db.add(user_settings)
        await db.flush()

    return UserSettingsResponse.model_validate(user_settings)


@router.patch("/", response_model=UserSettingsResponse)
async def update_settings(
    body: UserSettingsUpdateRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update the current user's settings."""
    result = await db.execute(
        select(UserSettings).where(UserSettings.user_id == current_user.id)
    )
    user_settings = result.scalar_one_or_none()

    if not user_settings:
        user_settings = UserSettings(user_id=current_user.id)
        db.add(user_settings)
        await db.flush()

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(user_settings, key) and value is not None:
            setattr(user_settings, key, value)
    await db.flush()

    # Audit
    audit = AuditLog(
        user_id=current_user.id,
        action=AuditAction.SETTINGS_UPDATED,
        resource_type="settings",
        resource_id=user_settings.id,
        details=update_data,
        ip_address=request.client.host if request.client else None,
    )
    db.add(audit)

    return UserSettingsResponse.model_validate(user_settings)
