"""
Creative Studios
AEC Collaboration Platform
AEC Workspace

Main Streamlit Application
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Creative Studios | AEC Workspace",
    page_icon="CS",
    layout="wide",
    initial_sidebar_state="expanded",
)


BASE_DIR = Path(__file__).resolve().parent

DATABASE_FILE = BASE_DIR / "creativestudios_db.json"


# ============================================================
# SESSION STATE
# ============================================================

DEFAULT_SESSION_STATE = {
    "authenticated": False,
    "user": None,
    "active_module": "Overview",
}


def initialize_session_state() -> None:
    """Initialize application session state safely."""

    for key, value in DEFAULT_SESSION_STATE.items():

        if key not in st.session_state:

            st.session_state[key] = value


initialize_session_state()


# ============================================================
# LOGO
# ============================================================

LOGO_CANDIDATES = [
    BASE_DIR / "logo.png",
    BASE_DIR / "logo.jpg",
    BASE_DIR / "logo.jpeg",
    BASE_DIR / "logo.webp",
    BASE_DIR / "logo.svg",

    BASE_DIR / "assets" / "logo.png",
    BASE_DIR / "assets" / "logo.jpg",
    BASE_DIR / "assets" / "logo.jpeg",
    BASE_DIR / "assets" / "logo.webp",
    BASE_DIR / "assets" / "logo.svg",

    BASE_DIR / "assets" / "creative_studios.png",
    BASE_DIR / "assets" / "creative_studios.jpg",
    BASE_DIR / "assets" / "creative_studios.jpeg",
    BASE_DIR / "assets" / "creative_studios.webp",
    BASE_DIR / "assets" / "creative_studios.svg",
]


def find_logo() -> Path | None:
    """Return the first available logo file."""

    for path in LOGO_CANDIDATES:

        try:

            if path.is_file():
                return path

        except OSError:
            continue

    return None


LOGO_FILE = find_logo()


# ============================================================
# DATABASE
# ============================================================

def empty_database() -> dict[str, Any]:
    """Return the minimum valid application database."""

    return {
        "users": [],
        "projects": [],
        "drawings": [],
        "documents": [],
        "approvals": [],
        "boq": [],
        "rfis": [],
        "site_logs": [],
        "team": [],
    }


def load_database() -> dict[str, Any]:
    """
    Load the JSON database.

    The app will not crash if the database is missing,
    invalid, or an optional database module is unavailable.
    """

    # --------------------------------------------------------
    # First try the application's database module.
    # --------------------------------------------------------

    try:

        from modules.database import load_memory

        result = load_memory()

        if isinstance(result, dict):
            return result

    except Exception:
        pass


    # --------------------------------------------------------
    # Direct JSON fallback.
    # --------------------------------------------------------

    if DATABASE_FILE.exists():

        try:

            with DATABASE_FILE.open(
                "r",
                encoding="utf-8",
            ) as file:

                result = json.load(file)

            if isinstance(result, dict):
                return result

        except (
            OSError,
            json.JSONDecodeError,
            TypeError,
            ValueError,
        ):
            pass


    return empty_database()


db = load_database()


# ============================================================
# DATABASE NORMALIZATION
# ============================================================

def normalize_database(data: dict[str, Any]) -> dict[str, Any]:
    """
    Ensure expected database collections exist.
    """

    defaults = empty_database()

    for key, default_value in defaults.items():

        if key not in data:

            data[key] = default_value

        elif not isinstance(
            data[key],
            list,
        ):

            data[key] = default_value

    return data


db = normalize_database(db)


# ============================================================
# SAFE HELPERS
# ============================================================

def safe_text(
    value: Any,
    default: str = "",
) -> str:

    if value is None:
        return default

    return str(value)


def get_current_user() -> dict[str, Any]:

    user = st.session_state.get(
        "user"
    )

    if isinstance(
        user,
        dict,
    ):

        return user

    return {
        "id": 1,
        "username": "admin",
        "full_name": "System Administrator",
        "role": "Admin",
        "active": True,
    }


# ============================================================
# AUTHENTICATION
# ============================================================

def authenticate_user(
    username: str,
    password: str,
) -> tuple[bool, dict[str, Any] | None]:
    """
    Authenticate a user.

    We deliberately keep this wrapper tolerant of different
    versions of modules.auth.login_user().
    """

    username = username.strip()
    password = password


    if not username or not password:

        return False, None


    # --------------------------------------------------------
    # Try application authentication module.
    # --------------------------------------------------------

    try:

        from modules.auth import login_user

        # Try the common two-argument signature first.
        try:

            result = login_user(
                username,
                password,
            )

        except TypeError:

            # Try the older database-aware signature.
            result = login_user(
                db,
                username,
                password,
            )


        if isinstance(
            result,
            tuple,
        ):

            if len(result) >= 2:

                success = bool(
                    result[0]
                )

                user = result[1]


                if success:

                    if isinstance(
                        user,
                        dict,
                    ):

                        return True, user


                    return True, {
                        "username": username,
                        "full_name": username,
                        "role": "User",
                    }


            elif len(result) == 1:

                success = bool(
                    result[0]
                )

                if success:

                    return True, {
                        "username": username,
                        "full_name": username,
                        "role": "User",
                    }


        elif isinstance(
            result,
            dict,
        ):

            return True, result


        elif result is True:

            return True, {
                "username": username,
                "full_name": username,
                "role": "User",
            }

    except Exception:
        pass


    # --------------------------------------------------------
    # Search JSON users.
    # --------------------------------------------------------

    users = db.get(
        "users",
        [],
    )


    if isinstance(
        users,
        list,
    ):

        for user in users:

            if not isinstance(
                user,
                dict,
            ):
                continue


            stored_username = safe_text(
                user.get("username")
            ).strip()


            stored_password = safe_text(
                user.get("password")
            )


            if (
                stored_username == username
                and stored_password == password
            ):

                return True, user


    # --------------------------------------------------------
    # Development administrator fallback.
    #
    # This allows the application to remain usable when
    # authentication/database modules are not yet configured.
    # --------------------------------------------------------

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


    return False, None


# ============================================================
# GLOBAL STYLING
# ============================================================

st.markdown(
    """
<style>

/* ==========================================================
   APPLICATION
   ========================================================== */

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
    padding-top: 1.4rem !important;
    padding-bottom: 3rem !important;
}


/* ==========================================================
   SIDEBAR
   ========================================================== */

section[data-testid="stSidebar"] {
    background: #07090D !important;
    border-right: 1px solid #172033 !important;
}

section[data-testid="stSidebar"] > div {
    background: #07090D !important;
}


/* ==========================================================
   BRAND
   ========================================================== */

.cs-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 4px 2px 18px 2px;
}

.cs-logo {
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

.cs-logo-fallback {
    color: #60A5FA;
    font-size: 18px;
    font-weight: 950;
}

.cs-brand-name {
    color: #FFFFFF;
    font-size: 16px;
    font-weight: 900;
    line-height: 1.1;
}

.cs-brand-subtitle {
    color: #64748B;
    font-size: 9px;
    font-weight: 800;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-top: 4px;
}


/* ==========================================================
   USER PANEL
   ========================================================== */

.cs-user {
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


/* ==========================================================
   NAVIGATION
   ========================================================== */

.cs-section-title {
    color: #475569;
    font-size: 9px;
    font-weight: 850;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin: 12px 0 7px 2px;
}


/* ==========================================================
   BUTTONS
   ========================================================== */

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


/* ==========================================================
   INPUTS
   ========================================================== */

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


/* ==========================================================
   METRICS
   ========================================================== */

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


/* ==========================================================
   CARDS
   ========================================================== */

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


/* ==========================================================
   LOGIN
   ========================================================== */

.cs-login {
    max-width: 430px;
    margin: 8vh auto 0 auto;
}

.cs-login-logo {
    width: 88px;
    height: 88px;
    margin: 0 auto 20px auto;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    background: #0B0F16;
    border: 1px solid #2563EB;
    border-radius: 20px;
}

.cs-login-fallback {
    color: #60A5FA;
    font-size: 32px;
    font-weight: 950;
}

.cs-login-title {
    text-align: center;
    color: #FFFFFF;
    font-size: 30px;
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


/* ==========================================================
   DIVIDERS
   ========================================================== */

hr {
    border-color: #172033 !important;
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# LOGIN
# ============================================================

def render_login() -> None:
    """Render the login screen."""

    st.markdown(
        '<div class="cs-login">',
        unsafe_allow_html=True,
    )


    # --------------------------------------------------------
    # Logo
    # --------------------------------------------------------

    if LOGO_FILE:

        st.markdown(
            '<div class="cs-login-logo">',
            unsafe_allow_html=True,
        )

        try:

            st.image(
                str(LOGO_FILE),
                width=76,
            )

        except Exception:

            st.markdown(
                '<div class="cs-login-fallback">CS</div>',
                unsafe_allow_html=True,
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
    # Heading
    # --------------------------------------------------------

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

        submitted = st.form_submit_button(
            "Sign In",
            use_container_width=True,
        )


    if submitted:

        success, user = authenticate_user(
            username,
            password,
        )


        if success:

            st.session_state[
                "authenticated"
            ] = True

            st.session_state[
                "user"
            ] = user

            st.session_state[
                "active_module"
            ] = "Overview"

            st.rerun()


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

def render_sidebar() -> None:
    """Render the complete application sidebar."""

    user = get_current_user()


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
        # Branding
        # ----------------------------------------------------

        if LOGO_FILE:

            st.markdown(
                '<div class="cs-brand">',
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div class="cs-logo">',
                unsafe_allow_html=True,
            )

            try:

                st.image(
                    str(LOGO_FILE),
                    width=40,
                )

            except Exception:

                st.markdown(
                    '<div class="cs-logo-fallback">CS</div>',
                    unsafe_allow_html=True,
                )

            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )

            st.markdown(
                """
                <div>
                    <div class="cs-brand-name">
                        Creative Studios
                    </div>

                    <div class="cs-brand-subtitle">
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
                <div class="cs-brand">

                    <div class="cs-logo">
                        <div class="cs-logo-fallback">
                            CS
                        </div>
                    </div>

                    <div>

                        <div class="cs-brand-name">
                            Creative Studios
                        </div>

                        <div class="cs-brand-subtitle">
                            AEC Workspace
                        </div>

                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )


        # ----------------------------------------------------
        # User
        # ----------------------------------------------------

        st.markdown(
            f"""
            <div class="cs-user">

                <div class="user-label">
                    Signed In
                </div>

                <div class="user-name">
                    {safe_text(full_name)}
                </div>

                <div class="user-login">
                    @{safe_text(username)}
                </div>

                <div class="user-role">
                    {safe_text(role)}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


        # ----------------------------------------------------
        # Navigation
        # ----------------------------------------------------

        st.markdown(
            """
            <div class="cs-section-title">
                AEC Workspace
            </div>
            """,
            unsafe_allow_html=True,
        )


        workspace_modules = [
            "Overview",
            "Project Directory",
            "Drawing Repository",
            "AEC Library",
            "Sign-Off & Approvals",
            "Bill of Quantities",
            "RFI & Technical Queries",
            "Daily Site Logs",
        ]


        st.markdown(
            """
            <div class="cs-section-title">
                Management
            </div>
            """,
            unsafe_allow_html=True,
        )


        management_modules = [
            "Team & Collaboration",
            "Administration",
        ]


        modules = (
            workspace_modules
            + management_modules
        )


        active_module = st.session_state.get(
            "active_module",
            "Overview",
        )


        if active_module not in modules:

            active_module = "Overview"

            st.session_state[
                "active_module"
            ] = active_module


        selected_module = st.radio(
            "Module Navigation",
            modules,
            index=modules.index(
                active_module
            ),
            key="module_navigation",
            label_visibility="collapsed",
        )


        if selected_module != active_module:

            st.session_state[
                "active_module"
            ] = selected_module

            st.rerun()


        # ----------------------------------------------------
        # Logout
        # ----------------------------------------------------

        st.markdown(
            "<div style='height:25px'></div>",
            unsafe_allow_html=True,
        )


        if st.button(
            "Sign Out",
            key="sign_out_button",
            use_container_width=True,
        ):

            # Clear only application authentication state.
            # Do not manipulate Streamlit internals.

            st.session_state[
                "authenticated"
            ] = False

            st.session_state[
                "user"
            ] = None

            st.session_state[
                "active_module"
            ] = "Overview"

            st.rerun()


# ============================================================
# OVERVIEW
# ============================================================

def render_overview() -> None:
    """Render the application overview."""

    st.title(
        "AEC Workspace"
    )

    st.caption(
        "Creative Studios Collaboration Platform"
    )


    projects = db.get(
        "projects",
        [],
    )


    if not isinstance(
        projects,
        list,
    ):
        projects = []


    total_projects = len(
        projects
    )

    active_projects = 0
    planning_projects = 0
    completed_projects = 0

    portfolio_budget = 0.0


    for project in projects:

        if not isinstance(
            project,
            dict,
        ):
            continue


        status = safe_text(
            project.get(
                "status",
                "",
            )
        ).strip().lower()


        if status in {
            "active",
            "in progress",
            "in_progress",
        }:

            active_projects += 1


        elif status == "planning":

            planning_projects += 1


        elif status in {
            "completed",
            "complete",
        }:

            completed_projects += 1


        budget = project.get(
            "estimated_budget",
            project.get(
                "budget",
                0,
            ),
        )


        try:

            portfolio_budget += float(
                budget or 0
            )

        except (
            TypeError,
            ValueError,
        ):

            continue


    c1, c2, c3, c4 = st.columns(4)


    with c1:

        st.metric(
            "Total Projects",
            total_projects,
        )


    with c2:

        st.metric(
            "Active",
            active_projects,
        )


    with c3:

        st.metric(
            "Planning",
            planning_projects,
        )


    with c4:

        st.metric(
            "Completed",
            completed_projects,
        )


    st.markdown(
        "<br>",
        unsafe_allow_html=True,
    )


    st.markdown(
        f"""
        <div class="cs-card">

            <div class="cs-card-title">
                Portfolio Budget
            </div>

            <div style="
                color:#60A5FA;
                font-size:30px;
                font-weight:900;
                margin-top:8px;
            ">
                ${portfolio_budget:,.2f}
            </div>

            <div class="cs-card-subtitle">
                Current project portfolio value
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# PROJECTS
# ============================================================

def render_projects() -> None:
    """Load Project Directory safely."""

    try:

        from modules.projects import (
            render_projects_module,
        )

    except Exception as error:

        st.error(
            "Project Directory module could not be imported."
        )

        with st.expander(
            "Technical details"
        ):

            st.code(
                repr(error)
            )

        return


    try:

        render_projects_module(
            db
        )

    except Exception as error:

        st.error(
            "Project Directory encountered an error."
        )

        with st.expander(
            "Technical details"
        ):

            st.code(
                repr(error)
            )


# ============================================================
# AEC LIBRARY
# ============================================================

def render_library() -> None:

    st.title(
        "AEC Library"
    )

    st.caption(
        "Central repository for documents, standards, "
        "templates and technical resources."
    )


    documents = db.get(
        "documents",
        [],
    )


    if not isinstance(
        documents,
        list,
    ):

        documents = []


    c1, c2, c3 = st.columns(3)


    with c1:

        st.metric(
            "Documents",
            len(documents),
        )


    with c2:

        project_documents = 0

        for document in documents:

            if (
                isinstance(
                    document,
                    dict,
                )
                and document.get("project_id")
            ):

                project_documents += 1


        st.metric(
            "Project Documents",
            project_documents,
        )


    with c3:

        categories = set()


        for document in documents:

            if isinstance(
                document,
                dict,
            ):

                category = safe_text(
                    document.get(
                        "category",
                        "General",
                    )
                )

                categories.add(
                    category
                )


        st.metric(
            "Categories",
            len(categories),
        )


    st.markdown(
        "<br>",
        unsafe_allow_html=True,
    )


    st.markdown(
        """
        <div class="cs-card">

            <div class="cs-card-title">
                Document Library
            </div>

            <div class="cs-card-subtitle">
                Store and organize drawings, specifications,
                contracts, reports, templates and other
                AEC resources.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# PLACEHOLDER
# ============================================================

def render_placeholder(
    title: str,
    description: str,
) -> None:

    st.title(title)

    st.caption(description)

    st.markdown(
        """
        <div class="cs-card">

            <div class="cs-card-title">
                Module Ready
            </div>

            <div class="cs-card-subtitle">
                This module is registered in the
                Creative Studios navigation and is
                ready for its database workflow.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# DRAWINGS
# ============================================================

def render_drawings() -> None:

    try:

        from modules.drawings import (
            render_drawings_module,
        )

        render_drawings_module(
            db
        )

    except Exception:

        render_placeholder(
            "Drawing Repository",
            "Manage architectural, structural, MEP "
            "and construction drawings.",
        )


# ============================================================
# APPLICATION ROUTER
# ============================================================

def render_application() -> None:

    render_sidebar()


    active_module = st.session_state.get(
        "active_module",
        "Overview",
    )


    if active_module == "Overview":

        render_overview()


    elif active_module == "Project Directory":

        render_projects()


    elif active_module == "Drawing Repository":

        render_drawings()


    elif active_module == "AEC Library":

        render_library()


    elif active_module == "Sign-Off & Approvals":

        render_placeholder(
            "Sign-Off & Approvals",
            "Manage submissions, reviews, approvals "
            "and project sign-off workflows.",
        )


    elif active_module == "Bill of Quantities":

        render_placeholder(
            "Bill of Quantities",
            "Manage quantities, rates, materials "
            "and construction costs.",
        )


    elif active_module == "RFI & Technical Queries":

        render_placeholder(
            "RFI & Technical Queries",
            "Manage RFIs, technical queries, "
            "responses and technical assignments.",
        )


    elif active_module == "Daily Site Logs":

        render_placeholder(
            "Daily Site Logs",
            "Capture daily construction progress, "
            "labour, equipment, materials and issues.",
        )


    elif active_module == "Team & Collaboration":

        render_placeholder(
            "Team & Collaboration",
            "Manage project teams, responsibilities "
            "and collaboration.",
        )


    elif active_module == "Administration":

        render_placeholder(
            "Administration",
            "Manage users, permissions and "
            "system configuration.",
        )


    else:

        st.session_state[
            "active_module"
        ] = "Overview"

        st.rerun()


# ============================================================
# MAIN ENTRY POINT
# ============================================================

def main() -> None:

    if st.session_state.get(
        "authenticated",
        False,
    ):

        render_application()

    else:

        render_login()


if __name__ == "__main__":

    main()