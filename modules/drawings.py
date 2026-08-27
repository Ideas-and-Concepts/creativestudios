import streamlit as st
from typing import Any
from modules.database import save_memory

def render_drawings_module(database: dict[str, Any]) -> None:
    """Render Drawings module for CAD/PDF plans."""

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

    st.subheader("Drawings")
    if drawings:
        for idx, dr in enumerate(drawings):
            st.write(f"**{dr['title']}** (Phase: {dr['phase']}, Version: {dr['version']})")
            st.caption(f"Author: {dr['author']} | File: {dr['filename']}")
            st.write("---")
    else:
        st.caption("No drawings uploaded yet.")

    with st.form("add_drawing", clear_on_submit=True):
        title = st.text_input("Title")
        phase = st.selectbox("Phase", ["Architecture", "Engineering", "Construction", "MEP"])
        version = st.text_input("Version", "v1.0")
        author = st.text_input("Author")
        filename = st.text_input("Filename (stored path)")
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
            save_memory(database)
            st.success(f"Added drawing: {title} ({phase})")