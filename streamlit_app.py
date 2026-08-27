"""
Creative Studios
AEC Collaboration Platform

Main Streamlit application.

Authentication has been removed.
Dark mode has been removed.
Modules are loaded only when selected.
"""

from __future__ import annotations

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
# APPLICATION CSS
# ============================================================

def inject_css() -> None:
    """Apply the Creative Studios interface styling."""

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


        /* ==================================================
           SIDEBAR
           ================================================== */

        [data-testid="stSidebar"] {
            border-right: 1px solid #E2E8F0;
        }

        [data-testid="stSidebar"] img {
            display: block;
            margin-left: auto !important;
            margin-right: auto !important;
        }

        .cs-sidebar-brand {
            width: 100%;
            text-align: center;
            padding-top: 0.25rem;
            padding-bottom: 0.75rem;
        }

        .cs-sidebar-title {
            text-align: center;
            font-size: 17px;
            font-weight: 700;
            line-height: 1.2;
            margin-top: 5px;
        }

        .cs-sidebar-subtitle {
            text-align: center;
            font-size: 12px;
            color: #64748B;
            margin-top: 4px;
            line-height: 1.3;
        }

        .cs-divider {
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


        /* ==================================================
           SIDEBAR RADIO NAVIGATION
           ================================================== */

        [data-testid="stSidebar"] div[role="radiogroup"] {
            gap: 0.25rem;
        }

        [data-testid="stSidebar"] div[role="radiogroup"] label {
            border-radius: 8px;
            padding: 0.45rem 0.65rem;
            cursor: pointer;
            transition:
                background-color 0.15s ease,
                transform 0.1s ease;
        }

        [data-testid="stSidebar"] div[role="radiogroup"] label:hover {
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
            box-shadow: 0 3px 10px rgba(15, 23, 42, 0.10);
        }

        div.stButton > button:active {
            transform: translateY(0);
        }


        /* ==================================================
           FORM BUTTONS
           ================================================== */

        div[data-testid="stFormSubmitButton"] button {
            min-height: 42px;
            border-radius: 8px;
            font-weight: 600;
        }


        /* ==================================================
           MODULE HEADERS
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
           TABS
           ================================================== */

        button[data-baseweb="tab"] {
            font-weight: 600;
        }


        /* ==================================================
           EXPANDERS
           ================================================== */

        [data-testid="stExpander"] {
            border-radius: 10px;
            border: 1px solid #E2E8F0;
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
    """Initialize application state."""

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

    The same dictionary is shared with all modules.
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
# SIDEBAR BRANDING
# ============================================================

def render_sidebar_logo() -> None:
    """Render a small centered Creative Studios logo."""

    st.sidebar.markdown(
        '<div class="cs-sidebar-brand">',
        unsafe_allow_html=True,
    )

    if LOGO_PATH.exists():

        # Four-column layout gives the logo a dedicated
        # centered area and works reliably in Streamlit Cloud.
        left, center, right = st.sidebar.columns(
            [1, 2, 1]
        )

        with center:

            st.image(
                str(LOGO_PATH),
                width=64,
            )

    else:

        st.sidebar.markdown(
            """
            <div style="
                text-align: center;
                font-size: 17px;
                font-weight: 700;
            ">
                Creative Studios
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.sidebar.markdown(
        """
        <div class="cs-sidebar-title">
            Creative Studios
        </div>

        <div class="cs-sidebar-subtitle">
            AEC Collaboration Platform
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown(
        "</div>",
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
    """Render the main application navigation."""

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

    if choice != st.session_state.active_module:

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
    Import and return the renderer for a module.

    Modules are imported only when selected.
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
            f"{module_name} module. "
            f"Python reported: {exc}"
        ) from exc

    renderer = getattr(
        module,
        function_name,
        None,
    )

    if not callable(renderer):

        raise AttributeError(
            f"Module '{module_path}' does not "
            f"contain a callable "
            f"'{function_name}' function."
        )

    return renderer


# ============================================================
# MODULE ROUTER
# ============================================================

def render_module(
    choice: str,
    database: dict[str, Any],
) -> None:
    """Render the selected application module."""

    try:

        renderer = load_module_renderer(
            choice
        )

        renderer(database)

    except Exception as exc:

        st.error(
            f"Unable to render the {choice} module."
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
    """Run the Creative Studios application."""

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