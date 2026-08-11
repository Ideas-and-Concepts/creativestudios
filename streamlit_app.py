"""
Creative Studios
AEC Collaboration Platform

Main Streamlit Application
"""

from pathlib import Path
import streamlit as st


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
MODULES_DIR = BASE_DIR / "modules"
LOGO_FILE = BASE_DIR / "logo.svg"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Creative Studios — AEC Platform",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(
    """
    <style>

    /* =====================================================
       GLOBAL
       ===================================================== */

    html,
    body,
    [data-testid="stAppViewContainer"],
    [data-testid="stApp"] {

        background:
            #000000 !important;

        color:
            #FFFFFF !important;
    }


    [data-testid="stHeader"] {

        background:
            #000000 !important;

        border-bottom:
            1px solid #111827 !important;
    }


    [data-testid="stToolbar"] {

        background:
            #000000 !important;
    }


    /* Remove Streamlit decoration */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }


    /* =====================================================
       MAIN CONTENT
       ===================================================== */

    .block-container {

        max-width:
            1500px;

        padding-top:
            1.5rem;

        padding-bottom:
            3rem;
    }


    /* =====================================================
       SIDEBAR
       ===================================================== */

    [data-testid="stSidebar"] {

        background:
            #050505 !important;

        border-right:
            1px solid #172033 !important;
    }


    [data-testid="stSidebar"] > div:first-child {

        background:
            #050505 !important;

        padding-top:
            1rem;
    }


    [data-testid="stSidebar"] * {

        color:
            #E5E7EB;
    }


    /* =====================================================
       SIDEBAR BRAND
       ===================================================== */

    .sidebar-brand {

        padding:
            8px 8px 18px 8px;

        text-align:
            center;
    }


    .sidebar-logo {

        width:
            82px;

        height:
            82px;

        object-fit:
            contain;

        margin:
            0 auto 8px auto;

        display:
            block;
    }


    .sidebar-brand-name {

        color:
            #FFFFFF;

        font-size:
            19px;

        font-weight:
            800;

        letter-spacing:
            -0.3px;
    }


    .sidebar-brand-subtitle {

        color:
            #60A5FA;

        font-size:
            9px;

        font-weight:
            700;

        letter-spacing:
            1.3px;

        text-transform:
            uppercase;

        margin-top:
            4px;
    }


    .sidebar-divider {

        height:
            1px;

        background:
            #1E293B;

        margin:
            5px 0 18px 0;
    }


    /* =====================================================
       SIDEBAR USER
       ===================================================== */

    .sidebar-user {

        background:
            #080B10;

        border:
            1px solid #172033;

        border-radius:
            10px;

        padding:
            13px;

        margin:
            0 0 18px 0;
    }


    .user-label {

        color:
            #60A5FA;

        font-size:
            9px;

        font-weight:
            800;

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
            #94A3B8;

        font-size:
            11px;

        margin-top:
            3px;
    }


    .user-role {

        display:
            inline-block;

        margin-top:
            9px;

        padding:
            4px 9px;

        background:
            #2563EB;

        color:
            #FFFFFF;

        border-radius:
            999px;

        font-size:
            9px;

        font-weight:
            800;
    }


    /* =====================================================
       SIDEBAR NAVIGATION
       ===================================================== */

    .navigation-title {

        color:
            #64748B;

        font-size:
            9px;

        font-weight:
            800;

        letter-spacing:
            1.2px;

        text-transform:
            uppercase;

        margin:
            0 0 8px 4px;
    }


    [data-testid="stSidebar"] .stRadio > label {

        display:
            none;
    }


    [data-testid="stSidebar"] .stRadio > div {

        gap:
            5px;
    }


    [data-testid="stSidebar"] .stRadio label {

        background:
            transparent;

        border:
            1px solid transparent;

        border-radius:
            8px;

        padding:
            9px 10px;

        transition:
            all 0.15s ease;

        cursor:
            pointer;
    }


    [data-testid="stSidebar"] .stRadio label:hover {

        background:
            #0B1220;

        border-color:
            #172033;
    }


    [data-testid="stSidebar"] .stRadio label:has(
        input:checked
    ) {

        background:
            #0D1B35;

        border:
            1px solid #2563EB;
    }


    /* =====================================================
       PAGE HEADER
       ===================================================== */

    .page-header {

        margin-bottom:
            20px;
    }


    .page-title {

        color:
            #FFFFFF;

        font-size:
            30px;

        font-weight:
            850;

        letter-spacing:
            -0.8px;
    }


    .page-subtitle {

        color:
            #94A3B8;

        font-size:
            13px;

        margin-top:
            5px;

        line-height:
            1.6;
    }


    /* =====================================================
       KPI CARDS
       ===================================================== */

    [data-testid="stMetric"] {

        background:
            #070707;

        border:
            1px solid #172033;

        border-radius:
            10px;

        padding:
            15px;
    }


    [data-testid="stMetricLabel"] {

        color:
            #64748B !important;

        font-size:
            10px !important;

        text-transform:
            uppercase;

        letter-spacing:
            0.7px;
    }


    [data-testid="stMetricValue"] {

        color:
            #FFFFFF !important;
    }


    /* =====================================================
       PROJECT CARDS
       ===================================================== */

    .project-card {

        background:
            #070707;

        border:
            1px solid #172033;

        border-radius:
            12px;

        padding:
            18px;

        margin:
            12px 0;

        transition:
            border-color 0.15s ease,
            transform 0.15s ease;
    }


    .project-card:hover {

        border-color:
            #2563EB;

        transform:
            translateY(-1px);
    }


    .project-card-top {

        display:
            flex;

        justify-content:
            space-between;

        align-items:
            flex-start;

        gap:
            15px;
    }


    .project-name {

        color:
            #FFFFFF;

        font-size:
            18px;

        font-weight:
            800;
    }


    .project-code {

        color:
            #60A5FA;

        font-size:
            11px;

        margin-top:
            4px;

        font-weight:
            650;
    }


    .project-phase {

        color:
            #94A3B8;

        font-size:
            11px;

        margin-top:
            14px;

        padding-bottom:
            12px;

        border-bottom:
            1px solid #111827;
    }


    .project-phase strong {

        color:
            #E2E8F0;
    }


    .project-details {

        display:
            grid;

        grid-template-columns:
            repeat(4, 1fr);

        gap:
            15px;

        margin-top:
            14px;
    }


    .detail-label {

        color:
            #475569;

        font-size:
            8px;

        font-weight:
            800;

        letter-spacing:
            0.9px;
    }


    .detail-value {

        color:
            #CBD5E1;

        font-size:
            11px;

        margin-top:
            4px;
    }


    .project-description {

        color:
            #64748B;

        font-size:
            11px;

        line-height:
            1.6;

        margin-top:
            14px;
    }


    /* =====================================================
       STATUS
       ===================================================== */

    .project-status {

        display:
            inline-block;

        padding:
            5px 9px;

        border-radius:
            999px;

        font-size:
            8px;

        font-weight:
            850;

        letter-spacing:
            0.6px;

        white-space:
            nowrap;
    }


    .status-active {

        background:
            #052E16;

        color:
            #4ADE80;

        border:
            1px solid #166534;
    }


    .status-planning {

        background:
            #172554;

        color:
            #60A5FA;

        border:
            1px solid #1D4ED8;
    }


    .status-completed {

        background:
            #042F2E;

        color:
            #5EEAD4;

        border:
            1px solid #0F766E;
    }


    .status-hold {

        background:
            #422006;

        color:
            #FBBF24;

        border:
            1px solid #92400E;
    }


    .status-cancelled {

        background:
            #450A0A;

        color:
            #F87171;

        border:
            1px solid #991B1B;
    }


    .status-default {

        background:
            #111827;

        color:
            #94A3B8;

        border:
            1px solid #334155;
    }


    /* =====================================================
       FORMS
       ===================================================== */

    .stTextInput input,
    .stTextArea textarea,
    .stNumberInput input {

        background:
            #050505 !important;

        color:
            #FFFFFF !important;

        border:
            1px solid #1E293B !important;

        border-radius:
            7px !important;
    }


    .stSelectbox div[data-baseweb="select"] > div {

        background:
            #050505 !important;

        border-color:
            #1E293B !important;

        color:
            #FFFFFF !important;
    }


    /* =====================================================
       BUTTONS
       ===================================================== */

    .stButton button,
    .stFormSubmitButton button {

        background:
            #2563EB !important;

        color:
            #FFFFFF !important;

        border:
            1px solid #3B82F6 !important;

        border-radius:
            7px !important;

        font-weight:
            750 !important;
    }


    .stButton button:hover,
    .stFormSubmitButton button:hover {

        background:
            #1D4ED8 !important;

        border-color:
            #60A5FA !important;
    }


    /* =====================================================
       TABS
       ===================================================== */

    .stTabs [data-baseweb="tab-list"] {

        background:
            #050505;

        border-bottom:
            1px solid #172033;

        gap:
            4px;
    }


    .stTabs [data-baseweb="tab"] {

        color:
            #64748B;

        font-size:
            12px;
    }


    .stTabs [aria-selected="true"] {

        color:
            #60A5FA !important;

        border-bottom-color:
            #2563EB !important;
    }


    /* =====================================================
       CUSTOM MESSAGES
       ===================================================== */

    .app-message {

        border-radius:
            8px;

        padding:
            11px 14px;

        margin:
            10px 0;

        font-size:
            12px;
    }


    .app-message.success {

        background:
            #052E16;

        border:
            1px solid #166534;

        border-left:
            4px solid #22C55E;

        color:
            #BBF7D0;
    }


    .app-message.error {

        background:
            #450A0A;

        border:
            1px solid #991B1B;

        border-left:
            4px solid #EF4444;

        color:
            #FECACA;
    }


    .app-message.info {

        background:
            #071B3A;

        border:
            1px solid #1D4ED8;

        border-left:
            4px solid #2563EB;

        color:
            #BFDBFE;
    }


    /* =====================================================
       EMPTY STATE
       ===================================================== */

    .empty-state {

        background:
            #070707;

        border:
            1px dashed #1E293B;

        border-radius:
            12px;

        padding:
            50px 20px;

        text-align:
            center;

        margin-top:
            15px;
    }


    .empty-title {

        color:
            #FFFFFF;

        font-size:
            18px;

        font-weight:
            800;
    }


    .empty-text {

        color:
            #64748B;

        font-size:
            12px;

        margin-top:
            7px;
    }


    /* =====================================================
       LOGIN PAGE
       ===================================================== */

    .login-page {

        min-height:
            80vh;

        display:
            flex;

        align-items:
            center;

        justify-content:
            center;
    }


    .login-panel {

        width:
            390px;

        background:
            #050505;

        border:
            1px solid #172033;

        border-radius:
            14px;

        padding:
            32px;

        box-shadow:
            0 20px 70px rgba(0,0,0,0.55);
    }


    .login-logo {

        width:
            105px;

        height:
            105px;

        object-fit:
            contain;

        display:
            block;

        margin:
            0 auto 15px auto;
    }


    .login-title {

        color:
            #FFFFFF;

        text-align:
            center;

        font-size:
            25px;

        font-weight:
            850;
    }


    .login-subtitle {

        color:
            #64748B;

        text-align:
            center;

        font-size:
            11px;

        margin:
            6px 0 24px 0;
    }


    /* =====================================================
       MOBILE
       ===================================================== */

    @media (max-width: 900px) {

        .project-details {

            grid-template-columns:
                repeat(2, 1fr);
        }

    }


    @media (max-width: 600px) {

        .project-details {

            grid-template-columns:
                1fr;
        }

        .login-panel {

            width:
                100%;

            max-width:
                390px;

            margin:
                15px;
        }

    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SAFE MODULE IMPORTS
# ============================================================

from modules.database import load_memory


# ============================================================
# LOGO
# ============================================================

def logo_data_uri():

    try:

        if not LOGO_FILE.exists():
            return None

        svg = LOGO_FILE.read_text(
            encoding="utf-8"
        )

        import base64

        encoded = base64.b64encode(
            svg.encode("utf-8")
        ).decode("utf-8")

        return (
            "data:image/svg+xml;base64,"
            + encoded
        )

    except Exception:
        return None


# ============================================================
# LOGIN
# ============================================================

def login_user(db, username, password):

    users = db.get(
        "users",
        [],
    )

    username = str(
        username or ""
    ).strip().lower()

    password = str(
        password or ""
    )


    for user in users:

        stored_username = str(
            user.get(
                "username",
                "",
            )
        ).strip().lower()


        if (
            stored_username == username
            and str(
                user.get(
                    "password",
                    "",
                )
            ) == password
        ):

            st.session_state[
                "authenticated"
            ] = True

            st.session_state[
                "user"
            ] = user

            return True


    return False


# ============================================================
# LOGIN PAGE
# ============================================================

def render_login(db):

    logo = logo_data_uri()


    st.markdown(
        '<div class="login-page">',
        unsafe_allow_html=True,
    )


    st.markdown(
        '<div class="login-panel">',
        unsafe_allow_html=True,
    )


    if logo:

        st.markdown(
            f"""
            <img
                class="login-logo"
                src="{logo}"
            >
            """,
            unsafe_allow_html=True,
        )


    else:

        st.markdown(
            """
            <div style="
                text-align:center;
                color:#2563EB;
                font-size:42px;
                margin-bottom:15px;
            ">
                ◆
            </div>
            """,
            unsafe_allow_html=True,
        )


    st.markdown(
        """
        <div class="login-title">
            Creative Studios
        </div>

        <div class="login-subtitle">
            Architectural, Engineering &
            Construction Collaboration
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

        if login_user(
            db,
            username,
            password,
        ):

            st.rerun()

        else:

            st.markdown(
                """
                <div class="app-message error">
                    Invalid username or password.
                </div>
                """,
                unsafe_allow_html=True,
            )


    st.markdown(
        "</div></div>",
        unsafe_allow_html=True,
    )


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar():

    user = st.session_state.get(
        "user",
        {},
    )


    username = user.get(
        "username",
        "admin",
    )

    full_name = user.get(
        "name",
        user.get(
            "full_name",
            "System Administrator",
        ),
    )

    role = user.get(
        "role",
        "Admin",
    )


    logo = logo_data_uri()


    with st.sidebar:

        if logo:

            st.markdown(
                f"""
                <div class="sidebar-brand">

                    <img
                        class="sidebar-logo"
                        src="{logo}"
                    >

                    <div class="sidebar-brand-name">
                        Creative Studios
                    </div>

                    <div class="sidebar-brand-subtitle">
                        AEC Workspace
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            st.markdown(
                """
                <div class="sidebar-brand">

                    <div style="
                        color:#2563EB;
                        font-size:40px;
                        font-weight:900;
                    ">
                        ◆
                    </div>

                    <div class="sidebar-brand-name">
                        Creative Studios
                    </div>

                    <div class="sidebar-brand-subtitle">
                        AEC Workspace
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )


        st.markdown(
            '<div class="sidebar-divider"></div>',
            unsafe_allow_html=True,
        )


        st.markdown(
            f"""
            <div class="sidebar-user">

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


        st.markdown(
            """
            <div class="navigation-title">
                Navigation
            </div>
            """,
            unsafe_allow_html=True,
        )


        modules = [
            "Project Directory",
            "Drawing Repository",
            "Sign-Off & Approvals",
            "Bill of Quantities (BOQ)",
            "RFI & Technical Queries",
            "Daily Site Logs",
        ]


        selected = st.radio(
            "Navigation",
            modules,
            label_visibility="collapsed",
            key="main_navigation",
        )


        st.markdown(
            "<br>",
            unsafe_allow_html=True,
        )


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


    return selected


# ============================================================
# INITIAL DATABASE
# ============================================================

try:

    db = load_memory()

except Exception as exc:

    st.error(
        f"Unable to load database: {exc}"
    )

    st.stop()


if not isinstance(
    db,
    dict,
):

    db = {}


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


# ============================================================
# LOGIN / APPLICATION
# ============================================================

if not st.session_state[
    "authenticated"
]:

    render_login(
        db
    )

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

app_mode = render_sidebar()


# ============================================================
# MODULE ROUTING
# ============================================================

if app_mode == "Project Directory":

    from modules.projects import (
        render_projects_module
    )

    render_projects_module(
        db
    )


elif app_mode == "Drawing Repository":

    try:

        from modules.drawings import (
            render_drawings_module
        )

        render_drawings_module(
            db
        )

    except Exception as exc:

        st.markdown(
            f"""
            <div class="app-message error">
                Drawing Repository is currently
                unavailable: {exc}
            </div>
            """,
            unsafe_allow_html=True,
        )


elif app_mode == "Sign-Off & Approvals":

    try:

        from modules.approvals import (
            render_approvals_module
        )

        render_approvals_module(
            db
        )

    except Exception as exc:

        st.markdown(
            f"""
            <div class="app-message error">
                Sign-Off & Approvals is currently
                unavailable: {exc}
            </div>
            """,
            unsafe_allow_html=True,
        )


elif app_mode == "Bill of Quantities (BOQ)":

    try:

        from modules.boq import (
            render_boq_module
        )

        render_boq_module(
            db
        )

    except Exception as exc:

        st.markdown(
            f"""
            <div class="app-message error">
                BOQ module is currently
                unavailable: {exc}
            </div>
            """,
            unsafe_allow_html=True,
        )


elif app_mode == "RFI & Technical Queries":

    try:

        from modules.rfi import (
            render_rfi_module
        )

        render_rfi_module(
            db
        )

    except Exception as exc:

        st.markdown(
            f"""
            <div class="app-message error">
                RFI module is currently
                unavailable: {exc}
            </div>
            """,
            unsafe_allow_html=True,
        )


elif app_mode == "Daily Site Logs":

    try:

        from modules.site_logs import (
            render_site_logs_module
        )

        render_site_logs_module(
            db
        )

    except Exception as exc:

        st.markdown(
            f"""
            <div class="app-message error">
                Daily Site Logs is currently
                unavailable: {exc}
            </div>
            """,
            unsafe_allow_html=True,
        )