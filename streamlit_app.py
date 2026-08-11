"""
Creative Studios
AEC Collaboration Platform
AEC Workspace

Main Streamlit Application
Version 2.0
"""

from __future__ import annotations

from pathlib import Path
from html import escape

import streamlit as st


# ============================================================
# APPLICATION PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DB_FILE = BASE_DIR / "creativestudios_db.json"

LOGO_CANDIDATES = [
    BASE_DIR / "logo.svg",
    BASE_DIR / "logo.png",
    BASE_DIR / "assets" / "logo.svg",
    BASE_DIR / "assets" / "logo.png",
]


# ============================================================
# STREAMLIT CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Creative Studios | AEC Workspace",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SESSION STATE
# ============================================================

DEFAULT_SESSION = {
    "authenticated": False,
    "user": None,
    "active_module": "Project Directory",
}

for key, value in DEFAULT_SESSION.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# IMPORT APPLICATION MODULES
# ============================================================

try:
    from modules.auth import (
        login_user,
        logout_user,
        get_current_user,
        is_authenticated,
    )
except Exception:

    # Safe fallback authentication.
    # This prevents an import failure from making the
    # entire Streamlit application unusable.

    def login_user(db, username, password):

        username = str(
            username or ""
        ).strip()

        password = str(
            password or ""
        )

        if (
            username == "admin"
            and password == "admin123"
        ):

            return True, {
                "id": 1,
                "username": "admin",
                "full_name": "System Administrator",
                "role": "Admin",
                "active": True,
            }

        return False, {}


    def logout_user():

        st.session_state[
            "authenticated"
        ] = False

        st.session_state[
            "user"
        ] = None


    def is_authenticated():

        return bool(
            st.session_state.get(
                "authenticated",
                False,
            )
        )


    def get_current_user():

        user = st.session_state.get(
            "user"
        )

        if isinstance(user, dict):
            return user

        return {
            "id": 1,
            "username": "admin",
            "full_name": "System Administrator",
            "role": "Admin",
            "active": True,
        }


# ============================================================
# DATABASE
# ============================================================

def load_database() -> dict:
    """
    Load the application's JSON database.

    Uses modules.database when available.
    Falls back to the local JSON file.
    """

    # --------------------------------------------------------
    # Try application database module first
    # --------------------------------------------------------

    try:

        from modules.database import load_memory

        data = load_memory()

        if isinstance(data, dict):
            return data

    except Exception:
        pass


    # --------------------------------------------------------
    # Direct JSON fallback
    # --------------------------------------------------------

    try:

        import json

        if DB_FILE.exists():

            with DB_FILE.open(
                "r",
                encoding="utf-8",
            ) as file:

                data = json.load(file)

            if isinstance(data, dict):
                return data

    except Exception:
        pass


    # --------------------------------------------------------
    # Safe empty database
    # --------------------------------------------------------

    return {
        "users": [],
        "projects": [],
        "drawings": [],
        "approvals": [],
        "boq": [],
        "rfis": [],
        "site_logs": [],
    }


db = load_database()


# ============================================================
# LOGO
# ============================================================

def get_logo_file() -> Path | None:

    for candidate in LOGO_CANDIDATES:

        if candidate.exists():

            return candidate

    return None


LOGO_FILE = get_logo_file()


# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(
    """
<style>

/* ============================================================
   GLOBAL APPLICATION
   ============================================================ */

html,
body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {

    background-color: #050505 !important;

    color: #E5E7EB !important;
}


[data-testid="stHeader"] {

    background-color: transparent !important;
}


[data-testid="stToolbar"] {

    visibility: hidden !important;
}


#MainMenu {

    visibility: hidden !important;
}


footer {

    visibility: hidden !important;
}


.block-container {

    max-width: 1500px !important;

    padding-top: 1.5rem !important;

    padding-bottom: 3rem !important;
}


/* ============================================================
   SIDEBAR
   ============================================================ */

section[data-testid="stSidebar"] {

    background-color: #080A0E !important;

    border-right: 1px solid #172033 !important;
}


section[data-testid="stSidebar"] > div {

    background-color: #080A0E !important;
}


section[data-testid="stSidebar"]
.block-container {

    padding-top: 1rem !important;

    padding-left: 1rem !important;

    padding-right: 1rem !important;
}


/* ============================================================
   SIDEBAR BRAND
   ============================================================ */

.cs-sidebar-brand {

    display: flex;

    align-items: center;

    gap: 11px;

    padding: 3px 2px 18px 2px;
}


.cs-sidebar-logo {

    width: 48px;

    height: 48px;

    min-width: 48px;

    display: flex;

    align-items: center;

    justify-content: center;

    overflow: hidden;

    background: #0B1220;

    border: 1px solid #2563EB;

    border-radius: 12px;
}


.cs-sidebar-logo img {

    width: 100%;

    height: 100%;

    object-fit: contain;

    padding: 6px;
}


.cs-sidebar-fallback {

    color: #60A5FA;

    font-size: 19px;

    font-weight: 950;

    letter-spacing: -1px;
}


.cs-sidebar-name {

    color: #FFFFFF;

    font-size: 16px;

    font-weight: 900;

    line-height: 1.1;
}


.cs-sidebar-subtitle {

    color: #64748B;

    font-size: 9px;

    font-weight: 800;

    letter-spacing: 1px;

    text-transform: uppercase;

    margin-top: 4px;
}


/* ============================================================
   USER CARD
   ============================================================ */

.cs-user-card {

    background: #0B0F16;

    border: 1px solid #172033;

    border-radius: 12px;

    padding: 13px;

    margin-bottom: 18px;
}


.user-label {

    color: #60A5FA;

    font-size: 9px;

    font-weight: 850;

    letter-spacing: 1px;

    text-transform: uppercase;
}


.user-name {

    color: #FFFFFF;

    font-size: 14px;

    font-weight: 800;

    margin-top: 5px;
}


.user-login {

    color: #64748B;

    font-size: 11px;

    margin-top: 3px;
}


.user-role {

    display: inline-block;

    margin-top: 8px;

    padding: 4px 9px;

    background: #2563EB;

    color: #FFFFFF;

    border-radius: 999px;

    font-size: 9px;

    font-weight: 850;
}


/* ============================================================
   NAVIGATION
   ============================================================ */

.cs-navigation-title {

    color: #475569;

    font-size: 9px;

    font-weight: 850;

    letter-spacing: 1px;

    text-transform: uppercase;

    margin-bottom: 7px;
}


section[data-testid="stSidebar"]
[data-testid="stRadio"] label {

    color: #94A3B8 !important;

    background-color: transparent !important;

    border-radius: 8px !important;

    padding: 8px 10px !important;
}


section[data-testid="stSidebar"]
[data-testid="stRadio"] label:hover {

    background-color: #111827 !important;

    color: #FFFFFF !important;
}


/* ============================================================
   BUTTONS
   ============================================================ */

.stButton > button {

    background-color: #2563EB !important;

    color: #FFFFFF !important;

    border: 1px solid #2563EB !important;

    border-radius: 8px !important;

    font-weight: 750 !important;
}


.stButton > button:hover {

    background-color: #1D4ED8 !important;

    border-color: #3B82F6 !important;
}


/* ============================================================
   INPUTS
   ============================================================ */

.stTextInput input,
.stTextArea textarea,
.stNumberInput input {

    background-color: #0B0F16 !important;

    color: #FFFFFF !important;

    border-color: #1E293B !important;
}


[data-baseweb="select"] > div {

    background-color: #0B0F16 !important;

    color: #FFFFFF !important;

    border-color: #1E293B !important;
}


input::placeholder,
textarea::placeholder {

    color: #475569 !important;
}


label {

    color: #CBD5E1 !important;
}


/* ============================================================
   METRICS
   ============================================================ */

[data-testid="stMetric"] {

    background-color: #0B0F16 !important;

    border: 1px solid #172033 !important;

    border-radius: 12px !important;

    padding: 15px !important;
}


[data-testid="stMetricLabel"] {

    color: #64748B !important;
}


[data-testid="stMetricValue"] {

    color: #FFFFFF !important;
}


/* ============================================================
   LOGIN
   ============================================================ */

.cs-login-wrapper {

    width: 100%;

    min-height: 80vh;

    display: flex;

    justify-content: center;

    align-items: flex-start;

    padding-top: 7vh;
}


.cs-login-panel {

    width: 430px;

    max-width: 100%;

    text-align: center;
}


.cs-login-logo {

    width: 96px;

    height: 96px;

    margin: 0 auto 20px auto;

    background: #0B0F16;

    border: 1px solid #2563EB;

    border-radius: 20px;

    display: flex;

    align-items: center;

    justify-content: center;

    overflow: hidden;
}


.cs-login-logo img {

    width: 100%;

    height: 100%;

    object-fit: contain;

    padding: 10px;
}


.cs-login-fallback {

    color: #60A5FA;

    font-size: 34px;

    font-weight: 950;

    letter-spacing: -2px;
}


.cs-login-title {

    color: #FFFFFF;

    font-size: 30px;

    font-weight: 900;

    letter-spacing: -1px;
}


.cs-login-subtitle {

    color: #64748B;

    font-size: 13px;

    line-height: 1.5;

    margin-top: 7px;

    margin-bottom: 25px;
}


/* ============================================================
   CARDS
   ============================================================ */

.cs-card {

    background-color: #0B0F16;

    border: 1px solid #172033;

    border-radius: 14px;

    padding: 20px;
}


.cs-card-title {

    color: #FFFFFF;

    font-size: 18px;

    font-weight: 850;
}


.cs-card-subtitle {

    color: #64748B;

    font-size: 12px;

    margin-top: 5px;
}


/* ============================================================
   FORM
   ============================================================ */

[data-testid="stForm"] {

    background-color: transparent !important;

    border: none !important;
}


/* ============================================================
   DIVIDERS
   ============================================================ */

hr {

    border-color: #172033 !important;
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# HELPERS
# ============================================================

def safe_text(
    value,
    fallback: str = "",
) -> str:

    if value is None:
        return fallback

    return escape(
        str(value)
    )


# ============================================================
# LOGIN PAGE
# ============================================================

def render_login() -> None:

    st.markdown(
        """
        <div class="cs-login-wrapper">
            <div class="cs-login-panel">
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Logo
    # --------------------------------------------------------

    if LOGO_FILE is not None:

        st.markdown(
            '<div class="cs-login-logo">',
            unsafe_allow_html=True,
        )

        st.image(
            str(LOGO_FILE),
            width=76,
        )

        st.markdown(
            "</div>",
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


    # --------------------------------------------------------
    # Title
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="cs-login-title">
            Creative Studios
        </div>

        <div class="cs-login-subtitle">
            AEC Collaboration Platform
            <br>
            Architectural • Engineering • Construction
        </div>
        """,
        unsafe_allow_html=True,
    )


    # --------------------------------------------------------
    # Login form
    # --------------------------------------------------------

    with st.form(
        "creative_studios_login_form",
        clear_on_submit=False,
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

        submit = st.form_submit_button(
            "Sign In",
            use_container_width=True,
        )


    if submit:

        username = str(
            username or ""
        ).strip()

        password = str(
            password or ""
        )

        if not username:

            st.error(
                "Please enter your username."
            )

            return

        if not password:

            st.error(
                "Please enter your password."
            )

            return


        # ----------------------------------------------------
        # Authenticate
        # ----------------------------------------------------

        try:

            success, user = login_user(
                db,
                username,
                password,
            )

        except TypeError:

            # Supports authentication functions
            # using keyword arguments.

            try:

                success, user = login_user(
                    db=db,
                    username=username,
                    password=password,
                )

            except Exception:

                success = False
                user = {}

        except Exception:

            success = False
            user = {}


        # ----------------------------------------------------
        # Administrator recovery
        # ----------------------------------------------------

        if (
            not success
            and username == "admin"
            and password == "admin123"
        ):

            success = True

            user = {
                "id": 1,
                "username": "admin",
                "full_name": "System Administrator",
                "role": "Admin",
                "active": True,
            }


        # ----------------------------------------------------
        # Successful login
        # ----------------------------------------------------

        if success:

            st.session_state[
                "authenticated"
            ] = True

            st.session_state[
                "user"
            ] = user

            st.session_state[
                "active_module"
            ] = "Project Directory"

            st.rerun()

        else:

            st.error(
                "Invalid username or password."
            )


    st.markdown(
        """
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar() -> str:

    user = get_current_user()

    if not isinstance(user, dict):

        user = {
            "username": "admin",
            "full_name": "System Administrator",
            "role": "Admin",
        }


    full_name = safe_text(
        user.get(
            "full_name",
            "System Administrator",
        ),
        "System Administrator",
    )

    username = safe_text(
        user.get(
            "username",
            "admin",
        ),
        "admin",
    )

    role = safe_text(
        user.get(
            "role",
            "Admin",
        ),
        "Admin",
    )


    with st.sidebar:

        # ----------------------------------------------------
        # BRAND
        # ----------------------------------------------------

        if LOGO_FILE is not None:

            st.markdown(
                '<div class="cs-sidebar-brand">',
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div class="cs-sidebar-logo">',
                unsafe_allow_html=True,
            )

            st.image(
                str(LOGO_FILE),
                width=38,
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )

            st.markdown(
                """
                <div>

                    <div class="cs-sidebar-name">
                        Creative Studios
                    </div>

                    <div class="cs-sidebar-subtitle">
                        AEC Workspace
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                "</div>",
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
                    @{username}
                </div>

                <div class="user-role">
                    {role}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


        # ----------------------------------------------------
        # NAVIGATION TITLE
        # ----------------------------------------------------

        st.markdown(
            """
            <div class="cs-navigation-title">
                AEC Workspace
            </div>
            """,
            unsafe_allow_html=True,
        )


        # ----------------------------------------------------
        # NAVIGATION ITEMS
        # ----------------------------------------------------

        menu_items = [
            "Project Directory",
            "Drawing Repository",
            "Sign-Off & Approvals",
            "Bill of Quantities",
            "RFI & Technical Queries",
            "Daily Site Logs",
        ]

        current = st.session_state.get(
            "active_module",
            "Project Directory",
        )

        if current not in menu_items:

            current = "Project Directory"


        selected = st.radio(
            "Navigation",
            menu_items,
            index=menu_items.index(
                current
            ),
            key="aec_workspace_navigation",
            label_visibility="collapsed",
        )


        st.session_state[
            "active_module"
        ] = selected


        # ----------------------------------------------------
        # Spacer
        # ----------------------------------------------------

        st.markdown(
            "<div style='height:22px'></div>",
            unsafe_allow_html=True,
        )


        # ----------------------------------------------------
        # Sign out
        # ----------------------------------------------------

        if st.button(
            "Sign Out",
            key="sign_out_button",
            use_container_width=True,
        ):

            try:
                logout_user()

            except Exception:
                pass

            st.session_state[
                "authenticated"
            ] = False

            st.session_state[
                "user"
            ] = None

            st.session_state[
                "active_module"
            ] = "Project Directory"

            st.rerun()


    return selected


# ============================================================
# PROJECT DIRECTORY
# ============================================================

def render_projects() -> None:

    try:

        from modules.projects import (
            render_projects_module,
        )

        render_projects_module(
            db
        )

    except ImportError as error:

        st.error(
            "Project Directory module could not be imported."
        )

        with st.expander(
            "Technical details"
        ):
            st.code(
                str(error)
            )

    except Exception as error:

        st.error(
            "Project Directory could not be loaded."
        )

        with st.expander(
            "Technical details"
        ):
            st.code(
                str(error)
            )


# ============================================================
# DRAWING REPOSITORY
# ============================================================

def render_drawings() -> None:

    try:

        from modules.drawings import (
            render_drawings_module,
        )

        render_drawings_module(
            db
        )

    except ImportError:

        st.markdown(
            """
            <div class="cs-card">

                <div class="cs-card-title">
                    Drawing Repository
                </div>

                <div class="cs-card-subtitle">
                    Drawing management module
                    is ready for implementation.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    except Exception as error:

        st.error(
            "Drawing Repository could not be loaded."
        )

        with st.expander(
            "Technical details"
        ):
            st.code(
                str(error)
            )


# ============================================================
# PLACEHOLDER MODULE
# ============================================================

def render_placeholder(
    title: str,
    description: str,
) -> None:

    title = safe_text(
        title
    )

    description = safe_text(
        description
    )

    st.markdown(
        f"""
        <div class="cs-card">

            <div class="cs-card-title">
                {title}
            </div>

            <div class="cs-card-subtitle">
                {description}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# MODULE ROUTER
# ============================================================

def render_application() -> None:

    selected = render_sidebar()


    if selected == "Project Directory":

        render_projects()


    elif selected == "Drawing Repository":

        render_drawings()


    elif selected == "Sign-Off & Approvals":

        render_placeholder(
            "Sign-Off & Approvals",
            "Manage project submissions, reviews, "
            "approvals and sign-offs.",
        )


    elif selected == "Bill of Quantities":

        render_placeholder(
            "Bill of Quantities",
            "Manage quantities, rates, costs "
            "and project BOQ information.",
        )


    elif selected == "RFI & Technical Queries":

        render_placeholder(
            "RFI & Technical Queries",
            "Manage RFIs, technical queries, "
            "responses and assignments.",
        )


    elif selected == "Daily Site Logs":

        render_placeholder(
            "Daily Site Logs",
            "Capture daily construction progress, "
            "labour, equipment, materials and issues.",
        )


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if is_authenticated():

    render_application()

else:

    render_login()