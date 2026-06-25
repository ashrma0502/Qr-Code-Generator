"""
QR Code API endpoints.
The /generate endpoint returns the QR image as base64 inside the JSON body.
No files are stored; there is no separate download endpoint.
"""

import logging

from fastapi import APIRouter, HTTPException, Depends

from app.schemas.qr import QRGenerateRequest, QRGenerateResponse, ErrorResponse
from app.services.qr_service import QRCodeService, get_qr_service
from app.utils.validators import validate_data_length

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/qr", tags=["QR Code"])


@router.post(
    "/generate",
    response_model=QRGenerateResponse,
    summary="Generate QR Code",
    description=(
        "Generate a QR code from the provided data and customization options. "
        "Returns the image as a base64-encoded string inside the JSON response — "
        "no files are written to disk."
    ),
    responses={
        200: {"model": QRGenerateResponse, "description": "QR code generated"},
        400: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
)
async def generate_qr(
    request: QRGenerateRequest,
    service: QRCodeService = Depends(get_qr_service),
) -> QRGenerateResponse:
    """
    Generate a QR code and return it as base64 image data.

    Args:
        request: QR generation parameters
        service: Injected QR code service

    Returns:
        QRGenerateResponse: Contains base64 image_data, format, and metadata
    """
    logger.info(f"POST /generate | data_length={len(request.data)}")

    is_valid, error_msg = validate_data_length(request.data)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    response = service.generate(request)

    if not response.success:
        raise HTTPException(
            status_code=500,
            detail=response.message or "QR code generation failed",
        )

    return response


@router.get(
    "/info",
    summary="Service Information",
    description="Get QR code service configuration and supported options.",
)
async def get_info(
    service: QRCodeService = Depends(get_qr_service),
) -> dict:
    """Return service configuration details."""
    return {
        "success": True,
        "service_info": service.get_service_info(),
    }
