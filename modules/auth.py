"""
Creative Studios
Authentication module.

Uses the JSON database supplied by database.py.
"""

from __future__ import annotations

from typing import Any

import streamlit as st


# ============================================================
# DEFAULT USERS
# ============================================================

DEFAULT_USERS = [
    {
        "id": 1,
        "username": "admin",
        "password": "admin123",
        "full_name": "System Administrator",
        "role": "Admin",
        "active": True,
    },
    {
        "id": 2,
        "username": "arch_lead",
        "password": "arch123",
        "full_name": "Lead Architect",
        "role": "Architect",
        "active": True,
    },
    {
        "id": 3,
        "username": "struct_eng",
        "password": "struct123",
        "full_name": "Structural Engineer",
        "role": "Engineer",
        "active": True,
    },
]


# ============================================================
# AUTHENTICATION
# ============================================================

def login_user(
    db: dict,
    username: str,
    password: str,
) -> tuple[bool, dict]:

    username = str(
        username or ""
    ).strip()

    password = str(
        password or ""
    )

    if not username or not password:

        return False, {}


    users = db.get(
        "users",
        [],
    )

    if not isinstance(
        users,
        list,
    ):

        users = []


    # --------------------------------------------------------
    # Database users
    # --------------------------------------------------------

    for user in users:

        if not isinstance(
            user,
            dict,
        ):
            continue

        if not user.get(
            "active",
            True,
        ):
            continue

        db_username = str(
            user.get(
                "username",
                "",
            )
        ).strip()

        db_password = str(
            user.get(
                "password",
                user.get(
                    "password_hash",
                    "",
                ),
            )
        )

        if (
            db_username == username
            and db_password == password
        ):

            return True, normalize_user(
                user
            )


    # --------------------------------------------------------
    # Default development users
    # --------------------------------------------------------

    for user in DEFAULT_USERS:

        if (
            user["username"]
            == username
            and user["password"]
            == password
        ):

            return True, normalize_user(
                user
            )


    return False, {}


# ============================================================
# USER NORMALIZATION
# ============================================================

def normalize_user(
    user: dict,
) -> dict:

    username = str(
        user.get(
            "username",
            "admin",
        )
    )

    return {
        "id": user.get(
            "id",
            0,
        ),
        "username": username,
        "full_name": user.get(
            "full_name",
            user.get(
                "name",
                username,
            ),
        ),
        "role": user.get(
            "role",
            "User",
        ),
        "active": user.get(
            "active",
            True,
        ),
    }


# ============================================================
# SESSION HELPERS
# ============================================================

def is_authenticated() -> bool:

    return bool(
        st.session_state.get(
            "authenticated",
            False,
        )
    )


def get_current_user() -> dict:

    user = st.session_state.get(
        "user",
    )

    if isinstance(
        user,
        dict,
    ):

        return user

    return {
        "username": "admin",
        "full_name": "System Administrator",
        "role": "Admin",
        "active": True,
    }


def logout_user() -> None:

    st.session_state[
        "authenticated"
    ] = False

    st.session_state[
        "user"
    ] = None


# ============================================================
# COMPATIBILITY FUNCTION
# ============================================================

def require_auth() -> bool:

    """
    Compatibility helper for any older module that still calls
    require_auth().
    """

    if not is_authenticated():

        st.stop()

    return True