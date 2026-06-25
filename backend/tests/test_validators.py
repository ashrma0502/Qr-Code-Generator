"""
Tests for validation utilities.
"""

from app.utils.validators import (
    validate_url,
    validate_email,
    validate_phone,
    validate_color_hex,
    validate_data_length,
)
from app.utils.formatters import (
    format_url,
    format_email,
    format_phone,
    format_sms,
    format_wifi,
    format_vcard,
)


class TestURLValidation:
    """Tests for URL validation."""

    def test_valid_https_url(self):
        valid, msg = validate_url("https://www.google.com")
        assert valid is True

    def test_valid_http_url(self):
        valid, msg = validate_url("http://example.com")
        assert valid is True

    def test_valid_url_without_protocol(self):
        valid, msg = validate_url("www.example.com")
        assert valid is True

    def test_invalid_url_empty(self):
        valid, msg = validate_url("")
        assert valid is False
        assert msg != ""

    def test_invalid_url_no_tld(self):
        valid, msg = validate_url("notaurl")
        assert valid is False


class TestEmailValidation:
    """Tests for email validation."""

    def test_valid_email(self):
        valid, _ = validate_email("user@example.com")
        assert valid is True

    def test_valid_email_with_plus(self):
        valid, _ = validate_email("user+tag@example.co.in")
        assert valid is True

    def test_invalid_email_no_at(self):
        valid, _ = validate_email("userexample.com")
        assert valid is False

    def test_invalid_email_empty(self):
        valid, _ = validate_email("")
        assert valid is False

    def test_invalid_email_no_domain(self):
        valid, _ = validate_email("user@")
        assert valid is False


class TestPhoneValidation:
    """Tests for phone number validation."""

    def test_valid_phone_digits_only(self):
        valid, _ = validate_phone("9876543210")
        assert valid is True

    def test_valid_phone_with_country_code(self):
        valid, _ = validate_phone("+919876543210")
        assert valid is True

    def test_valid_phone_with_dashes(self):
        valid, _ = validate_phone("987-654-3210")
        assert valid is True

    def test_invalid_phone_too_short(self):
        valid, _ = validate_phone("123")
        assert valid is False

    def test_invalid_phone_empty(self):
        valid, _ = validate_phone("")
        assert valid is False


class TestColorValidation:
    """Tests for hex color validation."""

    def test_valid_hex_6_digits(self):
        valid, _ = validate_color_hex("#FF5733")
        assert valid is True

    def test_valid_hex_3_digits(self):
        valid, _ = validate_color_hex("#FFF")
        assert valid is True

    def test_valid_named_color_black(self):
        valid, _ = validate_color_hex("black")
        assert valid is True

    def test_valid_named_color_white(self):
        valid, _ = validate_color_hex("white")
        assert valid is True

    def test_invalid_hex_missing_hash(self):
        valid, _ = validate_color_hex("FF5733")
        assert valid is False

    def test_invalid_hex_wrong_length(self):
        valid, _ = validate_color_hex("#FFFFF")
        assert valid is False


class TestDataLengthValidation:
    """Tests for data length validation."""

    def test_valid_short_data(self):
        valid, _ = validate_data_length("Hello")
        assert valid is True

    def test_valid_empty_string_fails(self):
        valid, _ = validate_data_length("")
        assert valid is False

    def test_data_exceeding_max_length(self):
        too_long = "x" * 5000
        valid, _ = validate_data_length(too_long)
        assert valid is False


class TestFormatters:
    """Tests for data formatters."""

    def test_format_url_adds_https(self):
        result = format_url("example.com")
        assert result.startswith("https://")

    def test_format_url_preserves_existing_protocol(self):
        result = format_url("http://example.com")
        assert result == "http://example.com"

    def test_format_email_basic(self):
        result = format_email("user@example.com")
        assert result == "mailto:user@example.com"

    def test_format_email_with_subject(self):
        result = format_email("user@example.com", subject="Hello")
        assert "mailto:" in result
        assert "subject=" in result

    def test_format_phone(self):
        result = format_phone("+919876543210")
        assert result.startswith("tel:")

    def test_format_sms_basic(self):
        result = format_sms("+919876543210")
        assert result.startswith("sms:")

    def test_format_sms_with_message(self):
        result = format_sms("+919876543210", message="Hello")
        assert "body=" in result

    def test_format_wifi_wpa(self):
        result = format_wifi("MySSID", "MyPassword", "WPA")
        assert "WIFI:" in result
        assert "MySSID" in result
        assert "WPA" in result

    def test_format_wifi_no_password(self):
        result = format_wifi("OpenNetwork", encryption="nopass")
        assert "nopass" in result.lower()

    def test_format_vcard_basic(self):
        result = format_vcard("John Doe", phone="9876543210", email="john@example.com")
        assert "BEGIN:VCARD" in result
        assert "END:VCARD" in result
        assert "John Doe" in result

    def test_format_vcard_full(self):
        result = format_vcard(
            name="John Doe",
            phone="+919876543210",
            email="john@example.com",
            company="ACME Corp",
            title="Engineer",
            website="https://johndoe.com",
        )
        assert "ORG:ACME Corp" in result
        assert "TITLE:Engineer" in result
        assert "URL:" in result
