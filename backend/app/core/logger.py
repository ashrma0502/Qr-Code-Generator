"""
Logger configuration module.
Sets up structured logging for the application.
"""

import logging
import logging.handlers
from pathlib import Path


def setup_logger(settings) -> None:
    """
    Configure application-wide logging based on settings.

    Args:
        settings: Application settings object
    """
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Root logger configuration
    handlers = [logging.StreamHandler()]

    # File handler (optional)
    if settings.log_file:
        log_path = Path(settings.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
        )
        handlers.append(file_handler)

    logging.basicConfig(
        level=log_level,
        format=settings.log_format,
        handlers=handlers,
        force=True,
    )

    # Suppress noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("multipart").setLevel(logging.WARNING)
