"""Creative Studios Streamlit workspace."""
from __future__ import annotations

import importlib
import os
from pathlib import Path
from typing import Any, Callable
from urllib.parse import quote, urlparse

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
    "Architecture": ["Projects", "Documents", "Architecture", "Drawings"],
    "Engineering": ["Engineering", "MEP", "BOQ", "RFIs", "Approvals"],
    "Construction": ["Procurement", "Construction", "Cost Control", "Tasks", "Reports"],
    "Workspace": ["Dashboard", "Settings"],
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

st.set_page_config(page_title="Creative Studios", page_icon=str(LOGO_PATH) if LOGO_PATH else "CS", layout="wide", initial_sidebar_state="collapsed")


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
    :root{--bg:#f7f8fa;--panel:#fff;--text:#111827;--muted:#64748b;--border:#e5e7eb;--blue:#2563eb;--soft:#eff6ff}
    .stApp{background:var(--bg);color:var(--text)}
    [data-testid="stSidebar"],[data-testid="stSidebarCollapsedControl"]{display:none!important}
    .block-container{max-width:1500px;padding:5.25rem 2rem 2.5rem}
    header[data-testid="stHeader"]{background:transparent!important}
    .cs-stream-logo{position:fixed;z-index:1000000;top:.78rem;left:max(1rem,calc(50% - min(650px,calc(50vw - 2rem))));width:50px;height:50px;padding:7px;background:#fff;border:1px solid #eef2f7;border-radius:50%;box-shadow:0 7px 22px rgba(15,23,42,.10);object-fit:contain}
    .cs-stream-nav{position:fixed;z-index:999999;top:.85rem;left:50%;transform:translateX(-50%);width:min(1180px,calc(100vw - 2rem));height:50px;background:rgba(255,255,255,.98);border:1px solid var(--border);border-radius:10px;box-shadow:0 7px 24px rgba(15,23,42,.09);display:flex;align-items:center;padding:.35rem .45rem;backdrop-filter:blur(12px)}
    .cs-stream-links{display:flex;align-items:center;justify-content:center;gap:2px;width:100%;overflow-x:auto;scrollbar-width:none}.cs-stream-links::-webkit-scrollbar{display:none}
    .cs-stream-link{display:flex;align-items:center;justify-content:center;height:36px;padding:0 .62rem;border-radius:7px;text-decoration:none!important;color:#475569!important;font-size:.62rem;font-weight:700;white-space:nowrap}.cs-stream-link:hover{background:#f8fafc;color:#111827!important}.cs-stream-link.active{background:var(--soft);color:var(--blue)!important;box-shadow:inset 0 -2px 0 var(--blue)}
    .cs-stream-actions{display:flex;align-items:center;gap:2px;margin-left:auto}.cs-stream-action{font-size:.75rem;color:#334155;padding:.45rem}.cs-stream-user{width:27px;height:27px;border:1px solid #dbe2ea;border-radius:50%;display:grid;place-items:center;font-size:.52rem;font-weight:800;color:#475569;background:#fff;margin-left:2px}
    .cs-more{position:relative}.cs-more summary{list-style:none;cursor:pointer;height:36px;padding:0 .62rem;display:flex;align-items:center;border-radius:7px;color:#475569;font-size:.62rem;font-weight:700}.cs-more summary::-webkit-details-marker{display:none}.cs-more summary:hover,.cs-more[open] summary{background:#f8fafc;color:#111827}.cs-more-menu{position:absolute;right:0;top:40px;width:190px;padding:.35rem;background:#fff;border:1px solid var(--border);border-radius:9px;box-shadow:0 16px 38px rgba(15,23,42,.14)}.cs-more-menu a{display:block;padding:.48rem .55rem;border-radius:6px;text-decoration:none!important;color:#334155!important;font-size:.6rem}.cs-more-menu a:hover{background:var(--soft);color:var(--blue)!important}
    .cs-page-header,.cs-floating{display:none!important}
    .cs-footer{margin-top:1.6rem;padding-top:.8rem;border-top:1px solid var(--border);color:#94a3b8;text-align:center;font-size:.56rem}
    .stButton>button{border:1px solid #dfe3e8;border-radius:7px;background:#fff;color:#374151;font-size:.68rem;font-weight:650;box-shadow:none}.stButton>button:hover{background:#f9fafb;border-color:#cbd5e1}.stButton>button[kind="primary"]{background:var(--blue);border-color:var(--blue);color:#fff}
    @media(max-width:900px){.block-container{padding:4.7rem .65rem 2rem}.cs-stream-logo{left:.6rem;top:.6rem;width:43px;height:43px}.cs-stream-nav{left:58px;right:.6rem;transform:none;width:auto;top:.6rem;height:43px}.cs-stream-link{font-size:.57rem;padding:0 .5rem}.cs-stream-actions{display:none}}
    </style>
    """, unsafe_allow_html=True)


def render_brand() -> None:
    return None


def render_sidebar(database: dict[str, Any]) -> None:
    return None


def render_pwa_links() -> None:
    return None


def render_floating_navigation(database: dict[str, Any]) -> None:
    order, labels = get_navigation(database)
    current = st.session_state.get("active_module", "Dashboard")
    if current not in order:
        current = "Dashboard"
        st.session_state.active_module = current
    primary = [item for item in ["Dashboard", "Projects", "Documents", "Drawings", "RFIs", "Tasks", "Reports"] if item in order]
    links = "".join(f'<a class="cs-stream-link {"active" if item == current else ""}" href="?module={quote(item)}">{labels.get(item, item)}</a>' for item in primary)
    remaining = [item for item in order if item not in primary]
    more_links = "".join(f'<a href="?module={quote(item)}">{labels.get(item, item)}</a>' for item in remaining)
    more = f'<details class="cs-more"><summary>More</summary><div class="cs-more-menu">{more_links}</div></details>' if remaining else ""
    logo_src = f"/assets/{LOGO_PATH.name}" if LOGO_PATH else ""
    st.markdown(f'<img class="cs-stream-logo" src="{logo_src}" alt="Creative Studios"><nav class="cs-stream-nav"><div class="cs-stream-links">{links}{more}</div><div class="cs-stream-actions"><span class="cs-stream-action">⌕</span><span class="cs-stream-action">☼</span><span class="cs-stream-action">♧</span><span class="cs-stream-user">CS</span></div></nav>', unsafe_allow_html=True)
    query_module = st.query_params.get("module")
    if query_module in NAVIGATION and query_module != st.session_state.active_module:
        st.session_state.active_module = query_module
        st.session_state.navigation_nonce += 1


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
    copy = "Welcome back, Creative Studios" if name == "Dashboard" else f"Manage {name.lower()} records and project workflow from the shared workspace."
    st.markdown(f'<div class="cs-page-header"><div><div class="cs-eyebrow">Creative Studios</div><h1 class="cs-page-title">{title}</h1><p class="cs-page-copy">{copy}</p></div><div class="cs-page-meta">{count} modules</div></div>', unsafe_allow_html=True)


def render_system_status(database: dict[str, Any]) -> None:
    return None


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
    render_floating_navigation(database)
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
