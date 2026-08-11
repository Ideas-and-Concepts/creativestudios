import streamlit as st
from datetime import date
from pathlib import Path
from utils import load_memory, hash_password, render_sidebar, ensure_logo_svg, get_logo_html, save_memory, LOGO_FILE

ensure_logo_svg()

st.set_page_config(
    page_title="Creative Studios — AEC Collaboration Platform",
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
        st.markdown(get_logo_html(width=140), unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #1E293B;'>Creative Studios</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748B;'>Architectural, Engineering & Construction Collaboration</p><br>", unsafe_allow_html=True)
        
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
        
        with st.expander("Default Test Credentials"):
            st.markdown("""
            * **Architect**: `arch_lead` / `arch123`
            * **Structural Engineer**: `struct_eng` / `struct123`
            * **Electrical Engineer**: `elec_eng` / `elec123`
            * **Plumber**: `plumber_lead` / `plum123`
            * **Admin**: `admin` / `admin123`
            """)
else:
    render_sidebar()
    user = st.session_state["user"]
    
    st.title("🏗️ Project Directory & Dashboard")
    st.caption(f"Welcome back, **{user['name']}** ({user['role']}). Manage and track active architectural & engineering projects below.")
    
    tab1, tab2 = st.tabs(["📁 Active Projects", "➕ Create New Project"])
    
    with tab1:
        projects = db.get("projects", [])
        if not projects:
            st.info("No projects registered yet. Use the 'Create New Project' tab to add your first build.")
        else:
            for p in projects:
                with st.expander(f"📌 [{p['id']}] {p['name']} — *Phase: {p['phase']}*", expanded=True):
                    col_a, col_b, col_c = st.columns(3)
                    col_a.markdown(f"**Project Type:** `{p['type']}`")
                    col_b.markdown(f"**Estimated Budget:** `${p['budget']:,.2f}`")
                    col_c.markdown(f"**Created Date:** `{p['created_at']}`")
                    st.markdown(f"**Scope Description:** {p['description']}")
    
    with tab2:
        st.subheader("Register a New AEC Project")
        with st.form("new_project_form"):
            p_id = st.text_input("Project ID Code (e.g., PRJ-002)")
            p_name = st.text_input("Project Name")
            p_type = st.selectbox("Project Type", ["Commercial", "Residential", "Industrial", "Civic / Infrastructure", "Mixed-Use"])
            p_phase = st.selectbox("Current Lifecycle Phase", ["Concept Design", "Schematic Design", "Design Development", "Construction Documents", "Bidding & Negotiation", "Construction Administration"])
            p_budget = st.number_input("Estimated Budget ($)", min_value=1000.0, value=500000.0, step=10000.0)
            p_desc = st.text_area("Scope & Overview Description")
            
            submitted = st.form_submit_button("Save & Register Project", use_container_width=True)
            if submitted:
                if not p_id or not p_name:
                    st.error("Project ID and Name are required fields.")
                else:
                    if any(existing["id"].lower() == p_id.lower() for existing in db.get("projects", [])):
                        st.error(f"Project ID '{p_id}' already exists.")
                    else:
                        new_proj = {
                            "id": p_id,
                            "name": p_name,
                            "type": p_type,
                            "phase": p_phase,
                            "budget": p_budget,
                            "created_at": str(date.today()),
                            "description": p_desc
                        }
                        db["projects"].append(new_proj)
                        save_memory(db)
                        st.success(f"Project '{p_name}' successfully documented and saved!")
                        st.rerun()
