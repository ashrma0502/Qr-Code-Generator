"""
Test configuration and shared fixtures.
"""

import pytest
import sys
from pathlib import Path

# Add backend app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def client():
    """Create a test client for the FastAPI application."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def valid_qr_request():
    """Sample valid QR generation request payload."""
    return {
        "data": "https://example.com",
        "format": "png",
        "box_size": 10,
        "border": 4,
        "fill_color": "#000000",
        "back_color": "#FFFFFF",
        "error_correction": "M",
        "transparent_background": False,
    }


@pytest.fixture
def wifi_qr_request():
    """Sample WiFi QR generation request payload."""
    return {
        "data": "WIFI:T:WPA;S:MyNetwork;P:MyPassword;;H:false;;",
        "format": "png",
        "box_size": 10,
        "border": 4,
        "fill_color": "#000000",
        "back_color": "#FFFFFF",
        "error_correction": "M",
    }
