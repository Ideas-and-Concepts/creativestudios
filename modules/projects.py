"""Creative Studios - Projects Module."""
from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st

from modules.database import save_memory

PROJECT_STATUSES = ["Planning", "Active", "On Hold", "Completed", "Cancelled"]


def _text(value: Any, default: str = "") -> str:
    return default if value is None else str(value).strip()


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return default


def _normalize_projects(database: dict[str, Any]) -> list[dict[str, Any]]:
    value = database.get("projects", [])
    if not isinstance(value, list):
        value = []

    projects: list[dict[str, Any]] = []
    for index, item in enumerate(value, start=1):
        if isinstance(item, dict):
            record = dict(item)
            record.setdefault("id", index)
            name = _text(record.get("name")) or _text(record.get("project_name")) or f"Project {index}"
            client = _text(record.get("client")) or _text(record.get("client_name"))
            record.update(
                {
                    "id": record.get("id") or index,
                    "name": name,
                    "project_name": _text(record.get("project_name")) or name,
                    "client": client,
                    "client_name": _text(record.get("client_name")) or client,
                    "location": _text(record.get("location")),
                    "status": _text(record.get("status")) or "Planning",
                    "budget": _safe_float(record.get("budget", record.get("estimated_budget", 0))),
                    "estimated_budget": _safe_float(record.get("estimated_budget", record.get("budget", 0))),
                    "description": _text(record.get("description")),
                    "created_at": _text(record.get("created_at")),
                }
            )
            projects.append(record)
        elif isinstance(item, str):
            name = item.strip() or f"Project {index}"
            projects.append(
                {
                    "id": index,
                    "name": name,
                    "project_name": name,
                    "client": "",
                    "client_name": "",
                    "location": "",
                    "status": "Planning",
                    "budget": 0.0,
                    "estimated_budget": 0.0,
                    "description": "",
                    "created_at": "",
                }
            )

    database["projects"] = projects
    return projects


def _next_id(records: list[dict[str, Any]]) -> int:
    ids = []
    for record in records:
        try:
            ids.append(int(record.get("id", 0)))
        except (TypeError, ValueError):
            pass
    return max(ids, default=0) + 1


def _save(database: dict[str, Any]) -> None:
    save_memory(database)
    st.session_state.database = database


def _status_index(value: Any) -> int:
    status = _text(value, "Planning")
    return PROJECT_STATUSES.index(status) if status in PROJECT_STATUSES else 0


def render_projects_module(database: dict[str, Any]) -> None:
    """Render the Creative Studios project directory."""
    st.title("Projects")
    st.caption("Create, edit and manage Creative Studios projects.")

    projects = _normalize_projects(database)

    total_budget = sum(_safe_float(p.get("estimated_budget", p.get("budget", 0))) for p in projects)
    active = sum(1 for p in projects if _text(p.get("status")).lower() == "active")
    completed = sum(1 for p in projects if _text(p.get("status")).lower() == "completed")

    cols = st.columns(4)
    cols[0].metric("Projects", len(projects))
    cols[1].metric("Active", active)
    cols[2].metric("Completed", completed)
    cols[3].metric("Estimated Budget", f"{total_budget:,.2f}")
    st.divider()

    tab_directory, tab_create = st.tabs(["Project Directory", "Create Project"])

    with tab_directory:
        if not projects:
            st.info("No projects have been created yet.")
        else:
            search = st.text_input("Search projects", placeholder="Search by name, client or location", key="projects_search")
            term = search.strip().lower()
            filtered = [
                p for p in projects
                if not term or term in " ".join((_text(p.get("name")), _text(p.get("client")), _text(p.get("location")))).lower()
            ]
            if not filtered:
                st.info("No projects match the search.")

            for index, project in enumerate(filtered):
                project_id = project.get("id", index + 1)
                name = _text(project.get("name"), "Unnamed Project") or "Unnamed Project"
                with st.expander(name, expanded=False):
                    st.caption(f"Project ID: {project_id}")
                    with st.form(f"edit_project_{project_id}"):
                        edited_name = st.text_input("Project Name", value=name)
                        edited_client = st.text_input("Client", value=_text(project.get("client")))
                        edited_location = st.text_input("Project Location", value=_text(project.get("location")))
                        edited_status = st.selectbox("Status", PROJECT_STATUSES, index=_status_index(project.get("status")))
                        edited_budget = st.number_input("Estimated Budget", min_value=0.0, value=_safe_float(project.get("estimated_budget", project.get("budget", 0))), step=1000.0)
                        edited_description = st.text_area("Description", value=_text(project.get("description")))
                        submitted = st.form_submit_button("Save Changes", use_container_width=True)

                    if submitted:
                        if not edited_name.strip():
                            st.error("Project name is required.")
                        else:
                            project.update(
                                name=edited_name.strip(), project_name=edited_name.strip(),
                                client=edited_client.strip(), client_name=edited_client.strip(),
                                location=edited_location.strip(), status=edited_status,
                                budget=edited_budget, estimated_budget=edited_budget,
                                description=edited_description.strip(),
                            )
                            _save(database)
                            st.success("Project updated successfully.")
                            st.rerun()

                    if st.button("Delete Project", key=f"delete_project_{project_id}", use_container_width=True):
                        projects[:] = [item for item in projects if item is not project]
                        _save(database)
                        st.success("Project deleted successfully.")
                        st.rerun()

    with tab_create:
        with st.form("create_project_form", clear_on_submit=True):
            name = st.text_input("Project Name")
            client = st.text_input("Client")
            location = st.text_input("Project Location")
            status = st.selectbox("Status", PROJECT_STATUSES)
            budget = st.number_input("Estimated Budget", min_value=0.0, step=1000.0)
            description = st.text_area("Description")
            submitted = st.form_submit_button("Create Project", use_container_width=True)

        if submitted:
            if not name.strip():
                st.error("Project name is required.")
            else:
                projects.append(
                    {
                        "id": _next_id(projects), "name": name.strip(), "project_name": name.strip(),
                        "client": client.strip(), "client_name": client.strip(), "location": location.strip(),
                        "status": status, "budget": budget, "estimated_budget": budget,
                        "description": description.strip(), "created_at": datetime.now().isoformat(timespec="seconds"),
                    }
                )
                _save(database)
                st.success("Project created successfully.")
                st.rerun()