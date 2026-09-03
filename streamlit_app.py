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

# Canonical Creative Studios logo. The hyphenated filename is the production asset.
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
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

        :root {
            --cs-blue: #2f80ed;
            --cs-blue-dark: #1558b0;
            --cs-blue-soft: #67b3ff;
            --cs-black: #030509;
            --cs-ink: #f2f7ff;
            --cs-muted: #93a4bb;
            --cs-muted-2: #6f8097;
            --cs-border: rgba(111, 155, 214, .20);
            --cs-border-strong: rgba(90, 169, 255, .38);
            --cs-surface: rgba(10, 16, 27, .90);
            --cs-surface-strong: rgba(16, 25, 40, .97);
            --cs-input: #080f1a;
            --cs-shadow: 0 18px 50px rgba(0, 0, 0, .34);
        }

        html, body, [class*="css"] {
            font-family: 'Inter', 'Segoe UI', sans-serif;
        }

        .stApp {
            background:
                radial-gradient(circle at 8% 0%, rgba(47,128,237,.18), transparent 29%),
                radial-gradient(circle at 92% 3%, rgba(90,169,255,.08), transparent 25%),
                linear-gradient(135deg, #020408 0%, #07111f 50%, #03060b 100%);
            color: var(--cs-ink);
        }

        .block-container {
            max-width: 1480px;
            padding: 1.35rem 2.15rem 4rem;
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stSidebar"] {
            min-width: 278px;
            max-width: 278px;
            background: #04070c;
            border-right: 1px solid var(--cs-border);
        }

        [data-testid="stSidebar"] > div:first-child {
            padding-top: 1rem;
        }

        [data-testid="stSidebar"] .stRadio > div {
            gap: .18rem;
        }

        [data-testid="stSidebar"] .stRadio label {
            border-radius: 10px;
            padding: .48rem .68rem;
            color: #cbd9ea;
            font-size: .79rem;
            font-weight: 560;
            transition: background .16s ease, transform .16s ease, color .16s ease;
        }

        [data-testid="stSidebar"] .stRadio label:hover {
            background: rgba(47,128,237,.10);
            color: #ffffff;
            transform: translateX(2px);
        }

        [data-testid="stSidebar"] .stRadio label[data-checked="true"] {
            background: linear-gradient(90deg, rgba(47,128,237,.24), rgba(47,128,237,.08));
            color: #ffffff;
            box-shadow: inset 3px 0 0 var(--cs-blue);
        }

        .cs-brand-card {
            padding: .72rem .65rem .78rem;
            border: 1px solid var(--cs-border);
            border-radius: 15px;
            background: linear-gradient(145deg, rgba(20,31,49,.88), rgba(6,10,17,.92));
            box-shadow: 0 10px 30px rgba(0,0,0,.20);
        }

        .cs-brand-row {
            display: flex;
            align-items: center;
            gap: .78rem;
        }

        .cs-brand-logo {
            width: 58px;
            height: 58px;
            min-width: 58px;
            object-fit: contain;
            border-radius: 13px;
            display: block;
            background: #ffffff;
            padding: 3px;
            box-shadow: 0 8px 24px rgba(47,128,237,.20);
        }

        .cs-brand-title {
            font-family: 'Space Grotesk', 'Inter', sans-serif;
            font-size: 1.08rem;
            line-height: 1.05;
            font-weight: 700;
            letter-spacing: -.035em;
            color: #f7fbff;
        }

        .cs-brand-subtitle {
            margin-top: .28rem;
            color: var(--cs-muted);
            font-size: .68rem;
            line-height: 1.35;
        }

        .cs-brand-caption {
            margin-top: .62rem;
            color: var(--cs-muted-2);
            font-size: .62rem;
            letter-spacing: .02em;
        }

        .cs-divider {
            height: 1px;
            background: var(--cs-border);
            margin: .9rem 0;
        }

        .cs-section {
            color: #7f95b0;
            font-size: .61rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: .14em;
            margin: .72rem 0 .42rem;
        }

        .cs-pwa-link {
            display: block;
            text-decoration: none !important;
            padding: .62rem .72rem;
            margin: .32rem 0;
            border: 1px solid var(--cs-border);
            border-radius: 10px;
            color: #dceaff !important;
            font-size: .74rem;
            font-weight: 650;
            text-align: center;
            background: rgba(20, 36, 57, .42);
            transition: all .16s ease;
        }

        .cs-pwa-link.primary {
            color: #ffffff !important;
            border-color: rgba(47,128,237,.80);
            background: linear-gradient(135deg, var(--cs-blue), var(--cs-blue-dark));
            box-shadow: 0 8px 24px rgba(47,128,237,.20);
        }

        .cs-pwa-link:hover {
            transform: translateY(-1px);
            border-color: var(--cs-border-strong);
        }

        .cs-sidebar-note {
            color: #687b94;
            font-size: .64rem;
            text-align: center;
            line-height: 1.5;
            margin-top: .65rem;
        }

        .cs-hero {
            position: relative;
            overflow: hidden;
            border: 1px solid var(--cs-border);
            border-radius: 22px;
            padding: 1.55rem 1.65rem;
            margin-bottom: 1.25rem;
            background:
                linear-gradient(135deg, rgba(47,128,237,.16), rgba(5,8,14,.58)),
                var(--cs-surface);
            box-shadow: var(--cs-shadow);
            backdrop-filter: blur(14px);
        }

        .cs-hero::before {
            content: "";
            position: absolute;
            width: 340px;
            height: 340px;
            right: -180px;
            top: -210px;
            border-radius: 50%;
            border: 1px solid rgba(90,169,255,.12);
            box-shadow: 0 0 80px rgba(47,128,237,.08);
        }

        .cs-eyebrow {
            color: var(--cs-blue-soft);
            font-size: .64rem;
            font-weight: 800;
            letter-spacing: .16em;
            text-transform: uppercase;
            margin-bottom: .42rem;
        }

        .cs-hero-title {
            font-family: 'Space Grotesk', 'Inter', sans-serif;
            font-size: clamp(1.55rem, 3vw, 2.45rem);
            font-weight: 700;
            letter-spacing: -.055em;
            line-height: 1.02;
            margin: 0;
            color: #f7fbff;
        }

        .cs-hero-copy {
            max-width: 820px;
            color: var(--cs-muted);
            font-size: .86rem;
            line-height: 1.65;
            margin: .62rem 0 0;
        }

        .cs-status-row {
            display: flex;
            flex-wrap: wrap;
            gap: .46rem;
            margin-top: .95rem;
        }

        .cs-pill {
            display: inline-flex;
            align-items: center;
            gap: .4rem;
            border: 1px solid var(--cs-border);
            border-radius: 999px;
            padding: .31rem .62rem;
            font-size: .65rem;
            font-weight: 650;
            background: rgba(12,20,32,.88);
            color: #dceaff;
        }

        .cs-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: var(--cs-blue-soft);
            box-shadow: 0 0 0 3px rgba(47,128,237,.14);
        }

        .cs-dot.neutral {
            background: #71829a;
            box-shadow: 0 0 0 3px rgba(113,130,154,.12);
        }

        .cs-module-bar {
            display: flex;
            align-items: end;
            justify-content: space-between;
            gap: 1rem;
            padding: .2rem 0 .78rem;
            border-bottom: 1px solid var(--cs-border);
            margin-bottom: 1rem;
        }

        .cs-module-title {
            font-family: 'Space Grotesk', 'Inter', sans-serif;
            font-size: 1.18rem;
            font-weight: 650;
            letter-spacing: -.035em;
            margin: 0;
            color: #edf5ff;
        }

        .cs-module-meta {
            color: var(--cs-muted-2);
            font-size: .65rem;
            white-space: nowrap;
        }

        [data-testid="stMetric"] {
            border: 1px solid var(--cs-border);
            border-radius: 15px;
            padding: .88rem 1rem;
            background: linear-gradient(145deg, rgba(16,25,40,.92), rgba(7,12,20,.92));
            box-shadow: 0 9px 26px rgba(0,0,0,.18);
        }

        [data-testid="stMetricLabel"] {
            font-size: .65rem !important;
            font-weight: 650 !important;
            color: var(--cs-muted) !important;
        }

        [data-testid="stMetricValue"] {
            font-family: 'Space Grotesk', 'Inter', sans-serif;
            font-weight: 700 !important;
            letter-spacing: -.04em;
            color: #f4f9ff !important;
        }

        .stButton > button {
            border-radius: 10px;
            border: 1px solid var(--cs-border);
            font-weight: 650;
            min-height: 2.4rem;
            background: #0a1220;
            color: #dceaff;
            transition: transform .14s ease, box-shadow .14s ease, border-color .14s ease;
        }

        .stButton > button:hover {
            transform: translateY(-1px);
            border-color: var(--cs-border-strong);
            box-shadow: 0 7px 20px rgba(0,0,0,.22);
        }

        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, var(--cs-blue), var(--cs-blue-dark));
            border-color: var(--cs-blue);
            color: #ffffff;
            box-shadow: 0 6px 18px rgba(47,128,237,.16);
        }

        [data-testid="stTextInput"] input,
        [data-testid="stNumberInput"] input,
        [data-testid="stDateInput"] input,
        [data-testid="stTextArea"] textarea {
            border-radius: 10px;
            background: var(--cs-input);
            color: #edf5ff;
            border-color: var(--cs-border);
            font-size: .78rem;
        }

        [data-testid="stSelectbox"] > div,
        [data-testid="stMultiSelect"] > div {
            border-radius: 10px;
            background: var(--cs-input);
            color: #edf5ff;
            border-color: var(--cs-border);
        }

        [data-testid="stExpander"] {
            border: 1px solid var(--cs-border);
            border-radius: 13px;
            overflow: hidden;
            background: var(--cs-surface);
        }

        [data-testid="stDataFrame"] {
            border: 1px solid var(--cs-border);
            border-radius: 13px;
            overflow: hidden;
        }

        [data-testid="stAlert"] {
            border-radius: 11px;
        }

        .cs-footer {
            color: #5f7189;
            text-align: center;
            font-size: .62rem;
            padding: 2.4rem 0 .2rem;
            letter-spacing: .025em;
        }

        @media (max-width: 900px) {
            .block-container { padding: .85rem .85rem 3rem; }
            .cs-hero { border-radius: 16px; padding: 1.05rem; }
            .cs-module-bar { align-items: flex-start; flex-direction: column; gap: .22rem; }
            .cs-module-meta { white-space: normal; }
            .cs-brand-logo { width: 52px; height: 52px; min-width: 52px; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_brand() -> None:
    logo_markup = ""
    if LOGO_PATH:
        logo_markup = f'<img class="cs-brand-logo" src="{LOGO_PATH.as_uri()}" alt="Creative Studios logo">'
    else:
        logo_markup = '<div class="cs-brand-logo" aria-label="Creative Studios logo">CS</div>'

    st.sidebar.markdown(
        '<div class="cs-brand-card">'
        f'<div class="cs-brand-row">{logo_markup}'
        '<div><div class="cs-brand-title">Creative Studios</div>'
        '<div class="cs-brand-subtitle">AEC Collaboration Platform</div></div></div>'
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
        '<div class="cs-sidebar-note">Shared workspace data is available across the registered AEC modules.</div>',
        unsafe_allow_html=True,
    )
    return choice


def render_workspace_header(name: str) -> None:
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
