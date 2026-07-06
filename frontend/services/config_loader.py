"""
Config loader service for frontend.
Loads YAML configuration files from the configs directory.
"""

import logging
import yaml
from pathlib import Path


logger = logging.getLogger(__name__)

# Resolve config path relative to this file
_CONFIGS_DIR = Path(__file__).resolve().parent.parent.parent / "configs"


def _load_yaml(filename: str) -> dict:
    """
    Load a YAML configuration file.

    Args:
        filename: YAML filename (e.g., 'app.yaml')

    Returns:
        dict: Parsed config or empty dict
    """
    path = _CONFIGS_DIR / filename
    if not path.exists():
        logger.warning(f"Config not found: {path}")
        return {}
    try:
        with open(path, "r") as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        logger.error(f"Error parsing {filename}: {e}")
        return {}


def load_app_config() -> dict:
    """Load app.yaml configuration."""
    return _load_yaml("app.yaml")


def load_qr_config() -> dict:
    """Load qr.yaml configuration."""
    return _load_yaml("qr.yaml").get("qr", {})


def load_themes_config() -> dict:
    """Load themes.yaml configuration."""
    return _load_yaml("themes.yaml")


def get_error_correction_options() -> dict[str, str]:
    """
    Get error correction level options with labels.

    Returns:
        dict: {level_key: label_string}
    """
    config = load_qr_config()
    levels = config.get("error_correction_levels", {})
    if levels:
        return {k: v.get("label", k) for k, v in levels.items()}
    return {
        "L": "L - Low (~7% recovery)",
        "M": "M - Medium (~15% recovery)",
        "Q": "Q - Quartile (~25% recovery)",
        "H": "H - High (~30% recovery)",
    }


def get_input_types() -> dict:
    """
    Get supported input types with labels and icons.

    Returns:
        dict: {type_key: {label, icon, description}}
    """
    config = load_qr_config()
    return config.get("input_types", {
        "text": {"label": "Plain Text", "icon": "📝"},
        "url": {"label": "Website URL", "icon": "🔗"},
        "email": {"label": "Email Address", "icon": "📧"},
        "phone": {"label": "Phone Number", "icon": "📞"},
        "sms": {"label": "SMS Message", "icon": "💬"},
        "wifi": {"label": "WiFi Credentials", "icon": "📶"},
        "vcard": {"label": "Contact Card", "icon": "👤"},
        "custom": {"label": "Custom Data", "icon": "⚙️"},
    })


def get_wifi_encryption_types() -> list:
    """Get supported WiFi encryption types."""
    config = load_qr_config()
    return config.get("wifi_encryption_types", ["WPA", "WEP", "nopass"])


def get_supported_formats() -> list:
    """Get list of supported QR output formats."""
    config = load_qr_config()
    return config.get("supported_formats", ["png", "jpg", "svg"])
