"""
Upload service — file validation, MIME verification, and secure storage.
"""

from fastapi import UploadFile

from backend.config.constants import ALLOWED_MIME_TYPES
from backend.config.settings import settings
from backend.core.exceptions import FileUploadError
from backend.storage.local_storage import storage

# Try to import python-magic; fall back to extension-based detection
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False

# Fallback MIME map when python-magic isn't available
_EXT_TO_MIME = {
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".m4a": "audio/mp4",
    ".ogg": "audio/ogg",
    ".flac": "audio/flac",
    ".webm": "audio/webm",
    ".mp4": "video/mp4",
    ".wma": "audio/x-ms-wma",
}


class UploadService:
    """Handles audio file upload validation and storage."""

    async def validate_and_store(self, file: UploadFile) -> dict:
        """
        Validate the uploaded file and store it securely.
        Returns metadata dict with file details.
        """
        # Read file data
        file_data = await file.read()

        # 1. Validate file size
        if len(file_data) > settings.max_upload_size_bytes:
            raise FileUploadError(
                f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE_MB}MB."
            )

        if len(file_data) == 0:
            raise FileUploadError("Uploaded file is empty.")

        # 2. Validate file extension
        original_filename = file.filename or "unknown_audio"
        ext = ""
        if "." in original_filename:
            ext = "." + original_filename.rsplit(".", 1)[-1].lower()

        if ext not in settings.ALLOWED_AUDIO_EXTENSIONS:
            raise FileUploadError(
                f"Unsupported file extension: {ext}. "
                f"Allowed: {', '.join(settings.ALLOWED_AUDIO_EXTENSIONS)}"
            )

        # 3. Validate MIME type using magic bytes (with fallback)
        if HAS_MAGIC:
            detected_mime = magic.from_buffer(file_data[:8192], mime=True)
        else:
            # Fallback: derive MIME from extension
            detected_mime = _EXT_TO_MIME.get(ext, "application/octet-stream")

        if detected_mime not in ALLOWED_MIME_TYPES:
            raise FileUploadError(
                f"Unsupported file type: {detected_mime}. "
                f"Allowed types: audio/mpeg, audio/wav, audio/ogg, audio/flac, audio/mp4, etc."
            )

        # 4. Store file with random filename
        stored_filename, file_path, checksum = await storage.save(file_data, original_filename)

        return {
            "original_filename": original_filename,
            "stored_filename": stored_filename,
            "file_path": file_path,
            "mime_type": detected_mime,
            "file_size": len(file_data),
            "checksum": checksum,
        }

    async def delete_file(self, file_path: str) -> None:
        """Delete an uploaded file."""
        await storage.delete(file_path)
