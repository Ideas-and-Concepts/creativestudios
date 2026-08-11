import streamlit as st
from datetime import datetime
from utils import load_memory, save_memory, require_auth, safe_dataframe

st.set_page_config(page_title="Project Directory", page_icon="📁", layout="wide")
require_auth()

db = load_memory()
current_user = st.session_state["user"]

st.title("📁 Project Directory")

tab1, tab2 = st.tabs(["View Projects", "Register New Project"])

with tab1:
    if db.get("projects"):
        df_projects = safe_dataframe(
            db["projects"], 
            ["id", "name", "type", "status", "budget", "created", "description"]
        )
        st.dataframe(df_projects, use_container_width=True)
    else:
        st.info("No active projects.")

with tab2:
    st.subheader("Register a Project")
    if current_user["role"] in ["Admin", "Architect", "Procurement Officer"]:
        with st.form("new_project_form"):
            p_name = st.text_input("Project Title")
            p_type = st.selectbox("Classification", [
                "New Construction", "Renovation / MEP Overhaul", 
                "Structural Upgrade", "Fit-out & MEP Retrofit"
            ])
            p_status = st.selectbox("Status", ["Planning", "In Review", "Active Execution", "Completed"])
            p_budget = st.number_input("Estimated Budget ($)", min_value=0.0, step=1000.0)
            p_desc = st.text_area("Scope")

            submitted = st.form_submit_button("Create Project Entry")
            if submitted and p_name:
                new_id = f"PRJ-{len(db['projects']) + 1:03d}"
                db["projects"].append({
                    "id": new_id, "name": p_name, "type": p_type,
                    "status": p_status, "created": datetime.now().isoformat(),
                    "budget": p_budget, "description": p_desc
                })
                save_memory(db)
                st.success(f"Project '{p_name}' created with ID: {new_id}")
                st.rerun()
    else:
        st.warning("🔒 Role insufficient to create projects.")
