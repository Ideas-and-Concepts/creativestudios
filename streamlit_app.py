"""
Creative Studios
AEC Collaboration Platform

Main Application Controller
"""

import streamlit as st


# ============================================================
# MODULES
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


# Optional modules
try:
    from modules.rfi import render_rfi_module
except ImportError:
    render_rfi_module = None


try:
    from modules.site_logs import render_site_logs_module
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
    page_title="Creative Studios | AEC Platform",
    page_icon=LOGO_FILE,
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# BLACK + BLUE DESIGN SYSTEM
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       GLOBAL APPLICATION
       ======================================================== */

    html,
    body,
    [data-testid="stAppViewContainer"],
    [data-testid="stApp"] {

        background:#020617 !important;

        color:#E2E8F0 !important;
    }


    .stApp {

        background:#020617 !important;

        color:#E2E8F0 !important;
    }


    [data-testid="stAppViewContainer"] {

        background:#020617 !important;
    }


    .main {

        background:#020617 !important;
    }


    /* ========================================================
       MAIN CONTENT
       ======================================================== */

    [data-testid="stMain"] {

        background:#020617 !important;
    }


    [data-testid="stMainBlockContainer"] {

        background:#020617 !important;

        color:#E2E8F0 !important;
    }


    /* ========================================================
       HEADER
       ======================================================== */

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
                #020617 55%,
                #071B3A 100%
            ) !important;

        border-right:
            1px solid #1D4ED8;

        box-shadow:
            8px 0 35px
            rgba(0,0,0,.45);
    }


    section[data-testid="stSidebar"] > div {

        background:transparent !important;
    }


    section[data-testid="stSidebar"] * {

        color:#E2E8F0;
    }


    /* ========================================================
       SIDEBAR BRAND
       ======================================================== */

    .sidebar-brand {

        text-align:center;

        padding:
            8px 4px 12px 4px;
    }


    .sidebar-brand-title {

        color:#FFFFFF;

        font-size:21px;

        font-weight:850;

        margin-top:6px;
    }


    .sidebar-brand-subtitle {

        color:#60A5FA;

        font-size:9px;

        font-weight:800;

        letter-spacing:1px;

        text-transform:uppercase;

        margin-top:4px;
    }


    /* ========================================================
       SIDEBAR NAVIGATION
       ======================================================== */

    .sidebar-section-title {

        color:#3B82F6;

        font-size:10px;

        font-weight:850;

        letter-spacing:1px;

        text-transform:uppercase;

        margin:
            12px 0 8px 0;
    }


    section[data-testid="stSidebar"]
    .stRadio > div {

        gap:4px;
    }


    section[data-testid="stSidebar"]
    .stRadio label {

        background:
            transparent !important;

        color:#CBD5E1 !important;

        padding:
            10px 11px;

        border-radius:
            8px;

        font-size:
            13px;

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
       SIDEBAR USER CARD
       ======================================================== */

    .sidebar-user-card {

        background:
            #050B18;

        border:
            1px solid #1E293B;

        border-left:
            3px solid #2563EB;

        border-radius:
            10px;

        padding:
            12px;
    }


    .sidebar-user-label {

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


    .sidebar-user-name {

        color:
            #FFFFFF;

        font-size:
            15px;

        font-weight:
            800;

        margin-top:
            5px;
    }


    .sidebar-user-login {

        color:
            #64748B;

        font-size:
            11px;

        margin-top:
            3px;
    }


    .sidebar-user-role {

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


    /* ========================================================
       TEXT
       ======================================================== */

    h1,
    h2,
    h3,
    h4,
    p,
    label {

        color:
            #E2E8F0 !important;
    }


    .stMarkdown {

        color:
            #CBD5E1;
    }


    /* ========================================================
       PAGE HEADER
       ======================================================== */

    .page-header {

        background:
            linear-gradient(
                135deg,
                #000000 0%,
                #020617 60%,
                #071B3A 100%
            );

        border:
            1px solid #1E293B;

        border-left:
            5px solid #2563EB;

        border-radius:
            14px;

        padding:
            25px 28px;

        margin-bottom:
            20px;

        box-shadow:
            0 12px 30px
            rgba(0,0,0,.25);
    }


    .page-title {

        color:
            #FFFFFF;

        font-size:
            29px;

        font-weight:
            850;
    }


    .page-subtitle {

        color:
            #64748B;

        font-size:
            13px;

        margin-top:
            5px;
    }


    /* ========================================================
       SECTION HEADER
       ======================================================== */

    .section-header {

        background:
            #050B18;

        border:
            1px solid #1E293B;

        border-left:
            4px solid #2563EB;

        border-radius:
            10px;

        padding:
            17px 20px;

        margin-bottom:
            18px;
    }


    .section-title {

        color:
            #FFFFFF;

        font-size:
            20px;

        font-weight:
            800;
    }


    .section-description {

        color:
            #64748B;

        font-size:
            12px;

        margin-top:
            4px;
    }


    /* ========================================================
       METRICS
       ======================================================== */

    [data-testid="stMetric"] {

        background:
            #050B18 !important;

        border:
            1px solid #1E293B;

        border-top:
            3px solid #2563EB;

        border-radius:
            10px;

        padding:
            14px;

        box-shadow:
            0 8px 20px
            rgba(0,0,0,.20);
    }


    [data-testid="stMetricLabel"] {

        color:
            #64748B !important;

        font-size:
            10px !important;

        font-weight:
            800 !important;
    }


    [data-testid="stMetricValue"] {

        color:
            #FFFFFF !important;

        font-weight:
            850 !important;
    }


    /* ========================================================
       INFORMATION CARDS
       ======================================================== */

    .dark-info {

        background:
            #050B18;

        border:
            1px solid #1E293B;

        border-radius:
            8px;

        padding:
            10px;

        min-height:
            58px;
    }


    .dark-label {

        color:
            #64748B;

        font-size:
            8px;

        font-weight:
            850;

        letter-spacing:
            .8px;
    }


    .dark-value {

        color:
            #E2E8F0;

        font-size:
            12px;

        font-weight:
            650;

        margin-top:
            5px;
    }


    .blue-value {

        color:
            #60A5FA !important;
    }


    /* ========================================================
       INPUTS
       ======================================================== */

    .stTextInput input,
    .stTextArea textarea,
    .stNumberInput input {

        background:
            #050B18 !important;

        color:
            #FFFFFF !important;

        border:
            1px solid #334155 !important;

        border-radius:
            8px !important;
    }


    .stTextInput input:focus,
    .stTextArea textarea:focus,
    .stNumberInput input:focus {

        border-color:
            #2563EB !important;

        box-shadow:
            0 0 0 1px #2563EB !important;
    }


    /* ========================================================
       SELECTBOX
       ======================================================== */

    div[data-baseweb="select"] > div {

        background:
            #050B18 !important;

        color:
            #FFFFFF !important;

        border:
            1px solid #334155 !important;
    }


    div[data-baseweb="select"] span {

        color:
            #FFFFFF !important;
    }


    /* ========================================================
       BUTTONS
       ======================================================== */

    .stButton > button {

        background:
            #0F172A !important;

        color:
            #FFFFFF !important;

        border:
            1px solid #334155 !important;

        border-radius:
            8px !important;

        font-weight:
            750 !important;
    }


    .stButton > button:hover {

        background:
            #2563EB !important;

        border-color:
            #2563EB !important;

        color:
            #FFFFFF !important;
    }


    .stFormSubmitButton > button {

        background:
            #2563EB !important;

        color:
            #FFFFFF !important;

        border:
            1px solid #2563EB !important;

        border-radius:
            8px !important;

        font-weight:
            800 !important;
    }


    .stFormSubmitButton > button:hover {

        background:
            #1D4ED8 !important;
    }


    /* ========================================================
       TABS
       ======================================================== */

    button[data-baseweb="tab"] {

        color:
            #64748B !important;

        font-weight:
            750;
    }


    button[data-baseweb="tab"][aria-selected="true"] {

        color:
            #60A5FA !important;
    }


    /* ========================================================
       EXPANDERS
       ======================================================== */

    [data-testid="stExpander"] {

        background:
            #050B18 !important;

        border:
            1px solid #1E293B !important;

        border-radius:
            9px;
    }


    /* ========================================================
       ALERTS
       ======================================================== */

    [data-testid="stAlert"] {

        background:
            #0F172A;

        border-radius:
            8px;
    }


    /* ========================================================
       DIVIDER
       ======================================================== */

    hr {

        border-color:
            #1E293B !important;
    }


    /* ========================================================
       CAPTIONS
       ======================================================== */

    .stCaption {

        color:
            #64748B !important;
    }


    /* ========================================================
       SCROLLBAR
       ======================================================== */

    ::-webkit-scrollbar {

        width:
            8px;
    }


    ::-webkit-scrollbar-track {

        background:
            #020617;
    }


    ::-webkit-scrollbar-thumb {

        background:
            #1E3A8A;

        border-radius:
            10px;
    }


    ::-webkit-scrollbar-thumb:hover {

        background:
            #2563EB;
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
# LOGIN
# ============================================================

if not st.session_state[
    "authenticated"
]:

    st.markdown(
        """
        <style>

        section[data-testid="stSidebar"] {
            display:none;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


    left, center, right = st.columns(
        [1, 1.1, 1]
    )


    with center:

        st.markdown(
            "<br><br>",
            unsafe_allow_html=True,
        )


        st.markdown(
            """
            <div style="
                background:#050B18;
                border:1px solid #1E293B;
                border-top:4px solid #2563EB;
                border-radius:16px;
                padding:40px;
                box-shadow:
                    0 25px 60px
                    rgba(0,0,0,.45);
            ">
            """,
            unsafe_allow_html=True,
        )


        st.markdown(
            get_logo_html(
                width=125
            ),
            unsafe_allow_html=True,
        )


        st.markdown(
            """
            <div style="
                text-align:center;
                color:#FFFFFF;
                font-size:29px;
                font-weight:850;
                margin-top:12px;
            ">
                Creative Studios
            </div>

            <div style="
                text-align:center;
                color:#64748B;
                font-size:13px;
                margin-top:5px;
                margin-bottom:25px;
            ">
                Architectural, Engineering &
                Construction Collaboration Platform
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


            submit = st.form_submit_button(
                "Sign In",
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

                    st.warning(
                        "Username is required."
                    )


                elif not password:

                    st.warning(
                        "Password is required."
                    )


                elif login_user(
                    db,
                    username,
                    password,
                ):

                    st.rerun()


                else:

                    st.error(
                        "Invalid username or password."
                    )


        st.markdown(
            """
            <div style="
                text-align:center;
                color:#475569;
                font-size:10px;
                margin-top:20px;
            ">
                CREATIVE STUDIOS AEC PLATFORM
            </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


    st.stop()


# ============================================================
# AUTH
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
            width=82
        ),
        unsafe_allow_html=True,
    )


    st.markdown(
        """
        <div class="sidebar-brand-title">
            Creative Studios
        </div>

        <div class="sidebar-brand-subtitle">
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
        <div class="sidebar-section-title">
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

        current = "Project Directory"


    selected_module = st.radio(
        "AEC Navigation",
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

        display_name = user.get(
            "name",
            user.get(
                "full_name",
                user.get(
                    "username",
                    "User",
                ),
            ),
        )

        username = user.get(
            "username",
            "",
        )

        role = user.get(
            "role",
            "User",
        )

    else:

        display_name = str(
            user or "User"
        )

        username = ""
        role = "User"


    # IMPORTANT:
    # Keep the sidebar card as plain Streamlit
    # components rather than nested raw HTML.

    st.markdown(
        '<div class="sidebar-user-card">',
        unsafe_allow_html=True,
    )


    st.markdown(
        '<div class="sidebar-user-label">'
        'Signed In'
        '</div>',
        unsafe_allow_html=True,
    )


    st.markdown(
        f'<div class="sidebar-user-name">'
        f'{display_name}'
        f'</div>',
        unsafe_allow_html=True,
    )


    st.markdown(
        f'<div class="sidebar-user-login">'
        f'@{username}'
        f'</div>',
        unsafe_allow_html=True,
    )


    st.markdown(
        f'<div class="sidebar-user-role">'
        f'{role}'
        f'</div>',
        unsafe_allow_html=True,
    )


    st.markdown(
        '</div>',
        unsafe_allow_html=True,
    )


    st.write("")


    # --------------------------------------------------------
    # SIGN OUT
    # --------------------------------------------------------

    if st.button(
        "Sign Out",
        use_container_width=True,
        key="sidebar_logout",
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

        st.info(
            "RFI module is not currently available."
        )


elif selected_module == "Daily Site Logs":

    if render_site_logs_module:

        render_site_logs_module(
            db
        )

    else:

        st.info(
            "Daily Site Logs module is not currently available."
        )