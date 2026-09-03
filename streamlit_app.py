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
    "Dashboard", "Projects", "Documents", "Architecture", "Engineering", "Drawings",
    "MEP", "BOQ", "Procurement", "Construction", "Cost Control", "Tasks", "RFIs",
    "Approvals", "Reports", "Settings",
]

MODULE_GROUPS = {
    "Workspace": ["Dashboard", "Projects", "Documents", "Reports", "Settings"],
    "Architecture": ["Architecture", "Drawings"],
    "Engineering": ["Engineering", "MEP", "BOQ", "RFIs", "Approvals"],
    "Construction": ["Procurement", "Construction", "Cost Control", "Tasks"],
}

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

LOGO_PATH = next((p for p in (
    ASSETS_DIR / "creative-studios.png", ASSETS_DIR / "creative_studios.png",
    ASSETS_DIR / "creative_studios_logo.png", ASSETS_DIR / "logo.png",
) if p.is_file() and p.stat().st_size > 0), None)

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
    if st.session_state.get("active_module") not in NAVIGATION:
        st.session_state.active_module = "Dashboard"
    if not isinstance(st.session_state.get("database"), dict):
        st.session_state.database = load_memory()
    st.session_state.setdefault("navigation_nonce", 0)
    st.session_state.setdefault("sidebar_module", st.session_state.active_module)


def get_database(*, reload: bool = False) -> dict[str, Any]:
    if reload or not isinstance(st.session_state.get("database"), dict):
        st.session_state.database = load_memory()
    return st.session_state.database


def get_navigation(database: dict[str, Any]) -> tuple[list[str], dict[str, str]]:
    order, labels = get_page_configuration(database)
    valid = [page for page in order if page in MODULE_IMPORTS]
    valid.extend(page for page in NAVIGATION if page not in valid)
    return valid, labels


def inject_css() -> None:
    st.markdown("""
    <style>
    :root{--bg:#f7f8fa;--panel:#fff;--text:#111827;--muted:#64748b;--border:#e5e7eb;--blue:#2563eb;--soft:#eff6ff}
    .stApp{background:var(--bg);color:var(--text)}
    [data-testid="stSidebar"]{background:#fff;border-right:1px solid #e5e7eb}
    [data-testid="stSidebar"]>div:first-child{padding-top:1rem}
    [data-testid="stSidebar"] .stRadio>div{gap:3px}
    [data-testid="stSidebar"] label[data-baseweb="radio"]{padding:.48rem .55rem;border-radius:7px}
    [data-testid="stSidebar"] label[data-baseweb="radio"]:hover{background:#f8fafc}
    [data-testid="stSidebar"] [aria-checked="true"] + div{color:#2563eb;font-weight:700}
    .block-container{max-width:1500px;padding:2rem 2rem 2.5rem}
    .cs-sidebar-brand{text-align:center;padding:.2rem .4rem 1rem}
    .cs-sidebar-brand img{width:58px;height:58px;object-fit:contain;border:1px solid #eef2f7;border-radius:50%;padding:7px;background:#fff;box-shadow:0 5px 18px rgba(15,23,42,.08)}
    .cs-sidebar-title{font-size:.92rem;font-weight:800;color:#111827;margin-top:.55rem}.cs-sidebar-subtitle{font-size:.58rem;color:#64748b;margin-top:.15rem}
    .cs-sidebar-section{font-size:.56rem;color:#94a3b8;font-weight:800;text-transform:uppercase;letter-spacing:.08em;margin:.8rem .35rem .25rem}
    .cs-sidebar-status{border:1px solid #e5e7eb;border-radius:8px;padding:.55rem .6rem;margin-top:.8rem;background:#f8fafc;font-size:.58rem;color:#64748b}
    .cs-page-header{display:flex;justify-content:space-between;align-items:flex-end;gap:18px;margin-bottom:1rem;padding-bottom:.9rem;border-bottom:1px solid var(--border)}
    .cs-eyebrow{font-size:.58rem;color:#64748b;text-transform:uppercase;letter-spacing:.08em;font-weight:750}.cs-page-title{font-size:1.45rem;line-height:1.15;font-weight:780;letter-spacing:-.035em;margin:.2rem 0 0}.cs-page-copy{font-size:.68rem;color:#64748b;margin:.25rem 0 0}.cs-page-meta{font-size:.58rem;color:#64748b;border:1px solid var(--border);background:#fff;border-radius:999px;padding:.4rem .6rem}
    .cs-footer{margin-top:1.6rem;padding-top:.8rem;border-top:1px solid var(--border);color:#94a3b8;text-align:center;font-size:.56rem}
    .stButton>button{border:1px solid #dfe3e8;border-radius:7px;background:#fff;color:#374151;font-size:.68rem;font-weight:650;box-shadow:none}.stButton>button:hover{background:#f9fafb;border-color:#cbd5e1}.stButton>button[kind="primary"]{background:var(--blue);border-color:var(--blue);color:#fff}
    @media(max-width:900px){.block-container{padding:1rem .75rem 2rem}.cs-page-header{display:block}.cs-page-meta{display:inline-block;margin-top:.55rem}}
    </style>
    """, unsafe_allow_html=True)


def render_sidebar(database: dict[str, Any]) -> None:
    order, labels = get_navigation(database)
    current = st.session_state.get("active_module", "Dashboard")
    if current not in order:
        current = "Dashboard"
        st.session_state.active_module = current

    logo_html = ""
    if LOGO_PATH:
        logo_html = f'<img src="/app/static/{LOGO_PATH.name}" alt="Creative Studios">'
    with st.sidebar:
        if LOGO_PATH:
            st.image(str(LOGO_PATH), width=58)
        st.markdown('<div class="cs-sidebar-title">Creative Studios</div><div class="cs-sidebar-subtitle">AEC Collaboration Platform</div>', unsafe_allow_html=True)
        st.divider()
        for group, items in MODULE_GROUPS.items():
            available = [item for item in items if item in order]
            if not available:
                continue
            st.markdown(f'<div class="cs-sidebar-section">{group}</div>', unsafe_allow_html=True)
            for item in available:
                label = labels.get(item, item)
                if st.button(label, key=f"nav_{item}", use_container_width=True, type="primary" if item == current else "secondary"):
                    st.session_state.active_module = item
                    st.session_state.sidebar_module = item
                    st.session_state.navigation_nonce += 1
                    st.rerun()
        st.divider()
        try:
            backend = database_backend()
            backend_label = "Neon PostgreSQL" if backend == "neon" else "Local JSON"
        except Exception:
            backend_label = "Database unavailable"
        st.markdown(f'<div class="cs-sidebar-status"><strong>Data source</strong><br>{backend_label}</div>', unsafe_allow_html=True)
        st.link_button("Open Web App", PWA_URL, use_container_width=True)
        st.link_button("AI Workspace", AI_PWA_URL, use_container_width=True)


def load_module_renderer(name: str) -> Callable[[dict[str, Any]], Any] | None:
    module_path, function_name = MODULE_IMPORTS.get(name, ("", ""))
    if not module_path:
        return None
    importlib.invalidate_caches()
    module = importlib.import_module(module_path)
    renderer = getattr(module, function_name, None)
    if not callable(renderer):
        raise TypeError(f"{module_path}.{function_name} is missing or not callable")
    return renderer


def render_module(name: str, database: dict[str, Any]) -> None:
    try:
        renderer = load_module_renderer(name)
        if renderer is None:
            st.warning(f"The {name} renderer is not registered.")
            return
        renderer(database)
    except ImportError as exc:
        st.error(f"Unable to load {name} dependencies.")
        with st.expander("Technical details", expanded=True):
            st.code(str(exc))
    except Exception as exc:
        st.error(f"Unable to render the {name} module.")
        with st.expander("Technical details", expanded=False):
            st.exception(exc)


def render_workspace_header(name: str, count: int) -> None:
    title = "Project Dashboard" if name == "Dashboard" else name
    copy = "Live project, design and delivery intelligence" if name == "Dashboard" else f"Manage {name.lower()} records and project workflow from the shared workspace."
    st.markdown(f'<div class="cs-page-header"><div><div class="cs-eyebrow">Creative Studios</div><h1 class="cs-page-title">{title}</h1><p class="cs-page-copy">{copy}</p></div><div class="cs-page-meta">{count} modules</div></div>', unsafe_allow_html=True)


def main() -> None:
    try:
        initialize_session_state()
    except Exception as exc:
        st.error("Creative Studios could not load the shared workspace database.")
        st.caption("Check DATABASE_URL in Streamlit Cloud Secrets and reboot the app.")
        st.exception(exc)
        return

    inject_css()
    database = get_database()
    render_sidebar(database)
    order, _ = get_navigation(database)
    choice = st.session_state.get("active_module", "Dashboard")
    if choice not in order:
        choice = "Dashboard"
        st.session_state.active_module = choice
    render_workspace_header(choice, len(order))
    render_module(choice, database)

    try:
        backend = database_backend()
        label = "Neon PostgreSQL" if backend == "neon" else "Local JSON"
    except Exception:
        label = "Database unavailable"
    st.markdown(f'<div class="cs-footer">Creative Studios · AEC Collaboration Platform · {label}</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
