import streamlit as st
from pathlib import Path
from utils import load_memory, hash_password, render_sidebar_logo, ensure_logo_svg, get_logo_html, LOGO_FILE

ensure_logo_svg()

st.set_page_config(
    page_title="Architectural & MEP Management System",
    page_icon=LOGO_FILE if Path(LOGO_FILE).exists() else "📐",
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
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        # Perfectly centered logo display on login page
        st.markdown(get_logo_html(width=140), unsafe_allow_html=True)
        
        with st.form("login_form"):
            user_input = st.text_input("Username")
            pass_input = st.text_input("Password", type="password")
            submit_btn = st.form_submit_button("Sign In", use_container_width=True)

            if submit_btn:
                if login(user_input, pass_input):
                    st.success("Authentication successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
else:
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
