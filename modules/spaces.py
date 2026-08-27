import streamlit as st
from typing import Any
from modules.database import save_memory

def render_spaces_module(database: dict[str, Any]) -> None:
    """Render Spaces module for documenting rooms and linking files."""

    st.header("Project Spaces")

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

            # Linked files
            linked_docs = space.get("documents", [])
            linked_drawings = space.get("drawings", [])
            if linked_docs:
                st.write("**Linked Documents:**")
                for doc in linked_docs:
                    st.write(f"• {doc['title']} (v{doc['version']})")
            if linked_drawings:
                st.write("**Linked Drawings:**")
                for dr in linked_drawings:
                    st.write(f"• {dr['title']} (v{dr['version']})")

            st.write("---")

            # Add file linkage
            with st.form(f"link_file_{idx}", clear_on_submit=True):
                file_type = st.selectbox("Link Type", ["Document", "Drawing"])
                title = st.text_input("Title")
                version = st.text_input("Version", "v1.0")
                author = st.text_input("Author")
                filename = st.text_input("Filename (stored path)")
                submitted = st.form_submit_button("Link File")

                if submitted and title and filename:
                    new_file = {
                        "title": title,
                        "version": version,
                        "author": author,
                        "filename": filename
                    }
                    if file_type == "Document":
                        space.setdefault("documents", []).append(new_file)
                    else:
                        space.setdefault("drawings", []).append(new_file)
                    save_memory(database)
                    st.success(f"Linked {file_type}: {title}")
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
                "mep": {"hvac": hvac, "lighting": lighting, "plumbing": plumbing},
                "documents": [],
                "drawings": []
            }
            spaces.append(new_space)
            project["spaces"] = spaces
            save_memory(database)
            st.success(f"Added space: {name} ({area} m²)")