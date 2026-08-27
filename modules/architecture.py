import streamlit as st
import pandas as pd
from typing import Any
from modules.database import save_memory

# ============================================================
# ARCHITECTURE MODULE
# ============================================================

def render_architecture_module(database: dict[str, Any]) -> None:
    """Render Architecture module for drawings and design suggestions."""

    st.header("Architecture")

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

    # ---------------- Drawings ----------------
    st.subheader("Architectural Drawings")
    drawings = project.get("architecture_drawings", [])
    if drawings:
        st.dataframe(pd.DataFrame(drawings))
    else:
        st.caption("No drawings uploaded yet.")

    with st.form("add_arch_drawing", clear_on_submit=True):
        title = st.text_input("Drawing Title")
        filename = st.text_input("Filename")
        author = st.text_input("Author")
        submitted = st.form_submit_button("Upload Drawing")

        if submitted and title and filename:
            new_drawing = {
                "title": title,
                "filename": filename,
                "author": author
            }
            drawings.append(new_drawing)
            project["architecture_drawings"] = drawings
            save_memory(database)
            st.success(f"Uploaded drawing: {title}")

    # ---------------- Suggestions ----------------
    st.subheader("Design Suggestions")
    suggestions = project.get("architecture_suggestions", [])
    if suggestions:
        st.dataframe(pd.DataFrame(suggestions))
    else:
        st.caption("No suggestions yet.")

    with st.form("add_arch_suggestion", clear_on_submit=True):
        suggestion = st.text_area("Suggestion")
        suggested_by = st.text_input("Suggested By")
        submitted = st.form_submit_button("Add Suggestion")

        if submitted and suggestion:
            new_suggestion = {
                "suggestion": suggestion,
                "suggested_by": suggested_by
            }
            suggestions.append(new_suggestion)
            project["architecture_suggestions"] = suggestions
            save_memory(database)
            st.success("Added new suggestion")