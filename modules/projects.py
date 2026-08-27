import streamlit as st
from .database import save_memory

def render_projects_module(database):
    st.header("📂 Projects")

    # Create
    project_name = st.text_input("New Project Name")
    if st.button("Add Project"):
        new_project = {"name": project_name, "documents": [], "drawings": [], "mep": []}
        database.setdefault("projects", []).append(new_project)
        save_memory(database)
        st.success(f"Project '{project_name}' added successfully!")

    # Read + Update + Delete
    if "projects" in database and database["projects"]:
        st.subheader("Manage Projects")
        for i, project in enumerate(database["projects"]):
            with st.expander(f"Project: {project['name']}"):
                new_name = st.text_input("Edit Name", value=project["name"], key=f"name_{i}")
                if st.button("Update", key=f"update_{i}"):
                    project["name"] = new_name
                    save_memory(database)
                    st.success("Project updated!")

                if st.button("Delete", key=f"delete_{i}"):
                    database["projects"].pop(i)
                    save_memory(database)
                    st.warning("Project deleted!")
                    st.experimental_rerun()
