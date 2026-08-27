"""
Creative Studios
AEC Collaboration Platform

Main Streamlit application.

Authentication has been removed.
Dark mode has been removed.
Modules are loaded only when selected.
"""

from __future__ import annotations

import base64
import importlib
from pathlib import Path
from typing import Any, Callable

import streamlit as st

from modules.database import load_memory


# ============================================================
# PAGE CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

LOGO_PATH = (
    BASE_DIR
    / "assets"
    / "creative_studios.png"
)

st.set_page_config(
    page_title="Creative Studios",
    page_icon=(
        str(LOGO_PATH)
        if LOGO_PATH.exists()
        else None
    ),
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# GLOBAL CSS
# ============================================================

def inject_css() -> None:
    """Apply Creative Studios application styling."""

    st.markdown(
        """
        <style>

        /* ==================================================
           GLOBAL
           ================================================== */

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stAppViewContainer"] {
            background: #F8FAFC;
        }


        /* ==================================================
           SIDEBAR
           ================================================== */

        [data-testid="stSidebar"] {
            background: #FFFFFF;
            border-right: 1px solid #E2E8F0;
        }

        [data-testid="stSidebar"] > div:first-child {
            padding-top: 1rem;
        }


        /* ==================================================
           SIDEBAR BRANDING
           ================================================== */

        .cs-sidebar-brand {
            width: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            box-sizing: border-box;
            padding: 0.25rem 0 1rem 0;
            margin: 0;
        }

        .cs-sidebar-logo {
            display: block;
            width: 64px;
            height: 64px;
            object-fit: contain;
            object-position: center;
            margin: 0 auto 8px auto;
            padding: 0;
        }

        .cs-sidebar-title {
            display: block;
            width: 100%;
            text-align: center;
            font-size: 17px;
            font-weight: 700;
            line-height: 1.2;
            margin: 0;
            padding: 0;
        }

        .cs-sidebar-subtitle {
            display: block;
            width: 100%;
            text-align: center;
            font-size: 12px;
            font-weight: 400;
            line-height: 1.35;
            color: #64748B;
            margin: 4px 0 0 0;
            padding: 0;
        }


        /* ==================================================
           SIDEBAR NAVIGATION
           ================================================== */

        .cs-divider {
            width: 100%;
            height: 1px;
            background: #E2E8F0;
            margin: 0.75rem 0 1rem 0;
        }

        .cs-section-label {
            color: #64748B;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-top: 0.5rem;
            margin-bottom: 0.5rem;
        }

        [data-testid="stSidebar"] div[role="radiogroup"] {
            width: 100%;
            gap: 0.2rem;
        }

        [data-testid="stSidebar"] div[role="radiogroup"] label {
            width: 100%;
            box-sizing: border-box;
            border-radius: 8px;
            padding: 0.5rem 0.65rem;
            cursor: pointer;
            transition:
                background-color 0.15s ease,
                transform 0.1s ease;
        }

        [data-testid="stSidebar"]
        div[role="radiogroup"]
        label:hover {
            background-color: #F1F5F9;
            transform: translateX(2px);
        }


        /* ==================================================
           BUTTONS
           ================================================== */

        div.stButton > button {
            min-height: 42px;
            border-radius: 8px;
            font-weight: 600;
            transition:
                transform 0.1s ease,
                box-shadow 0.15s ease;
        }

        div.stButton > button:hover {
            transform: translateY(-1px);
            box-shadow:
                0 3px 10px rgba(15, 23, 42, 0.10);
        }

        div.stButton > button:active {
            transform: translateY(0);
        }

        div[data-testid="stFormSubmitButton"] button {
            min-height: 42px;
            border-radius: 8px;
            font-weight: 600;
            transition:
                transform 0.1s ease,
                box-shadow 0.15s ease;
        }

        div[data-testid="stFormSubmitButton"] button:hover {
            transform: translateY(-1px);
            box-shadow:
                0 3px 10px rgba(15, 23, 42, 0.10);
        }


        /* ==================================================
           MAIN MODULE HEADERS
           ================================================== */

        .cs-module-title {
            font-size: 30px;
            font-weight: 750;
            line-height: 1.15;
            margin-bottom: 0.25rem;
        }

        .cs-module-description {
            color: #64748B;
            font-size: 14px;
            margin-bottom: 1.25rem;
        }


        /* ==================================================
           CARDS
           ================================================== */

        .cs-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 1.25rem;
            margin-bottom: 1rem;
        }

        .cs-card-title {
            font-size: 18px;
            font-weight: 700;
        }

        .cs-card-subtitle {
            color: #64748B;
            font-size: 14px;
            line-height: 1.5;
            margin-top: 5px;
        }


        /* ==================================================
           METRICS
           ================================================== */

        [data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 0.75rem;
        }


        /* ==================================================
           EXPANDERS
           ================================================== */

        [data-testid="stExpander"] {
            border-radius: 10px;
            border: 1px solid #E2E8F0;
        }


        /* ==================================================
           TABS
           ================================================== */

        button[data-baseweb="tab"] {
            font-weight: 600;
        }


        /* ==================================================
           INPUTS
           ================================================== */

        input,
        textarea {
            border-radius: 7px !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# SESSION STATE
# ============================================================

def initialize_session_state() -> None:
    """Initialize application session state."""

    defaults: dict[str, Any] = {
        "active_module": "Dashboard",
        "database": None,
    }

    for key, value in defaults.items():

        if key not in st.session_state:
            st.session_state[key] = value


# ============================================================
# DATABASE
# ============================================================

def get_database() -> dict[str, Any]:
    """
    Load the application database once per session.

    All modules receive the same database dictionary.
    """

    database = st.session_state.get(
        "database"
    )

    if not isinstance(database, dict):

        database = load_memory()

        if not isinstance(database, dict):
            database = {}

        st.session_state.database = database

    return database


# ============================================================
# LOGO DATA
# ============================================================

def get_logo_data_uri() -> str | None:
    """
    Convert the Creative Studios PNG into a browser-safe
    data URI.

    This keeps the logo and branding in one HTML element,
    allowing reliable centering on Streamlit Cloud.
    """

    if not LOGO_PATH.exists():
        return None

    try:

        logo_bytes = LOGO_PATH.read_bytes()

    except OSError:

        return None

    encoded = base64.b64encode(
        logo_bytes
    ).decode("utf-8")

    extension = LOGO_PATH.suffix.lower()

    mime_type = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }.get(
        extension,
        "image/png",
    )

    return (
        f"data:{mime_type};base64,{encoded}"
    )


# ============================================================
# SIDEBAR BRANDING
# ============================================================

def render_sidebar_logo() -> None:
    """
    Render the complete centered Creative Studios branding.

    Logo, title and subtitle are intentionally contained in
    one HTML element.
    """

    logo_uri = get_logo_data_uri()

    if logo_uri:

        st.sidebar.markdown(
            f"""
            <div class="cs-sidebar-brand">

                <img
                    class="cs-sidebar-logo"
                    src="{logo_uri}"
                    alt="Creative Studios logo"
                />

                <div class="cs-sidebar-title">
                    Creative Studios
                </div>

                <div class="cs-sidebar-subtitle">
                    AEC Collaboration Platform
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        st.sidebar.markdown(
            """
            <div class="cs-sidebar-brand">

                <div class="cs-sidebar-title">
                    Creative Studios
                </div>

                <div class="cs-sidebar-subtitle">
                    AEC Collaboration Platform
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# NAVIGATION
# ============================================================

NAVIGATION = [
    "Dashboard",
    "Projects",
    "Documents",
    "Architecture",
    "Engineering",
    "Drawings",
    "BOQ",
    "MEP",
]


def render_sidebar() -> str:
    """Render the application navigation."""

    render_sidebar_logo()

    st.sidebar.markdown(
        '<div class="cs-divider"></div>',
        unsafe_allow_html=True,
    )

    st.sidebar.markdown(
        '<div class="cs-section-label">Navigation</div>',
        unsafe_allow_html=True,
    )

    current = st.session_state.get(
        "active_module",
        "Dashboard",
    )

    if current not in NAVIGATION:
        current = "Dashboard"

    choice = st.sidebar.radio(
        "Go to",
        NAVIGATION,
        index=NAVIGATION.index(current),
        key="module_navigation",
        label_visibility="collapsed",
    )

    st.session_state.active_module = choice

    return choice


# ============================================================
# MODULE REGISTRY
# ============================================================

MODULE_IMPORTS: dict[
    str,
    tuple[str, str],
] = {

    "Dashboard": (
        "modules.dashboard",
        "render_dashboard",
    ),

    "Projects": (
        "modules.projects",
        "render_projects_module",
    ),

    "Documents": (
        "modules.documents",
        "render_documents_module",
    ),

    "Architecture": (
        "modules.architecture",
        "render_architecture_module",
    ),

    "Engineering": (
        "modules.engineering",
        "render_engineering_module",
    ),

    "Drawings": (
        "modules.drawings",
        "render_drawings_module",
    ),

    "BOQ": (
        "modules.boq",
        "render_boq_module",
    ),

    "MEP": (
        "modules.mep",
        "render_mep_module",
    ),
}


# ============================================================
# MODULE LOADER
# ============================================================

def load_module_renderer(
    module_name: str,
) -> Callable[
    [dict[str, Any]],
    None,
]:
    """
    Dynamically load the selected module.

    Only the selected module is imported.
    """

    if module_name not in MODULE_IMPORTS:

        raise KeyError(
            f"Unknown module: {module_name}"
        )

    module_path, function_name = (
        MODULE_IMPORTS[module_name]
    )

    try:

        module = importlib.import_module(
            module_path
        )

    except Exception as exc:

        raise RuntimeError(
            f"Unable to load the "
            f"{module_name} module "
            f"('{module_path}')."
        ) from exc

    renderer = getattr(
        module,
        function_name,
        None,
    )

    if not callable(renderer):

        raise AttributeError(
            f"Module '{module_path}' does not "
            f"contain the required callable "
            f"'{function_name}'."
        )

    return renderer


# ============================================================
# MODULE ROUTER
# ============================================================

def render_module(
    choice: str,
    database: dict[str, Any],
) -> None:
    """Render the selected module."""

    try:

        renderer = load_module_renderer(
            choice
        )

        renderer(
            database
        )

    except Exception as exc:

        st.error(
            f"Unable to render the "
            f"{choice} module."
        )

        with st.expander(
            "Technical details",
            expanded=False,
        ):

            st.exception(exc)


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    """Run Creative Studios."""

    initialize_session_state()

    inject_css()

    database = get_database()

    choice = render_sidebar()

    render_module(
        choice,
        database,
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()