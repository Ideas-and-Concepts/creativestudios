import streamlit as st
from pathlib import Path
from modules.utils import ensure_logo_svg, get_logo_html, LOGO_FILE
from modules.database import load_memory
from modules.auth import login_user, require_auth
from modules.projects import render_projects_module
from modules.drawings import render_drawings_module
from modules.approvals import render_approvals_module
from modules.boq import render_boq_module

ensure_logo_svg()

st.set_page_config(
    page_title="Creative Studios — AEC Platform",
    page_icon=LOGO_FILE if Path(LOGO_FILE).exists() else "📐",
    layout="wide"
)

db = load_memory()

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["user"] = None

if not st.session_state["authenticated"]:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(get_logo_html(width=130), unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #0F172A; font-weight: 700;'>Creative Studios</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748B;'>Architectural, Engineering & Construction Collaboration</p><br>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            user_input = st.text_input("Username")
            pass_input = st.text_input("Password", type="password")
            submit_btn = st.form_submit_button("Sign In", use_container_width=True)

            if submit_btn:
                if login_user(db, user_input, pass_input):
                    st.success("Authentication successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
        
        with st.expander("Default Test Credentials"):
            st.markdown("""
            * **Lead Architect**: `arch_lead` / `arch123`
            * **Structural Engineer**: `struct_eng` / `struct123`
            * **Electrical Engineer**: `elec_eng` / `elec123`
            * **Master Plumber**: `plumber_lead` / `plum123`
            * **System Admin**: `admin` / `admin123`
            """)
else:
    require_auth()
    
    st.sidebar.markdown("### 🧭 Navigation")
    app_mode = st.sidebar.radio(
        "Select Module",
        [
            "Project Directory", 
            "Drawing Repository", 
            "Sign-Off & Approvals", 
            "Bill of Quantities (BOQ)"
        ],
        label_visibility="collapsed"
    )
    
    st.sidebar.markdown("---")
    
    if app_mode == "Project Directory":
        render_projects_module(db)
    elif app_mode == "Drawing Repository":
        render_drawings_module(db)
    elif app_mode == "Sign-Off & Approvals":
        render_approvals_module(db)
    elif app_mode == "Bill of Quantities (BOQ)":
        render_boq_module(db)
