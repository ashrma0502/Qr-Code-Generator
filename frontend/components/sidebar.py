"""
Sidebar component.
Renders backend settings, theme selection, and QR customization options.
"""

import streamlit as st
from services.config_loader import (
    load_qr_config,
    get_supported_formats,
    get_error_correction_options,
)


def render_sidebar() -> dict:
    """
    Render the sidebar with all settings and customization controls.

    Returns:
        dict: Dictionary of customization settings selected by user
    """
    qr_config = load_qr_config()

    with st.sidebar:
        # ── Brand ──────────────────────────────────────────────
        st.markdown(
            """
            <div class="sidebar-brand">
                <div style="font-size:2.5rem;">🔳</div>
                <h2>QR Generator</h2>
                <div style="font-size:0.75rem; color:rgba(255,255,255,0.4);">v1.0.0 • College Mini Project</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── QR Customization ────────────────────────────────────
        st.markdown('<p class="section-title">⚙️ Customization</p>', unsafe_allow_html=True)

        # Output format
        formats = get_supported_formats()
        qr_format = st.selectbox(
            "📁 Output Format",
            options=[f.upper() for f in formats],
            index=0,
            help="Image format for the generated QR code",
        ).lower()

        # Box size
        default_box = qr_config.get("default_box_size", 10)
        max_box = qr_config.get("max_box_size", 30)
        box_size = st.slider(
            "📐 Box Size",
            min_value=1,
            max_value=max_box,
            value=default_box,
            help="Size of each QR module in pixels",
        )

        # Border size
        default_border = qr_config.get("default_border", 4)
        max_border = qr_config.get("max_border", 20)
        border = st.slider(
            "🔲 Border Size",
            min_value=0,
            max_value=max_border,
            value=default_border,
            help="White border around the QR code (in modules)",
        )

        # Error correction
        err_options = get_error_correction_options()
        err_keys = list(err_options.keys())
        err_display = list(err_options.values())
        default_err = qr_config.get("default_error_correction", "M").upper()
        default_index = err_keys.index(default_err) if default_err in err_keys else 1

        selected_err_display = st.selectbox(
            "🛡️ Error Correction",
            options=err_display,
            index=default_index,
            help="Higher levels allow QR code to be read even if damaged or covered",
        )
        error_correction = err_keys[err_display.index(selected_err_display)]

        st.divider()

        # ── Colors ──────────────────────────────────────────────
        st.markdown('<p class="section-title">🎨 Colors</p>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            fill_color = st.color_picker("Foreground", value="#000000", help="QR module color")
        with col2:
            back_color = st.color_picker("Background", value="#FFFFFF", help="QR background color")

        transparent_bg = False
        if qr_format == "png":
            transparent_bg = st.checkbox(
                "🔲 Transparent Background",
                value=False,
                help="Remove background (PNG only)",
            )

        st.divider()

        # ── About ───────────────────────────────────────────────
        st.markdown(
            """
            <div style="text-align:center; padding: 0.5rem; opacity: 0.5; font-size: 0.75rem;">
                Built using FastAPI & Streamlit<br/>
                College Mini Project
            </div>
            """,
            unsafe_allow_html=True,
        )

    return {
        "backend_url": st.session_state.get("backend_url", "http://localhost:8000"),
        "format": qr_format,
        "box_size": box_size,
        "border": border,
        "error_correction": error_correction,
        "fill_color": fill_color,
        "back_color": back_color,
        "transparent_background": transparent_bg,
    }
