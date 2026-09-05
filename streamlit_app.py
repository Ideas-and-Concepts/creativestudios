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
    "MEP", "BOQ", "Procurement", "Construction", "Site Progress Logs", "Cost Control",
    "Tasks", "RFIs", "Approvals", "Reports", "Settings",
]

MODULE_GROUPS = {
    "Workspace": ["Dashboard", "Projects", "Documents", "Reports", "Settings"],
    "Architecture": ["Architecture", "Drawings"],
    "Engineering": ["Engineering", "MEP", "BOQ", "RFIs", "Approvals"],
    "Construction": ["Procurement", "Construction", "Site Progress Logs", "Cost Control", "Tasks"],
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
    "Site Progress Logs": ("modules.site_logs", "render_site_logs_module"),
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
    :root{--bg:#f8fafc;--panel:#fff;--text:#111827;--muted:#64748b;--border:#e5e7eb;--blue:#2563eb;--blue-soft:#eff6ff}
    .stApp{background:var(--bg);color:var(--text)}.stApp *{color:inherit}
    [data-testid="stSidebar"]{background:#fff!important;border-right:1px solid #e5e7eb!important;min-width:280px;max-width:280px}
    [data-testid="stSidebar"]>div:first-child{padding:14px 14px 20px}[data-testid="stSidebarContent"]{overflow-y:auto!important;scrollbar-width:thin}
    [data-testid="stSidebar"] .stButton{margin:0!important}[data-testid="stSidebar"] .stButton>button{width:100%;min-height:38px!important;padding:8px 11px!important;border:1px solid transparent!important;border-radius:8px!important;background:transparent!important;color:#64748b!important;box-shadow:none!important;text-align:left!important;font-size:13px!important;font-weight:600!important}
    [data-testid="stSidebar"] .stButton>button:hover{background:#f8fafc!important;border-color:#e5e7eb!important;color:#111827!important}[data-testid="stSidebar"] .stButton>button[kind="primary"]{background:#eff6ff!important;border-color:#dbeafe!important;color:#2563eb!important;font-weight:750!important}[data-testid="stSidebar"] .stButton>button[kind="primary"] *{color:#2563eb!important}
    [data-testid="stSidebar"] .stLinkButton>a{width:100%;border:1px solid #e5e7eb!important;border-radius:8px!important;background:#fff!important;color:#334155!important;font-size:12px!important;font-weight:650!important}
    [data-testid="stSidebar"] [data-testid="stImage"]{display:flex!important;justify-content:center!important;margin:0 auto!important}[data-testid="stSidebar"] [data-testid="stImage"] img{width:58px!important;height:58px!important;object-fit:contain!important;border:1px solid #e5e7eb!important;border-radius:50%!important;padding:6px!important;background:#fff!important;box-shadow:0 7px 22px rgba(15,23,42,.10)!important}
    .block-container{max-width:1500px;padding:86px 2rem 2.5rem}.cs-sidebar-brand{text-align:center;padding:2px 4px 4px}.cs-sidebar-title{font-size:14px;font-weight:800;color:#111827!important;margin-top:7px;text-align:center}.cs-sidebar-subtitle{font-size:9px;color:#64748b!important;margin-top:2px;text-align:center}.cs-sidebar-section{font-size:9px;color:#94a3b8!important;font-weight:800;text-transform:uppercase;letter-spacing:.08em;margin:13px 8px 6px}.cs-sidebar-status{border:1px solid #e5e7eb;border-radius:9px;padding:10px;margin:12px 0;background:#f8fafc;font-size:10px;color:#64748b!important}.cs-sidebar-status strong{color:#334155!important}
    .cs-page-header{display:flex;justify-content:space-between;align-items:flex-end;gap:18px;margin-bottom:1rem;padding-bottom:.9rem;border-bottom:1px solid #e5e7eb}.cs-eyebrow{font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:.08em;font-weight:750}.cs-page-title{font-size:1.55rem;line-height:1.15;font-weight:780;letter-spacing:-.035em;margin:.2rem 0 0;color:#111827}.cs-page-copy{font-size:.75rem;color:#64748b;margin:.25rem 0 0}.cs-page-meta{font-size:.65rem;color:#64748b;border:1px solid #e5e7eb;background:#fff;border-radius:999px;padding:.4rem .65rem}
    [data-testid="stMetricValue"],[data-testid="stMetricLabel"],[data-testid="stMetricDelta"]{color:var(--text)!important}[data-testid="stMetricLabel"]{color:#64748b!important}.stSelectbox label,.stMultiSelect label,.stTextInput label,.stNumberInput label,.stDateInput label,.stTextArea label,.stFileUploader label,.stCheckbox label,.stRadio label,.stSlider label{color:#334155!important}
    [data-baseweb="select"]>div{background:#fff!important;border-color:#cbd5e1!important;color:#111827!important}[data-baseweb="select"] span{color:#111827!important}[data-baseweb="input"] input,[data-baseweb="textarea"] textarea{color:#111827!important;background:#fff!important}.stDataFrame [role="columnheader"]{color:#111827!important;background:#f1f5f9!important}.stDataFrame [role="gridcell"]{color:#334155!important;background:#fff!important}
    .stTabs [data-baseweb="tab"]{color:#64748b!important}.stTabs [aria-selected="true"]{color:#2563eb!important}.stExpander{border-color:#e5e7eb!important;background:#fff!important}.stExpander p,.stExpander label{color:#334155!important}.stButton>button{border:1px solid #cbd5e1;border-radius:8px;background:#fff;color:#334155;font-size:.72rem;font-weight:650;box-shadow:none}.stButton>button:hover{background:#f8fafc;border-color:#94a3b8;color:#111827}.stButton>button[kind="primary"]{background:#2563eb;border-color:#2563eb;color:#fff}.stButton>button[kind="primary"] *{color:#fff!important}.stDownloadButton>button{background:#fff!important;color:#334155!important;border-color:#cbd5e1!important}.stLinkButton>a{background:#fff!important;color:#2563eb!important;border-color:#cbd5e1!important}.cs-footer{margin-top:1.6rem;padding-top:.8rem;border-top:1px solid #e5e7eb;color:#94a3b8;text-align:center;font-size:.6rem}@media(max-width:900px){[data-testid="stSidebar"]{min-width:250px;max-width:250px}.block-container{padding:70px 1rem 2rem}.cs-page-header{display:block}.cs-page-meta{display:inline-block;margin-top:.55rem}}
    </style>
    """, unsafe_allow_html=True)


def render_sidebar(database: dict[str, Any]) -> None:
    order, labels = get_navigation(database)
    current = st.session_state.get("active_module", "Dashboard")
    if current not in order:
        current = "Dashboard"
        st.session_state.active_module = current
    with st.sidebar:
        st.markdown('<div class="cs-sidebar-brand">', unsafe_allow_html=True)
        if LOGO_PATH: st.image(str(LOGO_PATH), width=58)
        else: st.markdown('<div style="width:58px;height:58px;border:1px solid #e5e7eb;border-radius:50%;display:grid;place-items:center;margin:0 auto;background:#fff;font-weight:800;color:#2563eb">CS</div>', unsafe_allow_html=True)
        st.markdown('<div class="cs-sidebar-title">Creative Studios</div><div class="cs-sidebar-subtitle">AEC Collaboration Platform</div></div>', unsafe_allow_html=True)
        st.divider()
        for group, items in MODULE_GROUPS.items():
            available = [item for item in items if item in order]
            if not available: continue
            st.markdown(f'<div class="cs-sidebar-section">{group}</div>', unsafe_allow_html=True)
            for item in available:
                label = labels.get(item, item)
                if st.button(label, key=f"nav_{item}", use_container_width=True, type="primary" if item == current else "secondary"):
                    st.session_state.active_module = item; st.session_state.sidebar_module = item; st.session_state.navigation_nonce += 1; st.rerun()
        st.divider()
        try: backend = database_backend(); backend_label = "Neon PostgreSQL" if backend == "neon" else "Local JSON"
        except Exception: backend_label = "Database unavailable"
        st.markdown(f'<div class="cs-sidebar-status"><strong>Data source</strong><br>{backend_label}</div>', unsafe_allow_html=True)
        st.link_button("Open Web App", PWA_URL, use_container_width=True); st.link_button("AI Workspace", AI_PWA_URL, use_container_width=True)


def load_module_renderer(name: str) -> Callable[[dict[str, Any]], Any] | None:
    module_path, function_name = MODULE_IMPORTS.get(name, ("", ""))
    if not module_path: return None
    importlib.invalidate_caches(); module = importlib.import_module(module_path); renderer = getattr(module, function_name, None)
    if not callable(renderer): raise TypeError(f"{module_path}.{function_name} is missing or not callable")
    return renderer


def render_module(name: str, database: dict[str, Any]) -> None:
    try:
        renderer = load_module_renderer(name)
        if renderer is None: st.warning(f"The {name} renderer is not registered."); return
        renderer(database)
    except ImportError as exc:
        st.error(f"Unable to load {name} dependencies.");
        with st.expander("Technical details", expanded=True): st.code(str(exc))
    except Exception as exc:
        st.error(f"Unable to render the {name} module.");
        with st.expander("Technical details", expanded=False): st.exception(exc)


def render_workspace_header(name: str, count: int) -> None:
    title = "Project Dashboard" if name == "Dashboard" else name
    copy = "Live project, design and delivery intelligence" if name == "Dashboard" else f"Manage {name.lower()} records and project workflow from the shared workspace."
    st.markdown(f'<div class="cs-page-header"><div><div class="cs-eyebrow">Creative Studios</div><h1 class="cs-page-title">{title}</h1><p class="cs-page-copy">{copy}</p></div><div class="cs-page-meta">{count} modules</div></div>', unsafe_allow_html=True)


def main() -> None:
    try: initialize_session_state()
    except Exception as exc:
        st.error("Creative Studios could not load the shared workspace database."); st.caption("Check DATABASE_URL in Streamlit Cloud Secrets and reboot the app."); st.exception(exc); return
    inject_css(); database = get_database(); render_sidebar(database); order, _ = get_navigation(database)
    choice = st.session_state.get("active_module", "Dashboard")
    if choice not in order: choice = "Dashboard"; st.session_state.active_module = choice
    render_workspace_header(choice, len(order)); render_module(choice, database)
    try: backend = database_backend(); label = "Neon PostgreSQL" if backend == "neon" else "Local JSON"
    except Exception: label = "Database unavailable"
    st.markdown(f'<div class="cs-footer">Creative Studios · AEC Collaboration Platform · {label}</div>', unsafe_allow_html=True)


if __name__ == "__main__": main()
