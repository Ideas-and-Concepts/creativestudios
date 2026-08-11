import streamlit as st
from datetime import date
from .database import save_memory

def render_projects_module(db):
    st.title("Project Directory & Dashboard")
    st.caption("Manage and track active architectural, engineering, and construction projects.")

    tab1, tab2 = st.tabs(["Active Projects", "Create New Project"])

    with tab1:
        projects = db.get("projects", [])
        if not projects:
            st.info("No projects registered yet. Use the 'Create New Project' tab to add your first build.")
        else:
            for p in projects:
                with st.expander(f"[{p['id']}] {p['name']} — Phase: {p['phase']}", expanded=True):
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