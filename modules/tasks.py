"""Creative Studios Tasks module."""
from __future__ import annotations

from typing import Any

import streamlit as st

from modules.module_utils import ensure_collection, now_iso, project_records, project_selector, save_new_record, save_updated_record

STATUSES = ["Not Started", "In Progress", "Blocked", "Completed", "Cancelled"]
PRIORITIES = ["Low", "Medium", "High", "Critical"]


def _progress(record: dict[str, Any]) -> int:
    try:
        return max(0, min(100, int(record.get("progress", 0) or 0)))
    except (TypeError, ValueError):
        return 0


def render_tasks_module(database: dict[str, Any]) -> None:
    st.title("Tasks")
    st.caption("Project actions, responsibilities, priorities and delivery progress.")
    records = ensure_collection(database, "tasks")
    project_id, _ = project_selector(database, "tasks_project")
    if project_id is None:
        return

    items = project_records(records, project_id)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tasks", len(items))
    c2.metric("In Progress", sum(r.get("status") == "In Progress" for r in items))
    c3.metric("Blocked", sum(r.get("status") == "Blocked" for r in items))
    c4.metric("Completed", sum(r.get("status") == "Completed" for r in items))

    for record in list(items):
        rid = record.get("id")
        with st.expander(f"{record.get('title', 'Task')} | {record.get('priority', 'Medium')}"):
            with st.form(f"task_edit_{rid}"):
                title = st.text_input("Task", value=str(record.get("title", "")))
                assignee = st.text_input("Assignee", value=str(record.get("assignee", "")))
                priority = st.selectbox("Priority", PRIORITIES, index=PRIORITIES.index(record.get("priority", "Medium")) if record.get("priority") in PRIORITIES else 1)
                status = st.selectbox("Status", STATUSES, index=STATUSES.index(record.get("status", "Not Started")) if record.get("status") in STATUSES else 0)
                progress = st.slider("Progress", 0, 100, _progress(record))
                due_date = st.text_input("Due Date", value=str(record.get("due_date", "")), placeholder="YYYY-MM-DD")
                notes = st.text_area("Notes", value=str(record.get("notes", "")))
                submitted = st.form_submit_button("Save Changes", use_container_width=True)
            if submitted:
                if not title.strip():
                    st.error("Task title is required.")
                else:
                    save_updated_record(database, "tasks", rid, {"title": title.strip(), "assignee": assignee.strip(), "priority": priority, "status": status, "progress": progress, "due_date": due_date.strip(), "notes": notes.strip(), "updated_at": now_iso()})
                    st.success("Task updated.")
                    st.rerun()
            if st.button("Delete Task", key=f"task_delete_{rid}", use_container_width=True):
                from modules.database import delete_record
                delete_record("tasks", rid, database)
                st.rerun()

    st.divider()
    with st.form("task_add", clear_on_submit=True):
        title = st.text_input("Task")
        assignee = st.text_input("Assignee")
        priority = st.selectbox("Priority", PRIORITIES, index=1)
        status = st.selectbox("Status", STATUSES)
        progress = st.slider("Progress", 0, 100, 0)
        due_date = st.text_input("Due Date", placeholder="YYYY-MM-DD")
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Add Task", use_container_width=True)
    if submitted:
        if not title.strip():
            st.error("Task title is required.")
        else:
            save_new_record(database, "tasks", {"project_id": project_id, "title": title.strip(), "assignee": assignee.strip(), "priority": priority, "status": status, "progress": progress, "due_date": due_date.strip(), "notes": notes.strip(), "created_at": now_iso(), "updated_at": now_iso()})
            st.success("Task added.")
            st.rerun()
