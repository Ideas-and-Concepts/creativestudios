"""
Creative Studios
AEC Collaboration Platform

Main Streamlit application.
"""

from __future__ import annotations

import base64
import html
from pathlib import Path
from typing import Any

import streamlit as st

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
# MODULE IMPORTS
# ============================================================
#
# Import modules individually so that a problem in one module
# can be identified clearly instead of failing on a grouped
# import statement.
# ============================================================

try:
    import modules.dashboard as dashboard
except Exception as exc:
    dashboard = None
    DASHBOARD_IMPORT_ERROR = exc

try:
    import modules.projects as projects
except Exception as exc:
    projects = None
    PROJECTS_IMPORT_ERROR = exc

try:
    import modules.documents as documents
except Exception as exc:
    documents = None
    DOCUMENTS_IMPORT_ERROR = exc

try:
    import modules.architecture as architecture
except Exception as exc:
    architecture = None
    ARCHITECTURE_IMPORT_ERROR = exc

try:
    import modules.engineering as engineering
except Exception as exc:
    engineering = None
    ENGINEERING_IMPORT_ERROR = exc

try:
    import modules.drawings as drawings
except Exception as exc:
    drawings = None
    DRAWINGS_IMPORT_ERROR = exc

try:
    import modules.mep as mep
except Exception as exc:
    mep = None
    MEP_IMPORT_ERROR = exc


# ============================================================
# DATABASE
# ============================================================

try:
    from modules.database import load_memory, save_memory
except Exception as exc:
    load_memory = None
    save_memory = None
    DATABASE_IMPORT_ERROR = exc


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"

LOGO_PATH = ASSETS_DIR / "creative_studios.png"


# ============================================================
# BRANDING / CSS
# ============================================================

def inject_css() -> None:
    """Inject Creative Studios application styling."""

    st.markdown(
        """
        <style>

        /* ==================================================
           GLOBAL
           ================================================== */

        .stApp {
            transition:
                background-color 0.25s ease,
                color 0.25s ease;
        }

        /* ==================================================
           SIDEBAR
           ================================================== */

        [data-testid="stSidebar"] {
            border-right: 1px solid rgba(128, 128, 128, 0.18);
        }

        [data-testid="stSidebar"] .block-container {
            padding-top: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }

        /* ==================================================
           SIDEBAR BRAND
           ================================================== */

        .cs-sidebar-brand {
            text-align: center;
            padding: 4px 0 16px 0;
        }

        .cs-sidebar-brand-name {
            font-size: 17px;
            font-weight: 800;
            line-height: 1.2;
            margin-top: 7px;
        }

        .cs-sidebar-brand-subtitle {
            color: #64748B;
            font-size: 11px;
            margin-top: 3px;
        }

        /* ==================================================
           LOGIN
           ================================================== */

        .cs-login {
            max-width: 440px;
            margin: 0 auto;
            padding-top: 5vh;
            text-align: center;
        }

        .cs-login-logo {
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
            margin: 0 auto 18px auto;
        }

        .cs-login-logo img {
            display: block;
            width: 105px;
            max-width: 105px;
            height: auto;
            margin: 0 auto;
        }

        .cs-login-title {
            font-size: 30px;
            font-weight: 800;
            line-height: 1.15;
            text-align: center;
        }

        .cs-login-subtitle {
            color: #64748B;
            font-size: 14px;
            margin-top: 6px;
            margin-bottom: 24px;
            text-align: center;
        }

        /* ==================================================
           MODULE HEADER
           ================================================== */

        .cs-module-header {
            margin-bottom: 22px;
        }

        .cs-module-title {
            font-size: 30px;
            font-weight: 800;
            line-height: 1.2;
        }

        .cs-module-description {
            color: #64748B;
            font-size: 14px;
            margin-top: 5px;
        }

        /* ==================================================
           CARDS
           ================================================== */

        .cs-card {
            border: 1px solid rgba(128, 128, 128, 0.18);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
        }

        .cs-card-title {
            font-size: 18px;
            font-weight: 750;
            margin-bottom: 5px;
        }

        .cs-card-subtitle {
            color: #64748B;
            font-size: 13px;
            line-height: 1.55;
        }

        /* ==================================================
           KPI
           ================================================== */

        .cs-kpi {
            border: 1px solid rgba(128, 128, 128, 0.18);
            border-radius: 12px;
            padding: 16px;
            min-height: 88px;
        }

        .cs-kpi-label {
            color: #64748B;
            font-size: 12px;
            margin-bottom: 7px;
        }

        .cs-kpi-value {
            font-size: 25px;
            font-weight: 800;
        }

        /* ==================================================
           USER CARD
           ================================================== */

        .cs-user-card {
            border: 1px solid rgba(128, 128, 128, 0.18);
            border-radius: 12px;
            padding: 13px;
            margin-top: 12px;
        }

        .cs-user-label {
            color: #64748B;
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }

        .cs-user-name {
            font-weight: 700;
            font-size: 14px;
            margin-top: 3px;
        }

        .cs-user-login {
            color: #64748B;
            font-size: 12px;
            margin-top: 2px;
        }

        .cs-user-role {
            color: #64748B;
            font-size: 11px;
            margin-top: 2px;
        }

        /* ==================================================
           NAVIGATION
           ================================================== */

        .cs-section-label {
            color: #64748B;
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-top: 14px;
            margin-bottom: 7px;
        }

        .cs-active-module {
            border-radius: 8px;
            padding: 8px 10px;
            font-weight: 700;
            margin-bottom: 4px;
        }

        .cs-active-indicator {
            margin-right: 6px;
        }

        /* ==================================================
           MOBILE
           ================================================== */

        @media (max-width: 768px) {

            .cs-login {
                padding-top: 3vh;
            }

            .cs-login-title {
                font-size: 26px;
            }

            .cs-module-title {
                font-size: 25px;
            }

        }

        </style>
        """,
        unsafe_allow_html=True,
    )


inject_css()


# ============================================================
# SESSION STATE
# ============================================================

def initialize_session_state() -> None:
    """Initialize application session state."""

    defaults = {
        "authenticated": False,
        "user": None,
        "active_module": "Dashboard",
        "database": None,
        "theme": "System",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ============================================================
# LOGO
# ============================================================

def _logo_base64() -> str | None:
    """Return the logo as base64 if it exists."""

    if not LOGO_PATH.exists():
        return None

    try:
        data = LOGO_PATH.read_bytes()
        return base64.b64encode(data).decode("utf-8")
    except OSError:
        return None


# ============================================================
# DATABASE
# ============================================================

def get_database() -> dict[str, Any]:
    """Load the database once per Streamlit session."""

    if load_memory is None:
        raise RuntimeError(
            "Unable to import modules.database.load_memory."
        )

    database = st.session_state.get("database")

    if not isinstance(database, dict):
        database = load_memory()

        if not isinstance(database, dict):
            database = {}

        st.session_state.database = database

    return database


# ============================================================
# AUTHENTICATION
# ============================================================

def authenticate_user(
    username: str,
    password: str,
    database: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Authenticate against the JSON database.

    Supports plaintext passwords and SHA-256 hashes.
    """

    username = str(username or "").strip()
    password = str(password or "")

    users = database.get("users", [])

    if not isinstance(users, list):
        return None

    for user in users:

        if not isinstance(user, dict):
            continue

        stored_username = str(
            user.get("username", "")
        ).strip()

        if stored_username != username:
            continue

        stored_password = str(
            user.get(
                "password",
                user.get("password_hash", ""),
            )
            or ""
        )

        password_match = False

        if stored_password == password:
            password_match = True

        else:
            import hashlib
            import hmac

            password_hash = hashlib.sha256(
                password.encode("utf-8")
            ).hexdigest()

            if hmac.compare_digest(
                password_hash,
                stored_password.lower(),
            ):
                password_match = True

        if not password_match:
            continue

        if user.get("active", True) is False:
            return None

        return user

    return None


# ============================================================
# LOGIN PAGE
# ============================================================

def render_login(
    database: dict[str, Any],
) -> None:
    """Render the centered Creative Studios login page."""

    st.markdown(
        '<div class="cs-login">',
        unsafe_allow_html=True,
    )

    logo_b64 = _logo_base64()

    if logo_b64:

        st.markdown(
            f"""
            <div class="cs-login-logo">
                <img
                    src="data:image/png;base64,{logo_b64}"
                    alt="Creative Studios"
                >
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        st.warning(
            f"Creative Studios logo was not found at: {LOGO_PATH}"
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
            "Login",
            use_container_width=True,
        )

    if submitted:

        user = authenticate_user(
            username,
            password,
            database,
        )

        if user is not None:

            st.session_state.authenticated = True
            st.session_state.user = user
            st.session_state.active_module = "Dashboard"

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
# SIDEBAR BRANDING
# ============================================================

def render_sidebar_branding() -> None:
    """Render the compact sidebar brand."""

    logo_b64 = _logo_base64()

    if logo_b64:

        st.sidebar.markdown(
            f"""
            <div class="cs-sidebar-brand">

                <img
                    src="data:image/png;base64,{logo_b64}"
                    width="58"
                    alt="Creative Studios"
                >

                <div class="cs-sidebar-brand-name">
                    Creative Studios
                </div>

                <div class="cs-sidebar-brand-subtitle">
                    AEC Collaboration Platform
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        st.sidebar.markdown(
            """
            <div class="cs-sidebar-brand">

                <div class="cs-sidebar-brand-name">
                    Creative Studios
                </div>

                <div class="cs-sidebar-brand-subtitle">
                    AEC Collaboration Platform
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar() -> str:
    """Render application navigation."""

    user = st.session_state.get("user") or {}

    render_sidebar_branding()

    st.sidebar.markdown(
        '<div class="cs-section-label">Navigation</div>',
        unsafe_allow_html=True,
    )

    navigation = [
        ("Dashboard", "Dashboard"),
        ("Projects", "Projects"),
        ("Documents", "Documents"),
        ("Architecture", "Architecture"),
        ("Engineering", "Engineering"),
        ("Drawings", "Drawings"),
        ("MEP", "MEP"),
    ]

    current_module = st.session_state.get(
        "active_module",
        "Dashboard",
    )

    for module_key, label in navigation:

        if module_key == current_module:

            st.sidebar.markdown(
                f"""
                <div class="cs-active-module">
                    <span class="cs-active-indicator">●</span>
                    {html.escape(label)}
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            if st.sidebar.button(
                label,
                key=f"nav_{module_key.lower()}",
                use_container_width=True,
            ):

                st.session_state.active_module = module_key
                st.rerun()

    # --------------------------------------------------------
    # Theme
    # --------------------------------------------------------

    st.sidebar.markdown(
        '<div class="cs-section-label">Appearance</div>',
        unsafe_allow_html=True,
    )

    theme = st.sidebar.selectbox(
        "Theme",
        [
            "System",
            "Light",
            "Dark",
        ],
        index=[
            "System",
            "Light",
            "Dark",
        ].index(
            st.session_state.get(
                "theme",
                "System",
            )
        ),
        key="theme_selector",
        label_visibility="collapsed",
    )

    st.session_state.theme = theme

    # --------------------------------------------------------
    # User
    # --------------------------------------------------------

    full_name = str(
        user.get(
            "full_name",
            user.get("name", ""),
        )
        or "System Administrator"
    ).strip()

    username = str(
        user.get("username", "")
        or "admin"
    ).strip()

    role = str(
        user.get("role", "")
        or "Admin"
    ).strip()

    st.sidebar.markdown(
        f"""
        <div class="cs-user-card">

            <div class="cs-user-label">
                Signed In
            </div>

            <div class="cs-user-name">
                {html.escape(full_name)}
            </div>

            <div class="cs-user-login">
                @{html.escape(username)}
            </div>

            <div class="cs-user-role">
                {html.escape(role)}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.write("")

    if st.sidebar.button(
        "Sign Out",
        key="logout_button",
        use_container_width=True,
    ):

        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.active_module = "Dashboard"

        st.rerun()

    return str(current_module)


# ============================================================
# OVERVIEW / DASHBOARD FALLBACK
# ============================================================

def render_fallback_dashboard(
    database: dict[str, Any],
) -> None:
    """Fallback dashboard if dashboard.py cannot be imported."""

    projects_data = database.get(
        "projects",
        [],
    )

    if not isinstance(projects_data, list):
        projects_data = []

    total_projects = len(
        [
            item
            for item in projects_data
            if isinstance(item, dict)
        ]
    )

    st.markdown(
        """
        <div class="cs-module-header">

            <div class="cs-module-title">
                Creative Studios Workspace
            </div>

            <div class="cs-module-description">
                AEC Collaboration Platform
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    columns = st.columns(1)

    with columns[0]:

        st.markdown(
            f"""
            <div class="cs-kpi">

                <div class="cs-kpi-label">
                    Projects
                </div>

                <div class="cs-kpi-value">
                    {total_projects}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# MODULE ERROR DISPLAY
# ============================================================

def render_import_error(
    module_name: str,
    error: Exception | None,
) -> None:
    """Display a readable module import error."""

    st.error(
        f"Unable to load the {module_name} module."
    )

    if error is not None:

        with st.expander(
            "Technical details",
            expanded=False,
        ):

            st.exception(error)


# ============================================================
# MODULE ROUTER
# ============================================================

def render_module(
    choice: str,
    database: dict[str, Any],
) -> None:
    """Render the selected application module."""

    if choice == "Dashboard":

        if dashboard is None:

            render_import_error(
                "Dashboard",
                globals().get(
                    "DASHBOARD_IMPORT_ERROR"
                ),
            )

        elif hasattr(
            dashboard,
            "render_dashboard",
        ):

            dashboard.render_dashboard(
                database
            )

        else:

            render_fallback_dashboard(
                database
            )

    elif choice == "Projects":

        if projects is None:

            render_import_error(
                "Projects",
                globals().get(
                    "PROJECTS_IMPORT_ERROR"
                ),
            )

        elif hasattr(
            projects,
            "render_projects_module",
        ):

            projects.render_projects_module(
                database
            )

        else:

            st.error(
                "Projects module does not expose render_projects_module()."
            )

    elif choice == "Documents":

        if documents is None:

            render_import_error(
                "Documents",
                globals().get(
                    "DOCUMENTS_IMPORT_ERROR"
                ),
            )

        elif hasattr(
            documents,
            "render_documents_module",
        ):

            documents.render_documents_module(
                database
            )

        else:

            st.error(
                "Documents module does not expose render_documents_module()."
            )

    elif choice == "Architecture":

        if architecture is None:

            render_import_error(
                "Architecture",
                globals().get(
                    "ARCHITECTURE_IMPORT_ERROR"
                ),
            )

        elif hasattr(
            architecture,
            "render_architecture_module",
        ):

            architecture.render_architecture_module(
                database
            )

        else:

            st.error(
                "Architecture module does not expose render_architecture_module()."
            )

    elif choice == "Engineering":

        if engineering is None:

            render_import_error(
                "Engineering",
                globals().get(
                    "ENGINEERING_IMPORT_ERROR"
                ),
            )

        elif hasattr(
            engineering,
            "render_engineering_module",
        ):

            engineering.render_engineering_module(
                database
            )

        else:

            st.error(
                "Engineering module does not expose render_engineering_module()."
            )

    elif choice == "Drawings":

        if drawings is None:

            render_import_error(
                "Drawings",
                globals().get(
                    "DRAWINGS_IMPORT_ERROR"
                ),
            )

        elif hasattr(
            drawings,
            "render_drawings_module",
        ):

            drawings.render_drawings_module(
                database
            )

        else:

            st.error(
                "Drawings module does not expose render_drawings_module()."
            )

    elif choice == "MEP":

        if mep is None:

            render_import_error(
                "MEP",
                globals().get(
                    "MEP_IMPORT_ERROR"
                ),
            )

        elif hasattr(
            mep,
            "render_mep_module",
        ):

            mep.render_mep_module(
                database
            )

        else:

            st.error(
                "MEP module does not expose render_mep_module()."
            )

    else:

        st.session_state.active_module = "Dashboard"

        render_fallback_dashboard(
            database
        )


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    """Run Creative Studios."""

    initialize_session_state()

    # --------------------------------------------------------
    # Database
    # --------------------------------------------------------

    try:

        database = get_database()

    except Exception as exc:

        st.error(
            "Unable to load Creative Studios database."
        )

        with st.expander(
            "Technical details",
            expanded=False,
        ):

            st.exception(exc)

        return

    # --------------------------------------------------------
    # Authentication
    # --------------------------------------------------------

    if not st.session_state.get(
        "authenticated",
        False,
    ):

        render_login(
            database
        )

        return

    # --------------------------------------------------------
    # Application
    # --------------------------------------------------------

    try:

        choice = render_sidebar()

        render_module(
            choice,
            database,
        )

    except Exception as exc:

        st.error(
            "Unable to render the selected module."
        )

        with st.expander(
            "Technical details",
            expanded=False,
        ):

            st.exception(exc)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()