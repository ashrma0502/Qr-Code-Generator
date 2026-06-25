"""
Input forms component.
Renders dynamic forms based on selected QR input type.
"""

import streamlit as st


from services.config_loader import (
    get_input_types,
    get_wifi_encryption_types,
)
from utils.formatters import (
    format_url_data,
    format_email_data,
    format_phone_data,
    format_sms_data,
    format_wifi_data,
    format_vcard_data,
)


def render_input_forms() -> tuple[str | None, bool]:
    """
    Render the dynamic QR input form section.

    Returns:
        Tuple[Optional[str], bool]: (formatted_qr_data, should_generate)
    """
    input_types = get_input_types()

    st.markdown('<p class="section-title">📋 Input Type</p>', unsafe_allow_html=True)

    # Build display options list
    type_options = {
        k: f"{v.get('icon', '')} {v.get('label', k)}"
        for k, v in input_types.items()
    }
    type_keys = list(type_options.keys())
    type_display = list(type_options.values())

    # Type selector — styled as a radio-like row
    selected_display = st.selectbox(
        "QR Code Type",
        options=type_display,
        index=type_keys.index(st.session_state.get("input_type", "url"))
        if st.session_state.get("input_type", "url") in type_keys
        else 1,
        label_visibility="collapsed",
    )
    selected_type = type_keys[type_display.index(selected_display)]
    st.session_state["input_type"] = selected_type

    # Description
    desc = input_types.get(selected_type, {}).get("description", "")
    if desc:
        st.caption(f"ℹ️ {desc}")

    st.divider()

    # ── Render Form for Selected Type ──────────────────────────
    qr_data: str | None = None
    should_generate = False

    if selected_type == "text":
        qr_data, should_generate = _form_text()
    elif selected_type == "url":
        qr_data, should_generate = _form_url()
    elif selected_type == "email":
        qr_data, should_generate = _form_email()
    elif selected_type == "phone":
        qr_data, should_generate = _form_phone()
    elif selected_type == "sms":
        qr_data, should_generate = _form_sms()
    elif selected_type == "wifi":
        qr_data, should_generate = _form_wifi()
    elif selected_type == "vcard":
        qr_data, should_generate = _form_vcard()
    elif selected_type == "custom":
        qr_data, should_generate = _form_custom()

    return qr_data, should_generate


# ─── Individual Form Renderers ────────────────────────────────────────────────

def _form_text() -> tuple[str | None, bool]:
    """Plain text form."""
    st.markdown('<p class="section-title">📝 Plain Text</p>', unsafe_allow_html=True)
    text = st.text_area(
        "Enter your text",
        placeholder="Type or paste any text here...",
        height=120,
        max_chars=1000,
        help="Any plain text content to encode in the QR code",
    )
    char_count = len(text) if text else 0
    st.caption(f"Characters: {char_count}/1000")

    btn = st.button("🔳 Generate QR Code", use_container_width=True, type="primary")
    if btn and text and text.strip():
        return text.strip(), True
    elif btn:
        st.warning("⚠️ Please enter some text first.")
    return text.strip() if text else None, False


def _form_url() -> tuple[str | None, bool]:
    """URL form."""
    st.markdown('<p class="section-title">🔗 Website URL</p>', unsafe_allow_html=True)
    url = st.text_input(
        "Website URL",
        placeholder="https://www.example.com",
        help="Enter a full URL. https:// will be added automatically if missing.",
    )
    btn = st.button("🔳 Generate QR Code", use_container_width=True, type="primary")

    if btn:
        if not url or not url.strip():
            st.warning("⚠️ Please enter a URL.")
            return None, False
        formatted = format_url_data(url.strip())
        return formatted, True

    return format_url_data(url.strip()) if url and url.strip() else None, False


def _form_email() -> tuple[str | None, bool]:
    """Email form."""
    st.markdown('<p class="section-title">📧 Email Address</p>', unsafe_allow_html=True)
    email = st.text_input(
        "Email Address *",
        placeholder="user@example.com",
        help="Recipient email address",
    )
    subject = st.text_input(
        "Subject (optional)",
        placeholder="Hello!",
        help="Pre-filled email subject",
    )
    body = st.text_area(
        "Message Body (optional)",
        placeholder="Enter message...",
        height=80,
        help="Pre-filled email body",
    )

    btn = st.button("🔳 Generate QR Code", use_container_width=True, type="primary")

    if btn:
        if not email or not email.strip():
            st.warning("⚠️ Please enter an email address.")
            return None, False
        if "@" not in email or "." not in email.split("@")[-1]:
            st.error("❌ Invalid email address format.")
            return None, False
        formatted = format_email_data(email.strip(), subject.strip(), body.strip())
        return formatted, True

    if email and email.strip():
        return format_email_data(email.strip(), subject.strip() if subject else "", body.strip() if body else ""), False
    return None, False


def _form_phone() -> tuple[str | None, bool]:
    """Phone number form."""
    st.markdown('<p class="section-title">📞 Phone Number</p>', unsafe_allow_html=True)
    phone = st.text_input(
        "Phone Number *",
        placeholder="+91 98765 43210",
        help="Include country code for international numbers (e.g., +91 for India)",
    )

    btn = st.button("🔳 Generate QR Code", use_container_width=True, type="primary")

    if btn:
        if not phone or not phone.strip():
            st.warning("⚠️ Please enter a phone number.")
            return None, False
        formatted = format_phone_data(phone.strip())
        return formatted, True

    return format_phone_data(phone.strip()) if phone and phone.strip() else None, False


def _form_sms() -> tuple[str | None, bool]:
    """SMS form."""
    st.markdown('<p class="section-title">💬 SMS Message</p>', unsafe_allow_html=True)
    phone = st.text_input(
        "Recipient Phone Number *",
        placeholder="+91 98765 43210",
        help="Phone number of the SMS recipient",
    )
    message = st.text_area(
        "Message (optional)",
        placeholder="Enter your SMS message...",
        height=80,
        max_chars=160,
        help="Pre-filled SMS message (max 160 characters)",
    )
    if message:
        st.caption(f"SMS characters: {len(message)}/160")

    btn = st.button("🔳 Generate QR Code", use_container_width=True, type="primary")

    if btn:
        if not phone or not phone.strip():
            st.warning("⚠️ Please enter a phone number.")
            return None, False
        formatted = format_sms_data(phone.strip(), message.strip() if message else "")
        return formatted, True

    if phone and phone.strip():
        return format_sms_data(phone.strip(), message.strip() if message else ""), False
    return None, False


def _form_wifi() -> tuple[str | None, bool]:
    """WiFi credentials form."""
    st.markdown('<p class="section-title">📶 WiFi Credentials</p>', unsafe_allow_html=True)

    ssid = st.text_input(
        "Network Name (SSID) *",
        placeholder="MyWiFiNetwork",
        max_chars=32,
        help="The exact name of the WiFi network",
    )

    encryption_types = get_wifi_encryption_types()
    encryption = st.selectbox(
        "Encryption Type",
        options=encryption_types,
        index=0,
        help="WiFi security type. Choose 'nopass' for open networks.",
    )

    password = ""
    if encryption.lower() != "nopass":
        password = st.text_input(
            "Password *",
            type="password",
            placeholder="WiFi password",
            help="The WiFi network password",
        )

    hidden = st.checkbox(
        "🙈 Hidden Network",
        value=False,
        help="Check if this is a hidden WiFi network",
    )

    btn = st.button("🔳 Generate QR Code", use_container_width=True, type="primary")

    if btn:
        if not ssid or not ssid.strip():
            st.warning("⚠️ Please enter the network SSID.")
            return None, False
        if encryption.lower() != "nopass" and not password:
            st.warning("⚠️ Please enter the WiFi password.")
            return None, False
        formatted = format_wifi_data(ssid.strip(), password, encryption, hidden)
        return formatted, True

    if ssid and ssid.strip():
        return format_wifi_data(ssid.strip(), password, encryption, hidden), False
    return None, False


def _form_vcard() -> tuple[str | None, bool]:
    """vCard contact form."""
    st.markdown('<p class="section-title">👤 Contact Card (vCard)</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        first_name = st.text_input("First Name *", placeholder="John")
        phone = st.text_input("Phone", placeholder="+91 98765 43210")
        company = st.text_input("Company", placeholder="ACME Corp")
        website = st.text_input("Website", placeholder="https://johndoe.com")

    with col2:
        last_name = st.text_input("Last Name", placeholder="Doe")
        email = st.text_input("Email", placeholder="john@example.com")
        title = st.text_input("Job Title", placeholder="Software Engineer")
        address = st.text_input("Address", placeholder="123 Main St, City")

    note = st.text_area(
        "Notes (optional)",
        placeholder="Additional information...",
        height=60,
    )

    btn = st.button("🔳 Generate QR Code", use_container_width=True, type="primary")

    if btn:
        if not first_name or not first_name.strip():
            st.warning("⚠️ Please enter at least a first name.")
            return None, False
        full_name = f"{first_name.strip()} {last_name.strip()}".strip()
        formatted = format_vcard_data(
            name=full_name,
            phone=phone.strip() if phone else "",
            email=email.strip() if email else "",
            company=company.strip() if company else "",
            title=title.strip() if title else "",
            website=website.strip() if website else "",
            address=address.strip() if address else "",
            note=note.strip() if note else "",
        )
        return formatted, True

    if first_name and first_name.strip():
        full_name = f"{first_name.strip()} {last_name.strip() if last_name else ''}".strip()
        formatted = format_vcard_data(
            name=full_name,
            phone=phone.strip() if phone else "",
            email=email.strip() if email else "",
            company=company.strip() if company else "",
        )
        return formatted, False
    return None, False


def _form_custom() -> tuple[str | None, bool]:
    """Custom data form."""
    st.markdown('<p class="section-title">⚙️ Custom Data</p>', unsafe_allow_html=True)
    st.info(
        "Enter any raw data string to encode. Useful for proprietary formats, "
        "deep links, or custom protocols.",
        icon="ℹ️",
    )
    data = st.text_area(
        "Custom Data *",
        placeholder="myapp://open?screen=home\nor any custom string...",
        height=150,
        max_chars=4000,
        help="Raw data to encode directly into the QR code",
    )
    char_count = len(data) if data else 0
    st.caption(f"Characters: {char_count}/4000")

    btn = st.button("🔳 Generate QR Code", use_container_width=True, type="primary")
    if btn and data and data.strip():
        return data.strip(), True
    elif btn:
        st.warning("⚠️ Please enter some data.")
    return data.strip() if data else None, False
