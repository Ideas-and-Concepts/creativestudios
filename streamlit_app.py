"""
Creative Studios
AEC Collaboration Platform

Main Streamlit application.

Authentication has been removed.

Top-level modules:
    Dashboard, Projects, Documents, Architecture, Engineering, MEP, BOQ, Construction

Drawings is intentionally NOT a standalone module.
"""

from __future__ import annotations

import base64
import importlib
import json
from pathlib import Path
from typing import Any, Callable
from datetime import datetime

import streamlit as st
import pandas as pd

from modules.database import load_memory, save_memory


# ============================================================
# APPLICATION PATHS
# ============================================================
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"


def find_logo() -> Path | None:
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
# GLOBAL CSS
# ============================================================
def inject_css() -> None:
    st.markdown(
        """
        <style>
        /* ... keep existing CSS ... */
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
# DATABASE BACKUP / RESTORE
# ============================================================
def render_backup_restore(database):
    st.sidebar.markdown("---")
    st.sidebar.subheader("Database Backup")

    # Download backup
    db_json = json.dumps(database, indent=2, default=str)
    st.sidebar.download_button(
        label="Download Backup",
        data=db_json,
        file_name=f"creativestudios_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        use_container_width=True,
    )

    # Upload restore
    uploaded = st.sidebar.file_uploader("Restore from backup", type=["json"])
    if uploaded is not None:
        try:
            restored = json.load(uploaded)
            if isinstance(restored, dict):
                st.session_state.database = restored
                save_memory(restored)
                st.sidebar.success("Database restored successfully!")
                st.rerun()
            else:
                st.sidebar.error("Invalid backup file.")
        except Exception as e:
            st.sidebar.error(f"Restore failed: {e}")


# ============================================================
# GLOBAL SEARCH
# ============================================================
def render_global_search(database):
    st.title("Global Search")
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
# SIDEBAR BRAND & NAVIGATION
# ============================================================
def render_sidebar_brand() -> None:
    # ... same as previous, including centered logo ...
    pass


def render_sidebar() -> str:
    render_sidebar_brand()
    st.sidebar.markdown('<div class="cs-sidebar-divider"></div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="cs-sidebar-section">Navigation</div>', unsafe_allow_html=True)

    current = st.session_state.get("active_module", "Dashboard")
    if current not in NAVIGATION:
        current = "Dashboard"

    # Add search option
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
# MODULE LOADER & ERROR HANDLING
# ============================================================
def load_module_renderer(module_name: str) -> Callable[[dict[str, Any]], Any]:
    if module_name not in MODULE_IMPORTS:
        raise KeyError(f"Unknown module: {module_name}")
    module_path, function_name = MODULE_IMPORTS[module_name]
    try:
        module = importlib.import_module(module_path)
    except Exception as exc:
        raise RuntimeError(f"Unable to import {module_name} module.") from exc
    renderer = getattr(module, function_name, None)
    if not callable(renderer):
        raise AttributeError(f"Module '{module_path}' missing callable '{function_name}'.")
    return renderer


def render_module_error(module_name: str, exc: Exception) -> None:
    st.error(f"Unable to load the {module_name} module.")
    st.caption("The Creative Studios application is still running.")
    with st.expander("Technical details"):
        st.exception(exc)


def render_module(choice: str, database: dict[str, Any]) -> None:
    try:
        renderer = load_module_renderer(choice)
        renderer(database)
    except Exception as exc:
        render_module_error(choice, exc)
        log_activity(database, "Module error", f"{choice}: {exc}")


# ============================================================
# FOOTER
# ============================================================
def render_footer() -> None:
    st.markdown(
        """
        <div style="text-align:center;opacity:0.45;font-size:11px;padding-top:2rem;">
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
    render_backup_restore(database)

    choice = render_sidebar()

    if choice == "Search":
        render_global_search(database)
    else:
        render_module(choice, database)

    render_footer()


if __name__ == "__main__":
    main()