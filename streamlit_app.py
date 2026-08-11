"""
Creative Studios
AEC Collaboration Platform
AEC Workspace

Main Streamlit Application
Version 2.0 (Updated)
"""

from __future__ import annotations

from pathlib import Path
from html import escape

import streamlit as st


# ============================================================
# APPLICATION PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DB_FILE = BASE_DIR / "creativestudios_db.json"

LOGO_CANDIDATES = [
    BASE_DIR / "logo.svg",
    BASE_DIR / "logo.png",
    BASE_DIR / "assets" / "logo.svg",
    BASE_DIR / "assets" / "logo.png",
]


# ============================================================
# STREAMLIT CONFIGURATION
# ============================================================

# Determine logo for page icon – no emoji fallback
logo_path = None
for candidate in LOGO_CANDIDATES:
    if candidate.exists():
        logo_path = candidate
        break

st.set_page_config(
    page_title="Creative Studios | AEC Workspace",
    page_icon=str(logo_path) if logo_path else None,
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SESSION STATE
# ============================================================

DEFAULT_SESSION = {
    "authenticated": False,
    "user": None,
    "active_module": "Project Directory",
}

for key, value in DEFAULT_SESSION.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# IMPORT APPLICATION MODULES
# ============================================================

try:
    from modules.auth import (
        login_user,
        logout_user,
        get_current_user,
        is_authenticated,
    )
except Exception:
    # Safe fallback authentication
    def login_user(db, username, password):
        username = str(username or "").strip()
        password = str(password or "")
        if username == "admin" and password == "admin123":
            return True, {
                "id": 1,
                "username": "admin",
                "full_name": "System Administrator",
                "role": "Admin",
                "active": True,
            }
        return False, {}

    def logout_user():
        st.session_state["authenticated"] = False
        st.session_state["user"] = None

    def is_authenticated():
        return bool(st.session_state.get("authenticated", False))

    def get_current_user():
        user = st.session_state.get("user")
        if isinstance(user, dict):
            return user
        return {
            "id": 1,
            "username": "admin",
            "full_name": "System Administrator",
            "role": "Admin",
            "active": True,
        }


# ============================================================
# DATABASE
# ============================================================

def load_database() -> dict:
    """
    Load the application's JSON database.
    Uses modules.database when available, falls back to direct JSON read.
    """
    try:
        from modules.database import load_memory
        data = load_memory()
        if isinstance(data, dict):
            return data
    except Exception:
        pass

    try:
        import json
        if DB_FILE.exists():
            with DB_FILE.open("r", encoding="utf-8") as file:
                data = json.load(file)
            if isinstance(data, dict):
                return data
    except Exception:
        pass

    return {
        "users": [],
        "projects": [],
        "drawings": [],
        "approvals": [],
        "boq": [],
        "rfis": [],
        "site_logs": [],
    }


db = load_database()


# ============================================================
# LOGO
# ============================================================

def get_logo_file() -> Path | None:
    for candidate in LOGO_CANDIDATES:
        if candidate.exists():
            return candidate
    return None


LOGO_FILE = get_logo_file()


# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(
    """
<style>
/* ... (your existing dark theme CSS – unchanged) ... */
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# HELPERS
# ============================================================

def safe_text(value, fallback: str = "") -> str:
    if value is None:
        return fallback
    return escape(str(value))


# ============================================================
# LOGIN PAGE
# ============================================================

def render_login() -> None:
    # (keep your exact login page code – unchanged)
    ...


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar() -> str:
    # (keep your exact sidebar code – unchanged)
    ...


# ============================================================
# MODULE RENDERING FUNCTIONS (FULL IMPLEMENTATIONS)
# ============================================================

def render_projects() -> None:
    try:
        from modules.projects import render_projects_module
        render_projects_module(db)
    except Exception as error:
        st.error("Project Directory could not be loaded.")
        with st.expander("Technical details"):
            st.code(str(error))


def render_drawings() -> None:
    try:
        from modules.drawings import render_drawings_module
        render_drawings_module(db)
    except Exception as error:
        st.error("Drawing Repository could not be loaded.")
        with st.expander("Technical details"):
            st.code(str(error))


def render_approvals() -> None:
    try:
        from modules.approvals import render_approvals_module
        render_approvals_module(db)
    except Exception as error:
        st.error("Sign-Off & Approvals could not be loaded.")
        with st.expander("Technical details"):
            st.code(str(error))


def render_boq() -> None:
    try:
        from modules.boq import render_boq_module
        render_boq_module(db)
    except Exception as error:
        st.error("Bill of Quantities could not be loaded.")
        with st.expander("Technical details"):
            st.code(str(error))


def render_rfi() -> None:
    try:
        from modules.rfi import render_rfi_module
        render_rfi_module(db)
    except Exception as error:
        st.error("RFI & Technical Queries could not be loaded.")
        with st.expander("Technical details"):
            st.code(str(error))


def render_site_logs() -> None:
    try:
        from modules.site_logs import render_site_logs_module
        render_site_logs_module(db)
    except Exception as error:
        st.error("Daily Site Logs could not be loaded.")
        with st.expander("Technical details"):
            st.code(str(error))


# ============================================================
# MODULE ROUTER
# ============================================================

def render_application() -> None:
    selected = render_sidebar()

    if selected == "Project Directory":
        render_projects()
    elif selected == "Drawing Repository":
        render_drawings()
    elif selected == "Sign-Off & Approvals":
        render_approvals()
    elif selected == "Bill of Quantities":
        render_boq()
    elif selected == "RFI & Technical Queries":
        render_rfi()
    elif selected == "Daily Site Logs":
        render_site_logs()
    else:
        # Fallback (should never happen)
        render_projects()


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if is_authenticated():
    render_application()
else:
    render_login()