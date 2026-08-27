import streamlit as st
from typing import Any
from modules.database import save_memory

def render_spaces_module(database: dict[str, Any]) -> None:
    """Render Spaces module for documenting rooms and areas."""

    st.header("Project Spaces")

    projects = database.get("projects", [])
    if not projects:
        st.info("No projects available.")
        return

    # Select project
    project_names = [p.get("name", "Unnamed Project") for p in projects]
    selected_project = st.selectbox("Select Project", project_names)

    project = next((p for p in projects if p.get("name") == selected_project), None)
    if not project:
        st.warning("Project not found.")
        return

    spaces = project.get("spaces", [])

    st.subheader("Spaces Overview")
    if spaces:
        for idx, space in enumerate(spaces):
            st.markdown(f"### {space['name']}")
            st.write(f"• Area: {space['area']} m²")
            st.write(f"• Usage: {space['usage']}")
            st.write(f"• Finishes: {space['finishes']}")
            st.write("**MEP Details:**")
            st.write(f"  - HVAC: {space['mep'].get('hvac','')}")
            st.write(f"  - Lighting: {space['mep'].get('lighting','')}")
            st.write(f"  - Plumbing: {space['mep'].get('plumbing','')}")
            st.write("---")

            # Edit/Delete controls
            col1, col2 = st.columns([1,1])
            if col1.button(f"Edit {idx}", key=f"edit_space_{idx}"):
                with st.form(f"edit_space_form_{idx}", clear_on_submit=True):
                    name = st.text_input("Name", space["name"])
                    area = st.number_input("Area (m²)", value=space["area"])
                    usage = st.text_input("Usage", space["usage"])
                    finishes = st.text_input("Finishes", space["finishes"])
                    hvac = st.text_input("HVAC", space["mep"].get("hvac",""))
                    lighting = st.text_input("Lighting", space["mep"].get("lighting",""))
                    plumbing = st.text_input("Plumbing", space["mep"].get("plumbing",""))
                    submitted = st.form_submit_button("Save Changes")
                    if submitted:
                        space.update({
                            "name": name,
                            "area": area,
                            "usage": usage,
                            "finishes": finishes,
                            "mep": {"hvac": hvac, "lighting": lighting, "plumbing": plumbing}
                        })
                        save_memory(database)
                        st.success("Space updated!")

            if col2.button(f"Delete {idx}", key=f"delete_space_{idx}"):
                spaces.pop(idx)
                project["spaces"] = spaces
                save_memory(database)
                st.warning("Space deleted.")

    else:
        st.caption("No spaces documented yet.")

    # Add new space form
    with st.form("add_space", clear_on_submit=True):
        name = st.text_input("Name")
        area = st.number_input("Area (m²)", min_value=0.0, step=1.0)
        usage = st.text_input("Usage")
        finishes = st.text_input("Finishes")
        hvac = st.text_input("HVAC")
        lighting = st.text_input("Lighting")
        plumbing = st.text_input("Plumbing")
        submitted = st.form_submit_button("Add Space")

        if submitted and name:
            new_space = {
                "name": name,
                "area": area,
                "usage": usage,
                "finishes": finishes,
                "mep": {"hvac": hvac, "lighting": lighting, "plumbing": plumbing}
            }
            spaces.append(new_space)
            project["spaces"] = spaces
            save_memory(database)
            st.success(f"Added space: {name} ({area} m²)")