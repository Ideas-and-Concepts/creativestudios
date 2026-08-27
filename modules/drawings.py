import streamlit as st
import pandas as pd
from typing import Any

# ============================================================
# DRAWINGS MODULE
# ============================================================

def render_drawings_module(database: dict[str, Any]) -> None:
    """Render Drawings module to view all project drawings."""

    st.header("Project Drawings")

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

    # Collect drawings from architecture + engineering
    arch_drawings = project.get("architecture_drawings", [])
    eng_drawings = project.get("engineering_drawings", [])

    combined = []
    for d in arch_drawings:
        combined.append({
            "Title": d.get("title"),
            "Filename": d.get("filename"),
            "Author/Engineer": d.get("author", ""),
            "Discipline": "Architecture"
        })
    for d in eng_drawings:
        combined.append({
            "Title": d.get("title"),
            "Filename": d.get("filename"),
            "Author/Engineer": d.get("engineer", ""),
            "Discipline": "Engineering"
        })

    # Display combined drawings
    st.subheader("All Drawings")
    if combined:
        df = pd.DataFrame(combined)
        st.dataframe(df)
    else:
        st.caption("No drawings uploaded yet.")