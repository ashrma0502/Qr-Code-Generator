"""
Core configuration module.
Loads settings from YAML config files
"""

import logging
from functools import lru_cache
from pathlib import Path


import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
CONFIGS_DIR = BASE_DIR / "configs"


def load_yaml_config(file_name: str) -> dict:
    """
    Load a YAML configuration file.

    Args:
        file_name: Name of the YAML file (e.g., 'app.yaml')

    Returns:
        dict: Parsed YAML content or empty dict on error
    """
    config_path = CONFIGS_DIR / file_name
    if not config_path.exists():
        logger.warning(f"Config file not found: {config_path}")
        return {}
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        logger.error(f"Failed to parse YAML config {file_name}: {e}")
        return {}


# Load all config files at module level
_app_config = load_yaml_config("app.yaml")
_qr_config = load_yaml_config("qr.yaml")


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables and YAML configs.
    Environment variables override YAML values.
    """

    # App info
    app_name: str = _app_config.get("app", {}).get("name", "QR Code Generator")
    app_version: str = _app_config.get("app", {}).get("version", "1.0.0")
    app_description: str = _app_config.get("app", {}).get(
        "description", "QR Code Generator API"
    )

    # Server settings
    server_host: str = _app_config.get("server", {}).get("host", "0.0.0.0")
    server_port: int = _app_config.get("server", {}).get("port", 8000)
    server_debug: bool = _app_config.get("server", {}).get("debug", False)
    server_reload: bool = _app_config.get("server", {}).get("reload", True)
    server_workers: int = _app_config.get("server", {}).get("workers", 1)

    # API settings
    api_prefix: str = _app_config.get("api", {}).get("prefix", "/api/v1")
    api_title: str = _app_config.get("api", {}).get(
        "title", "QR Code Generator API"
    )
    docs_url: str = _app_config.get("api", {}).get("docs_url", "/docs")
    redoc_url: str = _app_config.get("api", {}).get("redoc_url", "/redoc")
    openapi_url: str = _app_config.get("api", {}).get(
        "openapi_url", "/openapi.json"
    )

    # Storage settings
    output_dir: str = _app_config.get("storage", {}).get(
        "output_dir", "static/qr_codes"
    )
    max_file_age_hours: int = _app_config.get("storage", {}).get(
        "max_file_age_hours", 24
    )

    # CORS settings
    cors_allow_origins: list[str] = _app_config.get("cors", {}).get(
        "allow_origins", ["*"]
    )
    cors_allow_credentials: bool = _app_config.get("cors", {}).get(
        "allow_credentials", True
    )
    cors_allow_methods: list[str] = _app_config.get("cors", {}).get(
        "allow_methods", ["*"]
    )
    cors_allow_headers: list[str] = _app_config.get("cors", {}).get(
        "allow_headers", ["*"]
    )

    # Logging settings
    log_level: str = _app_config.get("logging", {}).get("level", "INFO")
    log_format: str = _app_config.get("logging", {}).get(
        "format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    log_file: str | None = _app_config.get("logging", {}).get("file", None)

    # QR settings from qr.yaml
    qr_default_box_size: int = _qr_config.get("qr", {}).get(
        "default_box_size", 10
    )
    qr_default_border: int = _qr_config.get("qr", {}).get("default_border", 4)
    qr_default_format: str = _qr_config.get("qr", {}).get(
        "default_format", "png"
    )
    qr_default_fill_color: str = _qr_config.get("qr", {}).get(
        "default_fill_color", "#000000"
    )
    qr_default_back_color: str = _qr_config.get("qr", {}).get(
        "default_back_color", "#FFFFFF"
    )
    qr_default_error_correction: str = _qr_config.get("qr", {}).get(
        "default_error_correction", "M"
    )
    qr_max_box_size: int = _qr_config.get("qr", {}).get("max_box_size", 30)
    qr_max_border: int = _qr_config.get("qr", {}).get("max_border", 20)
    qr_supported_formats: list[str] = _qr_config.get("qr", {}).get(
        "supported_formats", ["png", "jpg", "jpeg", "svg"]
    )

    # Environment variable overrides
    SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production",
        description="Secret key for application security",
    )
    ENVIRONMENT: str = Field(
        default="development",
        description="Application environment (development/production)",
    )
    BACKEND_HOST: str | None = Field(
        default=None, description="Override backend host"
    )
    BACKEND_PORT: int | None = Field(
        default=None, description="Override backend port"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings instance.
    Uses LRU cache to avoid re-loading configs on every call.

    Returns:
        Settings: Application settings
    """
    return Settings()


def get_qr_config() -> dict:
    """
    Get the full QR configuration dictionary.

    Returns:
        dict: QR configuration
    """
    return _qr_config.get("qr", {})


def get_app_config() -> dict:
    """
    Get the full application configuration dictionary.

    Returns:
        dict: Application configuration
    """
    return _app_config
