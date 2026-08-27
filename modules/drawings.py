import streamlit as st
from typing import Any
from modules.database import save_memory

def render_drawings_module(database: dict[str, Any]) -> None:
    st.header("Project Drawings")

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

    drawings = project.get("drawings", [])
    spaces = project.get("spaces", [])

    st.subheader("Drawings")
    if drawings:
        for dr in drawings:
            st.write(f"**{dr['title']}** (Phase: {dr['phase']}, v{dr['version']})")
            st.caption(f"Author: {dr['author']} | File: {dr['filename']}")
    else:
        st.caption("No drawings uploaded yet.")

    with st.form("add_drawing", clear_on_submit=True):
        title = st.text_input("Title")
        phase = st.selectbox("Phase", ["Architecture", "Engineering", "Construction", "MEP"])
        version = st.text_input("Version", "v1.0")
        author = st.text_input("Author")
        filename = st.text_input("Filename (stored path)")
        # New: link to space
        space_names = [s["name"] for s in spaces] if spaces else []
        link_space = st.selectbox("Link to Space", ["None"] + space_names)

        submitted = st.form_submit_button("Add Drawing")

        if submitted and title and filename:
            new_drawing = {
                "title": title,
                "phase": phase,
                "version": version,
                "author": author,
                "filename": filename
            }
            drawings.append(new_drawing)
            project["drawings"] = drawings

            # If linked to a space, also push into that space record
            if link_space != "None":
                for s in spaces:
                    if s["name"] == link_space:
                        s.setdefault("drawings", []).append(new_drawing)

            save_memory(database)
            st.success(f"Added drawing: {title} ({phase})")