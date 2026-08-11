"""
Creative Studios
Authentication Module

Handles:
- User authentication
- Session management
- Access protection
- Sidebar user profile
- Logout
"""

import streamlit as st

from .utils import hash_password


# ============================================================
# SESSION INITIALIZATION
# ============================================================

def initialize_auth_session() -> None:
    """Initialize authentication-related session state."""

    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if "user" not in st.session_state:
        st.session_state["user"] = None


# ============================================================
# LOGIN
# ============================================================

def login_user(
    db,
    username: str,
    password: str,
) -> bool:
    """
    Authenticate a user against the application database.

    On success, the complete user dictionary is stored in
    st.session_state["user"].
    """

    initialize_auth_session()

    username = (
        username or ""
    ).strip()

    password = password or ""

    if not username or not password:
        return False

    users = db.get(
        "users",
        [],
    )

    if not isinstance(users, list):
        return False

    password_hash = hash_password(
        password
    )

    for user in users:

        if not isinstance(user, dict):
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

        # Disabled account
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
            and stored_hash == password_hash
        ):

            # IMPORTANT:
            # Store the complete user record.
            st.session_state[
                "authenticated"
            ] = True

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
    """Log out the current user."""

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
# AUTHENTICATION STATUS
# ============================================================

def is_authenticated() -> bool:
    """Return True when a valid user session exists."""

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
    """
    Protect authenticated application content.

    Stops execution when the user is not authenticated.
    """

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
    """Return the authenticated user dictionary."""

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
    """Check whether the current user has one of the supplied roles."""

    current_role = (
        get_current_user_role()
    )

    if not current_role:
        return False

    current_role = current_role.lower()

    return current_role in {
        str(role).lower()
        for role in roles
    }


# ============================================================
# SIDEBAR USER PROFILE
# ============================================================

def render_sidebar() -> None:
    """
    Render the complete authenticated sidebar.

    This function intentionally owns the sidebar so that
    streamlit_app.py does not have a second competing sidebar.
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

    with st.sidebar:

        st.markdown(
            """
            <div style="
                text-align:center;
                padding:8px 0 18px 0;
            ">
                <div style="
                    font-size:20px;
                    font-weight:800;
                    color:#FFFFFF;
                    letter-spacing:-0.4px;
                ">
                    Creative Studios
                </div>

                <div style="
                    font-size:10px;
                    color:#BFDBFE;
                    text-transform:uppercase;
                    letter-spacing:1.2px;
                    margin-top:3px;
                ">
                    AEC Collaboration Platform
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        st.markdown(
            """
            <div style="
                font-size:10px;
                font-weight:800;
                color:#BFDBFE;
                text-transform:uppercase;
                letter-spacing:1.1px;
                margin-bottom:8px;
            ">
                AEC Workspace
            </div>
            """,
            unsafe_allow_html=True,
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

        app_mode = st.radio(
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
        ] = app_mode

        st.divider()

        # ----------------------------------------------------
        # USER PROFILE
        # ----------------------------------------------------

        st.markdown(
            f"""
            <div style="
                background:rgba(255,255,255,0.12);
                border:1px solid rgba(255,255,255,0.12);
                border-radius:12px;
                padding:12px;
                margin-bottom:10px;
            ">

                <div style="
                    font-size:10px;
                    color:#BFDBFE;
                    text-transform:uppercase;
                    letter-spacing:0.8px;
                    font-weight:700;
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
                    font-size:12px;
                    color:#DBEAFE;
                    margin-top:3px;
                ">
                    @{username}
                </div>

                <div style="
                    display:inline-block;
                    margin-top:8px;
                    padding:4px 8px;
                    border-radius:999px;
                    background:#FFFFFF;
                    color:#1D4ED8;
                    font-size:10px;
                    font-weight:800;
                ">
                    {role}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Sign Out",
            use_container_width=True,
            key="creative_studios_logout",
        ):

            logout_user()

            st.rerun()


# ============================================================
# COMPATIBILITY ALIAS
# ============================================================

def render_sidebar_logout() -> None:
    """
    Backwards-compatible logout helper.

    Older modules can safely call this without crashing.
    """

    if not is_authenticated():
        return

    if st.sidebar.button(
        "Sign Out",
        use_container_width=True,
        key="legacy_sidebar_logout",
    ):

        logout_user()

        st.rerun()