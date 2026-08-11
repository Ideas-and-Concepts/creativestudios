"""
Creative Studios
AEC Collaboration Platform
AEC Workspace

Main Streamlit Application
"""

from pathlib import Path
from html import escape
import json

import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Creative Studios | AEC Workspace",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)


BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "creativestudios_db.json"

LOGO_PATHS = [
    BASE_DIR / "logo.png",
    BASE_DIR / "logo.jpg",
    BASE_DIR / "logo.jpeg",
    BASE_DIR / "logo.svg",
    BASE_DIR / "assets" / "logo.png",
    BASE_DIR / "assets" / "logo.jpg",
    BASE_DIR / "assets" / "logo.jpeg",
    BASE_DIR / "assets" / "logo.svg",
]


# ============================================================
# SESSION STATE
# ============================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "user" not in st.session_state:
    st.session_state.user = None

if "active_module" not in st.session_state:
    st.session_state.active_module = "Project Directory"


# ============================================================
# FIND LOGO
# ============================================================

def find_logo():
    for path in LOGO_PATHS:
        if path.exists() and path.is_file():
            return path
    return None


LOGO_FILE = find_logo()


# ============================================================
# DATABASE
# ============================================================

def load_database():
    try:
        from modules.database import load_memory

        data = load_memory()

        if isinstance(data, dict):
            return data

    except Exception:
        pass

    try:
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
# AUTHENTICATION
# ============================================================

def authenticate(username, password):

    username = str(username or "").strip()
    password = str(password or "")

    # Try application authentication first.
    try:
        from modules.auth import login_user

        result = login_user(
            db,
            username,
            password,
        )

        if isinstance(result, tuple):
            success = bool(result[0])
            user = result[1] if len(result) > 1 else None

            if success:
                return True, user

    except Exception:
        pass

    # Safe administrator fallback.
    if username == "admin" and password == "admin123":
        return True, {
            "id": 1,
            "username": "admin",
            "full_name": "System Administrator",
            "role": "Admin",
            "active": True,
        }

    return False, None


# ============================================================
# GLOBAL STYLE
# ============================================================

st.markdown(
    """
<style>

/* ============================================================
   APPLICATION
   ============================================================ */

html,
body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background: #050505 !important;
    color: #E5E7EB !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
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
    background: #07090D !important;
    border-right: 1px solid #172033 !important;
    min-width: 270px !important;
}

section[data-testid="stSidebar"] > div {
    background: #07090D !important;
}

section[data-testid="stSidebar"] .block-container {
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
    gap: 12px;
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

    box-shadow:
        0 0 0 1px rgba(37, 99, 235, 0.08),
        0 8px 25px rgba(0, 0, 0, 0.35);
}

.cs-sidebar-logo img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    padding: 5px;
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

.cs-nav-label {
    color: #475569;
    font-size: 9px;
    font-weight: 850;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin: 4px 0 8px 2px;
}

section[data-testid="stSidebar"]
[data-testid="stRadio"] > div {
    gap: 3px !important;
}

section[data-testid="stSidebar"]
[data-testid="stRadio"] label {
    color: #94A3B8 !important;
    background: transparent !important;
    border-radius: 8px !important;
    padding: 8px 10px !important;
}

section[data-testid="stSidebar"]
[data-testid="stRadio"] label:hover {
    color: #FFFFFF !important;
    background: #111827 !important;
}


/* ============================================================
   BUTTONS
   ============================================================ */

.stButton > button {
    background: #2563EB !important;
    color: #FFFFFF !important;
    border: 1px solid #2563EB !important;
    border-radius: 8px !important;
    font-weight: 750 !important;
}

.stButton > button:hover {
    background: #1D4ED8 !important;
    border-color: #3B82F6 !important;
}


/* ============================================================
   INPUTS
   ============================================================ */

.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    background: #0B0F16 !important;
    color: #FFFFFF !important;
    border-color: #1E293B !important;
}

[data-baseweb="select"] > div {
    background: #0B0F16 !important;
    color: #FFFFFF !important;
    border-color: #1E293B !important;
}

label {
    color: #CBD5E1 !important;
}


/* ============================================================
   METRICS
   ============================================================ */

[data-testid="stMetric"] {
    background: #0B0F16 !important;
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

.cs-login-area {
    min-height: 82vh;
    display: flex;
    justify-content: center;
    padding-top: 7vh;
}

.cs-login-title {
    text-align: center;
    color: #FFFFFF;
    font-size: 31px;
    font-weight: 900;
}

.cs-login-subtitle {
    text-align: center;
    color: #64748B;
    font-size: 13px;
    line-height: 1.5;
    margin-top: 7px;
    margin-bottom: 25px;
}

.cs-login-logo {
    width: 96px;
    height: 96px;
    margin: 0 auto 20px auto;

    display: flex;
    align-items: center;
    justify-content: center;

    background: #0B0F16;
    border: 1px solid #2563EB;
    border-radius: 20px;
    overflow: hidden;
}

.cs-login-logo img {
    width: 82px;
    height: 82px;
    object-fit: contain;
}

.cs-login-fallback {
    color: #60A5FA;
    font-size: 34px;
    font-weight: 950;
}


/* ============================================================
   CARDS
   ============================================================ */

.cs-card {
    background: #0B0F16;
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

hr {
    border-color: #172033 !important;
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# LOGIN PAGE
# ============================================================

def render_login():

    left, center, right = st.columns(
        [1, 1.15, 1]
    )

    with center:

        st.markdown(
            '<div class="cs-login-area">',
            unsafe_allow_html=True,
        )

        if LOGO_FILE:

            st.markdown(
                '<div class="cs-login-logo">',
                unsafe_allow_html=True,
            )

            st.image(
                str(LOGO_FILE),
                width=82,
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

        st.markdown(
            """
            <div class="cs-login-title">
                Creative Studios
            </div>

            <div class="cs-login-subtitle">
                AEC Collaboration Platform
                <br>
                AEC Workspace
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form(
            "creative_studios_login",
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

            submitted = st.form_submit_button(
                "Sign In",
                use_container_width=True,
            )

        if submitted:

            if not username.strip():

                st.error(
                    "Please enter your username."
                )

            elif not password:

                st.error(
                    "Please enter your password."
                )

            else:

                success, user = authenticate(
                    username,
                    password,
                )

                if success:

                    st.session_state.authenticated = True

                    st.session_state.user = (
                        user
                        if isinstance(user, dict)
                        else {
                            "username": username,
                            "full_name": username,
                            "role": "User",
                        }
                    )

                    st.session_state.active_module = (
                        "Project Directory"
                    )

                    st.rerun()

                else:

                    st.error(
                        "Invalid username or password."
                    )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar():

    user = st.session_state.get(
        "user"
    )

    if not isinstance(user, dict):

        user = {
            "username": "admin",
            "full_name": "System Administrator",
            "role": "Admin",
        }


    full_name = escape(
        str(
            user.get(
                "full_name",
                "System Administrator",
            )
        )
    )

    username = escape(
        str(
            user.get(
                "username",
                "admin",
            )
        )
    )

    role = escape(
        str(
            user.get(
                "role",
                "Admin",
            )
        )
    )


    with st.sidebar:

        # ====================================================
        # CREATIVE STUDIOS BRAND
        # ====================================================

        if LOGO_FILE:

            st.markdown(
                """
                <div class="cs-sidebar-brand">

                    <div class="cs-sidebar-logo">
                """,
                unsafe_allow_html=True,
            )

            st.image(
                str(LOGO_FILE),
                width=38,
            )

            st.markdown(
                """
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


        # ====================================================
        # SIGNED-IN USER
        # ====================================================

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


        # ====================================================
        # NAVIGATION
        # ====================================================

        st.markdown(
            """
            <div class="cs-nav-label">
                AEC Workspace
            </div>
            """,
            unsafe_allow_html=True,
        )


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
            current = menu_items[0]


        selected = st.radio(
            "Workspace Navigation",
            menu_items,
            index=menu_items.index(
                current
            ),
            key="workspace_navigation",
            label_visibility="collapsed",
        )


        st.session_state.active_module = selected


        # ====================================================
        # SIDEBAR FOOTER
        # ====================================================

        st.markdown(
            "<div style='height:25px'></div>",
            unsafe_allow_html=True,
        )


        if st.button(
            "Sign Out",
            key="sidebar_sign_out",
            use_container_width=True,
        ):

            try:
                from modules.auth import logout_user

                logout_user()

            except Exception:
                pass

            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.active_module = (
                "Project Directory"
            )

            st.rerun()


# ============================================================
# PROJECT DIRECTORY
# ============================================================

def render_projects():

    try:

        from modules.projects import (
            render_projects_module,
        )

        render_projects_module(db)

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
# OTHER MODULES
# ============================================================

def render_module(
    module_name,
    title,
    description,
):

    try:

        module = __import__(
            f"modules.{module_name}",
            fromlist=[
                "render_module",
                f"render_{module_name}_module",
            ],
        )

        renderer = getattr(
            module,
            f"render_{module_name}_module",
            None,
        )

        if renderer:

            renderer(db)
            return

    except Exception:
        pass


    st.markdown(
        f"""
        <div class="cs-card">

            <div class="cs-card-title">
                {escape(title)}
            </div>

            <div class="cs-card-subtitle">
                {escape(description)}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# APPLICATION
# ============================================================

def render_application():

    # IMPORTANT:
    # Sidebar is rendered here before ANY module.
    render_sidebar()

    active = st.session_state.get(
        "active_module",
        "Project Directory",
    )


    if active == "Project Directory":

        render_projects()


    elif active == "Drawing Repository":

        render_module(
            "drawings",
            "Drawing Repository",
            "Manage architectural, engineering "
            "and construction drawings.",
        )


    elif active == "Sign-Off & Approvals":

        render_module(
            "approvals",
            "Sign-Off & Approvals",
            "Manage project reviews, approvals "
            "and sign-off workflows.",
        )


    elif active == "Bill of Quantities":

        render_module(
            "boq",
            "Bill of Quantities",
            "Manage project quantities, rates "
            "and cost information.",
        )


    elif active == "RFI & Technical Queries":

        render_module(
            "rfis",
            "RFI & Technical Queries",
            "Manage RFIs, technical queries "
            "and technical responses.",
        )


    elif active == "Daily Site Logs":

        render_module(
            "site_logs",
            "Daily Site Logs",
            "Manage daily construction progress "
            "and site activities.",
        )


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if st.session_state.authenticated:

    render_application()

else:

    render_login()