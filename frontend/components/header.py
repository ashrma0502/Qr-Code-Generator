"""
Header component for the main page.
"""

import streamlit as st


def render_header() -> None:
    """Render the main page hero header with theme toggle."""
    col_title, col_toggle = st.columns([0.94, 0.06], vertical_alignment="center")

    with col_title:
        st.markdown(
            """
            <div class="page-header">
                <h1>🔳 QR Code Generator</h1>
                <p>Generate QR codes for URLs, contacts, WiFi, SMS & more — instantly</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_toggle:
        current_theme = st.session_state.get("selected_theme", "dark")
        if current_theme == "dark":
            if st.button("☀️", key="theme_toggle"):
                st.session_state["selected_theme"] = "light"
                st.rerun()
        else:
            if st.button("🌙", key="theme_toggle"):
                st.session_state["selected_theme"] = "dark"
                st.rerun()
