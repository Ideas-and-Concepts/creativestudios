import streamlit as st
from typing import Any
from modules.database import save_memory

def render_engineering_module(database: dict[str, Any]) -> None:
    """Render Engineering module for structural and technical details."""

    st.header("Engineering Phase")

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

    engineering = project.get("engineering", {})

    st.subheader("Engineering Data")
    st.json(engineering)

    with st.form("add_engineering", clear_on_submit=True):
        structural_notes = st.text_area("Structural Notes")
        steel_schedule = st.text_area("Steel Schedule")
        bim_model = st.text_input("BIM/Model Reference")
        submitted = st.form_submit_button("Save Engineering")

        if submitted:
            project["engineering"] = {
                "structural_notes": structural_notes,
                "steel_schedule": steel_schedule,
                "bim_model": bim_model
            }
            save_memory(database)
            st.success("Engineering data saved.")