"""
Creative Studios
AEC Collaboration Platform

Main Streamlit application.

Authentication has been removed.
Modules are imported only when selected.
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

LOGO_PATH = BASE_DIR / "assets" / "creative_studios.png"

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
    """Render the dark/light theme selector."""

    current_theme = st.session_state.get(
        "theme",
        "Dark",
    )

    selected_theme = st.sidebar.selectbox(
        "Theme",
        ["Dark", "Light"],
        index=0 if current_theme == "Dark" else 1,
        key="theme_selector",
    )

    if selected_theme != current_theme:
        st.session_state.theme = selected_theme
        st.rerun()


def inject_theme_css() -> None:
    """Apply Creative Studios theme styling."""

    theme = st.session_state.get(
        "theme",
        "Dark",
    )

    if theme == "Light":

        background = "#F8FAFC"
        surface = "#FFFFFF"
        surface_alt = "#F1F5F9"
        input_background = "#FFFFFF"
        text = "#0F172A"
        muted = "#64748B"
        border = "#E2E8F0"
        accent = "#2563EB"
        accent_hover = "#1D4ED8"
        selected = "#DBEAFE"

    else:

        # Professional high-contrast dark palette.
        background = "#111827"
        surface = "#1E293B"
        surface_alt = "#273449"
        input_background = "#273449"
        text = "#F8FAFC"
        muted = "#CBD5E1"
        border = "#475569"
        accent = "#60A5FA"
        accent_hover = "#93C5FD"
        selected = "#1E3A5F"

    st.markdown(
        f"""
        <style>

        /* ==================================================
           APPLICATION
           ================================================== */

        [data-testid="stAppViewContainer"] {{
            background: {background};
            color: {text};
        }}

        [data-testid="stAppViewContainer"] .main {{
            background: {background};
        }}

        [data-testid="stHeader"] {{
            background: transparent;
        }}

        .block-container {{
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }}

        /* ==================================================
           GLOBAL TEXT
           ================================================== */

        html,
        body,
        [class*="css"],
        .stMarkdown,
        .stText {{
            color: {text};
        }}

        p,
        span,
        label,
        div {{
            color: inherit;
        }}

        small {{
            color: {muted};
        }}

        /* ==================================================
           SIDEBAR
           ================================================== */

        [data-testid="stSidebar"] {{
            background: {surface};
            border-right: 1px solid {border};
        }}

        [data-testid="stSidebar"] > div:first-child {{
            background: {surface};
        }}

        [data-testid="stSidebar"] * {{
            color: {text};
        }}

        .cs-sidebar-brand {{
            text-align: center;
            padding: 0.5rem 0 1rem 0;
        }}

        .cs-sidebar-title {{
            color: {text} !important;
            font-size: 17px;
            font-weight: 700;
            line-height: 1.2;
            text-align: center;
        }}

        .cs-sidebar-subtitle {{
            color: {muted} !important;
            font-size: 12px;
            margin-top: 4px;
            text-align: center;
        }}

        .cs-divider {{
            height: 1px;
            background: {border};
            margin: 0.75rem 0 1rem 0;
        }}

        .cs-section-label {{
            color: {muted} !important;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
        }}

        /* ==================================================
           SIDEBAR RADIO NAVIGATION
           ================================================== */

        [data-testid="stSidebar"] [role="radiogroup"] {{
            gap: 4px;
        }}

        [data-testid="stSidebar"] [role="radio"] {{
            background: transparent;
            border-radius: 8px;
            padding: 7px 10px;
            transition: background 0.15s ease;
        }}

        [data-testid="stSidebar"] [role="radio"]:hover {{
            background: {surface_alt};
        }}

        [data-testid="stSidebar"] [role="radio"][aria-checked="true"] {{
            background: {selected};
            border: 1px solid {accent};
        }}

        /* ==================================================
           HEADINGS
           ================================================== */

        h1,
        h2,
        h3,
        h4,
        h5,
        h6 {{
            color: {text} !important;
        }}

        .cs-module-title {{
            color: {text} !important;
            font-size: 30px;
            font-weight: 750;
            line-height: 1.15;
        }}

        .cs-module-description {{
            color: {muted} !important;
            font-size: 14px;
            margin-top: 6px;
        }}

        /* ==================================================
           CARDS
           ================================================== */

        .cs-card {{
            background: {surface};
            border: 1px solid {border};
            border-radius: 12px;
            padding: 1.25rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
        }}

        .cs-card-title {{
            color: {text} !important;
            font-size: 18px;
            font-weight: 700;
        }}

        .cs-card-subtitle {{
            color: {muted} !important;
            font-size: 14px;
            line-height: 1.5;
            margin-top: 5px;
        }}

        /* ==================================================
           KPI CARDS
           ================================================== */

        .cs-kpi {{
            background: {surface};
            border: 1px solid {border};
            border-radius: 12px;
            padding: 1rem;
            min-height: 95px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.10);
        }}

        .cs-kpi-label {{
            color: {muted} !important;
            font-size: 13px;
        }}

        .cs-kpi-value {{
            color: {text} !important;
            font-size: 27px;
            font-weight: 750;
            margin-top: 6px;
        }}

        /* ==================================================
           BUTTONS
           ================================================== */

        div.stButton > button {{
            border-radius: 8px;
            border: 1px solid {border};
            background: {surface_alt};
            color: {text};
            min-height: 40px;
            font-weight: 600;
        }}

        div.stButton > button:hover {{
            border-color: {accent};
            color: {accent_hover};
            background: {surface};
        }}

        div.stButton > button:focus {{
            border-color: {accent};
            box-shadow: 0 0 0 2px rgba(96, 165, 250, 0.20);
        }}

        /* ==================================================
           INPUTS
           ================================================== */

        input,
        textarea,
        [data-baseweb="select"] > div {{
            background: {input_background} !important;
            color: {text} !important;
            border-color: {border} !important;
        }}

        input::placeholder,
        textarea::placeholder {{
            color: {muted} !important;
            opacity: 1;
        }}

        [data-baseweb="input"] {{
            background: {input_background};
            border-color: {border};
        }}

        [data-baseweb="input"]:focus-within {{
            border-color: {accent};
        }}

        /* ==================================================
           SELECTBOX / DROPDOWN
           ================================================== */

        [data-baseweb="popover"] {{
            background: {surface} !important;
            border: 1px solid {border};
        }}

        [data-baseweb="menu"] {{
            background: {surface} !important;
        }}

        [role="option"] {{
            background: {surface} !important;
            color: {text} !important;
        }}

        [role="option"]:hover {{
            background: {surface_alt} !important;
        }}

        /* ==================================================
           TABS
           ================================================== */

        button[data-baseweb="tab"] {{
            color: {muted} !important;
        }}

        button[data-baseweb="tab"][aria-selected="true"] {{
            color: {text} !important;
        }}

        [data-baseweb="tab-highlight"] {{
            background: {accent} !important;
        }}

        /* ==================================================
           EXPANDERS
           ================================================== */

        [data-testid="stExpander"] {{
            background: {surface};
            border: 1px solid {border};
            border-radius: 10px;
        }}

        [data-testid="stExpander"] summary {{
            color: {text} !important;
        }}

        [data-testid="stExpander"] summary:hover {{
            background: {surface_alt};
        }}

        /* ==================================================
           DATAFRAMES / TABLES
           ================================================== */

        [data-testid="stDataFrame"] {{
            border: 1px solid {border};
            border-radius: 8px;
        }}

        /* ==================================================
           METRICS
           ================================================== */

        [data-testid="stMetric"] {{
            background: {surface};
            border: 1px solid {border};
            border-radius: 10px;
            padding: 12px;
        }}

        [data-testid="stMetricLabel"] {{
            color: {muted} !important;
        }}

        [data-testid="stMetricValue"] {{
            color: {text} !important;
        }}

        /* ==================================================
           CHECKBOXES / RADIO BUTTONS
           ================================================== */

        [data-testid="stCheckbox"] label,
        [data-testid="stRadio"] label {{
            color: {text} !important;
        }}

        /* ==================================================
           FORM CONTAINERS
           ================================================== */

        [data-testid="stForm"] {{
            background: {surface};
            border: 1px solid {border};
            border-radius: 12px;
            padding: 1rem;
        }}

        /* ==================================================
           ALERTS
           ================================================== */

        [data-testid="stAlert"] {{
            border-radius: 9px;
            border: 1px solid {border};
        }}

        /* ==================================================
           DIVIDERS
           ================================================== */

        hr {{
            border-color: {border} !important;
        }}

        /* ==================================================
           LINKS
           ================================================== */

        a {{
            color: {accent} !important;
        }}

        a:hover {{
            color: {accent_hover} !important;
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
    """Load the application database once per session."""

    database = st.session_state.get("database")

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
    """Render the Creative Studios sidebar branding."""

    st.sidebar.markdown(
        '<div class="cs-sidebar-brand">',
        unsafe_allow_html=True,
    )

    if LOGO_PATH.exists():

        try:

            st.sidebar.image(
                str(LOGO_PATH),
                width=64,
            )

        except Exception:
            pass

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
    """Render application navigation."""

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
        "BOQ",
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
) -> Callable[[dict[str, Any]], None]:
    """Load a module renderer dynamically."""

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
            f"Unable to load the {module_name} "
            f"module from '{module_path}': {exc}"
        ) from exc

    renderer = getattr(
        module,
        function_name,
        None,
    )

    if not callable(renderer):

        raise AttributeError(
            f"The module '{module_path}' does not "
            f"contain a callable '{function_name}' "
            f"function."
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
    """Run Creative Studios."""

    initialize_session_state()

    initialize_theme()

    inject_theme_css()

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