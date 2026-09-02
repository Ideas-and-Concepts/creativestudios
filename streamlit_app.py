"""Creative Studios legacy Streamlit workspace.

The production application is the Next.js PWA. This Streamlit application is
kept as a lightweight legacy/admin workspace for the existing Python modules.
It intentionally does not store Neon credentials or attempt to manage the
production PostgreSQL schema.
"""
from __future__ import annotations

import html
import importlib
import os
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

import streamlit as st

from modules.database import load_memory

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
DEFAULT_PWA_URL = "https://creativestudios-rho.vercel.app/"


def get_pwa_url() -> str:
    """Return a valid external PWA URL from Streamlit configuration."""
    configured_url = os.getenv("CREATIVE_STUDIOS_PWA_URL", "").strip()
    candidate = configured_url or DEFAULT_PWA_URL
    parsed = urlparse(candidate)

    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return candidate

    return DEFAULT_PWA_URL


PWA_URL = get_pwa_url()

LOGO_PATH = next(
    (
        path
        for path in (
            ASSETS_DIR / "creative_studios.png",
            ASSETS_DIR / "creative_studios_logo.png",
            ASSETS_DIR / "logo.png",
        )
        if path.exists()
    ),
    None,
)

st.set_page_config(
    page_title="Creative Studios",
    page_icon=str(LOGO_PATH) if LOGO_PATH else "CS",
    layout="wide",
    initial_sidebar_state="expanded",
)

NAVIGATION = [
    "Dashboard",
    "Projects",
    "Documents",
    "Architecture",
    "Engineering",
    "Drawings",
    "MEP",
    "BOQ",
    "Procurement",
    "Construction",
    "Cost Control",
    "Tasks",
    "RFIs",
    "Approvals",
    "Reports",
    "Settings",
]

MODULE_IMPORTS: dict[str, tuple[str, str]] = {
    "Dashboard": ("modules.dashboard", "render_dashboard"),
    "Projects": ("modules.projects", "render_projects_module"),
    "Documents": ("modules.documents", "render_documents_module"),
    "Architecture": ("modules.architecture", "render_architecture_module"),
    "Engineering": ("modules.engineering", "render_engineering_module"),
    "Drawings": ("modules.drawings", "render_drawings_module"),
    "MEP": ("modules.mep", "render_mep_module"),
    "BOQ": ("modules.boq", "render_boq_module"),
    "Construction": ("modules.construction", "render_construction_module"),
}

PRODUCTION_ONLY_MODULES = {
    "Procurement",
    "Cost Control",
    "Tasks",
    "RFIs",
    "Approvals",
    "Reports",
    "Settings",
}


def initialize_session_state() -> None:
    """Initialize Streamlit state before any state-dependent rendering."""
    if "active_module" not in st.session_state:
        st.session_state.active_module = "Dashboard"

    if "navigation" not in st.session_state:
        st.session_state.navigation = st.session_state.active_module

    if "database" not in st.session_state or not isinstance(
        st.session_state.database, dict
    ):
        st.session_state.database = load_memory()


def inject_css() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 1280px;
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }

        [data-testid="stSidebar"] {
            min-width: 250px;
            max-width: 250px;
        }

        .cs-sidebar-title {
            font-size: 18px;
            font-weight: 700;
            text-align: center;
            margin-top: .4rem;
        }

        .cs-sidebar-subtitle {
            font-size: 11px;
            opacity: .7;
            text-align: center;
            margin-top: .1rem;
        }

        .cs-sidebar-divider {
            height: 1px;
            background: rgba(127,127,127,.25);
            margin: 1rem 0 .8rem;
        }

        .cs-sidebar-section {
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: .08em;
            opacity: .65;
            text-align: center;
            margin: .8rem 0 .5rem;
        }

        .cs-sidebar-status {
            font-size: 11px;
            text-align: center;
            opacity: .72;
            margin-top: .7rem;
        }

        .cs-pwa-link {
            display: block;
            width: 100%;
            box-sizing: border-box;
            text-align: center;
            text-decoration: none !important;
            font-weight: 600;
            padding: .55rem .75rem;
            border: 1px solid rgba(127,127,127,.35);
            border-radius: 8px;
            margin: .4rem 0 .8rem;
        }

        .cs-pwa-link:hover {
            background: rgba(127,127,127,.12);
        }

        .cs-footer {
            text-align: center;
            opacity: .5;
            font-size: 11px;
            padding-top: 2rem;
        }

        [data-testid="stSidebar"] div[role="radiogroup"] label {
            width: 100%;
            text-align: center;
            border-radius: 8px;
            padding: .3rem .6rem;
        }

        [data-testid="stSidebar"] div[role="radiogroup"] label:hover {
            background: rgba(127,127,127,.12);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_pwa_link() -> None:
    """Render a browser-native external link to the production PWA."""
    safe_url = html.escape(PWA_URL, quote=True)
    st.sidebar.markdown(
        f'<a class="cs-pwa-link" href="{safe_url}" target="_blank" '
        'rel="noopener noreferrer">Open Production PWA</a>',
        unsafe_allow_html=True,
    )


def get_database() -> dict[str, Any]:
    """Return the legacy in-memory JSON-backed workspace database."""
    database = st.session_state.get("database")
    if not isinstance(database, dict):
        database = load_memory()
        st.session_state.database = database
    return database


def render_sidebar() -> str:
    """Render navigation and the link to the production PWA."""
    if LOGO_PATH:
        st.sidebar.image(str(LOGO_PATH), width=56)

    st.sidebar.markdown(
        '<div class="cs-sidebar-title">Creative Studios</div>',
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        '<div class="cs-sidebar-subtitle">AEC Collaboration Platform</div>',
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        '<div class="cs-sidebar-divider"></div>',
        unsafe_allow_html=True,
    )

    render_pwa_link()

    st.sidebar.markdown(
        '<div class="cs-sidebar-section">Workspace</div>',
        unsafe_allow_html=True,
    )

    current = st.session_state.get("active_module", "Dashboard")
    if current not in NAVIGATION:
        current = "Dashboard"
        st.session_state.active_module = current

    if st.session_state.get("navigation") not in NAVIGATION:
        st.session_state.navigation = current

    choice = st.sidebar.radio(
        "Go to",
        NAVIGATION,
        key="navigation",
        label_visibility="collapsed",
    )
    st.session_state.active_module = choice

    st.sidebar.markdown(
        '<div class="cs-sidebar-divider"></div>',
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        '<div class="cs-sidebar-status">'
        "Legacy Python workspace<br>"
        "Production data layer: Neon PostgreSQL"
        "</div>",
        unsafe_allow_html=True,
    )

    return choice


def load_module_renderer(
    name: str,
) -> Callable[[dict[str, Any]], Any] | None:
    """Load a Streamlit renderer when one exists."""
    if name not in MODULE_IMPORTS:
        return None

    module_path, function_name = MODULE_IMPORTS[name]
    module = importlib.import_module(module_path)
    renderer = getattr(module, function_name, None)

    if not callable(renderer):
        raise TypeError(
            f"{module_path}.{function_name} is missing or is not callable."
        )

    return renderer


def render_production_only_module(name: str) -> None:
    """Explain that the module is implemented in the production PWA."""
    st.title(name)
    st.caption("Production module in the Creative Studios Next.js workspace.")

    st.info(
        f"The {name} workspace is part of the production application. "
        "This legacy Streamlit shell does not duplicate the production module."
    )

    safe_url = html.escape(PWA_URL, quote=True)
    st.markdown(
        f'<a class="cs-pwa-link" href="{safe_url}" target="_blank" '
        'rel="noopener noreferrer">Open Production PWA</a>',
        unsafe_allow_html=True,
    )

    st.markdown("### Production architecture")
    st.write("Next.js PWA → API routes → Drizzle ORM → Neon PostgreSQL")


def render_module(
    name: str,
    database: dict[str, Any],
) -> None:
    """Render a Python module safely, or route to its production PWA page."""
    if name in PRODUCTION_ONLY_MODULES:
        render_production_only_module(name)
        return

    try:
        renderer = load_module_renderer(name)
        if renderer is None:
            st.warning(f"The {name} Streamlit renderer is not registered.")
            return
        renderer(database)
    except Exception as exc:
        st.error(f"Unable to render the {name} module.")
        with st.expander("Technical details", expanded=False):
            st.exception(exc)


def main() -> None:
    initialize_session_state()
    inject_css()

    database = get_database()
    choice = render_sidebar()
    render_module(choice, database)

    st.markdown(
        '<div class="cs-footer">'
        "Creative Studios · AEC Collaboration Platform · "
        "Legacy Streamlit Workspace"
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
