"""
Local file storage with abstract interface for future S3 support.
"""

import hashlib
import os
import uuid
from pathlib import Path

from backend.config.settings import settings


class StorageBackend:
    """Abstract storage interface."""

    async def save(self, file_data: bytes, filename: str) -> str:
        raise NotImplementedError

    async def delete(self, file_path: str) -> None:
        raise NotImplementedError

    async def get_path(self, file_path: str) -> str:
        raise NotImplementedError


class LocalStorage(StorageBackend):
    """Local filesystem storage."""

    def __init__(self, base_dir: str | None = None):
        self.base_dir = Path(base_dir or settings.UPLOAD_DIR)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _generate_stored_filename(self, original_filename: str) -> str:
        """Generate a UUID-based random filename preserving the extension."""
        ext = Path(original_filename).suffix.lower()
        return f"{uuid.uuid4().hex}{ext}"

    async def save(self, file_data: bytes, original_filename: str) -> tuple[str, str, str]:
        """
        Save file data to disk.
        Returns (stored_filename, file_path, sha256_checksum).
        """
        stored_filename = self._generate_stored_filename(original_filename)
        file_path = self.base_dir / stored_filename

        # Write file
        with open(file_path, "wb") as f:
            f.write(file_data)

        # Compute checksum
        checksum = hashlib.sha256(file_data).hexdigest()

        return stored_filename, str(file_path), checksum

    async def delete(self, file_path: str) -> None:
        """Delete a file from disk."""
        path = Path(file_path)
        if path.exists():
            os.remove(path)

    async def get_path(self, file_path: str) -> str:
        """Return the full filesystem path."""
        return str(file_path)


# Singleton
storage = LocalStorage()
