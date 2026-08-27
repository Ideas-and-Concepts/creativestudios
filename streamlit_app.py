"""
Creative Studios
AEC Collaboration Platform

Main Streamlit application.

Authentication has been removed.

Top-level modules:

    Dashboard
    Projects
    Documents
    Architecture
    Engineering
    MEP
    BOQ

Drawings is intentionally NOT a standalone module.

Architectural drawings are handled by Architecture.

Engineering drawings are handled by Engineering.
"""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any, Callable

import streamlit as st

from modules.database import load_memory


# ============================================================
# APPLICATION PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"


# ============================================================
# LOGO
# ============================================================

def find_logo() -> Path | None:
    """Find the Creative Studios logo."""

    candidates = [
        ASSETS_DIR / "creative_studios.png",
        ASSETS_DIR / "creative_studios_logo.png",
        ASSETS_DIR / "logo.png",
        ASSETS_DIR / "creative_studios.jpg",
        ASSETS_DIR / "creative_studios.jpeg",
        ASSETS_DIR / "logo.jpg",
        ASSETS_DIR / "logo.jpeg",
    ]

    for path in candidates:

        if path.exists() and path.is_file():
            return path

    return None


LOGO_PATH = find_logo()


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Creative Studios",
    page_icon=str(LOGO_PATH) if LOGO_PATH else "CS",
    layout="wide",
    initial_sidebar_state="expanded",
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
# GLOBAL CSS
# ============================================================

def inject_css() -> None:
    """Apply global application styling."""

    st.markdown(
        """
        <style>

        /* ==================================================
           MAIN CONTENT
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
            padding-top: 0.75rem;
        }


        /* ==================================================
           SIDEBAR BRANDING
           ================================================== */

        .cs-sidebar-brand {
            width: 100%;
            text-align: center;
            padding: 0;
            margin: 0;
        }

        .cs-sidebar-title {
            width: 100%;
            text-align: center;
            font-size: 17px;
            font-weight: 700;
            line-height: 1.25;
            margin: 0.35rem 0 0 0;
            padding: 0;
        }

        .cs-sidebar-subtitle {
            width: 100%;
            text-align: center;
            font-size: 11px;
            line-height: 1.35;
            margin: 0.15rem 0 0 0;
            padding: 0;
            opacity: 0.65;
        }


        /* ==================================================
           SIDEBAR DIVIDER
           ================================================== */

        .cs-sidebar-divider {
            width: 100%;
            height: 1px;
            margin: 0.75rem 0 0.9rem 0;
            background: rgba(128, 128, 128, 0.20);
        }


        /* ==================================================
           NAVIGATION LABEL
           ================================================== */

        .cs-sidebar-section {
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            opacity: 0.60;
            margin: 0.5rem 0 0.45rem 0;
        }


        /* ==================================================
           RADIO NAVIGATION
           ================================================== */

        [data-testid="stSidebar"] div[role="radiogroup"] {
            gap: 0.2rem;
        }

        [data-testid="stSidebar"]
        div[role="radiogroup"]
        label {
            border-radius: 8px;
            padding: 0.2rem 0.45rem;
        }

        [data-testid="stSidebar"]
        div[role="radiogroup"]
        label:hover {
            background: rgba(128, 128, 128, 0.10);
        }


        /* ==================================================
           BUTTONS
           ================================================== */

        div.stButton > button {
            border-radius: 8px;
            min-height: 2.4rem;
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

            .cs-sidebar-title {
                font-size: 16px;
            }

            .cs-sidebar-subtitle {
                font-size: 10px;
            }
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# SIDEBAR BRAND
# ============================================================

def render_sidebar_brand() -> None:
    """
    Render the centered sidebar logo and branding.

    The logo uses Streamlit's native image component.
    No HTML <img> element is used.
    """

    # --------------------------------------------------------
    # LOGO
    # --------------------------------------------------------

    if LOGO_PATH is not None:

        # Equal-width columns provide a reliable centered
        # position on Streamlit Cloud.

        left, center, right = st.sidebar.columns(
            [1, 1, 1]
        )

        with center:

            st.image(
                str(LOGO_PATH),
                width=56,
            )

    else:

        # ----------------------------------------------------
        # Fallback logo
        # ----------------------------------------------------

        left, center, right = st.sidebar.columns(
            [1, 1, 1]
        )

        with center:

            st.markdown(
                """
                <div style="
                    width:56px;
                    height:56px;
                    margin:0 auto;
                    border-radius:12px;
                    border:1px solid rgba(128,128,128,0.25);
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    font-size:20px;
                    font-weight:800;
                    box-sizing:border-box;
                ">
                    CS
                </div>
                """,
                unsafe_allow_html=True,
            )

    # --------------------------------------------------------
    # BRANDING TEXT
    # --------------------------------------------------------

    st.sidebar.markdown(
        """
        <div class="cs-sidebar-title">
            Creative Studios
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown(
        """
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
    """Render the application sidebar."""

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
# DATABASE
# ============================================================

def get_database() -> dict[str, Any]:
    """Load the database safely."""

    database = st.session_state.get(
        "database"
    )

    if isinstance(database, dict):
        return database

    try:

        database = load_memory()

    except Exception as exc:

        st.error(
            "Unable to load the Creative Studios database."
        )

        with st.expander(
            "Database error details"
        ):

            st.exception(exc)

        database = {}

    if not isinstance(database, dict):

        database = {}

    st.session_state.database = database

    return database


# ============================================================
# MODULE LOADER
# ============================================================

def load_module_renderer(
    module_name: str,
) -> Callable[[dict[str, Any]], Any]:
    """Load the selected module dynamically."""

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
            f"Module '{module_path}' does not contain "
            f"a callable '{function_name}' function."
        )

    return renderer


# ============================================================
# MODULE ERROR
# ============================================================

def render_module_error(
    module_name: str,
    exc: Exception,
) -> None:
    """Display a controlled module error."""

    st.error(
        f"Unable to load the {module_name} module."
    )

    st.caption(
        "The Creative Studios application is still running."
    )

    with st.expander(
        "Technical details"
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
# FOOTER
# ============================================================

def render_footer() -> None:
    """Render the application footer."""

    st.markdown(
        """
        <div style="
            text-align:center;
            opacity:0.45;
            font-size:11px;
            padding-top:2rem;
        ">
            Creative Studios · AEC Collaboration Platform
        </div>
        """,
        unsafe_allow_html=True,
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

    render_footer()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()