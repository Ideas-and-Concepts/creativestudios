"""
Creative Studios
AEC Collaboration Platform
AEC Workspace

Main Streamlit Application
"""

from __future__ import annotations

import streamlit as st

from modules.database import (
    ensure_admin_user,
    find_one,
    load_memory,
    save_memory,
    verify_password,
)

from modules.projects import (
    render_projects_module,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Creative Studios",
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

    /* ======================================================
       GLOBAL
       ====================================================== */

    .stApp {
        background:
            #05070B;
        color:
            #E5E7EB;
    }

    [data-testid="stAppViewContainer"] {
        background:
            #05070B;
    }

    [data-testid="stHeader"] {
        background:
            #05070B;
    }

    [data-testid="stMain"] {
        background:
            #05070B;
    }

    .block-container {
        padding-top:
            1.5rem;
        padding-bottom:
            3rem;
        max-width:
            1500px;
    }


    /* ======================================================
       SIDEBAR
       ====================================================== */

    [data-testid="stSidebar"] {
        background:
            #070A10;
        border-right:
            1px solid #172033;
    }

    [data-testid="stSidebarContent"] {
        background:
            #070A10;
    }

    .cs-sidebar-brand {
        padding:
            12px 8px 22px 8px;
        border-bottom:
            1px solid #172033;
        margin-bottom:
            18px;
    }

    .cs-brand-row {
        display:
            flex;
        align-items:
            center;
        gap:
            12px;
    }

    .cs-logo {
        width:
            46px;
        height:
            46px;
        min-width:
            46px;
        border-radius:
            12px;
        background:
            #2563EB;
        display:
            flex;
        align-items:
            center;
        justify-content:
            center;
        box-shadow:
            0 8px 25px rgba(37,99,235,.25);
    }

    .cs-logo-text {
        color:
            #FFFFFF;
        font-size:
            17px;
        font-weight:
            950;
        letter-spacing:
            -1px;
    }

    .cs-brand-name {
        color:
            #FFFFFF;
        font-size:
            16px;
        font-weight:
            850;
        line-height:
            1.2;
    }

    .cs-brand-subtitle {
        color:
            #64748B;
        font-size:
            10px;
        margin-top:
            3px;
        letter-spacing:
            .5px;
        text-transform:
            uppercase;
    }


    /* ======================================================
       SIDEBAR USER
       ====================================================== */

    .cs-user-card {
        background:
            #0B0F17;
        border:
            1px solid #1E293B;
        border-radius:
            12px;
        padding:
            13px;
        margin-bottom:
            18px;
    }

    .cs-user-label {
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

    .cs-user-name {
        color:
            #FFFFFF;
        font-size:
            14px;
        font-weight:
            800;
        margin-top:
            5px;
    }

    .cs-user-login {
        color:
            #64748B;
        font-size:
            11px;
        margin-top:
            2px;
    }

    .cs-user-role {
        display:
            inline-block;
        margin-top:
            8px;
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
            850;
    }


    /* ======================================================
       SIDEBAR SECTIONS
       ====================================================== */

    .cs-nav-section {
        color:
            #475569;
        font-size:
            9px;
        font-weight:
            850;
        letter-spacing:
            1px;
        text-transform:
            uppercase;
        margin:
            18px 8px 7px 8px;
    }


    /* ======================================================
       SIDEBAR BUTTONS
       ====================================================== */

    [data-testid="stSidebar"] div.stButton > button {
        width:
            100%;
        text-align:
            left;
        border:
            1px solid transparent;
        background:
            transparent;
        color:
            #94A3B8;
        border-radius:
            9px;
        min-height:
            38px;
        padding-left:
            12px;
        font-weight:
            650;
    }

    [data-testid="stSidebar"] div.stButton > button:hover {
        background:
            #0F172A;
        color:
            #FFFFFF;
        border-color:
            #1E3A8A;
    }

    .cs-sidebar-footer {
        color:
            #334155;
        font-size:
            9px;
        text-align:
            center;
        margin-top:
            20px;
        padding-top:
            15px;
        border-top:
            1px solid #172033;
    }


    /* ======================================================
       LOGIN
       ====================================================== */

    .cs-login-wrapper {
        min-height:
            82vh;
        display:
            flex;
        align-items:
            center;
        justify-content:
            center;
    }

    .cs-login-card {
        width:
            min(430px, 100%);
        background:
            #090D14;
        border:
            1px solid #1E293B;
        border-radius:
            18px;
        padding:
            34px;
        box-shadow:
            0 20px 60px rgba(0,0,0,.45);
    }

    .cs-login-logo {
        width:
            68px;
        height:
            68px;
        border-radius:
            17px;
        background:
            #2563EB;
        display:
            flex;
        align-items:
            center;
        justify-content:
            center;
        margin:
            0 auto 18px auto;
    }

    .cs-login-logo-text {
        color:
            #FFFFFF;
        font-size:
            24px;
        font-weight:
            950;
    }

    .cs-login-title {
        color:
            #FFFFFF;
        text-align:
            center;
        font-size:
            25px;
        font-weight:
            900;
    }

    .cs-login-subtitle {
        color:
            #64748B;
        text-align:
            center;
        font-size:
            12px;
        margin-top:
            5px;
        margin-bottom:
            25px;
    }

    div.stButton > button {
        border-radius:
            9px;
        border:
            1px solid #26354D;
        background:
            #101827;
        color:
            #E5E7EB;
        font-weight:
            700;
    }

    div.stButton > button:hover {
        border-color:
            #2563EB;
        color:
            #FFFFFF;
    }

    div.stButton > button[kind="primary"] {
        background:
            #2563EB;
        border-color:
            #2563EB;
        color:
            #FFFFFF;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

def initialize_session() -> None:
    """Initialize all application session variables."""

    defaults = {
        "authenticated": False,
        "current_user": None,
        "current_module": "Overview",
        "selected_project_id": None,
        "project_action": None,
    }

    for key, value in defaults.items():

        if key not in st.session_state:
            st.session_state[key] = value


initialize_session()


# ============================================================
# DATABASE
# ============================================================

@st.cache_resource
def get_database():
    """
    Load the persistent JSON database.

    The returned dictionary is used during this Streamlit
    session. Mutating operations performed by database.py
    explicitly save to disk.
    """

    db = load_memory()

    ensure_admin_user(db)

    return db


db = get_database()


# ============================================================
# LOGIN
# ============================================================

def authenticate(
    username: str,
    password: str,
) -> dict | None:
    """Authenticate against the JSON user collection."""

    username = username.strip()

    if not username or not password:
        return None

    user = find_one(
        "users",
        "username",
        username,
        db,
    )

    if not user:
        return None

    if not user.get(
        "active",
        True,
    ):
        return None

    password_hash = user.get(
        "password_hash",
        "",
    )

    if not password_hash:
        return None

    if not verify_password(
        password,
        password_hash,
    ):
        return None

    return user


def render_login() -> None:
    """Render the Creative Studios login page."""

    st.markdown(
        """
        <div class="cs-login-wrapper">

            <div class="cs-login-card">

                <div class="cs-login-logo">
                    <div class="cs-login-logo-text">
                        CS
                    </div>
                </div>

                <div class="cs-login-title">
                    Creative Studios
                </div>

                <div class="cs-login-subtitle">
                    AEC Collaboration Platform
                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    # --------------------------------------------------------
    # Login form is intentionally outside the HTML card.
    # This avoids the empty rectangle/container problem.
    # --------------------------------------------------------

    _, center, _ = st.columns(
        [1, 2, 1]
    )


    with center:

        username = st.text_input(
            "Username",
            value="",
            placeholder="Enter username",
            key="login_username",
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter password",
            key="login_password",
        )

        login = st.button(
            "Sign In",
            type="primary",
            use_container_width=True,
            key="login_button",
        )

        if login:

            user = authenticate(
                username,
                password,
            )

            if user:

                st.session_state[
                    "authenticated"
                ] = True

                st.session_state[
                    "current_user"
                ] = {
                    "id": user.get("id"),
                    "username": user.get("username"),
                    "full_name": user.get(
                        "full_name",
                        user.get(
                            "username",
                            "User",
                        ),
                    ),
                    "role": user.get(
                        "role",
                        "User",
                    ),
                }

                st.session_state[
                    "current_module"
                ] = "Overview"

                st.rerun()

            else:

                st.error(
                    "Invalid username or password."
                )


        st.caption(
            "Creative Studios AEC Workspace"
        )


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar() -> str:
    """Render the complete Creative Studios sidebar."""

    user = st.session_state.get(
        "current_user"
    ) or {}


    # --------------------------------------------------------
    # Brand
    # --------------------------------------------------------

    st.sidebar.markdown(
        """
        <div class="cs-sidebar-brand">

            <div class="cs-brand-row">

                <div class="cs-logo">
                    <div class="cs-logo-text">
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

        </div>
        """,
        unsafe_allow_html=True,
    )


    # --------------------------------------------------------
    # User
    # --------------------------------------------------------

    full_name = user.get(
        "full_name",
        "System Administrator",
    )

    username = user.get(
        "username",
        "admin",
    )

    role = user.get(
        "role",
        "Admin",
    )


    st.sidebar.markdown(
        f"""
        <div class="cs-user-card">

            <div class="cs-user-label">
                Signed In
            </div>

            <div class="cs-user-name">
                {full_name}
            </div>

            <div class="cs-user-login">
                @{username}
            </div>

            <div class="cs-user-role">
                {role}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    # --------------------------------------------------------
    # Navigation
    # --------------------------------------------------------

    st.sidebar.markdown(
        '<div class="cs-nav-section">Workspace</div>',
        unsafe_allow_html=True,
    )


    modules = [
        (
            "Overview",
            "Overview",
        ),
        (
            "Projects",
            "Project Directory",
        ),
        (
            "Documents",
            "Documents",
        ),
        (
            "Drawings",
            "Drawings",
        ),
        (
            "Approvals",
            "Approvals",
        ),
    ]


    for module_key, label in modules:

        if st.sidebar.button(
            label,
            key=f"nav_{module_key}",
            use_container_width=True,
        ):

            st.session_state[
                "current_module"
            ] = module_key

            st.session_state[
                "project_action"
            ] = None

            st.session_state[
                "selected_project_id"
            ] = None

            st.rerun()


    st.sidebar.markdown(
        '<div class="cs-nav-section">Project Controls</div>',
        unsafe_allow_html=True,
    )


    controls = [
        (
            "BOQ",
            "Bill of Quantities",
        ),
        (
            "RFIs",
            "RFIs",
        ),
        (
            "Site Logs",
            "Site Logs",
        ),
        (
            "Tasks",
            "Tasks",
        ),
    ]


    for module_key, label in controls:

        if st.sidebar.button(
            label,
            key=f"nav_control_{module_key}",
            use_container_width=True,
        ):

            st.session_state[
                "current_module"
            ] = module_key

            st.session_state[
                "project_action"
            ] = None

            st.rerun()


    st.sidebar.markdown(
        '<div class="cs-nav-section">Administration</div>',
        unsafe_allow_html=True,
    )


    if st.sidebar.button(
        "Team",
        key="nav_team",
        use_container_width=True,
    ):

        st.session_state[
            "current_module"
        ] = "Team"

        st.rerun()


    if st.sidebar.button(
        "Settings",
        key="nav_settings",
        use_container_width=True,
    ):

        st.session_state[
            "current_module"
        ] = "Settings"

        st.rerun()


    st.sidebar.markdown(
        "<br>",
        unsafe_allow_html=True,
    )


    if st.sidebar.button(
        "Sign Out",
        key="logout_button",
        use_container_width=True,
    ):

        st.session_state[
            "authenticated"
        ] = False

        st.session_state[
            "current_user"
        ] = None

        st.session_state[
            "current_module"
        ] = "Overview"

        st.session_state[
            "selected_project_id"
        ] = None

        st.session_state[
            "project_action"
        ] = None

        st.rerun()


    st.sidebar.markdown(
        """
        <div class="cs-sidebar-footer">
            Creative Studios<br>
            AEC Collaboration Platform
        </div>
        """,
        unsafe_allow_html=True,
    )


    return st.session_state.get(
        "current_module",
        "Overview",
    )


# ============================================================
# OVERVIEW
# ============================================================

def render_overview() -> None:

    projects = db.get(
        "projects",
        [],
    )


    total = len(projects)

    active = sum(
        1
        for project in projects
        if str(
            project.get(
                "status",
                "",
            )
        ).lower()
        == "active"
    )


    planning = sum(
        1
        for project in projects
        if str(
            project.get(
                "status",
                "",
            )
        ).lower()
        == "planning"
    )


    completed = sum(
        1
        for project in projects
        if str(
            project.get(
                "status",
                "",
            )
        ).lower()
        == "completed"
    )


    st.title(
        "AEC Workspace"
    )

    st.caption(
        "Creative Studios project and construction collaboration platform."
    )


    col1, col2, col3, col4 = st.columns(
        4
    )


    col1.metric(
        "Projects",
        total,
    )

    col2.metric(
        "Active",
        active,
    )

    col3.metric(
        "Planning",
        planning,
    )

    col4.metric(
        "Completed",
        completed,
    )


    st.divider()


    st.subheader(
        "Workspace"
    )


    st.write(
        "Use the sidebar to navigate projects, documents, "
        "drawings, approvals and project controls."
    )


# ============================================================
# PLACEHOLDER MODULES
# ============================================================

def render_placeholder(
    title: str,
    description: str,
) -> None:

    st.title(
        title
    )

    st.caption(
        description
    )

    st.info(
        f"{title} module is ready for integration."
    )


# ============================================================
# MODULE ROUTER
# ============================================================

def render_module(
    module: str,
) -> None:

    if module == "Overview":

        render_overview()

        return


    if module == "Projects":

        render_projects_module(
            db
        )

        return


    module_descriptions = {
        "Documents":
            "Central project document management.",
        "Drawings":
            "Architectural, engineering and construction drawings.",
        "Approvals":
            "Track project reviews and approvals.",
        "BOQ":
            "Bill of Quantities and project cost planning.",
        "RFIs":
            "Requests for Information.",
        "Site Logs":
            "Daily construction site records.",
        "Tasks":
            "Project task and responsibility management.",
        "Team":
            "Project team and collaboration management.",
        "Settings":
            "Creative Studios workspace settings.",
    }


    render_placeholder(
        module,
        module_descriptions.get(
            module,
            "Creative Studios workspace module.",
        ),
    )


# ============================================================
# APPLICATION
# ============================================================

def main() -> None:

    if not st.session_state.get(
        "authenticated",
        False,
    ):

        render_login()

        return


    module = render_sidebar()

    render_module(
        module
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()