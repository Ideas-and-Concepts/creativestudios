"""Creative Studios Streamlit workspace."""
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


def get_pwa_url() -> str:
    candidate = os.getenv("CREATIVE_STUDIOS_PWA_URL", "").strip() or DEFAULT_PWA_URL
    parsed = urlparse(candidate)
    return candidate if parsed.scheme in {"http", "https"} and parsed.netloc else DEFAULT_PWA_URL


PWA_URL = get_pwa_url()


def initialize_session_state() -> None:
    if "active_module" not in st.session_state:
        st.session_state.active_module = "Dashboard"
    if "navigation" not in st.session_state or st.session_state.navigation not in NAVIGATION:
        st.session_state.navigation = st.session_state.active_module
    if st.session_state.navigation not in NAVIGATION:
        st.session_state.navigation = "Dashboard"
    if "database" not in st.session_state or not isinstance(st.session_state.database, dict):
        st.session_state.database = load_memory()


def inject_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --cs-green: #2f7d5b;
            --cs-green-dark: #245f46;
            --cs-gold: #c89b3c;
            --cs-ink: #17231d;
            --cs-muted: #6b766f;
            --cs-border: rgba(90, 105, 96, .18);
            --cs-surface: rgba(255, 255, 255, .78);
            --cs-surface-strong: rgba(255, 255, 255, .94);
            --cs-shadow: 0 10px 35px rgba(25, 45, 35, .08);
        }

        .stApp {
            background:
                radial-gradient(circle at 8% 0%, rgba(47,125,91,.08), transparent 28%),
                radial-gradient(circle at 92% 4%, rgba(200,155,60,.08), transparent 24%);
        }

        .block-container {
            max-width: 1420px;
            padding: 1.35rem 2.1rem 4rem;
        }

        [data-testid="stSidebar"] {
            min-width: 270px;
            max-width: 270px;
            border-right: 1px solid var(--cs-border);
        }

        [data-testid="stSidebar"] > div:first-child {
            padding-top: 1.2rem;
        }

        [data-testid="stSidebar"] .stRadio > div {
            gap: .22rem;
        }

        [data-testid="stSidebar"] .stRadio label {
            border-radius: 9px;
            padding: .46rem .65rem;
            transition: background .16s ease, transform .16s ease;
        }

        [data-testid="stSidebar"] .stRadio label:hover {
            background: rgba(47,125,91,.08);
            transform: translateX(2px);
        }

        [data-testid="stSidebar"] .stRadio label[data-checked="true"] {
            background: rgba(47,125,91,.13);
        }

        .cs-brand-wrap {
            display: flex;
            align-items: center;
            gap: .72rem;
            padding: .35rem .15rem .15rem;
        }

        .cs-brand-mark {
            width: 48px;
            height: 48px;
            border-radius: 13px;
            display: grid;
            place-items: center;
            background: linear-gradient(145deg, var(--cs-green), var(--cs-green-dark));
            color: white;
            font-weight: 800;
            letter-spacing: -.04em;
            box-shadow: 0 8px 22px rgba(47,125,91,.22);
            overflow: hidden;
        }

        .cs-brand-mark img {
            width: 100%;
            height: 100%;
            object-fit: contain;
            padding: 5px;
        }

        .cs-brand-title {
            font-size: 1.02rem;
            line-height: 1.1;
            font-weight: 780;
            letter-spacing: -.025em;
        }

        .cs-brand-subtitle {
            margin-top: .2rem;
            color: var(--cs-muted);
            font-size: .69rem;
            line-height: 1.35;
        }

        .cs-divider {
            height: 1px;
            background: var(--cs-border);
            margin: 1rem 0;
        }

        .cs-section {
            color: var(--cs-muted);
            font-size: .65rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: .12em;
            margin: .8rem 0 .45rem;
        }

        .cs-pwa-link {
            display: block;
            text-decoration: none !important;
            padding: .58rem .72rem;
            margin: .34rem 0;
            border: 1px solid var(--cs-border);
            border-radius: 9px;
            color: inherit !important;
            font-size: .76rem;
            font-weight: 620;
            text-align: center;
            background: rgba(127,127,127,.035);
            transition: all .16s ease;
        }

        .cs-pwa-link.primary {
            color: white !important;
            border-color: var(--cs-green);
            background: linear-gradient(135deg, var(--cs-green), var(--cs-green-dark));
            box-shadow: 0 6px 18px rgba(47,125,91,.16);
        }

        .cs-pwa-link:hover {
            transform: translateY(-1px);
            border-color: rgba(47,125,91,.42);
        }

        .cs-sidebar-note {
            color: var(--cs-muted);
            font-size: .68rem;
            text-align: center;
            line-height: 1.5;
            margin-top: .7rem;
        }

        .cs-hero {
            position: relative;
            overflow: hidden;
            border: 1px solid var(--cs-border);
            border-radius: 20px;
            padding: 1.35rem 1.45rem;
            margin-bottom: 1.15rem;
            background:
                linear-gradient(135deg, rgba(47,125,91,.12), rgba(200,155,60,.055)),
                var(--cs-surface);
            box-shadow: var(--cs-shadow);
            backdrop-filter: blur(10px);
        }

        .cs-hero::after {
            content: "";
            position: absolute;
            width: 170px;
            height: 170px;
            right: -65px;
            top: -85px;
            border-radius: 50%;
            border: 1px solid rgba(47,125,91,.12);
        }

        .cs-eyebrow {
            color: var(--cs-green);
            font-size: .68rem;
            font-weight: 850;
            letter-spacing: .13em;
            text-transform: uppercase;
            margin-bottom: .35rem;
        }

        .cs-hero-title {
            font-size: clamp(1.45rem, 2.7vw, 2.15rem);
            font-weight: 820;
            letter-spacing: -.045em;
            line-height: 1.05;
            margin: 0;
        }

        .cs-hero-copy {
            max-width: 780px;
            color: var(--cs-muted);
            font-size: .88rem;
            line-height: 1.55;
            margin: .55rem 0 0;
        }

        .cs-status-row {
            display: flex;
            flex-wrap: wrap;
            gap: .45rem;
            margin-top: .8rem;
        }

        .cs-pill {
            display: inline-flex;
            align-items: center;
            gap: .36rem;
            border: 1px solid var(--cs-border);
            border-radius: 999px;
            padding: .28rem .58rem;
            font-size: .67rem;
            font-weight: 650;
            background: var(--cs-surface-strong);
        }

        .cs-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: var(--cs-green);
            box-shadow: 0 0 0 3px rgba(47,125,91,.11);
        }

        .cs-dot.gold {
            background: var(--cs-gold);
            box-shadow: 0 0 0 3px rgba(200,155,60,.12);
        }

        .cs-module-bar {
            display: flex;
            align-items: end;
            justify-content: space-between;
            gap: 1rem;
            padding: .25rem 0 .85rem;
            border-bottom: 1px solid var(--cs-border);
            margin-bottom: 1rem;
        }

        .cs-module-title {
            font-size: 1.15rem;
            font-weight: 780;
            letter-spacing: -.025em;
            margin: 0;
        }

        .cs-module-meta {
            color: var(--cs-muted);
            font-size: .7rem;
            white-space: nowrap;
        }

        [data-testid="stMetric"] {
            border: 1px solid var(--cs-border);
            border-radius: 14px;
            padding: .82rem .95rem;
            background: var(--cs-surface);
            box-shadow: 0 6px 20px rgba(25,45,35,.045);
        }

        [data-testid="stMetricLabel"] {
            font-size: .68rem !important;
            font-weight: 700 !important;
            color: var(--cs-muted) !important;
        }

        [data-testid="stMetricValue"] {
            font-weight: 800 !important;
            letter-spacing: -.035em;
        }

        .stButton > button {
            border-radius: 9px;
            border: 1px solid var(--cs-border);
            font-weight: 650;
            min-height: 2.35rem;
            transition: transform .14s ease, box-shadow .14s ease, border-color .14s ease;
        }

        .stButton > button:hover {
            transform: translateY(-1px);
            border-color: rgba(47,125,91,.45);
            box-shadow: 0 5px 15px rgba(25,45,35,.08);
        }

        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, var(--cs-green), var(--cs-green-dark));
            border-color: var(--cs-green);
        }

        [data-testid="stTextInput"] input,
        [data-testid="stNumberInput"] input,
        [data-testid="stDateInput"] input,
        [data-testid="stTextArea"] textarea,
        [data-testid="stSelectbox"] > div,
        [data-testid="stMultiSelect"] > div {
            border-radius: 9px;
        }

        [data-testid="stExpander"] {
            border: 1px solid var(--cs-border);
            border-radius: 12px;
            overflow: hidden;
            background: var(--cs-surface);
        }

        [data-testid="stDataFrame"] {
            border: 1px solid var(--cs-border);
            border-radius: 12px;
            overflow: hidden;
        }

        .cs-footer {
            color: var(--cs-muted);
            text-align: center;
            font-size: .65rem;
            padding: 2.2rem 0 .2rem;
            letter-spacing: .01em;
        }

        @media (max-width: 900px) {
            .block-container { padding: .9rem 1rem 3rem; }
            .cs-hero { border-radius: 15px; padding: 1rem; }
            .cs-module-bar { align-items: flex-start; flex-direction: column; gap: .2rem; }
            .cs-module-meta { white-space: normal; }
        }

        @media (prefers-color-scheme: dark) {
            :root {
                --cs-ink: #eef5f0;
                --cs-muted: #aebbb3;
                --cs-border: rgba(190, 210, 199, .16);
                --cs-surface: rgba(27, 35, 31, .72);
                --cs-surface-strong: rgba(34, 43, 38, .94);
                --cs-shadow: 0 12px 36px rgba(0,0,0,.18);
            }
            .stApp {
                background:
                    radial-gradient(circle at 8% 0%, rgba(47,125,91,.15), transparent 28%),
                    radial-gradient(circle at 92% 4%, rgba(200,155,60,.09), transparent 24%);
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_brand() -> None:
    if LOGO_PATH:
        mark = f'<img src="data:image/png;base64,{LOGO_PATH.read_bytes().hex()}" />'
    else:
        mark = "CS"
    # Streamlit's image component is used for the real logo below when available.
    st.sidebar.markdown(
        '<div class="cs-brand-wrap"><div class="cs-brand-mark">CS</div>'
        '<div><div class="cs-brand-title">Creative Studios</div>'
        '<div class="cs-brand-subtitle">AEC Collaboration Platform</div></div></div>',
        unsafe_allow_html=True,
    )
    if LOGO_PATH:
        st.sidebar.image(str(LOGO_PATH), width=36)


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
    render_brand()
    st.sidebar.markdown('<div class="cs-divider"></div>', unsafe_allow_html=True)
    render_pwa_links()
    st.sidebar.markdown('<div class="cs-divider"></div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="cs-section">Workspace</div>', unsafe_allow_html=True)

    current = st.session_state.get("active_module", "Dashboard")
    if current not in NAVIGATION:
        current = "Dashboard"
    navigation = st.session_state.get("navigation", current)
    if navigation not in NAVIGATION:
        navigation = current
    st.session_state.navigation = navigation

    choice = st.sidebar.radio(
        "Workspace",
        NAVIGATION,
        index=NAVIGATION.index(navigation),
        key="navigation",
        label_visibility="collapsed",
    )
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
        status_class = "" if backend == "neon" else "gold"
        st.sidebar.markdown(
            f'<div class="cs-pill"><span class="cs-dot {status_class}"></span>{backend_label}</div>',
            unsafe_allow_html=True,
        )
    except Exception:
        st.sidebar.markdown(
            '<div class="cs-pill"><span class="cs-dot gold"></span>Database unavailable</div>',
            unsafe_allow_html=True,
        )
    st.sidebar.markdown(
        '<div class="cs-sidebar-note">Shared workspace data is available across the registered AEC modules.</div>',
        unsafe_allow_html=True,
    )
    return choice


def render_workspace_header(name: str) -> None:
    try:
        backend = database_backend()
        backend_label = "Neon PostgreSQL" if backend == "neon" else "Local JSON"
        dot_class = "" if backend == "neon" else "gold"
    except Exception:
        backend_label = "Database unavailable"
        dot_class = "gold"

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
                <span class="cs-pill">{len(NAVIGATION)} modules</span>
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
    choice = render_sidebar()
    render_workspace_header(choice)
    render_module(choice, get_database())
    st.markdown(
        '<div class="cs-footer">Creative Studios · AEC Collaboration Platform · Shared workspace</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
