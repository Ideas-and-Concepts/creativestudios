"""Creative Studios AEC Collaboration Platform."""
from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any, Callable

import streamlit as st

from modules.database import load_memory

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
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
    "Construction",
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


def initialize_session_state() -> None:
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


def get_database() -> dict[str, Any]:
    database = st.session_state.get("database")
    if not isinstance(database, dict):
        database = load_memory()
        st.session_state.database = database
    return database


def render_sidebar() -> str:
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
    st.sidebar.markdown(
        '<div class="cs-sidebar-section">Navigation</div>',
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
    return choice


def load_module_renderer(name: str) -> Callable[[dict[str, Any]], Any]:
    if name not in MODULE_IMPORTS:
        raise KeyError(f"Unknown module: {name}")

    module_path, function_name = MODULE_IMPORTS[name]
    module = importlib.import_module(module_path)
    renderer = getattr(module, function_name, None)
    if not callable(renderer):
        raise TypeError(
            f"{module_path}.{function_name} is missing or is not callable."
        )
    return renderer


def render_module(name: str, database: dict[str, Any]) -> None:
    try:
        renderer = load_module_renderer(name)
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
        '<div style="text-align:center;opacity:.5;font-size:11px;padding-top:2rem;">'
        "Creative Studios · AEC Collaboration Platform"
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
