"""
Tests for API endpoints: health check, QR generation, and info.
Updated for in-memory architecture — no download endpoint, no file storage.
QR images are returned as base64 inside the JSON response.
"""

import base64
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_returns_200(self, client: TestClient):
        """Health check should return HTTP 200."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_healthy_status(self, client: TestClient):
        """Health check should return status=healthy."""
        data = client.get("/health").json()
        assert data["status"] == "healthy"

    def test_health_has_version(self, client: TestClient):
        """Health check should include app version."""
        data = client.get("/health").json()
        assert "version" in data


class TestRootEndpoint:
    """Tests for the root / endpoint."""

    def test_root_returns_200(self, client: TestClient):
        """Root endpoint should return HTTP 200."""
        assert client.get("/").status_code == 200

    def test_root_has_docs_link(self, client: TestClient):
        """Root endpoint should include docs URL."""
        assert "docs" in client.get("/").json()


class TestQRGenerateEndpoint:
    """Tests for POST /api/v1/qr/generate (in-memory, base64 response)."""

    def test_generate_success(self, client: TestClient, valid_qr_request: dict):
        """Should return success=True and base64 image_data."""
        response = client.post("/api/v1/qr/generate", json=valid_qr_request)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["image_data"] is not None
        assert data["image_format"] == "png"

    def test_generate_image_data_is_valid_base64(self, client: TestClient, valid_qr_request: dict):
        """image_data should be decodable base64 bytes."""
        data = client.post("/api/v1/qr/generate", json=valid_qr_request).json()
        decoded = base64.b64decode(data["image_data"])
        # PNG magic bytes: \x89PNG
        assert decoded[:4] == b"\x89PNG"

    def test_generate_returns_metadata(self, client: TestClient, valid_qr_request: dict):
        """Generation response should include fully-populated metadata."""
        data = client.post("/api/v1/qr/generate", json=valid_qr_request).json()
        meta = data["metadata"]
        assert meta["format"] == "png"
        assert "x" in meta["size"]
        assert meta["file_size_bytes"] > 0
        assert meta["generation_time_ms"] >= 0
        assert meta["data_length"] == len(valid_qr_request["data"])
        assert meta["error_correction"] == valid_qr_request["error_correction"]

    def test_generate_no_file_name_in_response(self, client: TestClient, valid_qr_request: dict):
        """Response must NOT contain file_name or download_url (no disk storage)."""
        data = client.post("/api/v1/qr/generate", json=valid_qr_request).json()
        assert "file_name" not in data
        assert "download_url" not in data

    def test_generate_plain_text(self, client: TestClient):
        """Should generate QR for plain text."""
        payload = {"data": "Hello, College QR Project!", "format": "png", "error_correction": "L"}
        data = client.post("/api/v1/qr/generate", json=payload).json()
        assert data["success"] is True
        assert data["image_data"] is not None

    def test_generate_svg_format(self, client: TestClient):
        """Should generate QR in SVG format and return base64-encoded SVG."""
        payload = {"data": "https://example.com", "format": "svg"}
        response = client.post("/api/v1/qr/generate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["image_format"] == "svg"
        # Decode and verify it's an SVG document
        svg_bytes = base64.b64decode(data["image_data"])
        assert b"<svg" in svg_bytes.lower() or b"<?xml" in svg_bytes

    def test_generate_jpg_format(self, client: TestClient):
        """Should generate QR in JPG format."""
        payload = {"data": "Hello World", "format": "jpg"}
        data = client.post("/api/v1/qr/generate", json=payload).json()
        assert data["success"] is True
        assert data["image_format"] == "jpg"
        # JPEG magic bytes: FF D8
        decoded = base64.b64decode(data["image_data"])
        assert decoded[:2] == b"\xff\xd8"

    def test_generate_all_error_correction_levels(self, client: TestClient):
        """Should work with all four error correction levels."""
        for level in ["L", "M", "Q", "H"]:
            payload = {"data": "test", "format": "png", "error_correction": level}
            data = client.post("/api/v1/qr/generate", json=payload).json()
            assert data["success"] is True, f"Failed for level {level}"
            assert data["metadata"]["error_correction"] == level

    def test_generate_transparent_background_png(self, client: TestClient):
        """Should generate PNG with transparent background."""
        payload = {"data": "transparent test", "format": "png", "transparent_background": True}
        data = client.post("/api/v1/qr/generate", json=payload).json()
        assert data["success"] is True

    def test_generate_transparent_fails_for_jpg(self, client: TestClient):
        """Transparent background must be rejected for JPG format."""
        payload = {"data": "test", "format": "jpg", "transparent_background": True}
        assert client.post("/api/v1/qr/generate", json=payload).status_code == 422

    def test_generate_rejects_empty_data(self, client: TestClient):
        """Should reject empty data field."""
        assert client.post("/api/v1/qr/generate", json={"data": ""}).status_code == 422

    def test_generate_rejects_invalid_format(self, client: TestClient):
        """Should reject unsupported image format."""
        assert client.post("/api/v1/qr/generate", json={"data": "test", "format": "bmp"}).status_code == 422

    def test_generate_rejects_invalid_error_correction(self, client: TestClient):
        """Should reject invalid error correction level."""
        assert client.post("/api/v1/qr/generate", json={"data": "test", "error_correction": "X"}).status_code == 422

    def test_generate_rejects_invalid_color(self, client: TestClient):
        """Should reject invalid hex color."""
        assert client.post("/api/v1/qr/generate", json={"data": "test", "fill_color": "notacolor"}).status_code == 422

    def test_generate_rejects_box_size_too_large(self, client: TestClient):
        """Should reject box_size above maximum."""
        assert client.post("/api/v1/qr/generate", json={"data": "test", "box_size": 100}).status_code == 422

    def test_generate_rejects_box_size_too_small(self, client: TestClient):
        """Should reject box_size of zero."""
        assert client.post("/api/v1/qr/generate", json={"data": "test", "box_size": 0}).status_code == 422


class TestDownloadEndpointRemoved:
    """Confirm the old /download endpoint no longer exists."""

    def test_download_endpoint_is_gone(self, client: TestClient):
        """GET /api/v1/qr/download/* should return 404 (endpoint removed)."""
        response = client.get("/api/v1/qr/download/qrcode_test.png")
        assert response.status_code == 404


class TestQRInfoEndpoint:
    """Tests for GET /api/v1/qr/info."""

    def test_info_returns_service_config(self, client: TestClient):
        """Info endpoint should return service configuration."""
        response = client.get("/api/v1/qr/info")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        info = data["service_info"]
        assert "supported_formats" in info
        assert "error_correction_levels" in info
        assert "png" in info["supported_formats"]
        # Confirm in-memory mode is advertised
        assert "in-memory" in info.get("storage", "")
