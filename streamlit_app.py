"""Creative Studios Streamlit workspace.

This remains the Streamlit-compatible workspace while the Next.js PWA is the
primary production interface. Both can use the same Neon-backed workspace
state when DATABASE_URL is configured.
"""
from __future__ import annotations

import importlib
import os
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

import streamlit as st

from modules.database import database_backend, load_memory

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
DEFAULT_PWA_URL = "https://creativestudios-app.vercel.app/"
AI_PWA_URL = "https://creativestudios-ai.vercel.app/"

NAVIGATION = [
    "Dashboard", "Projects", "Documents", "Architecture", "Engineering",
    "Drawings", "MEP", "BOQ", "Procurement", "Construction", "Cost Control",
    "Tasks", "RFIs", "Approvals", "Reports", "Settings",
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
    "Procurement": ("modules.procurement", "render_procurement_module"),
    "Construction": ("modules.construction", "render_construction_module"),
    "Cost Control": ("modules.cost_control", "render_cost_control_module"),
    "Tasks": ("modules.tasks", "render_tasks_module"),
    "RFIs": ("modules.rfis", "render_rfis_module"),
    "Approvals": ("modules.approvals", "render_approvals_module"),
    "Reports": ("modules.reports", "render_reports_module"),
    "Settings": ("modules.settings", "render_settings_module"),
}

LOGO_PATH = next(
    (path for path in (
        ASSETS_DIR / "creative_studios.png",
        ASSETS_DIR / "creative_studios_logo.png",
        ASSETS_DIR / "logo.png",
    ) if path.exists()),
    None,
)

st.set_page_config(
    page_title="Creative Studios",
    page_icon=str(LOGO_PATH) if LOGO_PATH else "CS",
    layout="wide",
    initial_sidebar_state="expanded",
)


def get_pwa_url() -> str:
    candidate = os.getenv("CREATIVE_STUDIOS_PWA_URL", "").strip() or DEFAULT_PWA_URL
    parsed = urlparse(candidate)
    return candidate if parsed.scheme in {"http", "https"} and parsed.netloc else DEFAULT_PWA_URL


PWA_URL = get_pwa_url()


def initialize_session_state() -> None:
    if "active_module" not in st.session_state:
        st.session_state.active_module = "Dashboard"
    if "navigation" not in st.session_state:
        st.session_state.navigation = st.session_state.active_module
    if "database" not in st.session_state or not isinstance(st.session_state.database, dict):
        st.session_state.database = load_memory()


def inject_css() -> None:
    st.markdown(
        """
        <style>
        .block-container { max-width: 1320px; padding-top: 1.2rem; padding-bottom: 3rem; }
        [data-testid="stSidebar"] { min-width: 255px; max-width: 255px; }
        .cs-brand { text-align:center; }
        .cs-brand-title { font-size:18px; font-weight:700; margin-top:.35rem; }
        .cs-brand-subtitle { font-size:11px; opacity:.68; margin-top:.1rem; }
        .cs-divider { height:1px; background:rgba(127,127,127,.24); margin:1rem 0; }
        .cs-section { font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:.08em; opacity:.62; margin:.7rem 0 .45rem; }
        .cs-sidebar-note { font-size:11px; text-align:center; opacity:.62; line-height:1.5; margin-top:.7rem; }
        .cs-pwa-link { display:block; text-decoration:none !important; padding:.55rem .7rem; margin:.3rem 0; border:1px solid rgba(127,127,127,.3); border-radius:8px; color:inherit !important; font-size:13px; text-align:center; }
        .cs-pwa-link.primary { background:rgba(127,127,127,.12); font-weight:650; }
        .cs-pwa-link:hover { background:rgba(127,127,127,.16); }
        .cs-footer { text-align:center; opacity:.48; font-size:11px; padding-top:2rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_pwa_links() -> None:
    st.sidebar.markdown(
        f'<a class="cs-pwa-link primary" href="{PWA_URL}" target="_blank" rel="noopener noreferrer">Open Production PWA</a>',
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        f'<a class="cs-pwa-link" href="{AI_PWA_URL}" target="_blank" rel="noopener noreferrer">Open Creative Studios AI</a>',
        unsafe_allow_html=True,
    )


def get_database(*, reload: bool = False) -> dict[str, Any]:
    if reload or not isinstance(st.session_state.get("database"), dict):
        st.session_state.database = load_memory()
    return st.session_state.database


def render_sidebar() -> str:
    if LOGO_PATH:
        st.sidebar.image(str(LOGO_PATH), width=54)
    st.sidebar.markdown(
        '<div class="cs-brand"><div class="cs-brand-title">Creative Studios</div><div class="cs-brand-subtitle">AEC Collaboration Platform</div></div>',
        unsafe_allow_html=True,
    )
    st.sidebar.markdown('<div class="cs-divider"></div>', unsafe_allow_html=True)
    render_pwa_links()
    st.sidebar.markdown('<div class="cs-divider"></div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="cs-section">Workspace</div>', unsafe_allow_html=True)

    current = st.session_state.get("active_module", "Dashboard")
    if current not in NAVIGATION:
        current = "Dashboard"
    st.session_state.active_module = current
    st.session_state.navigation = current

    choice = st.sidebar.radio("Workspace", NAVIGATION, key="navigation", label_visibility="collapsed")
    st.session_state.active_module = choice

    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("Refresh", use_container_width=True, key="refresh_database"):
            get_database(reload=True)
            st.rerun()
    with col2:
        if st.button("Top", use_container_width=True, key="top_workspace"):
            st.rerun()

    st.sidebar.markdown('<div class="cs-divider"></div>', unsafe_allow_html=True)
    backend = database_backend()
    backend_label = "Neon PostgreSQL" if backend == "neon" else "Local JSON"
    st.sidebar.caption(f"Data layer: {backend_label}")
    st.sidebar.markdown(
        '<div class="cs-sidebar-note">Create, edit and delete records directly inside each module. Changes are persisted through the shared database layer.</div>',
        unsafe_allow_html=True,
    )
    return choice


def load_module_renderer(name: str) -> Callable[[dict[str, Any]], Any] | None:
    module_path, function_name = MODULE_IMPORTS.get(name, ("", ""))
    if not module_path:
        return None
    module = importlib.import_module(module_path)
    renderer = getattr(module, function_name, None)
    if not callable(renderer):
        raise TypeError(f"{module_path}.{function_name} is missing or is not callable.")
    return renderer


def render_module(name: str, database: dict[str, Any]) -> None:
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
    choice = render_sidebar()
    render_module(choice, get_database())
    st.markdown('<div class="cs-footer">Creative Studios · AEC Collaboration Platform · Shared workspace</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
