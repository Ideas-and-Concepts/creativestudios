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

NAVIGATION = ["Dashboard", "Projects", "Documents", "Architecture", "Engineering", "Drawings", "MEP", "BOQ", "Procurement", "Construction", "Cost Control", "Tasks", "RFIs", "Approvals", "Reports", "Settings"]
MODULE_GROUPS = {
    "Architecture": ["Projects", "Documents", "Architecture", "Drawings"],
    "Engineering": ["Engineering", "MEP", "BOQ", "RFIs", "Approvals"],
    "Construction": ["Procurement", "Construction", "Cost Control", "Tasks", "Reports"],
    "Workspace": ["Dashboard", "Settings"],
}
MODULE_IMPORTS: dict[str, tuple[str, str]] = {
    "Dashboard": ("modules.dashboard", "render_dashboard"), "Projects": ("modules.projects", "render_projects_module"), "Documents": ("modules.documents", "render_documents_module"), "Architecture": ("modules.architecture", "render_architecture_module"), "Engineering": ("modules.engineering", "render_engineering_module"), "Drawings": ("modules.drawings", "render_drawings_module"), "MEP": ("modules.mep", "render_mep_module"), "BOQ": ("modules.boq", "render_boq_module"), "Procurement": ("modules.procurement", "render_procurement_module"), "Construction": ("modules.construction", "render_construction_module"), "Cost Control": ("modules.cost_control", "render_cost_control_module"), "Tasks": ("modules.tasks", "render_tasks_module"), "RFIs": ("modules.rfis", "render_rfis_module"), "Approvals": ("modules.approvals", "render_approvals_module"), "Reports": ("modules.reports", "render_reports_module"), "Settings": ("modules.settings", "render_settings_module"),
}
LOGO_PATH = next((p for p in (ASSETS_DIR / "creative-studios.png", ASSETS_DIR / "creative_studios.png", ASSETS_DIR / "creative_studios_logo.png", ASSETS_DIR / "logo.png") if p.is_file() and p.stat().st_size > 0), None)
st.set_page_config(page_title="Creative Studios", page_icon=str(LOGO_PATH) if LOGO_PATH else "CS", layout="wide", initial_sidebar_state="expanded")


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
    :root{--bg:#f6f7f9;--panel:#fff;--text:#171a1f;--muted:#6b7280;--border:#e5e7eb;--blue:#2f80ed;--soft:#eef5ff}
    .stApp{background:var(--bg);color:var(--text)}.block-container{max-width:1480px;padding:1.4rem 2rem 3rem}
    [data-testid="stSidebar"]{background:#fff;border-right:1px solid var(--border);min-width:250px;max-width:250px}
    [data-testid="stSidebar"]>div:first-child{padding:1rem .85rem}[data-testid="stSidebar"] img{display:block!important;width:72px!important;max-width:72px!important;margin:.1rem auto .7rem!important}
    .cs-brand{text-align:center;padding-bottom:.9rem;border-bottom:1px solid var(--border)}.cs-brand-title{font-weight:700;font-size:1rem}.cs-brand-subtitle{color:var(--muted);font-size:.62rem;margin-top:.2rem}
    .cs-section{margin:.9rem .2rem .35rem;color:#9ca3af;font-size:.58rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em}
    .stButton>button{border:1px solid #dfe3e8;border-radius:7px;background:#fff;color:#374151;font-size:.68rem;font-weight:600;box-shadow:none}.stButton>button:hover{background:#f9fafb;border-color:#cbd5e1}.stButton>button[kind="primary"]{background:var(--blue);border-color:var(--blue);color:#fff}
    .cs-link{display:block;padding:.45rem .6rem;margin:.2rem 0;border:1px solid var(--border);border-radius:7px;color:#4b5563!important;background:#fff;text-decoration:none!important;font-size:.64rem;font-weight:600;text-align:center}.cs-link.primary{background:var(--blue);border-color:var(--blue);color:#fff!important}
    .cs-db{display:flex;gap:.4rem;align-items:center;margin-top:.6rem;padding:.45rem .55rem;border:1px solid var(--border);border-radius:7px;background:#fafafa;color:var(--muted);font-size:.6rem}.cs-db-dot{width:6px;height:6px;border-radius:50%;background:var(--blue)}.cs-db-dot.local{background:#9ca3af}
    .cs-page-header{display:flex;justify-content:space-between;gap:1rem;align-items:flex-end;margin-bottom:1rem;padding-bottom:.8rem;border-bottom:1px solid var(--border)}.cs-eyebrow{color:var(--blue);font-size:.58rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em}.cs-page-title{margin:.2rem 0 0;font-size:clamp(1.45rem,2.5vw,2.05rem);letter-spacing:-.04em}.cs-page-copy{margin:.35rem 0 0;color:var(--muted);font-size:.74rem}.cs-page-meta{color:#9ca3af;font-size:.58rem}
    [data-testid="stMetric"]{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:.7rem}.cs-footer{margin-top:2rem;padding-top:1rem;border-top:1px solid var(--border);color:#9ca3af;text-align:center;font-size:.56rem}
    @media(max-width:900px){.block-container{padding:1rem .8rem 2rem}[data-testid="stSidebar"]{min-width:230px;max-width:230px}.cs-page-header{align-items:flex-start;flex-direction:column}.cs-page-meta{white-space:normal}}
    </style>
    """, unsafe_allow_html=True)


def render_brand() -> None:
    if LOGO_PATH:
        st.sidebar.image(str(LOGO_PATH), width=72)
    st.sidebar.markdown('<div class="cs-brand"><div class="cs-brand-title">Creative Studios</div><div class="cs-brand-subtitle">AEC Collaboration Platform</div></div>', unsafe_allow_html=True)


def render_pwa_links() -> None:
    st.sidebar.markdown(f'<a class="cs-link primary" href="{PWA_URL}" target="_blank" rel="noopener noreferrer">Open Production PWA</a>', unsafe_allow_html=True)
    st.sidebar.markdown(f'<a class="cs-link" href="{AI_PWA_URL}" target="_blank" rel="noopener noreferrer">Open Creative Studios AI</a>', unsafe_allow_html=True)


def render_sidebar(database: dict[str, Any]) -> None:
    render_brand()
    order, labels = get_navigation(database)
    current = st.session_state.active_module if st.session_state.active_module in order else "Dashboard"
    st.session_state.active_module = current
    for group, candidates in MODULE_GROUPS.items():
        st.sidebar.markdown(f'<div class="cs-section">{group}</div>', unsafe_allow_html=True)
        for page in candidates:
            if page not in order:
                continue
            label = labels.get(page, page)
            if st.sidebar.button(label, key=f"nav_{group}_{page}", use_container_width=True, type="primary" if page == current else "secondary"):
                st.session_state.active_module = page
                st.session_state.navigation_nonce += 1
                st.rerun()
    st.sidebar.markdown('<div class="cs-section">Workspace links</div>', unsafe_allow_html=True)
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
                st.sidebar.exception(exc)
    with c2:
        if st.button("Top", use_container_width=True, key="top_workspace"):
            st.rerun()
    try:
        backend = database_backend()
        label = "Neon PostgreSQL" if backend == "neon" else "Local JSON"
        dot = "" if backend == "neon" else "local"
    except Exception:
        label, dot = "Database unavailable", "local"
    st.sidebar.markdown(f'<div class="cs-db"><span class="cs-db-dot {dot}"></span>{label}</div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div style="color:#9ca3af;font-size:.56rem;text-align:center;margin-top:.5rem;">Saved changes are retained. Refresh reloads current state.</div>', unsafe_allow_html=True)


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
    title = "AEC Project Workspace" if name == "Dashboard" else name
    copy = "Projects, design, documentation, procurement, construction and cost control in one workspace." if name == "Dashboard" else f"Manage {name.lower()} records and project workflow from the shared workspace."
    st.markdown(f'<div class="cs-page-header"><div><div class="cs-eyebrow">Creative Studios</div><h1 class="cs-page-title">{title}</h1><p class="cs-page-copy">{copy}</p></div><div class="cs-page-meta">{count} modules</div></div>', unsafe_allow_html=True)


def render_system_status(database: dict[str, Any]) -> None:
    def count(key: str) -> int:
        value = database.get(key, [])
        return len(value) if isinstance(value, list) else 0
    cols = st.columns(5)
    for col, label, key in zip(cols, ["Projects", "Documents", "Drawings", "Tasks", "RFIs"], ["projects", "documents", "drawings", "tasks", "rfis"]):
        col.metric(label, count(key))


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
    order, _ = get_navigation(database)
    render_sidebar(database)
    choice = st.session_state.get("active_module", "Dashboard")
    if choice not in order:
        choice = "Dashboard"
        st.session_state.active_module = choice
    render_workspace_header(choice, len(order))
    if choice != "Settings":
        render_system_status(database)
    render_module(choice, database)
    st.markdown('<div class="cs-footer">Creative Studios · AEC Collaboration Platform · Shared workspace</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
