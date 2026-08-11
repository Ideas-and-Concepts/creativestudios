"""
Creative Studios
AEC Collaboration Platform

Main Streamlit application.
"""

from pathlib import Path
import base64
import html

import streamlit as st

from modules.database import load_memory


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
LOGO_FILE = BASE_DIR / "logo.svg"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Creative Studios | AEC Workspace",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# LOGO HELPER
# ============================================================

def get_logo_data_uri() -> str | None:
    """
    Safely load logo.svg as a base64 data URI.
    This avoids Streamlit static-file/path issues.
    """

    try:
        if not LOGO_FILE.exists():
            return None

        svg_data = LOGO_FILE.read_bytes()

        encoded = base64.b64encode(
            svg_data
        ).decode("utf-8")

        return f"data:image/svg+xml;base64,{encoded}"

    except Exception:
        return None


LOGO_URI = get_logo_data_uri()


# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(
    """
    <style>

    /* =====================================================
       GLOBAL APPLICATION
       ===================================================== */

    html,
    body,
    [data-testid="stAppViewContainer"],
    [data-testid="stApp"] {
        background: #050505 !important;
    }

    .stApp {
        background: #050505 !important;
        color: #F8FAFC !important;
    }

    [data-testid="stHeader"] {
        background: #050505 !important;
    }

    .main {
        background: #050505 !important;
    }

    .block-container {
        max-width: 1500px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }


    /* =====================================================
       SIDEBAR
       ===================================================== */

    [data-testid="stSidebar"] {
        background: #080808 !important;
        border-right: 1px solid #172033 !important;
    }

    [data-testid="stSidebar"] > div:first-child {
        background: #080808 !important;
    }


    /* =====================================================
       SIDEBAR BRAND
       ===================================================== */

    .cs-sidebar-brand {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 8px 2px 17px 2px;
    }

    .cs-sidebar-logo {
        width: 48px;
        height: 48px;
        min-width: 48px;

        display: flex;
        align-items: center;
        justify-content: center;

        background: #2563EB;
        color: #FFFFFF;

        border-radius: 12px;

        overflow: hidden;

        box-shadow:
            0 0 25px rgba(37, 99, 235, 0.25);
    }

    .cs-sidebar-logo img {
        width: 100%;
        height: 100%;
        object-fit: contain;
        padding: 7px;
    }

    .cs-sidebar-fallback {
        color: #FFFFFF;
        font-size: 17px;
        font-weight: 900;
        letter-spacing: -1px;
    }

    .cs-sidebar-name {
        color: #FFFFFF;
        font-size: 16px;
        font-weight: 900;
        line-height: 1.1;
        white-space: nowrap;
    }

    .cs-sidebar-subtitle {
        color: #64748B;
        font-size: 9px;
        font-weight: 800;
        letter-spacing: 1.1px;
        text-transform: uppercase;
        margin-top: 5px;
        white-space: nowrap;
    }

    .cs-divider {
        height: 1px;
        background: #172033;
        margin: 7px 0 17px 0;
    }


    /* =====================================================
       USER PANEL
       ===================================================== */

    .cs-user-card {
        background: #0C1016;
        border: 1px solid #172033;
        border-radius: 11px;
        padding: 13px;
        margin-bottom: 15px;
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
        font-size: 15px;
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


    /* =====================================================
       SIDEBAR NAVIGATION
       ===================================================== */

    .cs-section-title {
        color: #475569;
        font-size: 9px;
        font-weight: 850;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        margin: 3px 0 9px 0;
    }

    [data-testid="stSidebar"] .stRadio label {
        color: #CBD5E1 !important;
        font-size: 13px !important;
        font-weight: 600 !important;
    }

    [data-testid="stSidebar"] .stRadio label:hover {
        color: #FFFFFF !important;
    }

    [data-testid="stSidebar"] .stButton button {
        background: #0D1117 !important;
        color: #CBD5E1 !important;
        border: 1px solid #172033 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
    }

    [data-testid="stSidebar"] .stButton button:hover {
        background: #2563EB !important;
        border-color: #2563EB !important;
        color: #FFFFFF !important;
    }


    /* =====================================================
       MAIN CONTENT
       ===================================================== */

    h1,
    h2,
    h3,
    h4,
    h5,
    h6 {
        color: #FFFFFF !important;
    }

    p {
        color: #94A3B8;
    }


    /* =====================================================
       INPUTS
       ===================================================== */

    input,
    textarea {
        background: #0D1117 !important;
        color: #FFFFFF !important;
        border-color: #1E293B !important;
    }

    [data-baseweb="select"] > div {
        background: #0D1117 !important;
        color: #FFFFFF !important;
        border-color: #1E293B !important;
    }


    /* =====================================================
       METRICS
       ===================================================== */

    [data-testid="stMetric"] {
        background: #0B0F14;
        border: 1px solid #172033;
        border-radius: 12px;
        padding: 17px;
    }

    [data-testid="stMetricLabel"] {
        color: #64748B !important;
    }

    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
    }


    /* =====================================================
       BUTTONS
       ===================================================== */

    .stButton button {
        border-radius: 8px;
        font-weight: 700;
    }


    /* =====================================================
       LOGIN
       ===================================================== */

    .cs-login-wrapper {
        min-height: 80vh;

        display: flex;
        justify-content: center;
        align-items: center;
    }

    .cs-login-container {
        width: 100%;
        max-width: 410px;
    }

    .cs-login-logo {
        width: 78px;
        height: 78px;

        margin: 0 auto 18px auto;

        display: flex;
        align-items: center;
        justify-content: center;

        background: #2563EB;

        border-radius: 17px;

        overflow: hidden;

        box-shadow:
            0 0 35px rgba(37, 99, 235, 0.30);
    }

    .cs-login-logo img {
        width: 100%;
        height: 100%;
        object-fit: contain;
        padding: 10px;
    }

    .cs-login-fallback {
        color: #FFFFFF;
        font-size: 26px;
        font-weight: 900;
    }

    .cs-login-title {
        text-align: center;
        color: #FFFFFF;
        font-size: 30px;
        font-weight: 900;
        letter-spacing: -0.8px;
    }

    .cs-login-subtitle {
        text-align: center;
        color: #64748B;
        font-size: 13px;
        margin-top: 6px;
        margin-bottom: 27px;
    }

    .cs-login-label {
        color: #94A3B8;
        font-size: 10px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: .7px;
        margin-bottom: 5px;
    }


    /* =====================================================
       PROJECT CARDS
       ===================================================== */

    .project-card {
        background: #0B0F14;
        border: 1px solid #172033;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 10px;
    }

    .project-card:hover {
        border-color: #2563EB;
    }

    .project-title {
        color: #FFFFFF;
        font-size: 18px;
        font-weight: 850;
    }

    .project-meta {
        color: #64748B;
        font-size: 12px;
        margin-top: 5px;
    }

    .project-status {
        display: inline-block;
        padding: 4px 9px;
        border-radius: 999px;
        font-size: 9px;
        font-weight: 850;
        text-transform: uppercase;
    }

    .status-active {
        background: #0B3B82;
        color: #93C5FD;
    }

    .status-planning {
        background: #422006;
        color: #FCD34D;
    }

    .status-completed {
        background: #064E3B;
        color: #6EE7B7;
    }

    .status-on-hold {
        background: #27272A;
        color: #D4D4D8;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATABASE
# ============================================================

db = load_memory()


# ============================================================
# SESSION STATE
# ============================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "user" not in st.session_state:
    st.session_state.user = None

if "app_mode" not in st.session_state:
    st.session_state.app_mode = "Project Directory"


# ============================================================
# LOGIN PAGE
# ============================================================

if not st.session_state.authenticated:

    st.markdown(
        '<div class="cs-login-wrapper">'
        '<div class="cs-login-container">',
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Logo
    # --------------------------------------------------------

    if LOGO_URI:

        logo_html = (
            '<div class="cs-login-logo">'
            f'<img src="{LOGO_URI}" alt="Creative Studios Logo">'
            '</div>'
        )

    else:

        logo_html = (
            '<div class="cs-login-logo">'
            '<div class="cs-login-fallback">CS</div>'
            '</div>'
        )

    st.markdown(
        logo_html,
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

    # --------------------------------------------------------
    # Login form
    # --------------------------------------------------------

    with st.form(
        "creative_studios_login",
        clear_on_submit=False,
    ):

        st.markdown(
            '<div class="cs-login-label">Username</div>',
            unsafe_allow_html=True,
        )

        username = st.text_input(
            "Username",
            label_visibility="collapsed",
            placeholder="Enter username",
        )

        st.markdown(
            '<div class="cs-login-label">Password</div>',
            unsafe_allow_html=True,
        )

        password = st.text_input(
            "Password",
            type="password",
            label_visibility="collapsed",
            placeholder="Enter password",
        )

        submitted = st.form_submit_button(
            "Sign In",
            use_container_width=True,
        )

    if submitted:

        username_clean = username.strip().lower()

        authenticated_user = None

        for user in db.get(
            "users",
            [],
        ):

            if not isinstance(
                user,
                dict,
            ):
                continue

            stored_username = str(
                user.get(
                    "username",
                    "",
                )
            ).strip().lower()

            stored_password = str(
                user.get(
                    "password",
                    "",
                )
            )

            active = user.get(
                "active",
                True,
            )

            if (
                stored_username == username_clean
                and stored_password == password
                and active
            ):

                authenticated_user = user
                break

        if authenticated_user is not None:

            st.session_state.authenticated = True
            st.session_state.user = authenticated_user

            st.rerun()

        else:

            st.error(
                "Invalid username or password."
            )

    st.markdown(
        "</div></div>",
        unsafe_allow_html=True,
    )

    st.stop()


# ============================================================
# CURRENT USER
# ============================================================

current_user = st.session_state.get(
    "user",
    {},
)

if not isinstance(
    current_user,
    dict,
):

    current_user = {}


username = str(
    current_user.get(
        "username",
        "admin",
    )
)

full_name = str(
    current_user.get(
        "full_name",
        current_user.get(
            "name",
            "System Administrator",
        ),
    )
)

role = str(
    current_user.get(
        "role",
        "Admin",
    )
)


# Escape user values before putting them into HTML.

username_html = html.escape(
    username
)

full_name_html = html.escape(
    full_name
)

role_html = html.escape(
    role
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # --------------------------------------------------------
    # BRAND
    # --------------------------------------------------------

    if LOGO_URI:

        sidebar_logo = (
            '<div class="cs-sidebar-logo">'
            f'<img src="{LOGO_URI}" '
            'alt="Creative Studios Logo">'
            '</div>'
        )

    else:

        sidebar_logo = (
            '<div class="cs-sidebar-logo">'
            '<div class="cs-sidebar-fallback">'
            'CS'
            '</div>'
            '</div>'
        )

    st.markdown(
        f"""
        <div class="cs-sidebar-brand">

            {sidebar_logo}

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

    st.markdown(
        '<div class="cs-divider"></div>',
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # USER
    # --------------------------------------------------------

    st.markdown(
        f"""
        <div class="cs-user-card">

            <div class="user-label">
                Signed In
            </div>

            <div class="user-name">
                {full_name_html}
            </div>

            <div class="user-login">
                @{username_html}
            </div>

            <div class="user-role">
                {role_html}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="cs-divider"></div>',
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # NAVIGATION
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="cs-section-title">
            AEC Workspace
        </div>
        """,
        unsafe_allow_html=True,
    )

    navigation_items = [
        "Project Directory",
        "Drawing Repository",
        "Sign-Off & Approvals",
        "Bill of Quantities (BOQ)",
        "RFI & Technical Queries",
        "Daily Site Logs",
    ]

    current_mode = st.session_state.get(
        "app_mode",
        "Project Directory",
    )

    if current_mode not in navigation_items:

        current_mode = "Project Directory"

    selected_index = navigation_items.index(
        current_mode
    )

    app_mode = st.radio(
        "Select Module",
        navigation_items,
        index=selected_index,
        label_visibility="collapsed",
    )

    st.session_state.app_mode = app_mode

    st.markdown(
        '<div class="cs-divider"></div>',
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # SIGN OUT
    # --------------------------------------------------------

    if st.button(
        "Sign Out",
        use_container_width=True,
    ):

        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.app_mode = "Project Directory"

        st.rerun()


# ============================================================
# APPLICATION ROUTER
# ============================================================

if app_mode == "Project Directory":

    from modules.projects import render_projects_module

    render_projects_module(
        db
    )


elif app_mode == "Drawing Repository":

    st.title("Drawing Repository")

    st.caption(
        "Central repository for architectural, structural, "
        "MEP and construction drawings."
    )

    st.info(
        "Drawing Repository module is ready for integration."
    )


elif app_mode == "Sign-Off & Approvals":

    st.title("Sign-Off & Approvals")

    st.caption(
        "Review, approval and document sign-off workflow."
    )

    st.info(
        "Sign-Off & Approvals module is ready for integration."
    )


elif app_mode == "Bill of Quantities (BOQ)":

    st.title("Bill of Quantities")

    st.caption(
        "Project quantities, rates, costs and BOQ management."
    )

    st.info(
        "BOQ module is ready for integration."
    )


elif app_mode == "RFI & Technical Queries":

    st.title("RFI & Technical Queries")

    st.caption(
        "Technical queries and request-for-information workflow."
    )

    st.info(
        "RFI module is ready for integration."
    )


elif app_mode == "Daily Site Logs":

    st.title("Daily Site Logs")

    st.caption(
        "Daily construction activities, manpower, equipment "
        "and site observations."
    )

    st.info(
        "Daily Site Logs module is ready for integration."
    )