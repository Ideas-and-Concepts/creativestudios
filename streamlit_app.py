"""
Creative Studios
AEC Collaboration Platform

Main Streamlit application.

Authentication has been removed.

Architecture and Engineering manage their own drawings.
There is no standalone Drawings module.
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

ASSETS_DIR = BASE_DIR / "assets"

LOGO_CANDIDATES = [
    ASSETS_DIR / "creative_studios.png",
    ASSETS_DIR / "creative_studios_logo.png",
    ASSETS_DIR / "logo.png",
]

LOGO_PATH: Path | None = None

for candidate in LOGO_CANDIDATES:
    if candidate.exists():
        LOGO_PATH = candidate
        break


st.set_page_config(
    page_title="Creative Studios",
    page_icon=str(LOGO_PATH) if LOGO_PATH else None,
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# APPLICATION CONSTANTS
# ============================================================

APP_NAME = "Creative Studios"
APP_DESCRIPTION = "AEC Collaboration Platform"

NAVIGATION = [
    "Dashboard",
    "Projects",
    "Documents",
    "Architecture",
    "Engineering",
    "MEP",
    "BOQ",
]


# ============================================================
# MODULE REGISTRY
# ============================================================

MODULE_IMPORTS: dict[str, tuple[str, str]] = {
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
    "MEP": (
        "modules.mep",
        "render_mep_module",
    ),
    "BOQ": (
        "modules.boq",
        "render_boq_module",
    ),
}


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
    """Load the application database once per session."""

    database = st.session_state.get(
        "database"
    )

    if isinstance(
        database,
        dict,
    ):
        return database

    try:

        database = load_memory()

    except Exception as exc:

        st.error(
            "Unable to load the Creative Studios database."
        )

        st.exception(exc)

        database = {}

    if not isinstance(
        database,
        dict,
    ):
        database = {}

    st.session_state.database = database

    return database


# ============================================================
# GLOBAL CSS
# ============================================================

def inject_css() -> None:
    """Apply application-wide styling."""

    st.markdown(
        """
        <style>

        /* ==================================================
           MAIN APPLICATION
           ================================================== */

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }


        /* ==================================================
           SIDEBAR
           ================================================== */

        [data-testid="stSidebar"] {
            min-width: 250px;
            max-width: 250px;
        }

        [data-testid="stSidebar"] > div:first-child {
            padding-top: 1rem;
        }


        /* ==================================================
           SIDEBAR BRANDING
           ================================================== */

        .cs-sidebar-brand {
            width: 100%;
            text-align: center !important;
            margin: 0;
            padding: 0.25rem 0 1rem 0;
        }

        .cs-sidebar-title {
            width: 100%;
            text-align: center !important;
            font-size: 18px;
            font-weight: 750;
            line-height: 1.25;
            margin: 0.5rem 0 0 0;
        }

        .cs-sidebar-subtitle {
            width: 100%;
            text-align: center !important;
            font-size: 12px;
            line-height: 1.4;
            margin-top: 0.25rem;
            opacity: 0.68;
        }

        .cs-sidebar-divider {
            width: 100%;
            height: 1px;
            margin: 0.75rem 0 1rem 0;
            background: rgba(128, 128, 128, 0.20);
        }

        .cs-sidebar-section {
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            opacity: 0.60;
            margin: 0.5rem 0 0.5rem 0;
        }


        /* ==================================================
           SIDEBAR NAVIGATION
           ================================================== */

        [data-testid="stSidebar"] div[role="radiogroup"] {
            gap: 0.25rem;
        }

        [data-testid="stSidebar"] div[role="radiogroup"] label {
            border-radius: 8px;
            padding: 0.25rem 0.5rem;
        }

        [data-testid="stSidebar"] div[role="radiogroup"] label:hover {
            background: rgba(128, 128, 128, 0.10);
        }


        /* ==================================================
           BUTTONS
           ================================================== */

        div.stButton > button {
            border-radius: 8px;
            min-height: 2.5rem;
            font-weight: 600;
        }


        /* ==================================================
           MOBILE
           ================================================== */

        @media (max-width: 768px) {

            [data-testid="stSidebar"] {
                min-width: 230px;
                max-width: 230px;
            }

        }

        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# SIDEBAR BRANDING
# ============================================================

def render_sidebar_brand() -> None:
    """
    Render centered Creative Studios branding.

    The actual logo is rendered with st.image() rather than
    an HTML img tag because this is more reliable on
    Streamlit Cloud.
    """

    st.sidebar.markdown(
        '<div class="cs-sidebar-brand">',
        unsafe_allow_html=True,
    )

    if LOGO_PATH is not None:

        # Three-column layout centers the real Streamlit image.
        left, center, right = st.sidebar.columns(
            [1, 2, 1]
        )

        with center:

            st.image(
                str(LOGO_PATH),
                width=72,
            )

    else:

        # Fallback if the asset is unavailable.
        left, center, right = st.sidebar.columns(
            [1, 2, 1]
        )

        with center:

            st.markdown(
                """
                <div style="
                    width:72px;
                    height:72px;
                    border-radius:14px;
                    border:1px solid rgba(128,128,128,0.25);
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    font-size:24px;
                    font-weight:800;
                    margin:auto;
                ">
                    CS
                </div>
                """,
                unsafe_allow_html=True,
            )

    # These are deliberately outside the image container so
    # Streamlit Cloud renders them reliably.
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
# SIDEBAR NAVIGATION
# ============================================================

def render_sidebar() -> str:
    """Render the application sidebar navigation."""

    render_sidebar_brand()

    st.sidebar.markdown(
        '<div class="cs-sidebar-divider"></div>',
        unsafe_allow_html=True,
    )

    st.sidebar.markdown(
        '<div class="cs-sidebar-section">Navigation</div>',
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
# MODULE LOADER
# ============================================================

def load_module_renderer(
    module_name: str,
) -> Callable[[dict[str, Any]], None]:
    """
    Dynamically load a module renderer.

    Modules are imported only when selected.
    """

    if module_name not in MODULE_IMPORTS:

        raise KeyError(
            f"Unknown module: {module_name}"
        )

    module_path, function_name = MODULE_IMPORTS[
        module_name
    ]

    try:

        module = importlib.import_module(
            module_path
        )

    except Exception as exc:

        raise RuntimeError(
            f"Unable to import the {module_name} module "
            f"from '{module_path}'."
        ) from exc

    renderer = getattr(
        module,
        function_name,
        None,
    )

    if not callable(renderer):

        raise AttributeError(
            f"The module '{module_path}' does not "
            f"provide a callable '{function_name}' function."
        )

    return renderer


# ============================================================
# MODULE ERROR DISPLAY
# ============================================================

def render_module_error(
    module_name: str,
    exc: Exception,
) -> None:
    """Display a readable module error."""

    st.error(
        f"Unable to load the {module_name} module."
    )

    with st.expander(
        "Technical details",
        expanded=True,
    ):

        st.exception(exc)


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

        render_module_error(
            choice,
            exc,
        )


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