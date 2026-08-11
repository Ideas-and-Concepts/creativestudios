"""
Creative Studios
Authentication Module

Handles:
- Login
- Logout
- Session management
- Authentication protection
- Current user information
- Sidebar navigation
"""

import streamlit as st

from .utils import hash_password


# ============================================================
# SESSION
# ============================================================

def initialize_auth_session() -> None:
    """Initialize authentication session variables."""

    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if "user" not in st.session_state:
        st.session_state["user"] = None

    if "app_mode" not in st.session_state:
        st.session_state[
            "app_mode"
        ] = "Project Directory"


# ============================================================
# LOGIN
# ============================================================

def login_user(
    db: dict,
    username: str,
    password: str,
) -> bool:
    """
    Authenticate a user.

    Returns:
        True if authentication succeeds.
        False otherwise.
    """

    initialize_auth_session()

    username = (
        username or ""
    ).strip()

    password = (
        password or ""
    )

    if not username or not password:
        return False

    users = db.get(
        "users",
        [],
    )

    if not isinstance(
        users,
        list,
    ):
        return False

    entered_hash = hash_password(
        password
    )

    for user in users:

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
        ).strip()

        if (
            stored_username.lower()
            != username.lower()
        ):
            continue

        if user.get(
            "active",
            True,
        ) is False:

            return False

        stored_hash = str(
            user.get(
                "password_hash",
                "",
            )
        )

        if (
            stored_hash
            and stored_hash == entered_hash
        ):

            st.session_state[
                "authenticated"
            ] = True

            # Store complete user record.
            st.session_state[
                "user"
            ] = user

            return True

        return False

    return False


# ============================================================
# LOGOUT
# ============================================================

def logout_user() -> None:
    """Clear the current login session."""

    st.session_state[
        "authenticated"
    ] = False

    st.session_state[
        "user"
    ] = None

    st.session_state[
        "app_mode"
    ] = "Project Directory"


# ============================================================
# AUTHENTICATION
# ============================================================

def is_authenticated() -> bool:
    """Check whether a valid user is logged in."""

    initialize_auth_session()

    user = st.session_state.get(
        "user"
    )

    return bool(
        st.session_state.get(
            "authenticated",
            False,
        )
        and isinstance(
            user,
            dict,
        )
        and user.get(
            "username"
        )
    )


def require_auth() -> None:
    """Prevent unauthenticated access."""

    initialize_auth_session()

    if not is_authenticated():

        st.warning(
            "Please sign in to access Creative Studios."
        )

        st.stop()


# ============================================================
# CURRENT USER
# ============================================================

def get_current_user():
    """Return the current user record."""

    user = st.session_state.get(
        "user"
    )

    if isinstance(
        user,
        dict,
    ):
        return user

    return None


def get_current_username() -> str:
    """Return the current username."""

    user = get_current_user()

    if not user:
        return ""

    return str(
        user.get(
            "username",
            "",
        )
    )


def get_current_user_name() -> str:
    """Return the user's display name."""

    user = get_current_user()

    if not user:
        return ""

    return str(
        user.get(
            "name",
            user.get(
                "username",
                "User",
            ),
        )
    )


def get_current_user_role() -> str:
    """Return the user's role."""

    user = get_current_user()

    if not user:
        return ""

    return str(
        user.get(
            "role",
            "User",
        )
    )


def has_role(
    *roles: str,
) -> bool:
    """Check whether the current user has one of the roles."""

    current_role = (
        get_current_user_role()
    )

    if not current_role:
        return False

    current_role = (
        current_role.lower()
    )

    allowed_roles = {
        str(role).lower()
        for role in roles
    }

    return (
        current_role
        in allowed_roles
    )


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar() -> None:
    """
    Render the complete Creative Studios sidebar.
    """

    if not is_authenticated():
        return

    user = get_current_user()

    if not user:
        return

    name = str(
        user.get(
            "name",
            user.get(
                "username",
                "User",
            ),
        )
    )

    username = str(
        user.get(
            "username",
            "",
        )
    )

    role = str(
        user.get(
            "role",
            "User",
        )
    )

    menu_items = [
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

    if current_mode not in menu_items:
        current_mode = (
            "Project Directory"
        )

    with st.sidebar:

        # ----------------------------------------------------
        # BRAND
        # ----------------------------------------------------

        st.markdown(
            """
            <div style="
                text-align:center;
                padding:8px 0 15px;
            ">

                <div style="
                    font-size:21px;
                    font-weight:800;
                    color:#FFFFFF;
                    letter-spacing:-0.5px;
                ">
                    Creative Studios
                </div>

                <div style="
                    font-size:9px;
                    color:#DBEAFE;
                    font-weight:700;
                    letter-spacing:1.2px;
                    text-transform:uppercase;
                    margin-top:4px;
                ">
                    AEC Collaboration Platform
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        # ----------------------------------------------------
        # NAVIGATION
        # ----------------------------------------------------

        st.markdown(
            """
            <div style="
                font-size:10px;
                color:#BFDBFE;
                font-weight:800;
                letter-spacing:1px;
                text-transform:uppercase;
                margin-bottom:6px;
            ">
                Workspace
            </div>
            """,
            unsafe_allow_html=True,
        )

        selected = st.radio(
            "Navigation",
            menu_items,
            index=menu_items.index(
                current_mode
            ),
            key="creative_studios_navigation",
            label_visibility="collapsed",
        )

        st.session_state[
            "app_mode"
        ] = selected

        st.divider()

        # ----------------------------------------------------
        # USER
        # ----------------------------------------------------

        st.markdown(
            f"""
            <div style="
                padding:12px;
                background:rgba(255,255,255,0.13);
                border:1px solid rgba(255,255,255,0.15);
                border-radius:12px;
                margin-bottom:10px;
            ">

                <div style="
                    font-size:9px;
                    color:#BFDBFE;
                    font-weight:800;
                    letter-spacing:1px;
                    text-transform:uppercase;
                ">
                    Signed In
                </div>

                <div style="
                    font-size:15px;
                    font-weight:800;
                    color:#FFFFFF;
                    margin-top:4px;
                ">
                    {name}
                </div>

                <div style="
                    font-size:11px;
                    color:#DBEAFE;
                    margin-top:3px;
                ">
                    @{username}
                </div>

                <div style="
                    display:inline-block;
                    margin-top:8px;
                    padding:4px 9px;
                    border-radius:999px;
                    background:#FFFFFF;
                    color:#1D4ED8;
                    font-size:9px;
                    font-weight:800;
                ">
                    {role}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        # ----------------------------------------------------
        # LOGOUT
        # ----------------------------------------------------

        if st.button(
            "Sign Out",
            use_container_width=True,
            key="creative_studios_signout",
        ):

            logout_user()

            st.rerun()


# ============================================================
# BACKWARD COMPATIBILITY
# ============================================================

def render_user_profile() -> None:
    """
    Compatibility function for older modules.
    """

    user = get_current_user()

    if not user:
        return

    name = user.get(
        "name",
        user.get(
            "username",
            "User",
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

    st.sidebar.markdown(
        f"""
        <div style="
            padding:10px;
            border-radius:10px;
            background:rgba(255,255,255,0.10);
        ">
            <strong>{name}</strong><br>
            <small>@{username}</small><br>
            <small>{role}</small>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_logout() -> None:
    """
    Compatibility function for older modules.

    Logout is now rendered by render_sidebar().
    """

    return