"""
Creative Studios
AEC Collaboration Platform

Main Streamlit Application
Version 2.0.0

Architecture:
    streamlit_app.py
        |
        +-- modules.database
        +-- modules.auth
        +-- modules.projects
        +-- modules.drawings
        +-- modules.approvals
        +-- modules.boq
        +-- modules.rfi
        +-- modules.site_logs

UI:
    Black / Blue
    Floating-style sidebar
    Creative Studios branding
    No pages/ directory required
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

LOGO_FILE = BASE_DIR / "logo.svg"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Creative Studios — AEC Workspace",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SAFE MODULE IMPORTS
# ============================================================

try:

    from modules.database import load_memory

except Exception:

    load_memory = None


try:

    from modules.auth import (
        login_user,
        require_auth,
    )

except Exception:

    login_user = None
    require_auth = None


try:

    from modules.projects import (
        render_projects_module,
    )

except Exception:

    render_projects_module = None


try:

    from modules.drawings import (
        render_drawings_module,
    )

except Exception:

    render_drawings_module = None


try:

    from modules.approvals import (
        render_approvals_module,
    )

except Exception:

    render_approvals_module = None


try:

    from modules.boq import (
        render_boq_module,
    )

except Exception:

    render_boq_module = None


try:

    from modules.rfi import (
        render_rfi_module,
    )

except Exception:

    render_rfi_module = None


try:

    from modules.site_logs import (
        render_site_logs_module,
    )

except Exception:

    render_site_logs_module = None


# ============================================================
# GLOBAL CSS
# ============================================================

def inject_global_css() -> None:

    st.markdown(
        """
        <style>

        /* ==================================================
           GLOBAL
           ================================================== */

        html,
        body,
        [data-testid="stAppViewContainer"],
        [data-testid="stApp"] {

            background:
                #05070A !important;

            color:
                #E5E7EB !important;

        }


        [data-testid="stAppViewContainer"] {

            background:
                #05070A !important;

        }


        .main {

            background:
                #05070A !important;

        }


        /* ==================================================
           REMOVE STREAMLIT DEFAULT DECORATIONS
           ================================================== */

        #MainMenu {

            visibility:
                hidden;

        }


        footer {

            visibility:
                hidden;

        }


        header {

            background:
                transparent !important;

        }


        [data-testid="stDecoration"] {

            display:
                none !important;

        }


        /* ==================================================
           SIDEBAR
           ================================================== */

        section[data-testid="stSidebar"] {

            background:
                #070A0F !important;

            border-right:
                1px solid #172033 !important;

        }


        section[data-testid="stSidebar"] > div {

            background:
                #070A0F !important;

        }


        /* ==================================================
           SIDEBAR BRAND
           ================================================== */

        .cs-sidebar-brand {

            display:
                flex;

            align-items:
                center;

            gap:
                12px;

            padding:
                8px 4px 20px 4px;

        }


        .cs-sidebar-logo {

            width:
                48px;

            height:
                48px;

            min-width:
                48px;

            border-radius:
                12px;

            background:
                #0B1220;

            border:
                1px solid #1D4ED8;

            display:
                flex;

            align-items:
                center;

            justify-content:
                center;

            overflow:
                hidden;

        }


        .cs-sidebar-logo img {

            width:
                100%;

            height:
                100%;

            object-fit:
                contain;

            padding:
                6px;

        }


        .cs-sidebar-fallback {

            color:
                #60A5FA;

            font-size:
                19px;

            font-weight:
                900;

            letter-spacing:
                -1px;

        }


        .cs-sidebar-name {

            color:
                #FFFFFF;

            font-size:
                17px;

            font-weight:
                850;

            line-height:
                1.1;

        }


        .cs-sidebar-subtitle {

            color:
                #64748B;

            font-size:
                10px;

            margin-top:
                4px;

            text-transform:
                uppercase;

            letter-spacing:
                1px;

            font-weight:
                700;

        }


        /* ==================================================
           USER CARD
           ================================================== */

        .cs-user-card {

            background:
                #0A0F16;

            border:
                1px solid #172033;

            border-radius:
                12px;

            padding:
                13px;

            margin:
                4px 0 18px 0;

        }


        .user-label {

            color:
                #60A5FA;

            font-size:
                9px;

            font-weight:
                850;

            letter-spacing:
                1px;

            text-transform:
                uppercase;

        }


        .user-name {

            color:
                #FFFFFF;

            font-size:
                14px;

            font-weight:
                800;

            margin-top:
                5px;

        }


        .user-login {

            color:
                #64748B;

            font-size:
                11px;

            margin-top:
                3px;

        }


        .user-role {

            display:
                inline-block;

            margin-top:
                8px;

            padding:
                4px 9px;

            background:
                #1D4ED8;

            color:
                #FFFFFF;

            border-radius:
                999px;

            font-size:
                9px;

            font-weight:
                850;

        }


        /* ==================================================
           SIDEBAR NAVIGATION
           ================================================== */

        section[data-testid="stSidebar"]
        .stRadio > div {

            gap:
                5px;

        }


        section[data-testid="stSidebar"]
        .stRadio label {

            background:
                transparent;

            border-radius:
                9px;

            padding:
                8px 10px;

            color:
                #94A3B8 !important;

        }


        section[data-testid="stSidebar"]
        .stRadio label:hover {

            background:
                #0F172A;

            color:
                #FFFFFF !important;

        }


        /* ==================================================
           BUTTONS
           ================================================== */

        .stButton > button {

            background:
                #2563EB !important;

            color:
                #FFFFFF !important;

            border:
                1px solid #2563EB !important;

            border-radius:
                8px !important;

            font-weight:
                750 !important;

        }


        .stButton > button:hover {

            background:
                #1D4ED8 !important;

            border-color:
                #3B82F6 !important;

        }


        /* ==================================================
           INPUTS
           ================================================== */

        input,
        textarea,
        [data-baseweb="select"] > div {

            background:
                #0A0F16 !important;

            color:
                #FFFFFF !important;

            border-color:
                #1E293B !important;

        }


        label {

            color:
                #CBD5E1 !important;

        }


        /* ==================================================
           METRICS
           ================================================== */

        [data-testid="stMetric"] {

            background:
                #0A0F16;

            border:
                1px solid #172033;

            border-radius:
                12px;

            padding:
                15px;

        }


        [data-testid="stMetricLabel"] {

            color:
                #64748B !important;

        }


        [data-testid="stMetricValue"] {

            color:
                #FFFFFF !important;

        }


        /* ==================================================
           DIVIDERS
           ================================================== */

        hr {

            border-color:
                #172033 !important;

        }


        /* ==================================================
           MAIN CONTAINER
           ================================================== */

        .block-container {

            padding-top:
                2rem;

            padding-bottom:
                3rem;

            max-width:
                1500px;

        }


        /* ==================================================
           LOGIN PAGE
           ================================================== */

        .cs-login-wrapper {

            max-width:
                440px;

            margin:
                7vh auto 0 auto;

            text-align:
                center;

        }


        .cs-login-logo {

            width:
                92px;

            height:
                92px;

            margin:
                0 auto 20px auto;

            border-radius:
                20px;

            background:
                #0A0F16;

            border:
                1px solid #1D4ED8;

            display:
                flex;

            align-items:
                center;

            justify-content:
                center;

            overflow:
                hidden;

        }


        .cs-login-logo img {

            width:
                100%;

            height:
                100%;

            object-fit:
                contain;

            padding:
                12px;

        }


        .cs-login-fallback {

            color:
                #60A5FA;

            font-size:
                34px;

            font-weight:
                950;

        }


        .cs-login-title {

            color:
                #FFFFFF;

            font-size:
                30px;

            font-weight:
                900;

            letter-spacing:
                -1px;

        }


        .cs-login-subtitle {

            color:
                #64748B;

            font-size:
                13px;

            margin-top:
                6px;

            margin-bottom:
                25px;

        }


        /* Remove empty Streamlit form decoration */

        [data-testid="stForm"] {

            background:
                transparent !important;

            border:
                none !important;

            padding:
                0 !important;

        }


        /* ==================================================
           RESPONSIVE
           ================================================== */

        @media (max-width: 768px) {

            .block-container {

                padding-left:
                    1rem;

                padding-right:
                    1rem;

            }

            .cs-sidebar-brand {

                padding-bottom:
                    12px;

            }

        }

        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# LOGO HTML
# ============================================================

def logo_html(
    css_class: str,
) -> str:

    if LOGO_FILE.exists():

        logo_path = str(
            LOGO_FILE
        ).replace(
            "\\",
            "/",
        )

        return f"""
        <div class="{css_class}">
            <img src="file://{logo_path}">
        </div>
        """

    return f"""
    <div class="{css_class}">
        <div class="cs-login-fallback">
            CS
        </div>
    </div>
    """


# ============================================================
# DATABASE
# ============================================================

def get_database() -> dict:

    if load_memory is None:

        return {
            "projects": [],
            "users": [],
        }

    try:

        db = load_memory()

        if not isinstance(
            db,
            dict,
        ):

            db = {}

        db.setdefault(
            "projects",
            [],
        )

        db.setdefault(
            "users",
            [],
        )

        return db

    except Exception:

        return {
            "projects": [],
            "users": [],
        }


# ============================================================
# SESSION STATE
# ============================================================

def initialize_session() -> None:

    if "authenticated" not in st.session_state:

        st.session_state[
            "authenticated"
        ] = False

    if "user" not in st.session_state:

        st.session_state[
            "user"
        ] = None


# ============================================================
# LOGIN
# ============================================================

def render_login(
    db: dict,
) -> None:

    st.markdown(
        """
        <div class="cs-login-wrapper">
        """,
        unsafe_allow_html=True,
    )

    if LOGO_FILE.exists():

        logo_path = str(
            LOGO_FILE
        ).replace(
            "\\",
            "/",
        )

        st.markdown(
            f"""
            <div class="cs-login-logo">
                <img src="file://{logo_path}">
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        st.markdown(
            """
            <div class="cs-login-logo">
                <div class="cs-login-fallback">
                    CS
                </div>
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
            Architectural, Engineering & Construction
            Collaboration Platform
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form(
        "creative_studios_login"
    ):

        username = st.text_input(
            "Username",
            placeholder="Enter username",
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter password",
        )

        submitted = st.form_submit_button(
            "Sign In",
            use_container_width=True,
        )

    if submitted:

        if not username.strip():

            st.error(
                "Username is required."
            )

            return

        if not password:

            st.error(
                "Password is required."
            )

            return

        authenticated = False

        user = None

        if login_user is not None:

            try:

                result = login_user(
                    db,
                    username.strip(),
                    password,
                )

                authenticated = bool(
                    result
                )

            except Exception:

                authenticated = False

        # ----------------------------------------------------
        # Compatibility fallback
        # ----------------------------------------------------

        if not authenticated:

            for candidate in db.get(
                "users",
                [],
            ):

                if not isinstance(
                    candidate,
                    dict,
                ):
                    continue

                candidate_username = str(
                    candidate.get(
                        "username",
                        "",
                    )
                )

                candidate_password = str(
                    candidate.get(
                        "password",
                        candidate.get(
                            "password_hash",
                            "",
                        ),
                    )
                )

                if (
                    candidate_username
                    == username.strip()
                    and candidate_password
                    == password
                ):

                    authenticated = True

                    user = candidate

                    break

        if authenticated:

            st.session_state[
                "authenticated"
            ] = True

            if user is None:

                user = {
                    "username":
                        username.strip(),
                    "full_name":
                        "System Administrator"
                    if username.strip()
                    == "admin"
                    else username.strip(),
                    "role":
                        "Admin"
                    if username.strip()
                    == "admin"
                    else "User",
                }

            st.session_state[
                "user"
            ] = user

            st.rerun()

        st.error(
            "Invalid username or password."
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


# ============================================================
# USER DETAILS
# ============================================================

def get_user_details() -> tuple[str, str, str]:

    user = st.session_state.get(
        "user"
    )

    if not isinstance(
        user,
        dict,
    ):

        return (
            "System Administrator",
            "@admin",
            "Admin",
        )

    username = str(
        user.get(
            "username",
            "admin",
        )
    )

    full_name = str(
        user.get(
            "full_name",
            user.get(
                "name",
                "System Administrator",
            ),
        )
    )

    role = str(
        user.get(
            "role",
            "Admin",
        )
    )

    return (
        full_name,
        f"@{username}"
        if not username.startswith("@")
        else username,
        role,
    )


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar() -> str:

    full_name, username, role = (
        get_user_details()
    )

    with st.sidebar:

        # ----------------------------------------------------
        # BRAND
        # ----------------------------------------------------

        if LOGO_FILE.exists():

            logo_path = str(
                LOGO_FILE
            ).replace(
                "\\",
                "/",
            )

            st.markdown(
                f"""
                <div class="cs-sidebar-brand">

                    <div class="cs-sidebar-logo">

                        <img
                            src="file://{logo_path}"
                        >

                    </div>

                    <div>

                        <div class="cs-sidebar-name">
                            Creative Studios
                        </div>

                        <div class="cs-sidebar-subtitle">
                            AEC Workspace
                        </div>

                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            st.markdown(
                """
                <div class="cs-sidebar-brand">

                    <div class="cs-sidebar-logo">

                        <div class="cs-sidebar-fallback">
                            CS
                        </div>

                    </div>

                    <div>

                        <div class="cs-sidebar-name">
                            Creative Studios
                        </div>

                        <div class="cs-sidebar-subtitle">
                            AEC Workspace
                        </div>

                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

        # ----------------------------------------------------
        # USER
        # ----------------------------------------------------

        st.markdown(
            f"""
            <div class="cs-user-card">

                <div class="user-label">
                    Signed In
                </div>

                <div class="user-name">
                    {full_name}
                </div>

                <div class="user-login">
                    {username}
                </div>

                <div class="user-role">
                    {role}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        # ----------------------------------------------------
        # NAVIGATION
        # ----------------------------------------------------

        st.markdown(
            """
            <div style="
                color:#475569;
                font-size:9px;
                font-weight:850;
                letter-spacing:1px;
                text-transform:uppercase;
                margin-bottom:8px;
            ">
                AEC Workspace
            </div>
            """,
            unsafe_allow_html=True,
        )

        menu = st.radio(
            "Navigation",
            [
                "Project Directory",
                "Drawing Repository",
                "Sign-Off & Approvals",
                "Bill of Quantities",
                "RFI & Technical Queries",
                "Daily Site Logs",
            ],
            label_visibility="collapsed",
        )

        st.markdown(
            "<br>",
            unsafe_allow_html=True,
        )

        # ----------------------------------------------------
        # LOGOUT
        # ----------------------------------------------------

        if st.button(
            "Sign Out",
            use_container_width=True,
        ):

            st.session_state[
                "authenticated"
            ] = False

            st.session_state[
                "user"
            ] = None

            st.rerun()

    return menu


# ============================================================
# MODULE FALLBACK
# ============================================================

def module_unavailable(
    module_name: str,
) -> None:

    st.markdown(
        f"""
        <div style="
            background:#0A0F16;
            border:1px solid #172033;
            border-radius:14px;
            padding:30px;
        ">

            <div style="
                color:#60A5FA;
                font-size:20px;
                font-weight:850;
            ">
                {module_name}
            </div>

            <div style="
                color:#64748B;
                margin-top:8px;
                font-size:13px;
            ">
                This module is not currently available.
                Check the corresponding file inside
                the modules directory.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# MODULE ROUTER
# ============================================================

def render_module(
    menu: str,
    db: dict,
) -> None:

    if menu == "Project Directory":

        if render_projects_module is None:

            module_unavailable(
                "Project Directory"
            )

        else:

            render_projects_module(
                db
            )

        return


    if menu == "Drawing Repository":

        if render_drawings_module is None:

            module_unavailable(
                "Drawing Repository"
            )

        else:

            render_drawings_module(
                db
            )

        return


    if menu == "Sign-Off & Approvals":

        if render_approvals_module is None:

            module_unavailable(
                "Sign-Off & Approvals"
            )

        else:

            render_approvals_module(
                db
            )

        return


    if menu == "Bill of Quantities":

        if render_boq_module is None:

            module_unavailable(
                "Bill of Quantities"
            )

        else:

            render_boq_module(
                db
            )

        return


    if menu == "RFI & Technical Queries":

        if render_rfi_module is None:

            module_unavailable(
                "RFI & Technical Queries"
            )

        else:

            render_rfi_module(
                db
            )

        return


    if menu == "Daily Site Logs":

        if render_site_logs_module is None:

            module_unavailable(
                "Daily Site Logs"
            )

        else:

            render_site_logs_module(
                db
            )

        return


# ============================================================
# APPLICATION
# ============================================================

def main() -> None:

    inject_global_css()

    initialize_session()

    db = get_database()

    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------

    if not st.session_state.get(
        "authenticated",
        False,
    ):

        render_login(db)

        return

    # --------------------------------------------------------
    # SIDEBAR
    # --------------------------------------------------------

    menu = render_sidebar()

    # --------------------------------------------------------
    # MAIN MODULE
    # --------------------------------------------------------

    render_module(
        menu,
        db,
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()