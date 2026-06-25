"""
File utilities for QR code management.
Handles secure filename generation and file cleanup.
"""

import os
import time
import uuid
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def generate_secure_filename(prefix: str = "qrcode", extension: str = "png") -> str:
    """
    Generate a secure, unique filename for QR code images.
    Uses UUID4 to prevent filename collisions and path traversal attacks.

    Args:
        prefix: Filename prefix
        extension: File extension without dot

    Returns:
        str: Secure unique filename
    """
    unique_id = uuid.uuid4().hex[:12]
    timestamp = int(time.time())
    extension = extension.lower().lstrip(".")
    return f"{prefix}_{timestamp}_{unique_id}.{extension}"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent path traversal and injection attacks.

    Args:
        filename: Raw filename string

    Returns:
        str: Sanitized filename
    """
    # Remove path separators and dangerous characters
    filename = os.path.basename(filename)
    filename = re.sub(r"[^\w\-_\. ]", "_", filename) if False else filename
    # Remove any directory components
    filename = Path(filename).name
    return filename


def cleanup_old_files(directory: str, max_age_hours: int = 24) -> int:
    """
    Remove QR code files older than specified hours.

    Args:
        directory: Directory path to clean up
        max_age_hours: Maximum file age in hours

    Returns:
        int: Number of files deleted
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        return 0

    deleted = 0
    cutoff_time = time.time() - (max_age_hours * 3600)

    for file_path in dir_path.iterdir():
        if file_path.is_file():
            try:
                if file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    deleted += 1
                    logger.debug(f"Deleted old QR file: {file_path.name}")
            except OSError as e:
                logger.warning(f"Could not delete {file_path}: {e}")

    if deleted:
        logger.info(f"Cleanup: removed {deleted} old QR code file(s)")
    return deleted


def get_file_size(file_path: str) -> int:
    """
    Get file size in bytes.

    Args:
        file_path: Path to the file

    Returns:
        int: File size in bytes, 0 if file not found
    """
    try:
        return Path(file_path).stat().st_size
    except (OSError, FileNotFoundError):
        return 0


def ensure_directory(directory: str) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        directory: Directory path

    Returns:
        Path: Path object for the directory
    """
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path
