"""
Input validation utilities.
Provides validation functions for various QR input types.
"""

import re
import logging

logger = logging.getLogger(__name__)


def validate_url(url: str) -> tuple[bool, str]:
    """
    Validate a URL format.

    Args:
        url: URL string to validate

    Returns:
        tuple[bool, str]: (is_valid, error_message)
    """
    pattern = re.compile(
        r"^(https?://)?"                       # protocol (optional)
        r"(([a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,})"  # domain
        r"(:\d+)?"                              # optional port
        r"(/[^\s]*)?"                           # optional path
        r"(\?[^\s]*)?"                          # optional query
        r"(#[^\s]*)?$"                          # optional fragment
    )
    if not url or not url.strip():
        return False, "URL cannot be empty"
    if not re.match(pattern, url.strip()):
        return False, f"Invalid URL format: '{url}'"
    return True, ""


def validate_email(email: str) -> tuple[bool, str]:
    """
    Validate an email address format.

    Args:
        email: Email string to validate

    Returns:
        tuple[bool, str]: (is_valid, error_message)
    """
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    if not email or not email.strip():
        return False, "Email cannot be empty"
    if not re.match(pattern, email.strip()):
        return False, f"Invalid email format: '{email}'"
    return True, ""


def validate_phone(phone: str) -> tuple[bool, str]:
    """
    Validate a phone number format.
    Accepts international formats with optional + prefix.

    Args:
        phone: Phone number string to validate

    Returns:
        tuple[bool, str]: (is_valid, error_message)
    """
    pattern = r"^\+?[\d\s\-\(\)]{7,20}$"
    if not phone or not phone.strip():
        return False, "Phone number cannot be empty"
    cleaned = re.sub(r"[\s\-\(\)]", "", phone.strip())
    if not re.match(r"^\+?\d{7,15}$", cleaned):
        return False, f"Invalid phone number format: '{phone}'"
    return True, ""


def validate_color_hex(color: str) -> tuple[bool, str]:
    """
    Validate a hex color code.

    Args:
        color: Color string to validate

    Returns:
        tuple[bool, str]: (is_valid, error_message)
    """
    named_colors = {"black", "white", "red", "blue", "green", "transparent"}
    if color.lower() in named_colors:
        return True, ""
    pattern = r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
    if not re.match(pattern, color.strip()):
        return False, f"Invalid color code: '{color}'. Use #RRGGBB or #RGB"
    return True, ""


def validate_ssid(ssid: str) -> tuple[bool, str]:
    """
    Validate a WiFi SSID.

    Args:
        ssid: SSID string to validate

    Returns:
        tuple[bool, str]: (is_valid, error_message)
    """
    if not ssid or not ssid.strip():
        return False, "WiFi SSID cannot be empty"
    if len(ssid) > 32:
        return False, "WiFi SSID cannot exceed 32 characters"
    return True, ""


def validate_data_length(data: str, max_length: int = 4296) -> tuple[bool, str]:
    """
    Validate that data does not exceed QR code capacity.

    Args:
        data: Data string to validate
        max_length: Maximum allowed character count

    Returns:
        tuple[bool, str]: (is_valid, error_message)
    """
    if not data:
        return False, "Data cannot be empty"
    if len(data) > max_length:
        return (
            False,
            f"Data too long ({len(data)} chars). Max allowed: {max_length}",
        )
    return True, ""
