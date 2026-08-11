import streamlit as st
from .utils import hash_password

def login_user(db, username, password):
    user = next((u for u in db.get("users", []) if u["username"].lower() == username.lower()), None)
    if user and user["password_hash"] == hash_password(password):
        st.session_state["authenticated"] = True
        st.session_state["user"] = user
        return True
    return False

def render_sidebar():
    current_user = st.session_state.get("user")
    if current_user:
        st.sidebar.markdown(f"👤 **{current_user['name']}**")
        st.sidebar.caption(f"Role: `{current_user['role']}`")
        if st.sidebar.button("🚪 Sign Out", use_container_width=True):
            st.session_state["authenticated"] = False
            st.session_state["user"] = None
            st.rerun()
    st.sidebar.markdown("---")

def require_auth():
    if not st.session_state.get("authenticated", False):
        st.warning("Please sign in from the main login screen to access Creative Studios.")
        st.stop()
    render_sidebar()

