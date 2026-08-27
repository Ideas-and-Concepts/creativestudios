"""
Creative Studios
AEC Collaboration Platform

Main Streamlit application.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from modules import (
    architecture,
    dashboard,
    documents,
    drawings,
    engineering,
    mep,
    projects,
)

from modules.database import load_memory


# ============================================================
# PAGE CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "assets" / "creative_studios.png"

st.set_page_config(
    page_title="Creative Studios",
    page_icon=str(LOGO_PATH),
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# GLOBAL BRANDING
# ============================================================

st.markdown(
    """
    <style>

    .cs-login-brand {
        width: 100%;
        text-align: center;
        margin: 25px auto 20px auto;
    }

    .cs-login-title {
        color: #FFFFFF;
        font-size: 28px;
        font-weight: 800;
        line-height: 1.2;
        text-align: center;
        margin-top: 8px;
    }

    .cs-login-subtitle {
        color: #64748B;
        font-size: 13px;
        text-align: center;
        margin-top: 5px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR LOGO
# ============================================================

def render_sidebar_logo() -> None:
    """Render the Creative Studios logo in the sidebar."""

    if LOGO_PATH.is_file():

        try:

            st.sidebar.image(
                str(LOGO_PATH),
                width=90,
            )

        except Exception:

            st.sidebar.markdown(
                """
                <div style="
                    text-align: center;
                    padding: 8px 0 16px 0;
                    font-size: 20px;
                    font-weight: 800;
                    color: #FFFFFF;
                ">
                    Creative Studios
                </div>
                """,
                unsafe_allow_html=True,
            )

    else:

        st.sidebar.markdown(
            """
            <div style="
                text-align: center;
                padding: 8px 0 16px 0;
                font-size: 20px;
                font-weight: 800;
                color: #FFFFFF;
            ">
                Creative Studios
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# LOGIN BRANDING
# ============================================================

def render_login_branding() -> None:
    """
    Render centered Creative Studios branding.

    The logo is deliberately kept small.
    """

    left_column, center_column, right_column = st.columns(
        [1, 2, 1]
    )

    with center_column:

        if LOGO_PATH.is_file():

            st.image(
                str(LOGO_PATH),
                width=100,
            )

        else:

            st.markdown(
                """
                <div class="cs-login-title">
                    Creative Studios
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            """
            <div class="cs-login-title">
                Creative Studios
            </div>

            <div class="cs-login-subtitle">
                Architecture • Engineering • Construction
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# NAVIGATION
# ============================================================

def render_navigation() -> str:
    """Render the main application navigation."""

    st.sidebar.title("Navigation")

    return st.sidebar.radio(
        "Go to",
        [
            "Dashboard",
            "Projects",
            "Documents",
            "Architecture",
            "Engineering",
            "Drawings",
            "MEP",
        ],
    )


# ============================================================
# MODULE ROUTER
# ============================================================

def render_module(
    choice: str,
    database: dict,
) -> None:
    """Route navigation selection to the appropriate module."""

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


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    """Run Creative Studios."""

    # --------------------------------------------------------
    # Sidebar branding
    # --------------------------------------------------------

    render_sidebar_logo()

    # --------------------------------------------------------
    # Navigation
    # --------------------------------------------------------

    choice = render_navigation()

    # --------------------------------------------------------
    # Database
    # --------------------------------------------------------

    try:

        database = load_memory()

        if not isinstance(
            database,
            dict,
        ):
            database = {}

    except Exception as exc:

        st.error(
            "Unable to load Creative Studios database."
        )

        st.exception(exc)

        st.stop()

    # --------------------------------------------------------
    # Module rendering
    # --------------------------------------------------------

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
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()