"""
QR Code Generator - Streamlit Frontend
Main application file - entry point.
"""

import os
import sys
from pathlib import Path

# Add frontend directory to path for local imports
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
from components.sidebar import render_sidebar
from components.input_forms import render_input_forms
from components.qr_preview import render_qr_preview
from components.header import render_header
from services.config_loader import load_themes_config, load_app_config

# ─── Page Configuration ───────────────────────────────────────────────────────

themes_config = load_themes_config()
app_config = load_app_config()
streamlit_cfg = themes_config.get("streamlit", {})

st.set_page_config(
    page_title=streamlit_cfg.get("page_title", "QR Code Generator"),
    page_icon=streamlit_cfg.get("page_icon", "🔳"),
    layout=streamlit_cfg.get("layout", "wide"),
    initial_sidebar_state=streamlit_cfg.get("initial_sidebar_state", "expanded"),
    menu_items={
        "Get Help": "https://github.com/your-repo",
        "About": "# QR Code Generator\nA college mini-project built with FastAPI + Streamlit",
    },
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────

def inject_custom_css(theme_name: str = "dark") -> None:
    """Inject custom CSS styles based on selected theme."""
    themes = themes_config.get("themes", {}).get("available", {})
    theme = themes.get(theme_name, themes.get("dark", {}))

    primary = theme.get("primary_color", "#6366F1")
    bg = theme.get("background_color", "#0F172A")
    secondary_bg = theme.get("secondary_background_color", "#1E293B")
    text = theme.get("text_color", "#F1F5F9")

    if theme_name == "light":
        bg_gradient = f"linear-gradient(135deg, {bg} 0%, {secondary_bg} 100%)"
        border_color = "rgba(0, 0, 0, 0.08)"
        input_bg = "rgba(0, 0, 0, 0.04)"
        input_border = "rgba(0, 0, 0, 0.1)"
        card_bg = "rgba(0, 0, 0, 0.02)"
        card_hover_border = "rgba(79, 70, 229, 0.4)"
        text_muted = "rgba(0, 0, 0, 0.65)"
        text_muted_light = "rgba(0, 0, 0, 0.45)"
    else:
        bg_gradient = f"linear-gradient(135deg, {bg} 0%, #0D1117 100%)"
        border_color = "rgba(255, 255, 255, 0.08)"
        input_bg = "rgba(255, 255, 255, 0.06)"
        input_border = "rgba(255, 255, 255, 0.12)"
        card_bg = "rgba(255, 255, 255, 0.04)"
        card_hover_border = "rgba(99, 102, 241, 0.4)"
        text_muted = "rgba(255, 255, 255, 0.65)"
        text_muted_light = "rgba(255, 255, 255, 0.35)"

    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

        /* ── Global Reset ── */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {{
            font-family: 'Inter', sans-serif;
        }}

        .stButton > button, .stDownloadButton > button, .stSelectbox, .stTextInput, .stTextArea, .stNumberInput {{
            font-family: 'Inter', sans-serif !important;
        }}

        /* ── Main App Background ── */
        .stApp {{
            background: {bg_gradient};
            color: {text};
        }}

        /* Ensure all text labels and markdown elements update to the correct theme text color */
        [data-testid="stWidgetLabel"] p,
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] h1,
        [data-testid="stMarkdownContainer"] h2,
        [data-testid="stMarkdownContainer"] h3,
        [data-testid="stMarkdownContainer"] h4,
        .streamlit-expanderHeader p,
        [data-testid="stSlider"] label,
        [data-testid="stSlider"] span {{
            color: {text} !important;
        }}

        [data-testid="stCaptionContainer"],
        [data-testid="stCaptionContainer"] p,
        .stCaption,
        .stCaption p {{
            color: {text_muted} !important;
        }}

        /* ── Sidebar ── */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {secondary_bg} 0%, {bg} 100%);
            border-right: 1px solid {border_color};
        }}

        [data-testid="stSidebar"] * {{
            color: {text} !important;
        }}

        /* ── Sidebar header ── */
        .sidebar-brand {{
            text-align: center;
            padding: 1rem 0.5rem 1.5rem;
            border-bottom: 1px solid {border_color};
            margin-bottom: 1rem;
        }}

        .sidebar-brand h2 {{
            font-size: 1.4rem;
            font-weight: 800;
            background: linear-gradient(135deg, {primary}, #A78BFA);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0.3rem 0;
        }}

        /* ── Page Header ── */
        .page-header {{
            text-align: left;
            padding: 1.5rem 0 1rem;
            margin-bottom: 1rem;
        }}

        .page-header h1 {{
            font-size: 2.8rem;
            font-weight: 800;
            background: linear-gradient(135deg, {primary} 0%, #A78BFA 50%, #EC4899 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            line-height: 1.2;
            margin: 0;
        }}

        .page-header p {{
            font-size: 1.15rem;
            color: {text_muted};
            margin-top: 0.4rem;
        }}

        /* ── Cards / Containers ── */
        .qr-card {{
            background: {card_bg};
            border: 1px solid {border_color};
            border-radius: 16px;
            padding: 1.5rem;
            backdrop-filter: blur(10px);
            transition: border-color 0.2s ease;
        }}

        .qr-card:hover {{
            border-color: {card_hover_border};
        }}

        /* ── Section titles ── */
        .section-title {{
            font-size: 0.85rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            color: {primary};
            margin-bottom: 0.75rem;
        }}

        /* ── QR Preview Container ── */
        .qr-preview-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 1rem;
            padding: 1.5rem;
            background: {card_bg};
            border: 1px solid {border_color};
            border-radius: 16px;
            min-height: 350px;
            justify-content: center;
        }}

        .qr-preview-placeholder {{
            color: {text_muted_light};
            text-align: center;
            font-size: 0.95rem;
        }}

        /* ── Metadata Table ── */
        .metadata-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 0.6rem;
            margin-top: 0.5rem;
        }}

        .meta-item {{
            background: {card_bg};
            border-radius: 8px;
            padding: 0.5rem 0.75rem;
        }}

        .meta-label {{
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: {text_muted};
        }}

        .meta-value {{
            font-size: 0.9rem;
            font-weight: 600;
            color: {text};
        }}

        /* ── Streamlit overrides ── */
        .stSelectbox > div > div,
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stNumberInput > div > div > input {{
            background: {input_bg} !important;
            border: 1px solid {input_border} !important;
            border-radius: 8px !important;
            color: {text} !important;
        }}

        .stButton > button {{
            background: linear-gradient(135deg, {primary}, #8B5CF6) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            padding: 0.6rem 2rem !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 4px 15px rgba(99,102,241,0.3) !important;
        }}

        .stButton > button:hover {{
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 20px rgba(99,102,241,0.45) !important;
        }}

        .st-key-theme_toggle button {{
            padding: 0px !important;
            width: 40px !important;
            height: 40px !important;
            min-width: 40px !important;
            min-height: 40px !important;
            max-width: 40px !important;
            max-height: 40px !important;
            font-size: 1.2rem !important;
            border-radius: 50% !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            box-shadow: 0 2px 8px rgba(99,102,241,0.2) !important;
        }}

        .st-key-theme_toggle button:hover {{
            box-shadow: 0 4px 12px rgba(99,102,241,0.35) !important;
            transform: translateY(-1px) !important;
        }}

        .stDownloadButton > button {{
            background: linear-gradient(135deg, #10B981, #059669) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 15px rgba(16,185,129,0.3) !important;
        }}

        /* ── Slider ── */
        .stSlider [data-baseweb="slider"] {{
            padding: 0.2rem 0;
        }}

        /* ── Color pickers ── */
        .stColorPicker {{
            border-radius: 8px;
        }}

        /* ── Expander ── */
        .streamlit-expanderHeader {{
            background: {card_bg} !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
        }}

        /* ── Success/Error messages ── */
        .stSuccess {{
            background: rgba(16,185,129,0.1) !important;
            border-left: 3px solid #10B981 !important;
            border-radius: 8px !important;
        }}

        .stError {{
            background: rgba(239,68,68,0.1) !important;
            border-left: 3px solid #EF4444 !important;
            border-radius: 8px !important;
        }}

        .stWarning {{
            background: rgba(245,158,11,0.1) !important;
            border-left: 3px solid #F59E0B !important;
            border-radius: 8px !important;
        }}

        /* ── Divider ── */
        hr {{
            border-color: {border_color} !important;
        }}

        /* ── Tabs ── */
        .stTabs [data-baseweb="tab-list"] {{
            background: {card_bg};
            border-radius: 10px;
            gap: 4px;
            padding: 4px;
        }}

        .stTabs [data-baseweb="tab"] {{
            border-radius: 8px !important;
            font-weight: 500 !important;
        }}

        .stTabs [aria-selected="true"] {{
            background: {primary} !important;
            color: white !important;
        }}

        /* ── Hide Streamlit branding ── */
        #MainMenu, footer, [data-testid="stHeaderActionElements"] {{
            visibility: hidden;
        }}

        header[data-testid="stHeader"] {{
            background-color: transparent !important;
        }}

        /* ── Input type selector cards ── */
        .type-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 0.5rem;
            margin-bottom: 1rem;
        }}

        /* ── Animated gradient border ── */
        @keyframes gradient-shift {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ─── State Initialization ─────────────────────────────────────────────────────

def init_session_state() -> None:
    """Initialize all session state variables."""
    backend_url = os.environ.get("BACKEND_URL")
    if not backend_url:
        try:
            backend_url = st.secrets.get("BACKEND_URL")
        except Exception:
            pass
    if not backend_url:
        backend_url = "http://localhost:8000"

    defaults = {
        "qr_image_data": None,
        "qr_metadata": None,
        "qr_filename": None,
        "qr_download_url": None,
        "backend_url": backend_url,
        "selected_theme": "dark",
        "last_error": None,
        "generate_triggered": False,
        "input_type": "URL",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ─── Main App ─────────────────────────────────────────────────────────────────

def main() -> None:
    """Main application entry point."""
    init_session_state()

    # Inject CSS (based on selected theme)
    inject_custom_css(st.session_state.get("selected_theme", "dark"))

    # ── Sidebar ──────────────────────────────────────────────────
    customization = render_sidebar()

    # ── Page Header ──────────────────────────────────────────────
    render_header()

    # ── Main Content: Two-column layout ──────────────────────────
    col_left, col_right = st.columns([1.05, 0.95], gap="large")

    with col_left:
        # Input forms section
        qr_data, should_generate = render_input_forms()

    with col_right:
        # QR preview section
        render_qr_preview(
            qr_data=qr_data,
            customization=customization,
            should_generate=should_generate,
        )


if __name__ == "__main__":
    main()
