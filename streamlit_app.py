"""
Creative Studios
AEC Collaboration Platform

Main Streamlit Application
"""

import streamlit as st


# ============================================================
# IMPORTS
# ============================================================

from modules.utils import (
    ensure_logo_svg,
    get_logo_html,
    LOGO_FILE,
)

from modules.database import (
    load_memory,
)

from modules.auth import (
    login_user,
    require_auth,
)

from modules.projects import (
    render_projects_module,
)

from modules.drawings import (
    render_drawings_module,
)

from modules.approvals import (
    render_approvals_module,
)

from modules.boq import (
    render_boq_module,
)


try:
    from modules.rfi import (
        render_rfi_module,
    )
except ImportError:
    render_rfi_module = None


try:
    from modules.site_logs import (
        render_site_logs_module,
    )
except ImportError:
    render_site_logs_module = None


# ============================================================
# LOGO
# ============================================================

ensure_logo_svg()


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Creative Studios",
    page_icon=LOGO_FILE,
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# GLOBAL BLACK / BLUE THEME
# ============================================================

st.markdown(
    """
    <style>

    html,
    body,
    .stApp,
    [data-testid="stApp"],
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"] {

        background:#020617 !important;

        color:#E2E8F0 !important;
    }


    [data-testid="stHeader"] {

        background:#020617 !important;
    }


    /* ========================================================
       SIDEBAR
       ======================================================== */

    section[data-testid="stSidebar"] {

        background:
            linear-gradient(
                180deg,
                #000000 0%,
                #020617 60%,
                #071B3A 100%
            ) !important;

        border-right:
            1px solid #1D4ED8 !important;
    }


    section[data-testid="stSidebar"] > div {

        background:
            transparent !important;
    }


    section[data-testid="stSidebar"] * {

        color:#E2E8F0;
    }


    .sidebar-brand {

        text-align:center;

        padding:
            6px 0 10px 0;
    }


    .sidebar-title {

        color:#FFFFFF;

        font-size:20px;

        font-weight:850;

        margin-top:6px;
    }


    .sidebar-subtitle {

        color:#60A5FA;

        font-size:8px;

        font-weight:850;

        letter-spacing:1px;

        text-transform:uppercase;

        margin-top:4px;
    }


    .sidebar-section {

        color:#3B82F6;

        font-size:9px;

        font-weight:850;

        letter-spacing:1px;

        text-transform:uppercase;

        margin:
            12px 0 7px 0;
    }


    /* ========================================================
       SIDEBAR RADIO
       ======================================================== */

    section[data-testid="stSidebar"]
    .stRadio label {

        color:#CBD5E1 !important;

        background:
            transparent !important;

        border-radius:
            8px;

        padding:
            9px 10px;

        font-size:
            12px;

        font-weight:
            650;
    }


    section[data-testid="stSidebar"]
    .stRadio label:hover {

        background:
            #0F172A !important;

        color:
            #FFFFFF !important;
    }


    /* ========================================================
       USER
       ======================================================== */

    .sidebar-user {

        background:#050B18;

        border:1px solid #1E293B;

        border-left:3px solid #2563EB;

        border-radius:9px;

        padding:11px;
    }


    .user-label {

        color:#60A5FA;

        font-size:8px;

        font-weight:850;

        letter-spacing:1px;

        text-transform:uppercase;
    }


    .user-name {

        color:#FFFFFF;

        font-size:14px;

        font-weight:800;

        margin-top:4px;
    }


    .user-login {

        color:#64748B;

        font-size:10px;

        margin-top:2px;
    }


    .user-role {

        display:inline-block;

        margin-top:7px;

        padding:4px 8px;

        background:#2563EB;

        color:#FFFFFF;

        border-radius:999px;

        font-size:8px;

        font-weight:850;
    }


    /* ========================================================
       PAGE HEADER
       ======================================================== */

    .page-header {

        background:
            linear-gradient(
                135deg,
                #000000,
                #020617 65%,
                #071B3A
            );

        border:1px solid #1E293B;

        border-left:4px solid #2563EB;

        border-radius:12px;

        padding:22px 24px;

        margin-bottom:18px;
    }


    .page-title {

        color:#FFFFFF;

        font-size:28px;

        font-weight:850;
    }


    .page-subtitle {

        color:#64748B;

        font-size:12px;

        margin-top:4px;
    }


    /* ========================================================
       SECTION
       ======================================================== */

    .section-header {

        background:#050B18;

        border:1px solid #1E293B;

        border-left:4px solid #2563EB;

        border-radius:9px;

        padding:15px 18px;

        margin-bottom:15px;
    }


    .section-title {

        color:#FFFFFF;

        font-size:18px;

        font-weight:800;
    }


    .section-description {

        color:#64748B;

        font-size:11px;

        margin-top:3px;
    }


    /* ========================================================
       METRICS
       ======================================================== */

    [data-testid="stMetric"] {

        background:#050B18 !important;

        border:1px solid #1E293B;

        border-top:3px solid #2563EB;

        border-radius:9px;

        padding:12px;
    }


    [data-testid="stMetricLabel"] {

        color:#64748B !important;

        font-size:9px !important;

        font-weight:850 !important;
    }


    [data-testid="stMetricValue"] {

        color:#FFFFFF !important;

        font-weight:850 !important;
    }


    /* ========================================================
       INPUTS
       ======================================================== */

    .stTextInput input,
    .stTextArea textarea,
    .stNumberInput input {

        background:#050B18 !important;

        color:#FFFFFF !important;

        border:1px solid #334155 !important;

        border-radius:7px !important;
    }


    .stTextInput input:focus,
    .stTextArea textarea:focus,
    .stNumberInput input:focus {

        border-color:#2563EB !important;

        box-shadow:
            0 0 0 1px #2563EB !important;
    }


    /* ========================================================
       SELECT
       ======================================================== */

    div[data-baseweb="select"] > div {

        background:#050B18 !important;

        border:1px solid #334155 !important;

        color:#FFFFFF !important;
    }


    div[data-baseweb="select"] span {

        color:#FFFFFF !important;
    }


    /* ========================================================
       BUTTONS
       ======================================================== */

    .stButton > button {

        background:#0F172A !important;

        color:#FFFFFF !important;

        border:1px solid #334155 !important;

        border-radius:7px !important;

        font-weight:750 !important;
    }


    .stButton > button:hover {

        background:#2563EB !important;

        border-color:#2563EB !important;
    }


    .stFormSubmitButton > button {

        background:#2563EB !important;

        color:#FFFFFF !important;

        border:1px solid #2563EB !important;

        border-radius:7px !important;

        font-weight:800 !important;
    }


    .stFormSubmitButton > button:hover {

        background:#1D4ED8 !important;
    }


    /* ========================================================
       TABS
       ======================================================== */

    button[data-baseweb="tab"] {

        color:#64748B !important;

        font-weight:750;
    }


    button[data-baseweb="tab"][aria-selected="true"] {

        color:#60A5FA !important;
    }


    /* ========================================================
       EXPANDERS
       ======================================================== */

    [data-testid="stExpander"] {

        background:#050B18 !important;

        border:1px solid #1E293B !important;

        border-radius:8px;
    }


    /* ========================================================
       DIVIDER
       ======================================================== */

    hr {

        border-color:#1E293B !important;
    }


    /* ========================================================
       LOGIN
       ======================================================== */

    .login-page {

        min-height:82vh;

        display:flex;

        align-items:center;

        justify-content:center;

        background:#020617;

        padding:30px 15px;
    }


    .login-content {

        width:100%;

        max-width:430px;

        text-align:center;
    }


    .login-title {

        color:#FFFFFF;

        font-size:30px;

        font-weight:850;

        margin-top:14px;
    }


    .login-subtitle {

        color:#64748B;

        font-size:12px;

        margin-top:5px;

        margin-bottom:25px;
    }


    .login-label {

        color:#60A5FA;

        font-size:9px;

        font-weight:850;

        letter-spacing:1px;

        text-transform:uppercase;

        margin-bottom:8px;
    }


    /* Remove Streamlit form border */
    [data-testid="stForm"] {

        background:
            transparent !important;

        border:
            0 !important;

        padding:
            0 !important;
    }


    /* Remove unnecessary empty containers */
    .login-page > div {

        background:transparent !important;
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
# SESSION
# ============================================================

if "authenticated" not in st.session_state:

    st.session_state[
        "authenticated"
    ] = False


if "user" not in st.session_state:

    st.session_state[
        "user"
    ] = None


if "app_mode" not in st.session_state:

    st.session_state[
        "app_mode"
    ] = "Project Directory"


# ============================================================
# LOGIN PAGE
# ============================================================

if not st.session_state[
    "authenticated"
]:

    # Hide sidebar completely
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] {
            display:none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


    st.markdown(
        '<div class="login-page">',
        unsafe_allow_html=True,
    )


    st.markdown(
        '<div class="login-content">',
        unsafe_allow_html=True,
    )


    # LOGO
    st.markdown(
        get_logo_html(
            width=115
        ),
        unsafe_allow_html=True,
    )


    # TITLE
    st.markdown(
        """
        <div class="login-title">
            Creative Studios
        </div>

        <div class="login-subtitle">
            AEC Collaboration Platform
        </div>
        """,
        unsafe_allow_html=True,
    )


    # FORM
    with st.form(
        "login_form",
        border=False,
    ):

        username = st.text_input(
            "Username",
            placeholder="Username",
        )


        password = st.text_input(
            "Password",
            type="password",
            placeholder="Password",
        )


        submit = st.form_submit_button(
            "Sign In",
            type="primary",
            use_container_width=True,
        )


    if submit:

        username = (
            username or ""
        ).strip()

        password = (
            password or ""
        )


        if not username:

            st.markdown(
                """
                <div style="
                    color:#F87171;
                    font-size:12px;
                    margin-top:10px;
                ">
                    Username is required.
                </div>
                """,
                unsafe_allow_html=True,
            )


        elif not password:

            st.markdown(
                """
                <div style="
                    color:#F87171;
                    font-size:12px;
                    margin-top:10px;
                ">
                    Password is required.
                </div>
                """,
                unsafe_allow_html=True,
            )


        else:

            try:

                result = login_user(
                    db,
                    username,
                    password,
                )

                if result:

                    st.rerun()

                else:

                    st.markdown(
                        """
                        <div style="
                            color:#F87171;
                            font-size:12px;
                            margin-top:10px;
                        ">
                            Invalid username or password.
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            except Exception:

                st.markdown(
                    """
                    <div style="
                        color:#F87171;
                        font-size:12px;
                        margin-top:10px;
                    ">
                        Unable to authenticate.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


    st.markdown(
        """
        <div style="
            color:#334155;
            font-size:9px;
            margin-top:30px;
            letter-spacing:.7px;
        ">
            CREATIVE STUDIOS AEC PLATFORM
        </div>
        """,
        unsafe_allow_html=True,
    )


    st.markdown(
        "</div></div>",
        unsafe_allow_html=True,
    )


    st.stop()


# ============================================================
# AUTHENTICATED
# ============================================================

require_auth()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # --------------------------------------------------------
    # BRAND
    # --------------------------------------------------------

    st.markdown(
        '<div class="sidebar-brand">',
        unsafe_allow_html=True,
    )


    st.markdown(
        get_logo_html(
            width=78
        ),
        unsafe_allow_html=True,
    )


    st.markdown(
        """
        <div class="sidebar-title">
            Creative Studios
        </div>

        <div class="sidebar-subtitle">
            AEC Collaboration Platform
        </div>
        """,
        unsafe_allow_html=True,
    )


    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


    st.divider()


    # --------------------------------------------------------
    # NAVIGATION
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="sidebar-section">
            AEC Workspace
        </div>
        """,
        unsafe_allow_html=True,
    )


    navigation = [
        "Project Directory",
        "Drawing Repository",
        "Sign-Off & Approvals",
        "Bill of Quantities (BOQ)",
        "RFI & Technical Queries",
        "Daily Site Logs",
    ]


    current = st.session_state.get(
        "app_mode",
        "Project Directory",
    )


    if current not in navigation:

        current = navigation[0]


    selected_module = st.radio(
        "Navigation",
        navigation,
        index=navigation.index(
            current
        ),
        label_visibility="collapsed",
    )


    st.session_state[
        "app_mode"
    ] = selected_module


    st.divider()


    # --------------------------------------------------------
    # USER
    # --------------------------------------------------------

    user = st.session_state.get(
        "user"
    )


    if isinstance(
        user,
        dict,
    ):

        username = str(
            user.get(
                "username",
                "admin",
            )
        )

        display_name = str(
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

    else:

        username = str(
            user or "admin"
        )

        display_name = (
            "System Administrator"
        )

        role = "Admin"


    st.markdown(
        f"""
        <div class="sidebar-user">

            <div class="user-label">
                Signed In
            </div>

            <div class="user-name">
                {display_name}
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


    st.write("")


    # --------------------------------------------------------
    # SIGN OUT
    # --------------------------------------------------------

    if st.button(
        "Sign Out",
        use_container_width=True,
        key="logout",
    ):

        st.session_state[
            "authenticated"
        ] = False

        st.session_state[
            "user"
        ] = None

        st.session_state[
            "app_mode"
        ] = "Project Directory"

        st.rerun()


# ============================================================
# MODULE ROUTER
# ============================================================

if selected_module == "Project Directory":

    render_projects_module(
        db
    )


elif selected_module == "Drawing Repository":

    render_drawings_module(
        db
    )


elif selected_module == "Sign-Off & Approvals":

    render_approvals_module(
        db
    )


elif selected_module == "Bill of Quantities (BOQ)":

    render_boq_module(
        db
    )


elif selected_module == "RFI & Technical Queries":

    if render_rfi_module:

        render_rfi_module(
            db
        )

    else:

        st.markdown(
            """
            <div class="page-header">
                <div class="page-title">
                    RFI & Technical Queries
                </div>
                <div class="page-subtitle">
                    This module is not yet installed.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


elif selected_module == "Daily Site Logs":

    if render_site_logs_module:

        render_site_logs_module(
            db
        )

    else:

        st.markdown(
            """
            <div class="page-header">
                <div class="page-title">
                    Daily Site Logs
                </div>
                <div class="page-subtitle">
                    This module is not yet installed.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )