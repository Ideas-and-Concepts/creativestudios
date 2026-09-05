"""Creative Studios Tasks module."""
from __future__ import annotations
from datetime import date
from typing import Any
import streamlit as st
from modules.module_utils import ensure_collection, now_iso, project_records, project_selector, remove_record, save_new_record, save_updated_record

STATUSES = ["Not Started", "In Progress", "Blocked", "Completed", "Cancelled"]
PRIORITIES = ["Low", "Medium", "High", "Critical"]

def _index(options: list[str], value: Any, default: int = 0) -> int:
    return options.index(value) if value in options else default

def _date(value: Any) -> date | None:
    if not value: return None
    try: return date.fromisoformat(str(value)[:10])
    except ValueError: return None

def render_tasks_module(database: dict[str, Any]) -> None:
    st.title("Tasks")
    st.caption("Project actions, responsibilities, priorities and delivery progress.")
    records = ensure_collection(database, "tasks")
    project_id, _ = project_selector(database, "tasks_project")
    if project_id is None: return
    items = project_records(records, project_id)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tasks", len(items)); c2.metric("In Progress", sum(r.get("status") == "In Progress" for r in items)); c3.metric("Blocked", sum(r.get("status") == "Blocked" for r in items)); c4.metric("Completed", sum(r.get("status") == "Completed" for r in items))

    for record in list(items):
        rid = record.get("id")
        with st.expander(f"{record.get('title', 'Task')} | {record.get('priority', 'Medium')}"):
            with st.form(f"task_edit_{rid}"):
                title = st.text_input("Task", value=str(record.get("title", "")))
                description = st.text_area("Description", value=str(record.get("description", "")))
                priority = st.selectbox("Priority", PRIORITIES, index=_index(PRIORITIES, record.get("priority"), 1))
                status = st.selectbox("Status", STATUSES, index=_index(STATUSES, record.get("status")))
                due_date = st.date_input("Due Date", value=_date(record.get("due_date")))
                submitted = st.form_submit_button("Save Changes", use_container_width=True)
            if submitted:
                if not title.strip():
                    st.error("Task title is required.")
                else:
                    try:
                        saved = save_updated_record(database, "tasks", rid, {"project_id": project_id, "title": title.strip(), "description": description.strip(), "priority": priority, "status": status, "due_date": due_date.isoformat() if due_date else None, "updated_at": now_iso()})
                        if not saved: st.error("The task could not be found.")
                        else: st.success("Task updated."); st.rerun()
                    except Exception as exc:
                        st.error("Unable to update the task.")
                        with st.expander("Technical details"): st.exception(exc)
            if st.button("Delete Task", key=f"task_delete_{rid}", use_container_width=True):
                try:
                    if remove_record(database, "tasks", rid): st.success("Task deleted."); st.rerun()
                    else: st.warning("The task was already removed.")
                except Exception as exc:
                    st.error("Unable to delete the task.")
                    with st.expander("Technical details"): st.exception(exc)

    st.divider(); st.subheader("Add Task")
    with st.form("task_add", clear_on_submit=True):
        title = st.text_input("Task")
        description = st.text_area("Description")
        priority = st.selectbox("Priority", PRIORITIES, index=1)
        status = st.selectbox("Status", STATUSES)
        due_date = st.date_input("Due Date", value=date.today())
        submitted = st.form_submit_button("Add Task", use_container_width=True)
    if submitted:
        if not title.strip(): st.error("Task title is required.")
        else:
            try:
                save_new_record(database, "tasks", {"project_id": project_id, "title": title.strip(), "description": description.strip(), "priority": priority, "status": status, "due_date": due_date.isoformat() if due_date else None, "created_at": now_iso(), "updated_at": now_iso()})
                st.success("Task added."); st.rerun()
            except Exception as exc:
                st.error("Unable to add the task.")
                with st.expander("Technical details"): st.exception(exc)
