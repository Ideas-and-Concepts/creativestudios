"""
Creative Studios
Authentication Module

Handles:
- User authentication
- Session management
- Access protection
- Logout
"""

import streamlit as st

from .utils import hash_password


def login_user(db, username: str, password: str) -> bool:
    """
    Authenticate a user against the application database.

    Returns:
        True  -> authentication successful
        False -> authentication failed
    """

    username = (username or "").strip()

    if not username or not password:
        return False

    users = db.get("users", [])

    for user in users:

        stored_username = str(user.get("username", "")).strip()

        if stored_username.lower() != username.lower():
            continue

        # Disabled users cannot sign in.
        if user.get("active", True) is False:
            return False

        stored_hash = user.get("password_hash", "")

        if stored_hash and stored_hash == hash_password(password):

            st.session_state["authenticated"] = True

            # Store the complete user record.
            st.session_state["user"] = user

            return True

        return False

    return False


def logout_user() -> None:
    """
    Clear the authenticated user session.
    """

    st.session_state["authenticated"] = False
    st.session_state["user"] = None

    # Reset navigation to the first module.
    st.session_state["app_mode"] = "Project Directory"


def get_current_user():
    """
    Return the currently authenticated user.

    Returns:
        dict | None
    """

    return st.session_state.get("user")


def is_authenticated() -> bool:
    """
    Check whether the current session is authenticated.
    """

    return bool(
        st.session_state.get("authenticated", False)
        and st.session_state.get("user")
    )


def get_current_username() -> str:
    """
    Return the current user's username.
    """

    user = get_current_user()

    if not user:
        return ""

    return str(user.get("username", ""))


def get_current_user_name() -> str:
    """
    Return the current user's display name.
    """

    user = get_current_user()

    if not user:
        return ""

    return str(
        user.get(
            "name",
            user.get("username", "User")
        )
    )


def get_current_user_role() -> str:
    """
    Return the current user's role.
    """

    user = get_current_user()

    if not user:
        return ""

    return str(user.get("role", "User"))


def has_role(*roles: str) -> bool:
    """
    Check whether the authenticated user has one of
    the supplied roles.
    """

    current_role = get_current_user_role()

    if not current_role:
        return False

    return current_role.lower() in {
        role.lower()
        for role in roles
    }


def require_auth() -> None:
    """
    Protect authenticated application content.

    If the user is not authenticated, display a warning
    and stop execution.
    """

    if not is_authenticated():

        st.warning(
            "Please sign in from the main login screen "
            "to access Creative Studios."
        )

        st.stop()


def render_user_profile() -> None:
    """
    Render the current user's information.
    """

    user = get_current_user()

    if not user:
        return

    name = user.get(
        "name",
        user.get("username", "User")
    )

    username = user.get("username", "")
    role = user.get("role", "User")

    st.sidebar.markdown(
        f"""
        <div style="
            padding:12px;
            background:#1E293B;
            border-radius:10px;
            margin-bottom:10px;
        ">
            <div style="
                font-size:11px;
                color:#94A3B8;
                text-transform:uppercase;
                letter-spacing:0.6px;
            ">
                Signed In
            </div>

            <div style="
                font-size:15px;
                font-weight:700;
                color:#F8FAFC;
                margin-top:3px;
            ">
                {name}
            </div>

            <div style="
                font-size:12px;
                color:#CBD5E1;
                margin-top:2px;
            ">
                @{username}
            </div>

            <div style="
                font-size:11px;
                color:#94A3B8;
                margin-top:5px;
            ">
                {role}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_logout() -> None:
    """
    Render the logout control.
    """

    if st.sidebar.button(
        "Sign Out",
        use_container_width=True,
    ):

        logout_user()
        st.rerun()