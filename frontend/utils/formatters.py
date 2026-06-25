"""
Frontend data formatters.
Formats user input into proper QR code data strings.
These mirror the backend formatters but run client-side for preview.
"""

from urllib.parse import quote


def format_url_data(url: str) -> str:
    """Format a URL, adding https:// if no protocol specified."""
    url = url.strip()
    if not url.startswith(("http://", "https://", "ftp://")):
        url = f"https://{url}"
    return url


def format_email_data(email: str, subject: str = "", body: str = "") -> str:
    """Format email as mailto: URI."""
    uri = f"mailto:{email}"
    params = []
    if subject:
        params.append(f"subject={quote(subject)}")
    if body:
        params.append(f"body={quote(body)}")
    if params:
        uri += "?" + "&".join(params)
    return uri


def format_phone_data(phone: str) -> str:
    """Format phone number as tel: URI."""
    cleaned = "".join(c for c in phone if c.isdigit() or c in "+-")
    return f"tel:{cleaned}"


def format_sms_data(phone: str, message: str = "") -> str:
    """Format SMS as sms: URI."""
    cleaned = "".join(c for c in phone if c.isdigit() or c in "+-")
    if message:
        return f"sms:{cleaned}?body={quote(message)}"
    return f"sms:{cleaned}"


def format_wifi_data(
    ssid: str,
    password: str = "",
    encryption: str = "WPA",
    hidden: bool = False,
) -> str:
    """Format WiFi credentials as WiFi QR string."""
    escaped_ssid = _escape_wifi(ssid)
    escaped_pass = _escape_wifi(password) if password else ""
    hidden_str = "true" if hidden else "false"
    if encryption.lower() == "nopass":
        return f"WIFI:T:nopass;S:{escaped_ssid};P:;;H:{hidden_str};;"
    return f"WIFI:T:{encryption.upper()};S:{escaped_ssid};P:{escaped_pass};;H:{hidden_str};;"


def format_vcard_data(
    name: str,
    phone: str = "",
    email: str = "",
    company: str = "",
    title: str = "",
    website: str = "",
    address: str = "",
    note: str = "",
) -> str:
    """Format contact info as vCard 3.0."""
    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"FN:{name}",
        f"N:{_split_name(name)}",
    ]
    if phone:
        lines.append(f"TEL:{phone}")
    if email:
        lines.append(f"EMAIL:{email}")
    if company:
        lines.append(f"ORG:{company}")
    if title:
        lines.append(f"TITLE:{title}")
    if website:
        lines.append(f"URL:{website}")
    if address:
        lines.append(f"ADR:;;{address};;;;")
    if note:
        lines.append(f"NOTE:{note}")
    lines.append("END:VCARD")
    return "\n".join(lines)


def _escape_wifi(value: str) -> str:
    """Escape special characters in WiFi strings."""
    for char in ['\\', ';', ',', '"', ':']:
        value = value.replace(char, f'\\{char}')
    return value


def _split_name(full_name: str) -> str:
    """Split full name into vCard N: format."""
    parts = full_name.strip().split()
    if len(parts) == 1:
        return f"{parts[0]};;;;"
    elif len(parts) == 2:
        return f"{parts[1]};{parts[0]};;;"
    return f"{parts[-1]};{parts[0]};{' '.join(parts[1:-1])};;"
