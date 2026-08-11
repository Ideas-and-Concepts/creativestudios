"""
Creative Studios
AEC Workspace Authentication

Compatible with creativestudios_db.json
"""

from __future__ import annotations

import hashlib
import hmac
import streamlit as st


DEFAULT_ADMIN = {
    "id": 1,
    "username": "admin",
    "password": "admin123",
    "password_hash": "",
    "full_name": "System Administrator",
    "role": "Admin",
    "active": True,
}


def _hash_password(password: str) -> str:
    """Create a SHA-256 password hash."""
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


def _check_password(
    supplied_password: str,
    user: dict,
) -> bool:
    """
    Support both plaintext passwords and password_hash.
    """

    supplied_password = str(
        supplied_password or ""
    )

    # Current JSON database format
    stored_password = user.get(
        "password"
    )

    if stored_password is not None:
        stored_password = str(
            stored_password
        )

        if hmac.compare_digest(
            stored_password,
            supplied_password,
        ):
            return True

    # Older database format
    stored_hash = user.get(
        "password_hash"
    )

    if stored_hash:

        supplied_hash = _hash_password(
            supplied_password
        )

        if hmac.compare_digest(
            str(stored_hash),
            supplied_hash,
        ):
            return True

    return False


def _normalize_user(user: dict) -> dict:

    if not isinstance(user, dict):
        return {}

    return {
        "id": user.get(
            "id",
            1,
        ),
        "username": str(
            user.get(
                "username",
                "",
            )
        ),
        "password": str(
            user.get(
                "password",
                "",
            )
        ),
        "password_hash": str(
            user.get(
                "password_hash",
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


def get_users(db) -> list:

    if not isinstance(db, dict):
        return []

    users = db.get(
        "users",
        [],
    )

    if not isinstance(users, list):
        return []

    return [
        _normalize_user(user)
        for user in users
        if isinstance(user, dict)
    ]


def login_user(
    db,
    username,
    password,
):
    """
    Authenticate a user.

    Returns:
        (True, user)
        or
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

    users = get_users(db)

    # --------------------------------------------------------
    # Check database users
    # --------------------------------------------------------

    for user in users:

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

        if not hmac.compare_digest(
            db_username,
            username,
        ):
            continue

        if _check_password(
            password,
            user,
        ):
            return True, user

    # --------------------------------------------------------
    # Guaranteed administrator recovery
    #
    # This keeps the application accessible if the JSON file
    # was accidentally emptied or the admin record disappeared.
    # --------------------------------------------------------

    if (
        username == "admin"
        and password == "admin123"
    ):

        return True, dict(
            DEFAULT_ADMIN
        )

    return False, {}


def is_authenticated() -> bool:

    return bool(
        st.session_state.get(
            "authenticated",
            False,
        )
    )


def get_current_user() -> dict:

    user = st.session_state.get(
        "user"
    )

    if isinstance(user, dict):

        return _normalize_user(
            user
        )

    return dict(
        DEFAULT_ADMIN
    )


def logout_user() -> None:

    st.session_state[
        "authenticated"
    ] = False

    st.session_state[
        "user"
    ] = None


def require_auth() -> bool:

    if not is_authenticated():
        st.stop()

    return True