import streamlit as st
from utils import load_memory, hash_password, render_sidebar_logo

st.set_page_config(
    page_title="Architectural & MEP Management System",
    page_icon="📐",
    layout="wide"
)

db = load_memory()

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["user"] = None

def login(username, password):
    user = next((u for u in db.get("users", []) if u["username"].lower() == username.lower()), None)
    if user and user["password_hash"] == hash_password(password):
        st.session_state["authenticated"] = True
        st.session_state["user"] = user
        return True
    return False

if not st.session_state["authenticated"]:
    # Display Logo on Login Page
    col_logo, col_text = st.columns([1, 3])
    with col_logo:
        try:
            st.image("logo.jpg", width=120)
        except Exception:
            st.warning("Logo image 'logo.jpg' not found in root directory.")
    with col_text:
        st.title("System Portal")
        st.markdown("Sign in to access project blueprints, approval pipelines, and BoQs.")

    col_login, col_demo = st.columns([1, 1])

    with col_login:
        with st.form("login_form"):
            user_input = st.text_input("Username")
            pass_input = st.text_input("Password", type="password")
            submit_btn = st.form_submit_button("Sign In")

            if submit_btn:
                if login(user_input, pass_input):
                    st.success("Authentication successful! Use the sidebar to navigate.")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

    with col_demo:
        st.subheader("💡 Demo Quick Switch")
        for u in db.get("users", []):
            if st.button(f"Login as {u['name']} [{u['role']}]", key=f"quick_{u['username']}"):
                pwd_map = {
                    "admin": "admin123", "jane_arch": "arch123",
                    "john_struct": "struct123", "mark_mep": "mep123",
                    "sam_proc": "proc123"
                }
                login(u['username'], pwd_map.get(u['username'], "admin123"))
                st.rerun()
else:
    # Render sidebar logo for logged-in users on root page too
    render_sidebar_logo()
    
    user = st.session_state["user"]
    st.title("Management System Dashboard")
    st.success(f"Welcome, **{user['name']}** ({user['role']}). Use the sidebar menu to open pages.")
    
    st.sidebar.markdown(f"👤 **{user['name']}**")
    st.sidebar.caption(f"Role: `{user['role']}`")
    if st.sidebar.button("🚪 Sign Out"):
        st.session_state["authenticated"] = False
        st.session_state["user"] = None
        st.rerun()
