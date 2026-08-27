import streamlit as st
from typing import Any
from modules.database import save_memory

def render_architecture_module(database: dict[str, Any]) -> None:
    """Render Architecture module for site plans, layouts, zoning."""

    st.header("Architecture Phase")

    projects = database.get("projects", [])
    if not projects:
        st.info("No projects available.")
        return

    project_names = [p.get("name", "Unnamed Project") for p in projects]
    selected_project = st.selectbox("Select Project", project_names)
    project = next((p for p in projects if p.get("name") == selected_project), None)
    if not project:
        st.warning("Project not found.")
        return

    architecture = project.get("architecture", {})

    st.subheader("Architectural Data")
    st.json(architecture)

    with st.form("add_architecture", clear_on_submit=True):
        site_plan = st.text_input("Site Plan Reference")
        zoning = st.text_input("Zoning/Compliance Notes")
        layout = st.text_area("Layout Description")
        submitted = st.form_submit_button("Save Architecture")

        if submitted:
            project["architecture"] = {
                "site_plan": site_plan,
                "zoning": zoning,
                "layout": layout
            }
            save_memory(database)
            st.success("Architecture data saved.")