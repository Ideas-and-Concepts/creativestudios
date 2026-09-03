"""Creative Studios Streamlit workspace."""
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
    return candidate if parsed.scheme in {"http", "https"} and parsed.netloc else DEFAULT_PWA_URL


PWA_URL = get_pwa_url()


def initialize_session_state() -> None:
    if "active_module" not in st.session_state or st.session_state.active_module not in NAVIGATION:
        st.session_state.active_module = "Dashboard"
    if "database" not in st.session_state or not isinstance(st.session_state.database, dict):
        st.session_state.database = load_memory()


def get_navigation(database: dict[str, Any]) -> tuple[list[str], dict[str, str]]:
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
            --cs-black: #050505;
            --cs-sidebar: #08090b;
            --cs-panel: #0d0f12;
            --cs-panel-2: #111419;
            --cs-input: #0a0c0f;
            --cs-blue: #2f80ed;
            --cs-blue-hover: #3b8ef3;
            --cs-blue-dark: #1558b0;
            --cs-text: #f5f7fa;
            --cs-text-2: #c5cbd4;
            --cs-muted: #8b95a3;
            --cs-muted-2: #68727f;
            --cs-border: #20252d;
            --cs-border-strong: #315f98;
        }

        html, body, [class*="css"] {
            font-family: 'Inter', 'Segoe UI', sans-serif;
        }

        .stApp {
            background: var(--cs-black);
            color: var(--cs-text);
        }

        .block-container {
            max-width: 1500px;
            padding: 1.25rem 2rem 3.5rem;
        }

        [data-testid="stHeader"] {
            background: var(--cs-black);
        }

        [data-testid="stSidebar"] {
            min-width: 278px;
            max-width: 278px;
            background: var(--cs-sidebar);
            border-right: 1px solid var(--cs-border);
        }

        [data-testid="stSidebar"] > div:first-child {
            padding: .9rem .8rem 1rem;
        }

        [data-testid="stSidebar"] img {
            display: block !important;
            width: 78px !important;
            max-width: 78px !important;
            height: auto !important;
            margin-left: auto !important;
            margin-right: auto !important;
            border-radius: 8px;
            object-fit: contain;
        }

        [data-testid="stSidebar"] .stRadio > div {
            gap: .12rem;
        }

        [data-testid="stSidebar"] .stRadio label {
            border-radius: 6px;
            padding: .46rem .62rem;
            color: var(--cs-text-2);
            font-size: .77rem;
            font-weight: 500;
            border-left: 2px solid transparent;
            transition: background .14s ease, color .14s ease, border-color .14s ease;
        }

        [data-testid="stSidebar"] .stRadio label:hover {
            background: #101419;
            color: #ffffff;
        }

        [data-testid="stSidebar"] .stRadio label[data-checked="true"] {
            background: #101923;
            color: #ffffff;
            border-left-color: var(--cs-blue);
        }

        .cs-brand-card {
            margin-top: .55rem;
            padding: .8rem .55rem .75rem;
            text-align: center;
            border-top: 1px solid var(--cs-border);
            border-bottom: 1px solid var(--cs-border);
        }

        .cs-brand-title {
            font-family: 'Space Grotesk', 'Inter', sans-serif;
            font-size: 1rem;
            line-height: 1.1;
            font-weight: 700;
            letter-spacing: -.03em;
            color: #ffffff;
        }

        .cs-brand-subtitle {
            margin-top: .28rem;
            color: var(--cs-muted);
            font-size: .61rem;
            line-height: 1.35;
        }

        .cs-brand-caption {
            margin-top: .5rem;
            color: var(--cs-muted-2);
            font-size: .58rem;
            letter-spacing: .02em;
        }

        .cs-brand-logo {
            display: block;
            width: 44px;
            height: 44px;
            margin: 0 auto;
            padding: 2px;
            object-fit: contain;
            border-radius: 7px;
            background: #ffffff;
        }

        .cs-divider {
            height: 1px;
            background: var(--cs-border);
            margin: .75rem 0;
        }

        .cs-section {
            color: var(--cs-muted-2);
            font-size: .59rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: .13em;
            margin: .7rem 0 .4rem;
        }

        .cs-pwa-link {
            display: block;
            text-decoration: none !important;
            padding: .55rem .6rem;
            margin: .28rem 0;
            border: 1px solid var(--cs-border);
            border-radius: 6px;
            color: var(--cs-text-2) !important;
            font-size: .69rem;
            font-weight: 600;
            text-align: center;
            background: #0c0f13;
            transition: background .14s ease, border-color .14s ease, color .14s ease;
        }

        .cs-pwa-link.primary {
            color: #ffffff !important;
            background: var(--cs-blue);
            border-color: var(--cs-blue);
        }

        .cs-pwa-link:hover {
            color: #ffffff !important;
            background: #121820;
            border-color: var(--cs-border-strong);
        }

        .cs-pwa-link.primary:hover {
            background: var(--cs-blue-hover);
            border-color: var(--cs-blue-hover);
        }

        .cs-sidebar-note {
            color: var(--cs-muted-2);
            font-size: .59rem;
            text-align: center;
            line-height: 1.45;
            margin-top: .58rem;
        }

        .cs-hero {
            border: 1px solid var(--cs-border);
            border-radius: 8px;
            padding: 1.35rem 1.45rem;
            margin-bottom: 1.1rem;
            background: var(--cs-panel);
        }

        .cs-eyebrow {
            color: var(--cs-blue);
            font-size: .61rem;
            font-weight: 700;
            letter-spacing: .15em;
            text-transform: uppercase;
            margin-bottom: .45rem;
        }

        .cs-hero-title {
            font-family: 'Space Grotesk', 'Inter', sans-serif;
            font-size: clamp(1.45rem, 2.7vw, 2.15rem);
            font-weight: 700;
            letter-spacing: -.045em;
            line-height: 1.05;
            margin: 0;
            color: #ffffff;
        }

        .cs-hero-copy {
            max-width: 850px;
            color: var(--cs-muted);
            font-size: .8rem;
            line-height: 1.6;
            margin: .58rem 0 0;
        }

        .cs-status-row {
            display: flex;
            flex-wrap: wrap;
            gap: .42rem;
            margin-top: .82rem;
        }

        .cs-pill {
            display: inline-flex;
            align-items: center;
            gap: .38rem;
            border: 1px solid var(--cs-border);
            border-radius: 5px;
            padding: .28rem .5rem;
            font-size: .61rem;
            font-weight: 600;
            background: #101318;
            color: var(--cs-text-2);
        }

        .cs-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: var(--cs-blue);
        }

        .cs-dot.neutral {
            background: var(--cs-muted-2);
        }

        .cs-module-bar {
            display: flex;
            align-items: end;
            justify-content: space-between;
            gap: 1rem;
            padding: .1rem 0 .68rem;
            border-bottom: 1px solid var(--cs-border);
            margin-bottom: .95rem;
        }

        .cs-module-title {
            font-family: 'Space Grotesk', 'Inter', sans-serif;
            font-size: 1.05rem;
            font-weight: 600;
            letter-spacing: -.025em;
            margin: 0;
            color: #ffffff;
        }

        .cs-module-meta {
            color: var(--cs-muted-2);
            font-size: .61rem;
            white-space: nowrap;
        }

        [data-testid="stMetric"] {
            border: 1px solid var(--cs-border);
            border-radius: 7px;
            padding: .78rem .9rem;
            background: var(--cs-panel);
            box-shadow: none;
        }

        [data-testid="stMetricLabel"] {
            font-size: .62rem !important;
            font-weight: 600 !important;
            color: var(--cs-muted) !important;
        }

        [data-testid="stMetricValue"] {
            font-family: 'Space Grotesk', 'Inter', sans-serif;
            font-weight: 700 !important;
            letter-spacing: -.035em;
            color: #ffffff !important;
        }

        .stButton > button {
            min-height: 2.25rem;
            border-radius: 6px;
            border: 1px solid #2a3038;
            font-weight: 600;
            background: #0d1014;
            color: var(--cs-text-2);
            box-shadow: none;
            transition: background .14s ease, border-color .14s ease, color .14s ease;
        }

        .stButton > button:hover {
            background: #151a21;
            border-color: var(--cs-border-strong);
            color: #ffffff;
        }

        .stButton > button[kind="primary"] {
            background: var(--cs-blue);
            border-color: var(--cs-blue);
            color: #ffffff;
            box-shadow: none;
        }

        .stButton > button[kind="primary"]:hover {
            background: var(--cs-blue-hover);
            border-color: var(--cs-blue-hover);
        }

        [data-testid="stTextInput"] input,
        [data-testid="stNumberInput"] input,
        [data-testid="stDateInput"] input,
        [data-testid="stTextArea"] textarea {
            border-radius: 6px;
            background: var(--cs-input);
            color: var(--cs-text);
            border-color: var(--cs-border);
            font-size: .76rem;
        }

        [data-testid="stSelectbox"] > div,
        [data-testid="stMultiSelect"] > div {
            border-radius: 6px;
            background: var(--cs-input);
            color: var(--cs-text);
            border-color: var(--cs-border);
            font-size: .76rem;
        }

        [data-testid="stExpander"] {
            border: 1px solid var(--cs-border);
            border-radius: 7px;
            overflow: hidden;
            background: var(--cs-panel);
            box-shadow: none;
        }

        [data-testid="stDataFrame"] {
            border: 1px solid var(--cs-border);
            border-radius: 7px;
            overflow: hidden;
        }

        [data-testid="stAlert"] {
            border-radius: 6px;
        }

        .cs-footer {
            color: #555d68;
            text-align: center;
            font-size: .58rem;
            padding: 2.2rem 0 .2rem;
            letter-spacing: .02em;
        }

        @media (max-width: 900px) {
            .block-container {
                padding: .8rem .75rem 2.8rem;
            }
            .cs-hero {
                padding: 1rem;
                border-radius: 7px;
            }
            .cs-module-bar {
                align-items: flex-start;
                flex-direction: column;
                gap: .2rem;
            }
            .cs-module-meta {
                white-space: normal;
            }
            [data-testid="stSidebar"] img {
                width: 72px !important;
                max-width: 72px !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_brand() -> None:
    if LOGO_PATH:
        st.sidebar.image(str(LOGO_PATH), width=78)
    else:
        st.sidebar.markdown('<div class="cs-brand-logo">CS</div>', unsafe_allow_html=True)

    st.sidebar.markdown(
        '<div class="cs-brand-card">'
        '<div class="cs-brand-title">Creative Studios</div>'
        '<div class="cs-brand-subtitle">AEC Collaboration Platform</div>'
        '<div class="cs-brand-caption">Project delivery workspace</div>'
        '</div>',
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


def render_sidebar(database: dict[str, Any]) -> str:
    render_brand()
    st.sidebar.markdown('<div class="cs-divider"></div>', unsafe_allow_html=True)
    render_pwa_links()
    st.sidebar.markdown('<div class="cs-divider"></div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="cs-section">Workspace</div>', unsafe_allow_html=True)

    order, labels = get_navigation(database)
    current = st.session_state.get("active_module", "Dashboard")
    if current not in order:
        current = order[0] if order else "Dashboard"

    options = [labels.get(page, page) for page in order]
    label_to_page = {labels.get(page, page): page for page in order}
    current_label = labels.get(current, current)
    index = options.index(current_label) if current_label in options else 0

    selected_label = st.sidebar.radio(
        "Workspace",
        options,
        index=index,
        key="navigation_choice",
        label_visibility="collapsed",
    )
    choice = label_to_page.get(selected_label, current)
    st.session_state.active_module = choice

    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("Refresh", use_container_width=True, key="refresh_database"):
            try:
                get_database(reload=True)
                st.rerun()
            except Exception as exc:
                st.sidebar.error("Database refresh failed.")
                st.sidebar.exception(exc)
    with col2:
        if st.button("Top", use_container_width=True, key="top_workspace"):
            st.rerun()

    st.sidebar.markdown('<div class="cs-divider"></div>', unsafe_allow_html=True)
    try:
        backend = database_backend()
        backend_label = "Neon PostgreSQL" if backend == "neon" else "Local JSON"
        dot_class = "" if backend == "neon" else "neutral"
        st.sidebar.markdown(
            f'<div class="cs-pill"><span class="cs-dot {dot_class}"></span>{backend_label}</div>',
            unsafe_allow_html=True,
        )
    except Exception:
        st.sidebar.markdown(
            '<div class="cs-pill"><span class="cs-dot neutral"></span>Database unavailable</div>',
            unsafe_allow_html=True,
        )
    st.sidebar.markdown(
        '<div class="cs-sidebar-note">Changes are saved to the shared workspace before the page refreshes.</div>',
        unsafe_allow_html=True,
    )
    return choice


def render_workspace_header(name: str, module_count: int) -> None:
    try:
        backend = database_backend()
        backend_label = "Neon PostgreSQL" if backend == "neon" else "Local JSON"
        dot_class = "" if backend == "neon" else "neutral"
    except Exception:
        backend_label = "Database unavailable"
        dot_class = "neutral"

    if name == "Dashboard":
        title = "AEC Project Workspace"
        copy = "A connected workspace for projects, technical design, documentation, procurement, construction and cost control."
        eyebrow = "Creative Studios"
    else:
        title = name
        copy = f"Manage {name.lower()} records and project workflow from the shared Creative Studios workspace."
        eyebrow = "AEC Collaboration Platform"

    st.markdown(
        f'''<section class="cs-hero">
            <div class="cs-eyebrow">{eyebrow}</div>
            <h1 class="cs-hero-title">{title}</h1>
            <p class="cs-hero-copy">{copy}</p>
            <div class="cs-status-row">
                <span class="cs-pill"><span class="cs-dot"></span>Workspace online</span>
                <span class="cs-pill"><span class="cs-dot {dot_class}"></span>{backend_label}</span>
                <span class="cs-pill">{module_count} pages</span>
            </div>
        </section>''',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'''<div class="cs-module-bar">
            <div><div class="cs-module-title">{name}</div></div>
            <div class="cs-module-meta">Creative Studios workspace</div>
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
    choice = render_sidebar(database)
    render_workspace_header(choice, len(order))
    render_module(choice, database)
    st.markdown(
        '<div class="cs-footer">Creative Studios · AEC Collaboration Platform · Shared workspace</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
