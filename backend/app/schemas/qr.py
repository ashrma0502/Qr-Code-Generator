"""
Pydantic schemas for QR code generation.
Defines request/response models with validation.
"""

import re
from pydantic import BaseModel, Field, field_validator, model_validator


# ─── Request Schemas ──────────────────────────────────────────────────────────

class QRGenerateRequest(BaseModel):
    """
    Schema for QR code generation request.
    All fields are validated with appropriate constraints.
    """

    data: str = Field(
        ...,
        min_length=1,
        max_length=4296,
        description="The data to encode in the QR code",
        examples=["https://example.com"],
    )
    format: str = Field(
        default="png",
        description="Output image format (png, jpg, svg)",
        examples=["png"],
    )
    box_size: int = Field(
        default=10,
        ge=1,
        le=30,
        description="Size of each QR code box in pixels",
        examples=[10],
    )
    border: int = Field(
        default=4,
        ge=0,
        le=20,
        description="Border size (number of boxes)",
        examples=[4],
    )
    fill_color: str = Field(
        default="#000000",
        description="Foreground (module) color as hex code",
        examples=["#000000"],
    )
    back_color: str = Field(
        default="#FFFFFF",
        description="Background color as hex code",
        examples=["#FFFFFF"],
    )
    error_correction: str = Field(
        default="M",
        description="Error correction level: L, M, Q, H",
        examples=["M"],
    )
    transparent_background: bool = Field(
        default=False,
        description="Use transparent background (PNG only)",
    )

    @field_validator("format")
    @classmethod
    def validate_format(cls, v: str) -> str:
        """Validate image format is supported."""
        allowed = ["png", "jpg", "jpeg", "svg"]
        v = v.lower().strip()
        if v not in allowed:
            raise ValueError(
                f"Unsupported format '{v}'. Must be one of: {', '.join(allowed)}"
            )
        return v

    @field_validator("error_correction")
    @classmethod
    def validate_error_correction(cls, v: str) -> str:
        """Validate error correction level."""
        allowed = ["L", "M", "Q", "H"]
        v = v.upper().strip()
        if v not in allowed:
            raise ValueError(
                f"Invalid error correction '{v}'. Must be one of: {', '.join(allowed)}"
            )
        return v

    @field_validator("fill_color", "back_color")
    @classmethod
    def validate_color(cls, v: str) -> str:
        """Validate hex color code format."""
        v = v.strip()
        # Accept named colors like 'black', 'white', 'transparent'
        named_colors = {"black", "white", "red", "blue", "green", "transparent"}
        if v.lower() in named_colors:
            return v
        # Validate hex format
        pattern = r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
        if not re.match(pattern, v):
            raise ValueError(
                f"Invalid color '{v}'. Use hex format like #RRGGBB or #RGB"
            )
        return v

    @model_validator(mode="after")
    def validate_transparent_format(self) -> "QRGenerateRequest":
        """Ensure transparent background is only used with PNG format."""
        if self.transparent_background and self.format not in ["png"]:
            raise ValueError(
                "Transparent background is only supported with PNG format"
            )
        return self

    model_config = {
        "json_schema_extra": {
            "example": {
                "data": "https://example.com",
                "format": "png",
                "box_size": 10,
                "border": 4,
                "fill_color": "#000000",
                "back_color": "#FFFFFF",
                "error_correction": "M",
                "transparent_background": False,
            }
        }
    }


# ─── Response Schemas ─────────────────────────────────────────────────────────

class QRMetadata(BaseModel):
    """Metadata about a generated QR code."""

    format: str = Field(description="Output image format")
    size: str = Field(description="Image dimensions (WxH)")
    file_size_bytes: int = Field(description="File size in bytes")
    error_correction: str = Field(description="Error correction level used")
    box_size: int = Field(description="Box size used")
    border: int = Field(description="Border size used")
    data_length: int = Field(description="Length of encoded data")
    generation_time_ms: float = Field(description="Time taken to generate in ms")


class QRGenerateResponse(BaseModel):
    """Response schema for QR code generation endpoint.

    The QR image is returned as a base64-encoded string inside the JSON
    response body. No files are stored on the server.
    """

    success: bool = Field(description="Whether generation was successful")
    image_data: str | None = Field(
        default=None,
        description="Base64-encoded QR code image (data URI ready)",
    )
    image_format: str | None = Field(
        default=None, description="Image format: png, jpg, or svg"
    )
    metadata: QRMetadata | None = Field(
        default=None, description="QR code metadata"
    )
    message: str | None = Field(
        default=None, description="Status or error message"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "image_data": "iVBORw0KGgoAAAANSUhEUgAA...",
                "image_format": "png",
                "metadata": {
                    "format": "png",
                    "size": "330x330",
                    "file_size_bytes": 1024,
                    "error_correction": "M",
                    "box_size": 10,
                    "border": 4,
                    "data_length": 19,
                    "generation_time_ms": 45.2,
                },
            }
        }
    }


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    success: bool = Field(default=False)
    message: str = Field(description="Error description")
    detail: str | None = Field(
        default=None, description="Detailed error information"
    )
