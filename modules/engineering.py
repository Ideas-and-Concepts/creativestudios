import streamlit as st
import pandas as pd
from typing import Any
from modules.database import save_memory

# ============================================================
# ENGINEERING MODULE
# ============================================================

def render_engineering_module(database: dict[str, Any]) -> None:
    """Render Engineering module for structural drawings and suggestions."""

    st.header("Engineering")

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

    # ---------------- Structural Drawings ----------------
    st.subheader("Structural Drawings")
    drawings = project.get("engineering_drawings", [])
    if drawings:
        st.dataframe(pd.DataFrame(drawings))
    else:
        st.caption("No structural drawings uploaded yet.")

    with st.form("add_eng_drawing", clear_on_submit=True):
        title = st.text_input("Drawing Title")
        filename = st.text_input("Filename")
        engineer = st.text_input("Engineer")
        submitted = st.form_submit_button("Upload Drawing")

        if submitted and title and filename:
            new_drawing = {
                "title": title,
                "filename": filename,
                "engineer": engineer
            }
            drawings.append(new_drawing)
            project["engineering_drawings"] = drawings
            save_memory(database)
            st.success(f"Uploaded structural drawing: {title}")

    # ---------------- Engineering Suggestions ----------------
    st.subheader("Engineering Suggestions")
    suggestions = project.get("engineering_suggestions", [])
    if suggestions:
        st.dataframe(pd.DataFrame(suggestions))
    else:
        st.caption("No suggestions yet.")

    with st.form("add_eng_suggestion", clear_on_submit=True):
        suggestion = st.text_area("Suggestion")
        suggested_by = st.text_input("Suggested By")
        submitted = st.form_submit_button("Add Suggestion")

        if submitted and suggestion:
            new_suggestion = {
                "suggestion": suggestion,
                "suggested_by": suggested_by
            }
            suggestions.append(new_suggestion)
            project["engineering_suggestions"] = suggestions
            save_memory(database)
            st.success("Added new engineering suggestion")