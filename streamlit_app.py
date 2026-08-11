"""
Creative Studios
AEC Collaboration Platform

Main Streamlit Application — Fixed (logo + CSS)
"""

from pathlib import Path
import base64

import streamlit as st

# ------------------------------------------------------------
# Ensure the default logo file exists before anything else
# ------------------------------------------------------------
from modules.utils import ensure_logo_svg   # <-- re‑added
ensure_logo_svg()                           # creates logo.svg if missing


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
LOGO_FILE = BASE_DIR / "logo.svg"


# ============================================================
# PAGE CONFIG (logo, no emoji)
# ============================================================

st.set_page_config(
    page_title="Creative Studios — AEC Platform",
    page_icon=str(LOGO_FILE) if LOGO_FILE.exists() else None,
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CSS (includes missing project card classes)
# ============================================================

st.markdown(
    """
    <style>

    /* ======================================================
       GLOBAL
       ====================================================== */

    html,
    body,
    [data-testid="stApp"],
    [data-testid="stAppViewContainer"] {

        background-color: #000000 !important;
        color: #FFFFFF !important;
    }


    [data-testid="stHeader"] {
        background-color: #000000 !important;
    }


    [data-testid="stToolbar"] {
        background-color: #000000 !important;
    }


    #MainMenu {
        visibility: hidden;
    }


    footer {
        visibility: hidden;
    }


    .block-container {

        max-width: 1500px;

        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }


    /* ======================================================
       SIDEBAR
       ====================================================== */

    [data-testid="stSidebar"] {

        background-color: #050505 !important;

        border-right:
            1px solid #172033 !important;
    }


    [data-testid="stSidebar"] > div:first-child {

        background-color: #050505 !important;
    }


    [data-testid="stSidebar"] * {

        color: #E5E7EB;
    }


    .sidebar-brand {

        text-align: center;

        padding:
            10px 5px 18px 5px;
    }


    .sidebar-logo {

        width: 78px;
        height: 78px;

        object-fit: contain;

        display: block;

        margin: 0 auto 9px auto;
    }


    .sidebar-brand-name {

        color: #FFFFFF;

        font-size: 19px;

        font-weight: 800;
    }


    .sidebar-brand-subtitle {

        color: #60A5FA;

        font-size: 9px;

        font-weight: 800;

        letter-spacing: 1.2px;

        text-transform: uppercase;

        margin-top: 4px;
    }


    .sidebar-line {

        height: 1px;

        background: #172033;

        margin: 5px 0 18px 0;
    }


    /* ======================================================
       USER PANEL
       ====================================================== */

    .user-panel {

        background: #080B10;

        border: 1px solid #172033;

        border-radius: 10px;

        padding: 13px;

        margin-bottom: 18px;
    }


    .user-label {

        color: #60A5FA;

        font-size: 9px;

        font-weight: 800;

        letter-spacing: 1px;

        text-transform: uppercase;
    }


    .user-name {

        color: #FFFFFF;

        font-size: 14px;

        font-weight: 800;

        margin-top: 5px;
    }


    .user-login {

        color: #94A3B8;

        font-size: 11px;

        margin-top: 3px;
    }


    .user-role {

        display: inline-block;

        margin-top: 9px;

        padding: 4px 9px;

        background: #2563EB;

        color: #FFFFFF;

        border-radius: 999px;

        font-size: 9px;

        font-weight: 800;
    }


    .nav-title {

        color: #64748B;

        font-size: 9px;

        font-weight: 800;

        letter-spacing: 1.2px;

        text-transform: uppercase;

        margin:
            0 0 8px 3px;
    }


    [data-testid="stSidebar"] .stRadio > label {

        display: none;
    }


    [data-testid="stSidebar"] .stRadio label {

        border-radius: 8px;

        padding: 8px 10px;

        border: 1px solid transparent;
    }


    [data-testid="stSidebar"] .stRadio label:hover {

        background: #0B1220;

        border-color: #172033;
    }


    /* ======================================================
       HEADERS
       ====================================================== */

    .page-title {

        color: #FFFFFF;

        font-size: 30px;

        font-weight: 850;

        letter-spacing: -0.8px;
    }


    .page-subtitle {

        color: #94A3B8;

        font-size: 13px;

        margin-top: 5px;

        margin-bottom: 20px;
    }


    /* ======================================================
       KPI
       ====================================================== */

    [data-testid="stMetric"] {

        background: #070707;

        border: 1px solid #172033;

        border-radius: 10px;

        padding: 14px;
    }


    [data-testid="stMetricLabel"] {

        color: #64748B !important;

        font-size: 10px !important;

        text-transform: uppercase;
    }


    [data-testid="stMetricValue"] {

        color: #FFFFFF !important;
    }


    /* ======================================================
       PROJECT CARD
       ====================================================== */

    .project-card {

        background: #070707;

        border: 1px solid #172033;

        border-radius: 12px;

        padding: 18px;

        margin: 12px 0;
    }


    .project-card:hover {

        border-color: #2563EB;
    }


    .project-header {

        display: flex;

        justify-content: space-between;

        align-items: flex-start;

        gap: 15px;
    }


    .project-name {

        color: #FFFFFF;

        font-size: 18px;

        font-weight: 800;
    }


    .project-code {

        color: #60A5FA;

        font-size: 11px;

        margin-top: 4px;
    }


    /* ----------  MISSING CLASSES (used in custom HTML) ---------- */

    .project-title {
        color: #FFFFFF;
        font-size: 18px;
        font-weight: 800;
    }


    .project-meta {
        color: #60A5FA;
        font-size: 11px;
        margin-top: 4px;
    }


    .status-badge {
        display: inline-block;
        padding: 5px 9px;
        border-radius: 999px;
        font-size: 8px;
        font-weight: 850;
        white-space: nowrap;
    }
    /* ------------------------------------------------------------- */


    .project-phase {

        color: #94A3B8;

        font-size: 11px;

        padding:
            13px 0;

        border-bottom:
            1px solid #111827;
    }


    .project-phase strong {

        color: #E2E8F0;
    }


    .project-details {

        display: grid;

        grid-template-columns:
            repeat(4, 1fr);

        gap: 15px;

        margin-top: 14px;
    }


    .detail-label {

        color: #475569;

        font-size: 8px;

        font-weight: 800;

        letter-spacing: .8px;
    }


    .detail-value {

        color: #CBD5E1;

        font-size: 11px;

        margin-top: 4px;
    }


    .project-description {

        color: #64748B;

        font-size: 11px;

        line-height: 1.6;

        margin-top: 14px;
    }


    /* ======================================================
       STATUS BADGES
       ====================================================== */

    .status {

        display: inline-block;

        padding: 5px 9px;

        border-radius: 999px;

        font-size: 8px;

        font-weight: 850;

        white-space: nowrap;
    }


    .status-active {

        background: #052E16;

        color: #4ADE80;

        border: 1px solid #166534;
    }


    .status-planning {

        background: #172554;

        color: #60A5FA;

        border: 1px solid #1D4ED8;
    }


    .status-completed {

        background: #042F2E;

        color: #5EEAD4;

        border: 1px solid #0F766E;
    }


    .status-hold {

        background: #422006;

        color: #FBBF24;

        border: 1px solid #92400E;
    }


    .status-cancelled {

        background: #450A0A;

        color: #F87171;

        border: 1px solid #991B1B;
    }


    .status-default {

        background: #111827;

        color: #94A3B8;

        border: 1px solid #334155;
    }


    /* ======================================================
       INPUTS
       ====================================================== */

    .stTextInput input,
    .stTextArea textarea,
    .stNumberInput input {

        background: #050505 !important;

        color: #FFFFFF !important;

        border:
            1px solid #1E293B !important;
    }


    /* ======================================================
       BUTTONS
       ====================================================== */

    .stButton button,
    .stFormSubmitButton button {

        background: #2563EB !important;

        color: #FFFFFF !important;

        border:
            1px solid #3B82F6 !important;

        border-radius: 7px !important;

        font-weight: 750 !important;
    }


    .stButton button:hover,
    .stFormSubmitButton button:hover {

        background: #1D4ED8 !important;
    }


    /* ======================================================
       LOGIN
       ====================================================== */

    .login-container {

        max-width: 390px;

        margin:
            70px auto 0 auto;

        text-align: center;
    }


    .login-logo {

        width: 120px;

        height: 120px;

        object-fit: contain;

        margin:
            0 auto 18px auto;
    }


    .login-title {

        color: #FFFFFF;

        font-size: 27px;

        font-weight: 850;
    }


    .login-subtitle {

        color: #64748B;

        font-size: 11px;

        margin:
            6px 0 25px 0;
    }


    /* ======================================================
       EMPTY STATE
       ====================================================== */

    .empty-state {

        background: #070707;

        border:
            1px dashed #1E293B;

        border-radius: 12px;

        padding: 50px 20px;

        text-align: center;

        margin-top: 15px;
    }


    .empty-title {

        color: #FFFFFF;

        font-size: 18px;

        font-weight: 800;
    }


    .empty-text {

        color: #64748B;

        font-size: 12px;

        margin-top: 7px;
    }


    @media (max-width: 800px) {

        .project-details {

            grid-template-columns:
                repeat(2, 1fr);
        }

    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LOGO (base64 helper)
# ============================================================

def get_logo_data():
    """Return a base64 data URI for the logo, or None if missing."""
    try:
        if not LOGO_FILE.exists():
            return None
        content = LOGO_FILE.read_bytes()
        encoded = base64.b64encode(content).decode("utf-8")
        return f"data:image/svg+xml;base64,{encoded}"
    except Exception:
        return None


# ============================================================
# DATABASE
# ============================================================

try:
    from modules.database import load_memory
    db = load_memory()
except Exception:
    db = {}

if not isinstance(db, dict):
    db = {}


# ============================================================
# SESSION STATE
# ============================================================

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user" not in st.session_state:
    st.session_state["user"] = None


# ============================================================
# AUTHENTICATION
# ============================================================

def authenticate(username, password):
    username = str(username or "").strip().lower()
    password = str(password or "")

    users = db.get("users", [])
    if not isinstance(users, list):
        users = []

    for user in users:
        if not isinstance(user, dict):
            continue
        stored_username = str(user.get("username", "")).strip().lower()
        stored_password = str(user.get("password", user.get("password_hash", "")))
        if username == stored_username and password == stored_password:
            st.session_state["authenticated"] = True
            st.session_state["user"] = user
            return True

    # Development fallback (only when DB is empty)
    if not users and username == "admin" and password == "admin123":
        user = {
            "username": "admin",
            "name": "System Administrator",
            "full_name": "System Administrator",
            "role": "Admin",
        }
        st.session_state["authenticated"] = True
        st.session_state["user"] = user
        return True

    return False


# ============================================================
# LOGIN PAGE
# ============================================================

def show_login():
    logo = get_logo_data()
    st.markdown('<div class="login-container">', unsafe_allow_html=True)

    if logo:
        st.markdown(f'<img src="{logo}" class="login-logo">', unsafe_allow_html=True)
    else:
        st.markdown(
            """
            <div style="width:120px;height:120px;margin:0 auto 18px auto;
                        display:flex;align-items:center;justify-content:center;
                        border:2px solid #2563EB;border-radius:28px;
                        color:#60A5FA;font-size:42px;font-weight:900;">
                CS
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="login-title">Creative Studios</div>
        <div class="login-subtitle">AEC Collaboration Platform</div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        submit = st.form_submit_button("Sign In", use_container_width=True)

    if submit:
        if authenticate(username, password):
            st.rerun()
        else:
            st.error("Invalid username or password.")

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

def show_sidebar():
    user = st.session_state.get("user") or {}
    username = str(user.get("username", "admin"))
    name = str(user.get("name", user.get("full_name", "System Administrator")))
    role = str(user.get("role", "Admin"))
    logo = get_logo_data()

    with st.sidebar:
        if logo:
            st.markdown(
                f"""
                <div class="sidebar-brand">
                    <img src="{logo}" class="sidebar-logo">
                    <div class="sidebar-brand-name">Creative Studios</div>
                    <div class="sidebar-brand-subtitle">AEC Workspace</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div class="sidebar-brand">
                    <div style="color:#2563EB;font-size:38px;font-weight:900;">CS</div>
                    <div class="sidebar-brand-name">Creative Studios</div>
                    <div class="sidebar-brand-subtitle">AEC Workspace</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown('<div class="sidebar-line"></div>', unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class="user-panel">
                <div class="user-label">Signed In</div>
                <div class="user-name">{name}</div>
                <div class="user-login">@{username}</div>
                <div class="user-role">{role}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="nav-title">Navigation</div>', unsafe_allow_html=True)

        menu = [
            "Project Directory",
            "Drawing Repository",
            "Sign-Off & Approvals",
            "Bill of Quantities (BOQ)",
            "RFI & Technical Queries",
            "Daily Site Logs",
        ]

        selected = st.radio("Navigation", menu, label_visibility="collapsed")

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Sign Out", use_container_width=True):
            st.session_state["authenticated"] = False
            st.session_state["user"] = None
            st.rerun()

    return selected


# ============================================================
# AUTHENTICATION GATE
# ============================================================

if not st.session_state["authenticated"]:
    show_login()
    st.stop()


# ============================================================
# ROUTING
# ============================================================

selected_module = show_sidebar()

if selected_module == "Project Directory":
    from modules.projects import render_projects_module
    render_projects_module(db)

elif selected_module == "Drawing Repository":
    try:
        from modules.drawings import render_drawings_module
        render_drawings_module(db)
    except Exception as exc:
        st.error(f"Drawing Repository is unavailable: {exc}")

elif selected_module == "Sign-Off & Approvals":
    try:
        from modules.approvals import render_approvals_module
        render_approvals_module(db)
    except Exception as exc:
        st.error(f"Sign-Off & Approvals is unavailable: {exc}")

elif selected_module == "Bill of Quantities (BOQ)":
    try:
        from modules.boq import render_boq_module
        render_boq_module(db)
    except Exception as exc:
        st.error(f"BOQ is unavailable: {exc}")

elif selected_module == "RFI & Technical Queries":
    try:
        from modules.rfi import render_rfi_module
        render_rfi_module(db)
    except Exception as exc:
        st.error(f"RFI module is unavailable: {exc}")

elif selected_module == "Daily Site Logs":
    try:
        from modules.site_logs import render_site_logs_module
        render_site_logs_module(db)
    except Exception as exc:
        st.error(f"Daily Site Logs is unavailable: {exc}")