"""
Creative Studios
Authentication Module
"""

import streamlit as st

from .utils import hash_password


# ============================================================
# SESSION
# ============================================================

def initialize_auth_session():

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
    db,
    username,
    password,
):

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

def logout_user():

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

def is_authenticated():

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


def require_auth():

    if not is_authenticated():

        st.warning(
            "Please sign in to access Creative Studios."
        )

        st.stop()


# ============================================================
# USER
# ============================================================

def get_current_user():

    user = st.session_state.get(
        "user"
    )

    if isinstance(user, dict):
        return user

    return None


def get_current_username():

    user = get_current_user()

    if not user:
        return ""

    return str(
        user.get(
            "username",
            "",
        )
    )


def get_current_user_name():

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


def get_current_user_role():

    user = get_current_user()

    if not user:
        return ""

    return str(
        user.get(
            "role",
            "User",
        )
    )


def has_role(*roles):

    role = get_current_user_role()

    if not role:
        return False

    role = role.lower()

    return role in {
        str(item).lower()
        for item in roles
    }


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar():

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

    current = st.session_state.get(
        "app_mode",
        "Project Directory",
    )

    if current not in menu_items:
        current = "Project Directory"

    with st.sidebar:

        st.markdown(
            """
            <div style="
                text-align:center;
                padding:8px 0 16px;
            ">

                <div style="
                    font-size:21px;
                    font-weight:800;
                    color:#FFFFFF;
                ">
                    Creative Studios
                </div>

                <div style="
                    font-size:9px;
                    color:#DBEAFE;
                    font-weight:700;
                    letter-spacing:1px;
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

        st.markdown(
            """
            <div style="
                color:#BFDBFE;
                font-size:10px;
                font-weight:800;
                text-transform:uppercase;
                letter-spacing:1px;
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
                current
            ),
            key="creative_navigation",
            label_visibility="collapsed",
        )

        st.session_state[
            "app_mode"
        ] = selected

        st.divider()

        st.markdown(
            f"""
            <div style="
                background:rgba(255,255,255,0.13);
                border:1px solid rgba(255,255,255,0.15);
                border-radius:12px;
                padding:12px;
            ">

                <div style="
                    font-size:9px;
                    color:#BFDBFE;
                    font-weight:800;
                    text-transform:uppercase;
                ">
                    Signed In
                </div>

                <div style="
                    color:#FFFFFF;
                    font-size:15px;
                    font-weight:800;
                    margin-top:4px;
                ">
                    {name}
                </div>

                <div style="
                    color:#DBEAFE;
                    font-size:11px;
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

        st.write("")

        if st.button(
            "Sign Out",
            use_container_width=True,
            key="creative_signout",
        ):

            logout_user()

            st.rerun()


# ============================================================
# COMPATIBILITY FUNCTIONS
# ============================================================

def render_user_profile():
    return


def render_sidebar_logout():
    return