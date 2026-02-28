"""
Logging utilities for the Voice Assistant backend
"""

import logging
import os
from pathlib import Path
from .settings import LogConfig


def setup_logging() -> logging.Logger:
    """Setup and configure logging for the application"""

    # Create log directory if it doesn't exist
    log_dir = Path(LogConfig.LOG_DIR)
    log_dir.mkdir(exist_ok=True)

    # Create logger
    logger = logging.getLogger("voice_assistant")
    logger.setLevel(LogConfig.LOG_LEVEL)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LogConfig.LOG_LEVEL)
    formatter = logging.Formatter(LogConfig.LOG_FORMAT)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    file_handler = logging.FileHandler(log_dir / "voice_assistant.log", encoding='utf-8')
    file_handler.setLevel(LogConfig.LOG_LEVEL)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


# Create module-level logger
logger = setup_logging()


def log_success(message: str) -> None:
    """Log a success message"""
    logger.info(f"[SUCCESS] {message}")


def log_error(message: str) -> None:
    """Log an error message"""
    logger.error(f"[ERROR] {message}")


def log_warning(message: str) -> None:
    """Log a warning message"""
    logger.warning(f"[WARNING] {message}")


def log_info(message: str) -> None:
    """Log an info message"""
    logger.info(f"[INFO] {message}")


def log_websocket(message: str) -> None:
    """Log a WebSocket message (debug only)"""
    from .settings import LogConfig
    if LogConfig.DEBUG:
        logger.debug(f"[WEBSOCKET] {message}")


def log_audio(message: str) -> None:
    """Log an audio message (debug only)"""
    from .settings import LogConfig
    if LogConfig.DEBUG:
        logger.debug(f"[AUDIO] {message}")


def log_chat(message: str) -> None:
    """Log a chat message"""
    logger.info(f"[CHAT] {message}")
