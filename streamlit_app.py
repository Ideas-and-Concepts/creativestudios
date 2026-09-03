"""Creative Studios Streamlit workspace.

Simple, modern Streamlit shell for the Creative Studios AEC workspace.
The sidebar owns navigation and workspace controls. Domain CRUD remains
inside the individual modules.
"""
from __future__ import annotations

import importlib
import os
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

import streamlit as st

from modules.database import database_backend, load_memory
from modules.settings import get_page_configuration

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
DEFAULT_PWA_URL = "https://creativestudios-app.vercel.app/"
AI_PWA_URL = "https://creativestudios-ai.vercel.app/"

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
    (
        path
        for path in (
            ASSETS_DIR / "creative-studios.png",
            ASSETS_DIR / "creative_studios.png",
            ASSETS_DIR / "creative_studios_logo.png",
            ASSETS_DIR / "logo.png",
        )
        if path.is_file() and path.stat().st_size > 0
    ),
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
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return candidate
    return DEFAULT_PWA_URL


PWA_URL = get_pwa_url()


def initialize_session_state() -> None:
    if "active_module" not in st.session_state or st.session_state.active_module not in NAVIGATION:
        st.session_state.active_module = "Dashboard"
    if "database" not in st.session_state or not isinstance(st.session_state.database, dict):
        st.session_state.database = load_memory()
    if "navigation_nonce" not in st.session_state:
        st.session_state.navigation_nonce = 0


def get_navigation(database: dict[str, Any]) -> tuple[list[str], dict[str, str]]:
    """Return persisted page order while guaranteeing all registered pages exist."""
    order, labels = get_page_configuration(database)
    valid_order = [page for page in order if page in MODULE_IMPORTS]
    for page in NAVIGATION:
        if page not in valid_order:
            valid_order.append(page)
    return valid_order, labels


def inject_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

        :root {
            --cs-bg: #f6f7f9;
            --cs-sidebar: #ffffff;
            --cs-panel: #ffffff;
            --cs-text: #171a1f;
            --cs-muted: #6b7280;
            --cs-border: #e5e7eb;
            --cs-blue: #2f80ed;
            --cs-blue-soft: #eef5ff;
        }

        html, body, [class*="css"] {
            font-family: 'Inter', 'Segoe UI', sans-serif;
        }

        .stApp {
            background: var(--cs-bg);
            color: var(--cs-text);
        }

        .block-container {
            max-width: 1480px;
            padding: 1.5rem 2rem 3rem;
        }

        [data-testid="stHeader"] {
            background: var(--cs-bg);
        }

        [data-testid="stSidebar"] {
            background: var(--cs-sidebar);
            border-right: 1px solid var(--cs-border);
            min-width: 250px;
            max-width: 250px;
        }

        [data-testid="stSidebar"] > div:first-child {
            padding: 1rem .85rem 1rem;
        }

        [data-testid="stSidebar"] img {
            display: block !important;
            width: 72px !important;
            max-width: 72px !important;
            height: auto !important;
            margin: .15rem auto .7rem !important;
            object-fit: contain;
            border-radius: 8px;
        }

        .cs-brand {
            text-align: center;
            padding: 0 .25rem .9rem;
            border-bottom: 1px solid var(--cs-border);
        }

        .cs-brand-title {
            font-family: 'Space Grotesk', 'Inter', sans-serif;
            font-size: 1rem;
            font-weight: 700;
            letter-spacing: -.035em;
            color: var(--cs-text);
        }

        .cs-brand-subtitle {
            margin-top: .2rem;
            color: var(--cs-muted);
            font-size: .62rem;
            line-height: 1.4;
        }

        .cs-section {
            margin: .95rem .2rem .42rem;
            color: #9ca3af;
            font-size: .58rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: .12em;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] > div[role="radiogroup"] {
            gap: .12rem;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] label {
            width: 100%;
            min-height: 2.05rem;
            padding: .38rem .65rem;
            margin: 0;
            border: 1px solid transparent;
            border-radius: 7px;
            color: #4b5563;
            background: transparent;
            font-size: .70rem;
            font-weight: 600;
            transition: background .12s ease, color .12s ease, border-color .12s ease;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
            background: #f3f4f6;
            color: var(--cs-text);
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"] {
            background: var(--cs-blue-soft);
            border-color: #d9e9ff;
            color: var(--cs-blue);
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label > div:first-child {
            display: none;
        }

        .cs-link {
            display: block;
            padding: .48rem .62rem;
            margin: .2rem 0;
            border: 1px solid var(--cs-border);
            border-radius: 7px;
            color: #4b5563 !important;
            background: #fff;
            text-decoration: none !important;
            font-size: .64rem;
            font-weight: 600;
            text-align: center;
        }

        .cs-link:hover {
            background: #f9fafb;
            color: var(--cs-text) !important;
        }

        .cs-link.primary {
            background: var(--cs-blue);
            border-color: var(--cs-blue);
            color: #fff !important;
        }

        .cs-link.primary:hover {
            background: #256fd3;
            color: #fff !important;
        }

        .cs-db {
            display: flex;
            align-items: center;
            gap: .4rem;
            margin-top: .65rem;
            padding: .48rem .58rem;
            border: 1px solid var(--cs-border);
            border-radius: 7px;
            color: #6b7280;
            background: #fafafa;
            font-size: .60rem;
            font-weight: 600;
        }

        .cs-db-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: var(--cs-blue);
        }

        .cs-db-dot.local {
            background: #9ca3af;
        }

        .cs-note {
            margin: .55rem .2rem 0;
            color: #9ca3af;
            font-size: .56rem;
            line-height: 1.45;
            text-align: center;
        }

        .cs-page-header {
            display: flex;
            align-items: end;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 1rem;
            padding-bottom: .8rem;
            border-bottom: 1px solid var(--cs-border);
        }

        .cs-eyebrow {
            margin-bottom: .2rem;
            color: var(--cs-blue);
            font-size: .58rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: .12em;
        }

        .cs-page-title {
            margin: 0;
            color: var(--cs-text);
            font-family: 'Space Grotesk', 'Inter', sans-serif;
            font-size: clamp(1.45rem, 2.5vw, 2.05rem);
            font-weight: 700;
            letter-spacing: -.045em;
            line-height: 1.05;
        }

        .cs-page-copy {
            margin: .35rem 0 0;
            max-width: 850px;
            color: var(--cs-muted);
            font-size: .74rem;
            line-height: 1.5;
        }

        .cs-page-meta {
            color: #9ca3af;
            font-size: .58rem;
            white-space: nowrap;
        }

        [data-testid="stMetric"] {
            background: var(--cs-panel);
            border: 1px solid var(--cs-border);
            border-radius: 8px;
            padding: .72rem .8rem;
            box-shadow: none;
        }

        [data-testid="stMetricLabel"] {
            color: var(--cs-muted) !important;
            font-size: .59rem !important;
            font-weight: 600 !important;
        }

        [data-testid="stMetricValue"] {
            color: var(--cs-text) !important;
            font-family: 'Space Grotesk', 'Inter', sans-serif;
            font-weight: 700 !important;
            letter-spacing: -.03em;
        }

        .stButton > button {
            min-height: 2.1rem;
            border: 1px solid #dfe3e8;
            border-radius: 7px;
            background: #fff;
            color: #374151;
            font-size: .68rem;
            font-weight: 600;
            box-shadow: none;
        }

        .stButton > button:hover {
            border-color: #cbd5e1;
            background: #f9fafb;
            color: var(--cs-text);
        }

        .stButton > button[kind="primary"] {
            background: var(--cs-blue);
            border-color: var(--cs-blue);
            color: #fff;
        }

        [data-testid="stTextInput"] input,
        [data-testid="stNumberInput"] input,
        [data-testid="stDateInput"] input,
        [data-testid="stTextArea"] textarea {
            background: #fff;
            border-color: #dfe3e8;
            border-radius: 7px;
            color: var(--cs-text);
            font-size: .72rem;
        }

        [data-testid="stSelectbox"] > div,
        [data-testid="stMultiSelect"] > div {
            background: #fff;
            border-radius: 7px;
            color: var(--cs-text);
            font-size: .72rem;
        }

        [data-testid="stExpander"] {
            background: #fff;
            border: 1px solid var(--cs-border);
            border-radius: 8px;
            box-shadow: none;
        }

        [data-testid="stDataFrame"] {
            border: 1px solid var(--cs-border);
            border-radius: 8px;
            overflow: hidden;
        }

        [data-testid="stAlert"] {
            border-radius: 7px;
        }

        .cs-footer {
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid var(--cs-border);
            color: #9ca3af;
            text-align: center;
            font-size: .56rem;
        }

        @media (max-width: 900px) {
            .block-container {
                padding: 1rem .8rem 2.5rem;
            }

            [data-testid="stSidebar"] {
                min-width: 230px;
                max-width: 230px;
            }

            [data-testid="stSidebar"] img {
                width: 66px !important;
                max-width: 66px !important;
            }

            .cs-page-header {
                align-items: flex-start;
                flex-direction: column;
                gap: .25rem;
            }

            .cs-page-meta {
                white-space: normal;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_brand() -> None:
    if LOGO_PATH:
        st.sidebar.image(str(LOGO_PATH), width=72)
    else:
        st.sidebar.markdown(
            '<div style="text-align:center;font-weight:700;font-size:1.1rem;">CS</div>',
            unsafe_allow_html=True,
        )

    st.sidebar.markdown(
        '<div class="cs-brand">'
        '<div class="cs-brand-title">Creative Studios</div>'
        '<div class="cs-brand-subtitle">AEC Collaboration Platform</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def render_pwa_links() -> None:
    st.sidebar.markdown(
        f'<a class="cs-link primary" href="{PWA_URL}" target="_blank" rel="noopener noreferrer">Open Production PWA</a>',
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        f'<a class="cs-link" href="{AI_PWA_URL}" target="_blank" rel="noopener noreferrer">Open Creative Studios AI</a>',
        unsafe_allow_html=True,
    )


def get_database(*, reload: bool = False) -> dict[str, Any]:
    if reload or not isinstance(st.session_state.get("database"), dict):
        st.session_state.database = load_memory()
    return st.session_state.database


def render_sidebar(database: dict[str, Any]) -> None:
    render_brand()

    order, labels = get_navigation(database)
    current = st.session_state.get("active_module", "Dashboard")
    if current not in order:
        current = order[0] if order else "Dashboard"

    label_map = {page: labels.get(page, page) for page in order}
    reverse_map = {label: page for page, label in label_map.items()}
    options = list(label_map.values())
    current_label = label_map.get(current, current)

    st.sidebar.markdown('<div class="cs-section">Modules</div>', unsafe_allow_html=True)
    selected_label = st.sidebar.radio(
        "Modules",
        options,
        index=options.index(current_label) if current_label in options else 0,
        key=f"sidebar_navigation_{st.session_state.navigation_nonce}",
        label_visibility="collapsed",
    )
    st.session_state.active_module = reverse_map.get(selected_label, current)

    st.sidebar.markdown('<div class="cs-section">Workspace</div>', unsafe_allow_html=True)
    render_pwa_links()

    c1, c2 = st.sidebar.columns(2)
    with c1:
        if st.button("Refresh", use_container_width=True, key="refresh_database"):
            try:
                get_database(reload=True)
                st.session_state.navigation_nonce += 1
                st.rerun()
            except Exception as exc:
                st.sidebar.error("Refresh failed.")
                with st.sidebar.expander("Details"):
                    st.exception(exc)
    with c2:
        if st.button("Top", use_container_width=True, key="top_workspace"):
            st.rerun()

    try:
        backend = database_backend()
        backend_label = "Neon PostgreSQL" if backend == "neon" else "Local JSON"
        dot_class = "" if backend == "neon" else "local"
    except Exception:
        backend_label = "Database unavailable"
        dot_class = "local"

    st.sidebar.markdown(
        f'<div class="cs-db"><span class="cs-db-dot {dot_class}"></span>{backend_label}</div>',
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        '<div class="cs-note">Changes are retained in the shared workspace. Refresh reloads the current saved state.</div>',
        unsafe_allow_html=True,
    )


def render_workspace_header(name: str, module_count: int) -> None:
    if name == "Dashboard":
        title = "AEC Project Workspace"
        copy = "Projects, design, documentation, procurement, construction and cost control in one workspace."
        eyebrow = "Creative Studios"
    else:
        title = name
        copy = f"Manage {name.lower()} records and project workflow from the shared workspace."
        eyebrow = "Creative Studios"

    st.markdown(
        f'''<div class="cs-page-header">
            <div>
                <div class="cs-eyebrow">{eyebrow}</div>
                <h1 class="cs-page-title">{title}</h1>
                <p class="cs-page-copy">{copy}</p>
            </div>
            <div class="cs-page-meta">{module_count} modules</div>
        </div>''',
        unsafe_allow_html=True,
    )


def load_module_renderer(name: str) -> Callable[[dict[str, Any]], Any] | None:
    module_path, function_name = MODULE_IMPORTS.get(name, ("", ""))
    if not module_path:
        return None
    importlib.invalidate_caches()
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
    except ImportError as exc:
        st.error(f"Unable to load the {name} module dependencies.")
        with st.expander("Technical details", expanded=True):
            st.code(str(exc))
            st.caption("Check requirements.txt and the module import path, then reboot the Streamlit Cloud app.")
    except Exception as exc:
        st.error(f"Unable to render the {name} module.")
        with st.expander("Technical details", expanded=False):
            st.exception(exc)


def render_system_status(database: dict[str, Any]) -> None:
    """Show live counts from the current shared database snapshot."""
    def count(key: str) -> int:
        value = database.get(key, [])
        return len(value) if isinstance(value, list) else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Projects", count("projects"))
    c2.metric("Documents", count("documents"))
    c3.metric("Drawings", count("drawings"))
    c4.metric("Tasks", count("tasks"))
    c5.metric("RFIs", count("rfis"))


def main() -> None:
    try:
        initialize_session_state()
    except Exception as exc:
        st.error("Creative Studios could not load the shared workspace database.")
        st.caption("Check DATABASE_URL in Streamlit Cloud Secrets, then reboot the app.")
        with st.expander("Technical details", expanded=True):
            st.exception(exc)
        return

    inject_css()
    database = get_database()
    order, _ = get_navigation(database)
    render_sidebar(database)
    choice = st.session_state.get("active_module", "Dashboard")
    if choice not in order:
        choice = order[0] if order else "Dashboard"
        st.session_state.active_module = choice

    render_workspace_header(choice, len(order))
    if choice != "Settings":
        render_system_status(database)
    render_module(choice, database)
    st.markdown(
        '<div class="cs-footer">Creative Studios · AEC Collaboration Platform · Shared workspace</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
