"""
JWT access and refresh token management.
"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from backend.config.constants import TokenType
from backend.config.settings import settings


def create_access_token(user_id: str, role: str) -> str:
    """Create a short-lived access token."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,
        "role": role,
        "type": TokenType.ACCESS,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    """Create a long-lived refresh token."""
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": user_id,
        "type": TokenType.REFRESH,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict | None:
    """
    Decode and validate a JWT token.
    Returns the payload dict or None if invalid/expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        return None


def verify_access_token(token: str) -> dict | None:
    """Decode token and verify it is an access token."""
    payload = decode_token(token)
    if payload and payload.get("type") == TokenType.ACCESS:
        return payload
    return None


def verify_refresh_token(token: str) -> dict | None:
    """Decode token and verify it is a refresh token."""
    payload = decode_token(token)
    if payload and payload.get("type") == TokenType.REFRESH:
        return payload
    return None
