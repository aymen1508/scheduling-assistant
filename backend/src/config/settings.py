"""
Configuration management for the Voice Assistant backend
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from centralized config directory
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, "../../../config/.env")
load_dotenv(env_path, override=True)


class AzureVoiceLiveConfig:
    """Azure VoiceLive API configuration"""

    ENDPOINT: str = os.environ.get(
        "AZURE_VOICELIVE_ENDPOINT",
        "https://vikara-speech-resource.services.ai.azure.com/",
    )

    AGENT_ID: str = os.environ.get(
        "AZURE_VOICELIVE_AGENT_ID", "scheduling-assistant-vikara:4"
    )

    AGENT_VERSION: Optional[str] = os.environ.get("AZURE_VOICELIVE_AGENT_VERSION")

    PROJECT_NAME: str = os.environ.get(
        "AZURE_VOICELIVE_PROJECT_NAME", "vikara-speech"
    )

    CONVERSATION_ID: Optional[str] = os.environ.get(
        "AZURE_VOICELIVE_CONVERSATION_ID"
    )

    FOUNDRY_RESOURCE_OVERRIDE: Optional[str] = os.environ.get(
        "AZURE_VOICELIVE_FOUNDRY_RESOURCE_OVERRIDE"
    )

    AUTH_IDENTITY_CLIENT_ID: Optional[str] = os.environ.get(
        "AZURE_VOICELIVE_AUTH_IDENTITY_CLIENT_ID"
    )

    API_VERSION: str = "2026-01-01-preview"


class AppConfig:
    """Application configuration"""

    DEBUG: bool = os.environ.get("DEBUG", "True").lower() == "true"
    HOST: str = os.environ.get("HOST", "0.0.0.0")
    PORT: int = int(os.environ.get("PORT", 8000))
    RELOAD: bool = os.environ.get("RELOAD", "True").lower() == "true"

    # CORS settings
    CORS_ORIGINS: list = os.environ.get("CORS_ORIGINS", "*").split(",")
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["*"]
    CORS_ALLOW_HEADERS: list = ["*"]

    # Audio settings
    AUDIO_SAMPLE_RATE: int = 24000
    AUDIO_CHANNELS: int = 1
    AUDIO_FORMAT: str = "PCM16"
    AUDIO_BUFFER_SIZE: int = 2048


class LogConfig:
    """Logging configuration"""

    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DIR: str = os.environ.get("LOG_DIR", "logs")
    DEBUG: bool = os.environ.get("DEBUG_LOGS", "False").lower() == "true"
