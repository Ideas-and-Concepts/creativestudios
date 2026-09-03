"""Creative Studios Projects module.

Projects are the shared master records for the AEC workflow. When Neon is
configured, this module reads and writes the same relational ``projects``
table used by the Next.js application. Local development without Neon keeps
the JSON workspace fallback.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any

import streamlit as st

from modules.database import (
    add_record,
    database_backend,
    delete_record,
    delete_relational_project,
    get_records,
    get_relational_projects,
    update_record,
    update_relational_project,
    create_relational_project,
)

PROJECT_STATUSES = ["planning", "active", "on_hold", "completed", "cancelled"]
STATUS_LABELS = {
    "planning": "Planning",
    "active": "Active",
    "on_hold": "On hold",
    "completed": "Completed",
    "cancelled": "Cancelled",
}


def _date_value(value: Any) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if value:
        try:
            return datetime.fromisoformat(str(value).replace("Z", "+00:00")).date()
        except ValueError:
            return None
    return None


def _iso_date(value: date | None) -> str | None:
    return value.isoformat() if value else None


def _load_projects(database: dict[str, Any]) -> list[dict[str, Any]]:
    if database_backend() == "neon":
        return get_relational_projects()
    return get_records("projects", database)


def _status_label(status: Any) -> str:
    value = str(status or "planning")
    return STATUS_LABELS.get(value, value.replace("_", " ").title())


def render_projects_module(database: dict[str, Any]) -> None:
    st.title("Projects")
    st.caption("Master project register shared by the Creative Studios AEC workflow.")

    if database_backend() == "neon":
        st.info("Connected to the shared Neon projects table used by the Vercel application.")

    with st.form("add_project_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            code = st.text_input("Project Code", placeholder="PRJ-001")
            name = st.text_input("Project Name")
            client = st.text_input("Client")
            location = st.text_input("Location")
        with c2:
            status = st.selectbox(
                "Status",
                PROJECT_STATUSES,
                format_func=_status_label,
            )
            start_date = st.date_input("Start Date", value=None)
            target_end_date = st.date_input("Target End Date", value=None)
            description = st.text_area("Project Description", height=120)
        submitted = st.form_submit_button("Create Project", use_container_width=True)

    if submitted:
        clean_code = code.strip()
        clean_name = name.strip()
        clean_client = client.strip() or None
        clean_location = location.strip() or None
        clean_description = description.strip() or None

        if not clean_code:
            st.error("Project code is required.")
        elif not clean_name:
            st.error("Project name is required.")
        elif target_end_date and start_date and target_end_date < start_date:
            st.error("Target end date cannot be earlier than the start date.")
        else:
            try:
                if database_backend() == "neon":
                    project = create_relational_project(
                        {
                            "code": clean_code,
                            "name": clean_name,
                            "client_name": clean_client,
                            "location": clean_location,
                            "description": clean_description,
                            "status": status,
                            "start_date": _iso_date(start_date),
                            "target_end_date": _iso_date(target_end_date),
                        }
                    )
                else:
                    project = add_record(
                        "projects",
                        {
                            "code": clean_code,
                            "name": clean_name,
                            "client": clean_client or "",
                            "location": clean_location or "",
                            "status": status,
                            "description": clean_description or "",
                            "start_date": _iso_date(start_date),
                            "target_end_date": _iso_date(target_end_date),
                            "created_at": datetime.now().isoformat(timespec="seconds"),
                        },
                        database,
                    )
                st.success(f"Project {project.get('code', clean_code)} created successfully.")
                st.rerun()
            except Exception as exc:
                message = "Project code already exists." if "unique" in str(exc).lower() else "Unable to create the project."
                st.error(message)
                with st.expander("Technical details"):
                    st.exception(exc)

    st.divider()
    try:
        projects = _load_projects(database)
    except Exception as exc:
        st.error("Unable to load the project register from the database.")
        with st.expander("Technical details"):
            st.exception(exc)
        return

    if not projects:
        st.info("No projects yet. Create the first project above.")
        return

    st.subheader("Project Register")
    st.caption(f"{len(projects)} project{'s' if len(projects) != 1 else ''} available to downstream AEC modules.")

    for project in projects:
        project_id = project.get("id")
        project_code = str(project.get("code") or project_id or "Project")
        project_name = str(project.get("name") or "Unnamed Project")
        with st.expander(f"{project_code} | {project_name}"):
            with st.form(f"edit_project_{project_id}"):
                c1, c2 = st.columns(2)
                with c1:
                    edited_code = st.text_input("Project Code", value=project_code)
                    edited_name = st.text_input("Project Name", value=project_name)
                    edited_client = st.text_input(
                        "Client",
                        value=str(project.get("client_name") if database_backend() == "neon" else project.get("client") or ""),
                    )
                    edited_location = st.text_input("Location", value=str(project.get("location") or ""))
                with c2:
                    current_status = str(project.get("status") or "planning")
                    status_index = PROJECT_STATUSES.index(current_status) if current_status in PROJECT_STATUSES else 0
                    edited_status = st.selectbox(
                        "Status",
                        PROJECT_STATUSES,
                        index=status_index,
                        format_func=_status_label,
                    )
                    edited_start = st.date_input(
                        "Start Date",
                        value=_date_value(project.get("start_date")),
                        key=f"start_{project_id}",
                    )
                    edited_end = st.date_input(
                        "Target End Date",
                        value=_date_value(project.get("target_end_date")),
                        key=f"end_{project_id}",
                    )
                    edited_description = st.text_area(
                        "Project Description",
                        value=str(project.get("description") or ""),
                        height=120,
                    )
                save = st.form_submit_button("Save Changes", use_container_width=True)

            if save:
                if not edited_code.strip():
                    st.error("Project code is required.")
                elif not edited_name.strip():
                    st.error("Project name is required.")
                elif edited_end and edited_start and edited_end < edited_start:
                    st.error("Target end date cannot be earlier than the start date.")
                else:
                    updates = {
                        "code": edited_code.strip(),
                        "name": edited_name.strip(),
                        "location": edited_location.strip() or None,
                        "description": edited_description.strip() or None,
                        "status": edited_status,
                        "start_date": _iso_date(edited_start),
                        "target_end_date": _iso_date(edited_end),
                    }
                    try:
                        if database_backend() == "neon":
                            updated = update_relational_project(
                                str(project_id),
                                {
                                    **updates,
                                    "client_name": edited_client.strip() or None,
                                },
                            )
                        else:
                            updated = update_record(
                                "projects",
                                project_id,
                                {
                                    **updates,
                                    "client": edited_client.strip(),
                                    "updated_at": datetime.now().isoformat(timespec="seconds"),
                                },
                                database,
                            )
                        if updated is None:
                            st.error("Project not found. Refresh the register and try again.")
                        else:
                            st.success("Project updated successfully.")
                            st.rerun()
                    except Exception as exc:
                        message = "Project code already exists." if "unique" in str(exc).lower() else "Unable to update the project."
                        st.error(message)
                        with st.expander("Technical details"):
                            st.exception(exc)

            created = project.get("created_at")
            updated = project.get("updated_at")
            st.caption(
                f"Project ID: {project_id} | Status: {_status_label(project.get('status'))} | "
                f"Created: {created or 'Not available'} | Updated: {updated or 'Not available'}"
            )

            if st.button("Delete Project", key=f"delete_project_{project_id}", use_container_width=True):
                try:
                    if database_backend() == "neon":
                        deleted = delete_relational_project(str(project_id))
                    else:
                        deleted = delete_record("projects", project_id, database)
                    if not deleted:
                        st.warning("Project was not found. Refresh the register.")
                    else:
                        st.success("Project deleted successfully.")
                        st.rerun()
                except Exception as exc:
                    st.error("Unable to delete the project.")
                    with st.expander("Technical details"):
                        st.exception(exc)
