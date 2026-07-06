"""
QR Code Generation Service.
Generates QR codes entirely in-memory and returns base64-encoded image data.
No files are written to disk.
"""

import io
import base64
import time
import logging
import qrcode
import qrcode.image.svg
from PIL import Image


from app.core.config import get_settings
from app.schemas.qr import QRGenerateRequest, QRGenerateResponse, QRMetadata

logger = logging.getLogger(__name__)

# Map error correction strings to qrcode constants
ERROR_CORRECTION_MAP = {
    "L": qrcode.constants.ERROR_CORRECT_L,
    "M": qrcode.constants.ERROR_CORRECT_M,
    "Q": qrcode.constants.ERROR_CORRECT_Q,
    "H": qrcode.constants.ERROR_CORRECT_H,
}


class QRCodeService:
    """
    Service class for in-memory QR code generation.
    Returns base64-encoded image bytes — nothing is stored on disk.
    """

    def __init__(self):
        self.settings = get_settings()
        logger.info("QRCodeService initialized (in-memory mode, no disk storage)")

    def generate(self, request: QRGenerateRequest) -> QRGenerateResponse:
        """
        Generate a QR code and return it as a base64-encoded string.

        Args:
            request: QRGenerateRequest with generation parameters

        Returns:
            QRGenerateResponse: Contains base64 image_data, format, and metadata
        """
        start_time = time.perf_counter()
        logger.info(
            f"Generating QR | format={request.format} "
            f"ec={request.error_correction} data_len={len(request.data)}"
        )

        try:
            image_bytes, width, height = self._generate_image_bytes(request)

            elapsed_ms = (time.perf_counter() - start_time) * 1000
            encoded = base64.b64encode(image_bytes).decode("utf-8")

            metadata = QRMetadata(
                format=request.format,
                size=f"{width}x{height}",
                file_size_bytes=len(image_bytes),
                error_correction=request.error_correction,
                box_size=request.box_size,
                border=request.border,
                data_length=len(request.data),
                generation_time_ms=round(elapsed_ms, 2),
            )

            logger.info(
                f"QR generated in {elapsed_ms:.1f}ms "
                f"({len(image_bytes)} bytes, {width}x{height}px)"
            )

            return QRGenerateResponse(
                success=True,
                image_data=encoded,
                image_format=request.format,
                metadata=metadata,
                message="QR code generated successfully",
            )

        except Exception as e:
            logger.error(f"QR generation failed: {e}", exc_info=True)
            return QRGenerateResponse(
                success=False,
                message=f"QR generation failed: {str(e)}",
            )

    def _generate_image_bytes(
        self, request: QRGenerateRequest
    ) -> tuple[bytes, int, int]:
        """
        Generate QR code and return raw bytes plus dimensions.

        Returns:
            tuple[bytes, int, int]: (image_bytes, width_px, height_px)
        """
        error_correction = ERROR_CORRECTION_MAP.get(
            request.error_correction.upper(), qrcode.constants.ERROR_CORRECT_M
        )

        fmt = request.format.lower()

        if fmt == "svg":
            return self._render_svg(request, error_correction)
        else:
            return self._render_raster(request, error_correction, fmt)

    def _render_raster(
        self,
        request: QRGenerateRequest,
        error_correction: int,
        fmt: str,
    ) -> tuple[bytes, int, int]:
        """Render PNG or JPG into a BytesIO buffer."""
        qr = qrcode.QRCode(
            version=None,
            error_correction=error_correction,
            box_size=request.box_size,
            border=request.border,
        )
        qr.add_data(request.data)
        qr.make(fit=True)

        if request.transparent_background and fmt == "png":
            back_color = (0, 0, 0, 0)
        else:
            back_color = request.back_color

        img = qr.make_image(
            fill_color=request.fill_color,
            back_color=back_color,
        )

        # Normalise to PIL Image
        if not isinstance(img, Image.Image):
            buf = io.BytesIO()
            img.save(buf)
            buf.seek(0)
            img = Image.open(buf).copy()

        # Transparency & colour mode
        if request.transparent_background and fmt == "png":
            img = img.convert("RGBA")
        elif fmt in ("jpg", "jpeg") and img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        width, height = img.size

        out = io.BytesIO()
        pil_fmt = "JPEG" if fmt in ("jpg", "jpeg") else "PNG"
        save_kwargs = {"optimize": True}
        if pil_fmt == "JPEG":
            save_kwargs["quality"] = 95
        img.save(out, format=pil_fmt, **save_kwargs)
        return out.getvalue(), width, height

    def _render_svg(
        self,
        request: QRGenerateRequest,
        error_correction: int,
    ) -> tuple[bytes, int, int]:
        """Render SVG into a BytesIO buffer."""
        factory = qrcode.image.svg.SvgPathImage
        qr = qrcode.QRCode(
            version=None,
            error_correction=error_correction,
            box_size=request.box_size,
            border=request.border,
            image_factory=factory,
        )
        qr.add_data(request.data)
        qr.make(fit=True)
        img = qr.make_image(
            fill_color=request.fill_color,
            back_color=request.back_color,
        )
        out = io.BytesIO()
        img.save(out)
        size = request.box_size * 21 + request.border * 2 * request.box_size
        return out.getvalue(), size, size

    def get_service_info(self) -> dict:
        """Return service configuration information."""
        return {
            "storage": "in-memory (no disk writes)",
            "supported_formats": self.settings.qr_supported_formats,
            "default_box_size": self.settings.qr_default_box_size,
            "default_border": self.settings.qr_default_border,
            "default_format": self.settings.qr_default_format,
            "error_correction_levels": list(ERROR_CORRECTION_MAP.keys()),
        }


# ── Singleton ─────────────────────────────────────────────────────────────────

_qr_service: "QRCodeService | None" = None


def get_qr_service() -> QRCodeService:
    """Return (or create) the module-level singleton QRCodeService."""
    global _qr_service
    if _qr_service is None:
        _qr_service = QRCodeService()
    return _qr_service
