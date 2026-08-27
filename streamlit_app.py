"""
Creative Studios
AEC Collaboration Platform

Main Streamlit application.

Authentication has been removed.
Modules are loaded lazily to prevent one broken module
from preventing the entire application from starting.
"""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any

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
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else None,
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# THEME
# ============================================================

def initialize_theme() -> None:
    """Initialize the application theme."""

    if "theme" not in st.session_state:
        st.session_state.theme = "Dark"


def render_theme_selector() -> None:
    """Render the dark/light mode selector."""

    current_theme = st.session_state.get(
        "theme",
        "Dark",
    )

    theme = st.sidebar.selectbox(
        "Theme",
        ["Dark", "Light"],
        index=0 if current_theme == "Dark" else 1,
        key="theme_selector",
    )

    if theme != current_theme:
        st.session_state.theme = theme
        st.rerun()


def inject_theme_css() -> None:
    """Inject theme-aware Creative Studios styling."""

    theme = st.session_state.get(
        "theme",
        "Dark",
    )

    if theme == "Light":

        background = "#F8FAFC"
        surface = "#FFFFFF"
        text = "#0F172A"
        muted = "#64748B"
        border = "#E2E8F0"

    else:

        background = "#05070B"
        surface = "#0B1018"
        text = "#F8FAFC"
        muted = "#94A3B8"
        border = "#1E293B"

    st.markdown(
        f"""
        <style>

        /* ================================================== */
        /* APPLICATION */
        /* ================================================== */

        [data-testid="stAppViewContainer"] {{
            background: {background};
            color: {text};
        }}

        [data-testid="stHeader"] {{
            background: transparent;
        }}

        .block-container {{
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }}

        /* ================================================== */
        /* SIDEBAR */
        /* ================================================== */

        [data-testid="stSidebar"] {{
            background: {surface};
            border-right: 1px solid {border};
        }}

        [data-testid="stSidebar"] * {{
            color: {text};
        }}

        .cs-sidebar-brand {{
            text-align: center;
            padding: 0.5rem 0 1rem 0;
        }}

        .cs-sidebar-brand img {{
            width: 64px;
            max-width: 64px;
            height: auto;
            display: block;
            margin: 0 auto 8px auto;
        }}

        .cs-sidebar-title {{
            color: {text};
            font-size: 17px;
            font-weight: 700;
            line-height: 1.2;
        }}

        .cs-sidebar-subtitle {{
            color: {muted};
            font-size: 12px;
            margin-top: 4px;
        }}

        .cs-divider {{
            height: 1px;
            background: {border};
            margin: 0.5rem 0 1rem 0;
        }}

        .cs-section-label {{
            color: {muted};
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
        }}

        /* ================================================== */
        /* MAIN HEADERS */
        /* ================================================== */

        .cs-module-header {{
            margin-bottom: 1.5rem;
        }}

        .cs-module-title {{
            color: {text};
            font-size: 30px;
            font-weight: 750;
            line-height: 1.15;
        }}

        .cs-module-description {{
            color: {muted};
            font-size: 14px;
            margin-top: 6px;
        }}

        /* ================================================== */
        /* CARDS */
        /* ================================================== */

        .cs-card {{
            background: {surface};
            border: 1px solid {border};
            border-radius: 12px;
            padding: 1.25rem;
            margin-bottom: 1rem;
        }}

        .cs-card-title {{
            color: {text};
            font-size: 18px;
            font-weight: 700;
        }}

        .cs-card-subtitle {{
            color: {muted};
            font-size: 14px;
            line-height: 1.5;
            margin-top: 5px;
        }}

        /* ================================================== */
        /* KPI */
        /* ================================================== */

        .cs-kpi {{
            background: {surface};
            border: 1px solid {border};
            border-radius: 12px;
            padding: 1rem;
            min-height: 95px;
        }}

        .cs-kpi-label {{
            color: {muted};
            font-size: 13px;
        }}

        .cs-kpi-value {{
            color: {text};
            font-size: 27px;
            font-weight: 750;
            margin-top: 6px;
        }}

        /* ================================================== */
        /* BUTTONS */
        /* ================================================== */

        div.stButton > button {{
            border-radius: 8px;
        }}

        /* ================================================== */
        /* FORMS */
        /* ================================================== */

        div[data-testid="stForm"] {{
            border-color: {border};
        }}

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
        "theme": "Dark",
    }

    for key, value in defaults.items():

        if key not in st.session_state:
            st.session_state[key] = value


# ============================================================
# DATABASE
# ============================================================

def get_database() -> dict[str, Any]:
    """
    Load the application database.

    The database is loaded once per Streamlit session.
    """

    database = st.session_state.get(
        "database"
    )

    if not isinstance(
        database,
        dict,
    ):

        database = load_memory()

        if not isinstance(
            database,
            dict,
        ):
            database = {}

        st.session_state.database = database

    return database


# ============================================================
# SIDEBAR BRANDING
# ============================================================

def render_sidebar_logo() -> None:
    """Render the small Creative Studios logo."""

    if LOGO_PATH.exists():

        st.sidebar.image(
            str(LOGO_PATH),
            width=64,
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

    else:

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


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

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

    navigation = [
        "Dashboard",
        "Projects",
        "Documents",
        "Architecture",
        "Engineering",
        "Drawings",
        "MEP",
    ]

    current = st.session_state.get(
        "active_module",
        "Dashboard",
    )

    if current not in navigation:
        current = "Dashboard"

    choice = st.sidebar.radio(
        "Go to",
        navigation,
        index=navigation.index(current),
        key="module_navigation",
        label_visibility="collapsed",
    )

    st.session_state.active_module = choice

    st.sidebar.markdown(
        '<div class="cs-divider"></div>',
        unsafe_allow_html=True,
    )

    render_theme_selector()

    return choice


# ============================================================
# LAZY MODULE IMPORT
# ============================================================

MODULE_IMPORTS = {
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
    "MEP": (
        "modules.mep",
        "render_mep_module",
    ),
}


def load_module_renderer(
    module_name: str,
):
    """
    Import a module only when it is requested.

    This prevents import errors in one module from crashing
    the entire Creative Studios application.
    """

    configuration = MODULE_IMPORTS.get(
        module_name
    )

    if configuration is None:

        raise ImportError(
            f"No renderer is registered for "
            f"'{module_name}'."
        )

    module_path, function_name = configuration

    try:

        module = importlib.import_module(
            module_path
        )

    except Exception as exc:

        raise RuntimeError(
            f"Unable to import {module_path}: "
            f"{type(exc).__name__}: {exc}"
        ) from exc

    renderer = getattr(
        module,
        function_name,
        None,
    )

    if not callable(renderer):

        raise AttributeError(
            f"{module_path} does not expose "
            f"a callable '{function_name}' function."
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

    except Exception as exc:

        st.error(
            f"Unable to load {choice}."
        )

        st.exception(exc)

        st.info(
            "The rest of Creative Studios is still available. "
            "This module can be repaired independently."
        )

        return

    try:

        renderer(
            database
        )

    except Exception as exc:

        st.error(
            f"Unable to render {choice}."
        )

        st.exception(exc)


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    """Run Creative Studios."""

    initialize_session_state()
    initialize_theme()
    inject_theme_css()

    try:

        database = get_database()

    except Exception as exc:

        st.error(
            "Unable to load workspace data."
        )

        st.exception(exc)

        st.stop()

    choice = render_sidebar()

    render_module(
        choice,
        database,
    )


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()