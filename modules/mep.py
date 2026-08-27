import streamlit as st
from typing import Any
from modules.database import save_memory

def render_mep_module(database: dict[str, Any]) -> None:
    """Render MEP module for mechanical, electrical, plumbing."""

    st.header("MEP Phase")

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

    mep = project.get("mep", {})

    st.subheader("MEP Data")
    st.json(mep)

    with st.form("add_mep", clear_on_submit=True):
        hvac = st.text_input("HVAC System")
        electrical = st.text_area("Electrical Layout")
        plumbing = st.text_area("Plumbing Layout")
        fire_safety = st.text_area("Fire Safety Notes")
        submitted = st.form_submit_button("Save MEP")

        if submitted:
            project["mep"] = {
                "hvac": hvac,
                "electrical": electrical,
                "plumbing": plumbing,
                "fire_safety": fire_safety
            }
            save_memory(database)
            st.success("MEP data saved.")