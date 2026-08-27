import streamlit as st
import pandas as pd
from typing import Any
from modules.database import save_memory

# ============================================================
# TASKS MODULE
# ============================================================

def render_tasks_module(database: dict[str, Any]) -> None:
    """Render Tasks module for managing project tasks."""

    st.header("Project Tasks")

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

    tasks = project.get("tasks", [])

    # Display tasks
    st.subheader("Existing Tasks")
    if tasks:
        df = pd.DataFrame(tasks)
        st.dataframe(df)
    else:
        st.caption("No tasks recorded yet.")

    # Add new task form
    with st.form("add_task", clear_on_submit=True):
        title = st.text_input("Task Title")
        description = st.text_area("Description")
        assigned_to = st.text_input("Assigned To")
        due_date = st.date_input("Due Date")
        status = st.selectbox("Status", ["Not Started", "In Progress", "Completed"])
        submitted = st.form_submit_button("Add Task")

        if submitted and title:
            new_task = {
                "title": title,
                "description": description,
                "assigned_to": assigned_to,
                "due_date": str(due_date),
                "status": status
            }
            tasks.append(new_task)
            project["tasks"] = tasks
            save_memory(database)
            st.success(f"Added task: {title}")

    # Update task status
    if tasks:
        st.subheader("Update Task Status")
        task_titles = [t["title"] for t in tasks]
        selected_task = st.selectbox("Select Task", task_titles)
        new_status = st.selectbox("New Status", ["Not Started", "In Progress", "Completed"])
        if st.button("Update Status"):
            for t in tasks:
                if t["title"] == selected_task:
                    t["status"] = new_status
                    save_memory(database)
                    st.success(f"Updated {selected_task} to {new_status}")