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
# CSS
# ============================================================

def inject_css() -> None:

    st.markdown(
        """
        <style>

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }

        [data-testid="stAppViewContainer"] {
            background: #F8FAFC;
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stSidebar"] {
            background: #FFFFFF;
            border-right: 1px solid #E2E8F0;
        }

        [data-testid="stSidebar"] > div:first-child {
            padding-top: 1rem;
        }

        .cs-sidebar-brand {
            width: 100%;
            text-align: center;
            margin: 0;
            padding: 0 0 1rem 0;
        }

        [data-testid="stSidebar"]
        [data-testid="stImage"] {
            width: 100% !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            text-align: center !important;
            margin: 0 auto !important;
            padding: 0 !important;
        }

        [data-testid="stSidebar"]
        [data-testid="stImage"] img {
            display: block !important;
            margin-left: auto !important;
            margin-right: auto !important;
            object-fit: contain !important;
        }

        .cs-sidebar-title {
            width: 100%;
            text-align: center !important;
            font-size: 17px;
            font-weight: 700;
            line-height: 1.2;
            margin: 7px 0 0 0;
            color: #0F172A;
        }

        .cs-sidebar-subtitle {
            width: 100%;
            text-align: center !important;
            font-size: 12px;
            line-height: 1.4;
            margin: 4px 0 0 0;
            color: #64748B;
        }

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
            margin-bottom: 0.5rem;
        }

        [data-testid="stSidebar"]
        div[role="radiogroup"] {
            width: 100%;
            gap: 0.2rem;
        }

        [data-testid="stSidebar"]
        div[role="radiogroup"] label {
            width: 100%;
            box-sizing: border-box;
            border-radius: 8px;
            padding: 0.5rem 0.65rem;
            cursor: pointer;
        }

        [data-testid="stSidebar"]
        div[role="radiogroup"] label:hover {
            background: #F1F5F9;
        }

        div.stButton > button {
            min-height: 42px;
            border-radius: 8px;
            font-weight: 600;
        }

        div[data-testid="stFormSubmitButton"] button {
            min-height: 42px;
            border-radius: 8px;
            font-weight: 600;
        }

        [data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 0.75rem;
        }

        [data-testid="stExpander"] {
            border-radius: 10px;
            border: 1px solid #E2E8F0;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# SESSION STATE
# ============================================================

def initialize_session_state() -> None:

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

    st.sidebar.markdown(
        '<div class="cs-sidebar-brand">',
        unsafe_allow_html=True,
    )

    if LOGO_PATH.exists():

        st.sidebar.image(
            str(LOGO_PATH),
            width=72,
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
            f"{module_name} module."
        ) from exc

    renderer = getattr(
        module,
        function_name,
        None,
    )

    if not callable(renderer):

        raise AttributeError(
            f"{module_path} does not contain "
            f"a callable {function_name}."
        )

    return renderer


# ============================================================
# ROUTER
# ============================================================

def render_module(
    choice: str,
    database: dict[str, Any],
) -> None:

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