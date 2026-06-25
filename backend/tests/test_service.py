"""
Tests for QR code generation service.
Updated for in-memory architecture — service returns base64 image_data,
no files are written to disk.
"""

import base64
import pytest

from app.services.qr_service import QRCodeService
from app.schemas.qr import QRGenerateRequest


@pytest.fixture
def service():
    """Create a fresh QRCodeService instance."""
    return QRCodeService()


@pytest.fixture
def basic_request():
    """Basic PNG QR generation request."""
    return QRGenerateRequest(
        data="https://example.com",
        format="png",
        box_size=10,
        border=4,
        fill_color="#000000",
        back_color="#FFFFFF",
        error_correction="M",
    )


class TestQRCodeService:
    """Unit tests for QRCodeService (in-memory mode)."""

    def test_service_initializes(self, service: QRCodeService):
        """Service should initialize without errors."""
        assert service is not None

    def test_generate_png_success(self, service: QRCodeService, basic_request: QRGenerateRequest):
        """Should return success=True with non-empty image_data."""
        response = service.generate(basic_request)
        assert response.success is True
        assert response.image_data is not None
        assert len(response.image_data) > 0

    def test_generate_png_image_format(self, service: QRCodeService, basic_request: QRGenerateRequest):
        """image_format should match requested format."""
        response = service.generate(basic_request)
        assert response.image_format == "png"

    def test_generate_png_valid_base64(self, service: QRCodeService, basic_request: QRGenerateRequest):
        """image_data should decode to valid PNG bytes."""
        response = service.generate(basic_request)
        decoded = base64.b64decode(response.image_data)
        assert decoded[:4] == b"\x89PNG", "Not a valid PNG"

    def test_generate_jpg_valid_base64(self, service: QRCodeService):
        """image_data for JPG should decode to valid JPEG bytes."""
        request = QRGenerateRequest(data="Hello World", format="jpg")
        response = service.generate(request)
        assert response.success is True
        assert response.image_format == "jpg"
        decoded = base64.b64decode(response.image_data)
        assert decoded[:2] == b"\xff\xd8", "Not a valid JPEG"

    def test_generate_svg_valid_base64(self, service: QRCodeService):
        """image_data for SVG should decode to an SVG document."""
        request = QRGenerateRequest(data="https://example.com", format="svg")
        response = service.generate(request)
        assert response.success is True
        assert response.image_format == "svg"
        decoded = base64.b64decode(response.image_data)
        assert b"<svg" in decoded.lower() or b"<?xml" in decoded

    def test_generate_no_file_written(self, service: QRCodeService, basic_request: QRGenerateRequest):
        """Service must not expose file_name or download_url (no disk writes)."""
        response = service.generate(basic_request)
        assert not hasattr(response, "file_name") or response.__dict__.get("file_name") is None
        assert not hasattr(response, "download_url") or response.__dict__.get("download_url") is None

    def test_generate_metadata_populated(self, service: QRCodeService, basic_request: QRGenerateRequest):
        """Response metadata should be fully populated."""
        response = service.generate(basic_request)
        meta = response.metadata
        assert meta is not None
        assert meta.format == "png"
        assert meta.file_size_bytes > 0
        assert meta.data_length == len(basic_request.data)
        assert meta.generation_time_ms >= 0
        assert "x" in meta.size

    def test_generate_all_error_correction_levels(self, service: QRCodeService):
        """Should generate successfully for all four error correction levels."""
        for level in ["L", "M", "Q", "H"]:
            request = QRGenerateRequest(data="test data", format="png", error_correction=level)
            response = service.generate(request)
            assert response.success is True, f"Failed for level {level}"
            assert response.metadata.error_correction == level

    def test_generate_custom_colors(self, service: QRCodeService):
        """Should accept and apply custom fill and back colors."""
        request = QRGenerateRequest(
            data="Color test", format="png",
            fill_color="#FF0000", back_color="#FFFF00",
        )
        response = service.generate(request)
        assert response.success is True

    def test_generate_large_box_size(self, service: QRCodeService):
        """Should handle maximum box size (30)."""
        request = QRGenerateRequest(data="Large box", format="png", box_size=30)
        response = service.generate(request)
        assert response.success is True

    def test_generate_transparent_background(self, service: QRCodeService):
        """Should generate a transparent PNG."""
        request = QRGenerateRequest(
            data="transparent", format="png", transparent_background=True
        )
        response = service.generate(request)
        assert response.success is True
        # Decoded bytes must still be a PNG
        decoded = base64.b64decode(response.image_data)
        assert decoded[:4] == b"\x89PNG"

    def test_generate_unique_image_data(self, service: QRCodeService, basic_request: QRGenerateRequest):
        """Two consecutive calls should produce identical image_data for the same input."""
        r1 = service.generate(basic_request)
        r2 = service.generate(basic_request)
        # Same input → same QR matrix → same image bytes (deterministic)
        assert r1.image_data == r2.image_data

    def test_get_service_info(self, service: QRCodeService):
        """get_service_info() should return expected keys."""
        info = service.get_service_info()
        assert "supported_formats" in info
        assert "error_correction_levels" in info
        assert "png" in info["supported_formats"]
        assert "in-memory" in info.get("storage", "")
