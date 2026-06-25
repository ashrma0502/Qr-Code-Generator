"""
API Client service for communicating with the FastAPI backend.
Handles all HTTP requests and error handling.

QR codes are returned as base64-encoded strings in the generate response —
no separate download request is needed.
"""

import logging


import requests

logger = logging.getLogger(__name__)


def check_backend_health(backend_url: str, timeout: int = 3) -> tuple[bool, str]:
    """
    Check if the backend API is healthy.

    Args:
        backend_url: Base URL of the backend API
        timeout: Request timeout in seconds

    Returns:
        Tuple[bool, str]: (is_online, status_message)
    """
    try:
        url = f"{backend_url.rstrip('/')}/health"
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            data = response.json()
            return True, data.get("status", "healthy")
        return False, f"Unhealthy (HTTP {response.status_code})"
    except requests.exceptions.ConnectionError:
        return False, "Backend not reachable"
    except requests.exceptions.Timeout:
        return False, "Request timed out"
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False, f"Error: {str(e)}"


def generate_qr_code(
    backend_url: str,
    payload: dict,
    timeout: int = 10,
) -> tuple[bool, dict]:
    """
    Call the backend API to generate a QR code.

    The response contains the image as a base64-encoded string in
    ``result["image_data"]`` — no second request is needed.

    Args:
        backend_url: Base URL of the backend API
        payload: QR generation request payload
        timeout: Request timeout in seconds

    Returns:
        Tuple[bool, dict]: (success, response_data_or_error)
            On success, response_data contains:
              - image_data  (str) base64-encoded image bytes
              - image_format (str) e.g. "png"
              - metadata    (dict) size, timing, etc.
    """
    try:
        url = f"{backend_url.rstrip('/')}/api/v1/qr/generate"
        response = requests.post(url, json=payload, timeout=timeout)

        if response.status_code == 200:
            return True, response.json()

        if response.status_code == 422:
            detail = response.json().get("detail", "Validation failed")
            if isinstance(detail, list):
                msgs = [e.get("msg", str(e)) for e in detail]
                detail = "; ".join(msgs)
            return False, {"message": detail}

        if response.status_code == 400:
            return False, {"message": response.json().get("detail", "Bad request")}

        return False, {"message": f"Server error (HTTP {response.status_code})"}

    except requests.exceptions.ConnectionError:
        return False, {"message": "Cannot connect to backend. Is it running?"}
    except requests.exceptions.Timeout:
        return False, {"message": "Request timed out. Try again."}
    except Exception as e:
        logger.error(f"QR generation request failed: {e}")
        return False, {"message": f"Unexpected error: {str(e)}"}
