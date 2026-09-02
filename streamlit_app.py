"""
Creative Studios
AEC Collaboration Platform

Main Streamlit application.

Authentication has been removed.

Top-level modules:
    Dashboard, Projects, Documents, Architecture, Engineering, MEP, BOQ, Construction
"""

from __future__ import annotations

import base64
import importlib
import json
from pathlib import Path
from typing import Any, Callable
from datetime import datetime

import streamlit as st

from modules.database import load_memory, save_memory


# ============================================================
# APPLICATION PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"


def find_logo() -> Path | None:
    """Find the Creative Studios logo."""
    candidates = [
        ASSETS_DIR / "creative_studios.png",
        ASSETS_DIR / "creative_studios_logo.png",
        ASSETS_DIR / "logo.png",
        ASSETS_DIR / "creative_studios.jpg",
        ASSETS_DIR / "creative_studios.jpeg",
        ASSETS_DIR / "logo.jpg",
        ASSETS_DIR / "logo.jpeg",
    ]
    for path in candidates:
        if path.exists() and path.is_file():
            return path
    return None


LOGO_PATH = find_logo()


def _get_logo_base64() -> str:
    if LOGO_PATH is None:
        return ""
    try:
        return base64.b64encode(LOGO_PATH.read_bytes()).decode("utf-8")
    except Exception:
        return ""


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Creative Studios",
    page_icon=str(LOGO_PATH) if LOGO_PATH else "CS",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# NAVIGATION & MODULE REGISTRY
# ============================================================

NAVIGATION = [
    "Dashboard",
    "Projects",
    "Documents",
    "Architecture",
    "Engineering",
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
    "MEP": ("modules.mep", "render_mep_module"),
    "BOQ": ("modules.boq", "render_boq_module"),
    "Construction": ("modules.construction", "render_construction_module"),
}


# ============================================================
# SESSION STATE
# ============================================================

def initialize_session_state() -> None:
    defaults: dict[str, Any] = {
        "active_module": "Dashboard",
        "database": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ============================================================
# GLOBAL CSS (Blue theme + centered sidebar)
# ============================================================

def inject_css() -> None:
    st.markdown(
        """
        <style>
        /* ==================================================
           GLOBAL
           ================================================== */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .block-container {
            padding-top: 1.75rem;
            padding-bottom: 3rem;
            max-width: 1200px;
        }

        /* ==================================================
           SIDEBAR - Blue gradient
           ================================================== */
        [data-testid="stSidebar"] {
            min-width: 260px;
            max-width: 260px;
            background: linear-gradient(180deg, #1e3a8a 0%, #2563eb 100%);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }

        [data-testid="stSidebar"] > div:first-child {
            padding-top: 1rem;
        }

        /* Sidebar brand */
        .cs-sidebar-title {
            font-size: 18px;
            font-weight: 700;
            color: #ffffff;
            letter-spacing: -0.02em;
            margin-top: 0.4rem;
            text-align: center;
        }
        .cs-sidebar-subtitle {
            font-size: 11px;
            color: #bfdbfe;
            margin-top: 0.1rem;
            letter-spacing: 0.03em;
            text-align: center;
        }

        .cs-sidebar-divider {
            height: 1px;
            background: rgba(255, 255, 255, 0.2);
            margin: 1rem 0 0.8rem 0;
        }

        .cs-sidebar-section {
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #bfdbfe;
            margin: 0.8rem 0 0.5rem 0;
            text-align: center;
        }

        /* ==================================================
           CENTER RADIO NAVIGATION
           ================================================== */
        [data-testid="stSidebar"] div[role="radiogroup"] {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 0.2rem;
        }

        [data-testid="stSidebar"] div[role="radiogroup"] label {
            width: 100%;
            text-align: center;
            border-radius: 8px;
            padding: 0.3rem 0.6rem;
            transition: all 0.2s ease;
            color: #ffffff;
        }

        [data-testid="stSidebar"] div[role="radiogroup"] label:hover {
            background: rgba(255, 255, 255, 0.15);
        }

        /* ==================================================
           BUTTONS (blue accent)
           ================================================== */
        div.stButton > button {
            border-radius: 8px;
            min-height: 2.4rem;
            font-weight: 600;
            border: 1px solid #2563eb;
            background-color: #eff6ff;
            color: #1e40af;
            transition: all 0.2s ease;
        }

        div.stButton > button:hover {
            border-color: #1d4ed8;
            background-color: #dbeafe;
            color: #1e3a8a;
        }

        /* Main headings */
        h1, h2, h3 {
            color: #1e3a8a;
            letter-spacing: -0.02em;
        }

        /* Cards */
        .cs-card {
            background: #ffffff;
            border: 1px solid #dbeafe;
            border-radius: 12px;
            padding: 1.25rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            margin-bottom: 1rem;
        }

        /* Search page */
        .search-highlight {
            background-color: #fef08a;
            padding: 0 0.2rem;
            border-radius: 3px;
        }

        /* Responsive */
        @media (max-width: 768px) {
            [data-testid="stSidebar"] {
                min-width: 230px;
                max-width: 230px;
            }
            .cs-sidebar-title {
                font-size: 16px;
            }
            .cs-sidebar-subtitle {
                font-size: 10px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# ACTIVITY LOG
# ============================================================

def log_activity(database, action: str, details: str = ""):
    """Add an activity log entry and save the database."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details,
        "user": "System",
    }
    database.setdefault("activity_log", []).append(entry)
    save_memory(database)


# ============================================================
# SIDEBAR BRAND
# ============================================================

def render_sidebar_brand() -> None:
    if LOGO_PATH is not None:
        logo_base64 = _get_logo_base64()
        logo_html = f"""
        <div style="display:flex; justify-content:center; align-items:center; width:100%; margin:0; padding:0;">
            <img src="data:image/png;base64,{logo_base64}" width="56" alt="Creative Studios Logo" style="display:block;">
        </div>
        """
        st.sidebar.markdown(logo_html, unsafe_allow_html=True)
    else:
        st.sidebar.markdown(
            """
            <div style="display:flex; justify-content:center; align-items:center; width:100%; margin:0; padding:0;">
                <div style="width:56px;height:56px;border-radius:12px;border:1px solid rgba(255,255,255,0.3);display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:800;color:#fff;background:#1e3a8a;">CS</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.sidebar.markdown(
        '<div class="cs-sidebar-title">Creative Studios</div>',
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        '<div class="cs-sidebar-subtitle">AEC Collaboration Platform</div>',
        unsafe_allow_html=True,
    )


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

def render_sidebar() -> str:
    render_sidebar_brand()
    st.sidebar.markdown('<div class="cs-sidebar-divider"></div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="cs-sidebar-section">Navigation</div>', unsafe_allow_html=True)

    current = st.session_state.get("active_module", "Dashboard")
    if current not in NAVIGATION:
        current = "Dashboard"

    # Include Search as an option
    nav_with_search = NAVIGATION + ["Search"]
    choice = st.sidebar.radio(
        "Go to",
        nav_with_search,
        index=nav_with_search.index(current) if current in nav_with_search else 0,
        key="module_navigation",
        label_visibility="collapsed",
    )

    st.session_state.active_module = choice
    return choice


# ============================================================
# DATABASE
# ============================================================

def get_database() -> dict[str, Any]:
    database = st.session_state.get("database")
    if isinstance(database, dict):
        return database
    try:
        database = load_memory()
    except Exception as exc:
        st.error("Unable to load the Creative Studios database.")
        with st.expander("Database error details"):
            st.exception(exc)
        database = {}
    if not isinstance(database, dict):
        database = {}
    st.session_state.database = database
    return database


# ============================================================
# GLOBAL SEARCH
# ============================================================

def render_global_search(database):
    st.title("🔍 Global Search")
    query = st.text_input("Search across all modules", placeholder="Enter keyword...")

    if query:
        query = query.lower()
        results = []

        # Search projects
        for p in database.get("projects", []):
            if query in json.dumps(p).lower():
                results.append(("Project", p.get("name", "Unnamed"), p))

        # Search documents
        for d in database.get("documents", []):
            if query in json.dumps(d).lower():
                results.append(("Document", d.get("title", "Untitled"), d))

        # Search BOQ items
        for b in database.get("boq", []):
            if query in json.dumps(b).lower():
                results.append(("BOQ", b.get("item", "Unnamed"), b))

        # Search construction phases
        for c in database.get("construction", []):
            if query in json.dumps(c).lower():
                results.append(("Construction", c.get("phase", "Phase"), c))

        if results:
            st.subheader(f"Found {len(results)} result(s)")
            for module, title, data in results:
                with st.expander(f"{module}: {title}"):
                    st.json(data)
        else:
            st.info("No results found.")


# ============================================================
# MODULE LOADER (with graceful fallback)
# ============================================================

def load_module_renderer(module_name: str) -> Callable[[dict[str, Any]], Any]:
    """
    Load the selected module renderer, or return a fallback that shows an error.
    This version avoids closure bugs by capturing error messages as strings.
    """
    if module_name not in MODULE_IMPORTS:
        return lambda db: st.error(f"Unknown module: {module_name}")

    module_path, function_name = MODULE_IMPORTS[module_name]

    try:
        module = importlib.import_module(module_path)
        renderer = getattr(module, function_name, None)
        if callable(renderer):
            return renderer
        else:
            # Return a fallback that displays a clear message
            return lambda db, path=module_path, func=function_name: st.error(
                f"Module '{path}' does not contain a callable '{func}'."
            )
    except Exception as import_error:
        # Capture the error message as a string to avoid free-variable issues
        error_message = str(import_error)

        def fallback(db, msg=error_message, name=module_name):
            st.error(f"Unable to load the {name} module: {msg}")
            st.caption("The Creative Studios application is still running.")

        return fallback


def render_module(choice: str, database: dict[str, Any]) -> None:
    renderer = load_module_renderer(choice)
    try:
        renderer(database)
    except Exception as exc:
        st.error(f"Error while rendering {choice} module.")
        with st.expander("Technical details"):
            st.exception(exc)
        log_activity(database, "Module rendering error", f"{choice}: {exc}")


# ============================================================
# FOOTER
# ============================================================

def render_footer() -> None:
    st.markdown(
        """
        <div style="text-align:center;opacity:0.5;font-size:11px;padding-top:2rem;color:#64748b;">
            Creative Studios · AEC Collaboration Platform
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    initialize_session_state()
    inject_css()
    database = get_database()

    choice = render_sidebar()

    if choice == "Search":
        render_global_search(database)
    else:
        render_module(choice, database)

    render_footer()


if __name__ == "__main__":
    main()