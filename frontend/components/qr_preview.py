"""
QR Preview component.
Decodes the base64 image returned by the backend and renders it directly —
no file storage, no second HTTP request.
"""

import base64
import streamlit as st


from ..services.api_client import generate_qr_code


def render_qr_preview(
    qr_data: str | None,
    customization: dict,
    should_generate: bool,
) -> None:
    """
    Render the QR code preview panel.

    Args:
        qr_data: Formatted QR data string (may be None before input)
        customization: Customization settings from sidebar
        should_generate: Whether user clicked Generate button
    """
    backend_url = customization.get("backend_url", "http://localhost:8000")

    # ── Trigger generation on button click ────────────────────
    if should_generate and qr_data:
        _do_generate(qr_data, customization, backend_url)

    # ── Display only if QR code has been generated ─────────────
    if st.session_state.get("qr_image_bytes"):
        st.markdown('<p class="section-title">👁️ QR Preview</p>', unsafe_allow_html=True)
        _display_qr_result()


def _do_generate(
    qr_data: str,
    customization: dict,
    backend_url: str,
) -> None:
    """
    Call the backend, decode the base64 image, and store in session state.
    """
    payload = {
        "data": qr_data,
        "format": customization.get("format", "png"),
        "box_size": customization.get("box_size", 10),
        "border": customization.get("border", 4),
        "fill_color": customization.get("fill_color", "#000000"),
        "back_color": customization.get("back_color", "#FFFFFF"),
        "error_correction": customization.get("error_correction", "M"),
        "transparent_background": customization.get("transparent_background", False),
    }

    with st.spinner("⚡ Generating QR code..."):
        success, result = generate_qr_code(backend_url, payload)

    if success:
        image_b64 = result.get("image_data", "")
        image_fmt = result.get("image_format", "png")

        try:
            image_bytes = base64.b64decode(image_b64)
        except Exception:
            st.error("❌ Failed to decode image data from backend.")
            return

        st.session_state["qr_image_bytes"] = image_bytes
        st.session_state["qr_image_format"] = image_fmt
        st.session_state["qr_metadata"] = result.get("metadata")
        st.success("✅ QR code generated successfully!")
    else:
        error_msg = result.get("message", "Unknown error")
        st.error(f"❌ {error_msg}")
        if "connect" in error_msg.lower() or "reach" in error_msg.lower():
            st.info(
                "💡 **Tip:** Make sure the FastAPI backend is running.\n\n"
                "```bash\ncd backend && python -m uvicorn app.main:app --reload\n```",
                icon="🔧",
            )


def _display_qr_result() -> None:
    """Display the QR image (decoded from base64) and metadata."""
    image_bytes: bytes = st.session_state["qr_image_bytes"]
    image_fmt: str = st.session_state.get("qr_image_format", "png")
    metadata: dict = st.session_state.get("qr_metadata") or {}

    # ── QR Image ────────────────────────────────────────────────
    _, col_img, _ = st.columns([0.15, 0.7, 0.15])
    with col_img:
        if image_fmt == "svg":
            svg_str = image_bytes.decode("utf-8", errors="replace")
            st.code(
                svg_str[:500] + "..." if len(svg_str) > 500 else svg_str,
                language="xml",
            )
            st.caption("SVG — use the download button below to view")
        else:
            st.image(image_bytes, caption="Your QR Code", use_container_width=True)

    # ── Metadata ────────────────────────────────────────────────
    if metadata:
        st.divider()
        st.markdown('<p class="section-title">📊 QR Metadata</p>', unsafe_allow_html=True)
        _render_metadata(metadata)

    # ── Download button ─────────────────────────────────────────
    st.divider()
    _render_download_button(image_bytes, image_fmt)

    st.caption("🔄 Modify settings and click **Generate QR Code** to regenerate.")


def _render_metadata(metadata: dict) -> None:
    """Render QR metadata in a theme-styled 2x2 grid layout to avoid truncation."""
    size = metadata.get("size", "—")
    kb = metadata.get("file_size_bytes", 0) / 1024
    gen_time = metadata.get("generation_time_ms", 0)
    data_length = metadata.get("data_length", 0)

    st.markdown(
        f"""
        <div class="metadata-grid">
            <div class="meta-item">
                <div class="meta-label">📐 Resolution</div>
                <div class="meta-value">{size}</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">💾 File Size</div>
                <div class="meta-value">{kb:.1f} KB</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">⚡ Gen Time</div>
                <div class="meta-value">{gen_time:.0f} ms</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">📝 Data Length</div>
                <div class="meta-value">{data_length} chars</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("<div style='margin-bottom: 0.8rem;'></div>", unsafe_allow_html=True)

    with st.expander("🔍 More Details"):
        c1, c2 = st.columns(2)
        with c1:
            st.write(f"**Format:** {metadata.get('format', '—').upper()}")
            st.write(f"**Box Size:** {metadata.get('box_size', '—')} px")
        with c2:
            st.write(f"**Error Correction:** {metadata.get('error_correction', '—')}")
            st.write(f"**Border:** {metadata.get('border', '—')} modules")


def _render_download_button(image_bytes: bytes, fmt: str) -> None:
    """Render a Streamlit download button for the in-memory image."""
    mime_map = {
        "png":  "image/png",
        "jpg":  "image/jpeg",
        "jpeg": "image/jpeg",
        "svg":  "image/svg+xml",
    }
    mime = mime_map.get(fmt.lower(), "application/octet-stream")
    file_name = f"qrcode.{fmt.lower()}"

    _, col_btn, _ = st.columns([0.2, 0.6, 0.2])
    with col_btn:
        st.download_button(
            label=f"⬇️ Download QR Code ({fmt.upper()})",
            data=image_bytes,
            file_name=file_name,
            mime=mime,
            use_container_width=True,
        )

