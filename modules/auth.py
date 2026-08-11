"""
Creative Studios
Authentication Module

Simple JSON-compatible authentication for the AEC Workspace.
"""

from __future__ import annotations

import streamlit as st


# ============================================================
# DEFAULT ADMIN
# ============================================================

DEFAULT_ADMIN = {
    "id": 1,
    "username": "admin",
    "password": "admin123",
    "full_name": "System Administrator",
    "role": "Admin",
    "active": True,
}


# ============================================================
# NORMALIZE USER
# ============================================================

def normalize_user(user):
    """
    Convert any user dictionary into a predictable structure.
    """

    if not isinstance(user, dict):
        user = {}

    return {
        "id": user.get("id", 1),
        "username": str(
            user.get(
                "username",
                "admin",
            )
        ),
        "password": str(
            user.get(
                "password",
                "",
            )
        ),
        "full_name": str(
            user.get(
                "full_name",
                user.get(
                    "name",
                    "System Administrator",
                ),
            )
        ),
        "role": str(
            user.get(
                "role",
                "Admin",
            )
        ),
        "active": bool(
            user.get(
                "active",
                True,
            )
        ),
    }


# ============================================================
# GET USERS
# ============================================================

def get_users(db):
    """
    Safely retrieve users from the JSON database.
    """

    if not isinstance(db, dict):
        return []

    users = db.get(
        "users",
        [],
    )

    if not isinstance(
        users,
        list,
    ):
        return []

    return [
        normalize_user(user)
        for user in users
        if isinstance(
            user,
            dict,
        )
    ]


# ============================================================
# LOGIN
# ============================================================

def login_user(
    db,
    username,
    password,
):
    """
    Authenticate a user.

    Returns:

        (True, user)

    or:

        (False, {})

    """

    username = str(
        username or ""
    ).strip()

    password = str(
        password or ""
    )

    if not username or not password:
        return False, {}


    # --------------------------------------------------------
    # Database users
    # --------------------------------------------------------

    users = get_users(
        db
    )

    for user in users:

        if not user.get(
            "active",
            True,
        ):
            continue

        stored_username = str(
            user.get(
                "username",
                "",
            )
        ).strip()

        stored_password = str(
            user.get(
                "password",
                "",
            )
        )

        if (
            stored_username == username
            and stored_password == password
        ):

            return True, user


    # --------------------------------------------------------
    # Emergency/default administrator
    #
    # This ensures the application can still be accessed
    # even if the JSON file has been damaged or contains
    # no users.
    # --------------------------------------------------------

    if (
        username
        == DEFAULT_ADMIN["username"]
        and password
        == DEFAULT_ADMIN["password"]
    ):

        return True, dict(
            DEFAULT_ADMIN
        )


    return False, {}


# ============================================================
# AUTHENTICATED STATE
# ============================================================

def is_authenticated():
    """
    Return True when a user is currently signed in.
    """

    return bool(
        st.session_state.get(
            "authenticated",
            False,
        )
    )


# ============================================================
# CURRENT USER
# ============================================================

def get_current_user():
    """
    Return the currently signed-in user.
    """

    user = st.session_state.get(
        "user"
    )

    if isinstance(
        user,
        dict,
    ):

        return normalize_user(
            user
        )

    return normalize_user(
        DEFAULT_ADMIN
    )


# ============================================================
# LOGOUT
# ============================================================

def logout_user():
    """
    Completely clear authentication state.
    """

    st.session_state[
        "authenticated"
    ] = False

    st.session_state[
        "user"
    ] = None


# ============================================================
# REQUIRE AUTH
# ============================================================

def require_auth():
    """
    Compatibility function for older modules.

    Returns True when authenticated.
    """

    if not is_authenticated():

        st.stop()

    return True