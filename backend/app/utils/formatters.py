"""
Data formatters for different QR code input types.
Formats raw user input into proper QR code data strings.
"""

import logging


logger = logging.getLogger(__name__)


def format_url(url: str) -> str:
    """
    Format a URL for QR encoding.
    Adds https:// prefix if no protocol is specified.

    Args:
        url: Raw URL string

    Returns:
        str: Formatted URL
    """
    url = url.strip()
    if not url.startswith(("http://", "https://", "ftp://")):
        url = f"https://{url}"
    return url


def format_email(email: str, subject: str = "", body: str = "") -> str:
    """
    Format an email address as a mailto: URI.

    Args:
        email: Email address
        subject: Optional email subject
        body: Optional email body

    Returns:
        str: mailto: URI
    """
    uri = f"mailto:{email.strip()}"
    params = []
    if subject:
        params.append(f"subject={_url_encode(subject)}")
    if body:
        params.append(f"body={_url_encode(body)}")
    if params:
        uri += "?" + "&".join(params)
    return uri


def format_phone(phone: str) -> str:
    """
    Format a phone number as a tel: URI.

    Args:
        phone: Phone number (digits, spaces, +, -, parentheses)

    Returns:
        str: tel: URI
    """
    # Keep only digits, +, and hyphens
    cleaned = "".join(c for c in phone if c.isdigit() or c in "+-")
    return f"tel:{cleaned}"


def format_sms(phone: str, message: str = "") -> str:
    """
    Format SMS data for QR encoding.

    Args:
        phone: Recipient phone number
        message: Optional SMS message body

    Returns:
        str: SMS URI
    """
    cleaned_phone = "".join(c for c in phone if c.isdigit() or c in "+-")
    if message:
        return f"sms:{cleaned_phone}?body={_url_encode(message)}"
    return f"sms:{cleaned_phone}"


def format_wifi(
    ssid: str,
    password: str = "",
    encryption: str = "WPA",
    hidden: bool = False,
) -> str:
    """
    Format WiFi credentials as a WiFi QR code string (WPA-QR format).

    Args:
        ssid: Network SSID
        password: Network password
        encryption: Encryption type (WPA, WEP, nopass)
        hidden: Whether the network is hidden

    Returns:
        str: WiFi QR code string
    """
    # Escape special characters in SSID and password
    escaped_ssid = _escape_wifi_string(ssid)
    escaped_password = _escape_wifi_string(password) if password else ""
    hidden_str = "true" if hidden else "false"

    if encryption.upper() == "NOPASS":
        return f"WIFI:T:nopass;S:{escaped_ssid};P:;;H:{hidden_str};;"
    return f"WIFI:T:{encryption.upper()};S:{escaped_ssid};P:{escaped_password};;H:{hidden_str};;"


def format_vcard(
    name: str,
    phone: str = "",
    email: str = "",
    company: str = "",
    title: str = "",
    website: str = "",
    address: str = "",
    note: str = "",
) -> str:
    """
    Format contact information as a vCard 3.0 string.

    Args:
        name: Full name
        phone: Phone number
        email: Email address
        company: Organization/company
        title: Job title
        website: Website URL
        address: Physical address
        note: Additional notes

    Returns:
        str: vCard 3.0 formatted string
    """
    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"FN:{name.strip()}",
        f"N:{_split_name(name)}",
    ]
    if phone:
        lines.append(f"TEL:{phone.strip()}")
    if email:
        lines.append(f"EMAIL:{email.strip()}")
    if company:
        lines.append(f"ORG:{company.strip()}")
    if title:
        lines.append(f"TITLE:{title.strip()}")
    if website:
        lines.append(f"URL:{website.strip()}")
    if address:
        lines.append(f"ADR:;;{address.strip()};;;;")
    if note:
        lines.append(f"NOTE:{note.strip()}")
    lines.append("END:VCARD")
    return "\n".join(lines)


# ─── Private Helpers ──────────────────────────────────────────────────────────

def _url_encode(text: str) -> str:
    """Simple URL-encode for mailto parameters."""
    from urllib.parse import quote
    return quote(text, safe="")


def _escape_wifi_string(value: str) -> str:
    """Escape special characters in WiFi SSID/password strings."""
    special_chars = ['\\', ';', ',', '"', ':']
    for char in special_chars:
        value = value.replace(char, f'\\{char}')
    return value


def _split_name(full_name: str) -> str:
    """
    Split a full name into vCard N: format (Last;First;Middle;;).

    Args:
        full_name: Full name string

    Returns:
        str: vCard name components
    """
    parts = full_name.strip().split()
    if len(parts) == 1:
        return f"{parts[0]};;;;"
    elif len(parts) == 2:
        return f"{parts[1]};{parts[0]};;;"
    else:
        return f"{parts[-1]};{parts[0]};{' '.join(parts[1:-1])};;"
