"""
Creative Studios
AEC Collaboration Platform

Main Streamlit application.

Authentication has been removed.
The application opens directly into the workspace.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import streamlit as st

from modules import (
    dashboard,
    projects,
    documents,
    architecture,
    engineering,
    drawings,
    mep,
)

from modules.database import load_memory


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Creative Studios",
    page_icon="assets/creative_studios.png",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

LOGO_PATH = (
    BASE_DIR
    / "assets"
    / "creative_studios.png"
)


# ============================================================
# BRANDING CSS
# ============================================================

def inject_branding_css() -> None:
    """Inject Creative Studios application styling."""

    st.markdown(
        """
        <style>

        /* -------------------------------------------------- */
        /* GLOBAL */
        /* -------------------------------------------------- */

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }

        /* -------------------------------------------------- */
        /* SIDEBAR */
        /* -------------------------------------------------- */

        [data-testid="stSidebar"] {
            padding-top: 1rem;
        }

        .cs-sidebar-brand {
            text-align: center;
            padding: 0.5rem 0 1rem 0;
        }

        .cs-sidebar-brand img {
            width: 72px;
            max-width: 72px;
            height: auto;
            display: block;
            margin: 0 auto 8px auto;
        }

        .cs-sidebar-title {
            font-size: 18px;
            font-weight: 700;
            line-height: 1.2;
        }

        .cs-sidebar-subtitle {
            font-size: 12px;
            opacity: 0.65;
            margin-top: 3px;
        }

        .cs-divider {
            height: 1px;
            background: rgba(128, 128, 128, 0.25);
            margin: 0.5rem 0 1rem 0;
        }

        /* -------------------------------------------------- */
        /* MODULE HEADER */
        /* -------------------------------------------------- */

        .cs-module-header {
            margin-bottom: 1.5rem;
        }

        .cs-module-title {
            font-size: 30px;
            font-weight: 750;
            line-height: 1.15;
        }

        .cs-module-description {
            margin-top: 5px;
            font-size: 14px;
            opacity: 0.65;
        }

        /* -------------------------------------------------- */
        /* CARDS */
        /* -------------------------------------------------- */

        .cs-card {
            border: 1px solid rgba(128, 128, 128, 0.20);
            border-radius: 12px;
            padding: 1.25rem;
            margin-bottom: 1rem;
        }

        .cs-card-title {
            font-size: 18px;
            font-weight: 700;
        }

        .cs-card-subtitle {
            margin-top: 5px;
            font-size: 14px;
            opacity: 0.70;
            line-height: 1.5;
        }

        /* -------------------------------------------------- */
        /* KPI */
        /* -------------------------------------------------- */

        .cs-kpi {
            border: 1px solid rgba(128, 128, 128, 0.20);
            border-radius: 12px;
            padding: 1rem;
            min-height: 95px;
        }

        .cs-kpi-label {
            font-size: 13px;
            opacity: 0.65;
        }

        .cs-kpi-value {
            font-size: 27px;
            font-weight: 750;
            margin-top: 6px;
        }

        /* -------------------------------------------------- */
        /* NAVIGATION */
        /* -------------------------------------------------- */

        .cs-section-label {
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            opacity: 0.55;
            margin: 1rem 0 0.5rem 0;
        }

        /* -------------------------------------------------- */
        /* BUTTONS */
        /* -------------------------------------------------- */

        div.stButton > button {
            border-radius: 8px;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# LOGO
# ============================================================

def render_sidebar_logo() -> None:
    """Render a small Creative Studios logo in the sidebar."""

    if LOGO_PATH.exists():

        st.sidebar.markdown(
            '<div class="cs-sidebar-brand">',
            unsafe_allow_html=True,
        )

        st.sidebar.image(
            str(LOGO_PATH),
            width=72,
        )

        st.sidebar.markdown(
            """
            <div class="cs-sidebar-title">
                Creative Studios
            </div>

            <div class="cs-sidebar-subtitle">
                AEC Collaboration Platform
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.sidebar.markdown(
            "</div>",
            unsafe_allow_html=True,
        )

    else:

        st.sidebar.markdown(
            """
            <div class="cs-sidebar-brand">
                <div class="cs-sidebar-title">
                    Creative Studios
                </div>

                <div class="cs-sidebar-subtitle">
                    AEC Collaboration Platform
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# SESSION STATE
# ============================================================

def initialize_session_state() -> None:
    """Initialize application session state."""

    defaults = {
        "active_module": "Dashboard",
        "database": None,
    }

    for key, value in defaults.items():

        if key not in st.session_state:
            st.session_state[key] = value


# ============================================================
# DATABASE
# ============================================================

def get_database() -> dict[str, Any]:
    """Load the application database once per session."""

    database = st.session_state.get(
        "database"
    )

    if not isinstance(
        database,
        dict,
    ):
        database = load_memory()

        if not isinstance(
            database,
            dict,
        ):
            database = {}

        st.session_state.database = database

    return database


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

def render_sidebar() -> str:
    """Render application navigation."""

    render_sidebar_logo()

    st.sidebar.markdown(
        '<div class="cs-divider"></div>',
        unsafe_allow_html=True,
    )

    st.sidebar.markdown(
        '<div class="cs-section-label">Navigation</div>',
        unsafe_allow_html=True,
    )

    navigation = [
        "Dashboard",
        "Projects",
        "Documents",
        "Architecture",
        "Engineering",
        "Drawings",
        "MEP",
    ]

    current = st.session_state.get(
        "active_module",
        "Dashboard",
    )

    if current not in navigation:
        current = "Dashboard"

    choice = st.sidebar.radio(
        "Go to",
        navigation,
        index=navigation.index(current),
        label_visibility="collapsed",
    )

    st.session_state.active_module = choice

    return choice


# ============================================================
# MODULE ROUTER
# ============================================================

def render_module(
    choice: str,
    database: dict[str, Any],
) -> None:
    """Render the selected application module."""

    if choice == "Dashboard":

        dashboard.render_dashboard(
            database
        )

    elif choice == "Projects":

        projects.render_projects_module(
            database
        )

    elif choice == "Documents":

        documents.render_documents_module(
            database
        )

    elif choice == "Architecture":

        architecture.render_architecture_module(
            database
        )

    elif choice == "Engineering":

        engineering.render_engineering_module(
            database
        )

    elif choice == "Drawings":

        drawings.render_drawings_module(
            database
        )

    elif choice == "MEP":

        mep.render_mep_module(
            database
        )

    else:

        st.session_state.active_module = (
            "Dashboard"
        )

        dashboard.render_dashboard(
            database
        )


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    """Run Creative Studios."""

    initialize_session_state()

    inject_branding_css()

    try:

        database = get_database()

    except Exception as exc:

        st.error(
            f"Unable to load workspace data: {exc}"
        )

        st.stop()

    choice = render_sidebar()

    try:

        render_module(
            choice,
            database,
        )

    except Exception as exc:

        st.error(
            f"Unable to render {choice}."
        )

        st.exception(exc)


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()