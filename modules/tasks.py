"""
Creative Studios
Tasks Module
"""

from __future__ import annotations

import html
from typing import Any

import streamlit as st

from modules.branding import render_module_header
from modules.database import (
    add_record,
    delete_record,
    next_id,
    update_record,
)


TASK_STATUSES = [
    "Not Started",
    "In Progress",
    "Blocked",
    "Completed",
]


TASK_PRIORITIES = [
    "Low",
    "Medium",
    "High",
    "Critical",
]


def _text(value: Any) -> str:
    return str(value or "").strip()


def render_tasks_module(
    database: dict[str, Any],
) -> None:

    render_module_header(
        "Tasks",
        "Plan, assign and track project tasks and activities.",
    )

    tasks = database.get(
        "tasks",
        [],
    )

    if not isinstance(
        tasks,
        list,
    ):
        tasks = []

    search = st.text_input(
        "Search tasks",
        placeholder=(
            "Search task, project, assignee "
            "or priority..."
        ),
        key="tasks_search",
    )

    if st.button(
        "New Task",
        key="new_task",
    ):

        st.session_state[
            "show_task_form"
        ] = True

    # ========================================================
    # CREATE TASK
    # ========================================================

    if st.session_state.get(
        "show_task_form",
        False,
    ):

        with st.form(
            "task_form",
            clear_on_submit=True,
        ):

            title = st.text_input(
                "Task"
            )

            project = st.text_input(
                "Project"
            )

            assignee = st.text_input(
                "Assigned To"
            )

            priority = st.selectbox(
                "Priority",
                TASK_PRIORITIES,
            )

            status = st.selectbox(
                "Status",
                TASK_STATUSES,
            )

            description = st.text_area(
                "Description"
            )

            submitted = st.form_submit_button(
                "Create Task",
                use_container_width=True,
            )

            if submitted:

                if not title.strip():

                    st.error(
                        "Task title is required."
                    )

                else:

                    task = {
                        "id": next_id(
                            tasks
                        ),
                        "title": title.strip(),
                        "project": project.strip(),
                        "assignee": assignee.strip(),
                        "priority": priority,
                        "status": status,
                        "description": description.strip(),
                    }

                    add_record(
                        database,
                        "tasks",
                        task,
                    )

                    st.session_state[
                        "show_task_form"
                    ] = False

                    st.success(
                        "Task created."
                    )

                    st.rerun()

    # ========================================================
    # FILTER
    # ========================================================

    search_value = search.lower().strip()

    filtered = []

    for task in tasks:

        if not isinstance(
            task,
            dict,
        ):
            continue

        searchable = " ".join(
            [
                _text(task.get("title")),
                _text(task.get("project")),
                _text(task.get("assignee")),
                _text(task.get("priority")),
                _text(task.get("status")),
            ]
        ).lower()

        if (
            not search_value
            or search_value in searchable
        ):

            filtered.append(task)

    # ========================================================
    # SUMMARY
    # ========================================================

    cols = st.columns(4)

    metrics = [
        (
            "Total",
            len(tasks),
        ),
        (
            "Not Started",
            sum(
                1
                for task in tasks
                if _text(
                    task.get("status")
                ).lower()
                == "not started"
            ),
        ),
        (
            "In Progress",
            sum(
                1
                for task in tasks
                if _text(
                    task.get("status")
                ).lower()
                == "in progress"
            ),
        ),
        (
            "Completed",
            sum(
                1
                for task in tasks
                if _text(
                    task.get("status")
                ).lower()
                == "completed"
            ),
        ),
    ]

    for col, (label, value) in zip(
        cols,
        metrics,
    ):

        with col:

            st.metric(
                label,
                value,
            )

    st.write("")

    # ========================================================
    # TASK LIST
    # ========================================================

    if not filtered:

        st.info(
            "No tasks found."
        )

        return

    for task in filtered:

        task_id = task.get(
            "id"
        )

        title = html.escape(
            _text(
                task.get(
                    "title",
                    "Untitled Task",
                )
            )
        )

        project = html.escape(
            _text(
                task.get("project")
            )
        )

        assignee = html.escape(
            _text(
                task.get("assignee")
            )
        )

        priority = html.escape(
            _text(
                task.get(
                    "priority",
                    "Medium",
                )
            )
        )

        status = html.escape(
            _text(
                task.get(
                    "status",
                    "Not Started",
                )
            )
        )

        # ====================================================
        # TASK CARD
        # ====================================================

        st.markdown(
            f"""
            <div class="cs-card">

                <div class="cs-card-title">
                    {title}
                </div>

                <div class="cs-card-subtitle">
                    {project}
                    &nbsp; • &nbsp;
                    {assignee}
                    &nbsp; • &nbsp;
                    {priority}
                    &nbsp; • &nbsp;
                    {status}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        # ====================================================
        # EDIT / DELETE
        # ====================================================

        with st.expander(
            f"Manage Task #{task_id}"
        ):

            with st.form(
                f"edit_task_{task_id}"
            ):

                edit_title = st.text_input(
                    "Task",
                    value=_text(
                        task.get("title")
                    ),
                )

                edit_project = st.text_input(
                    "Project",
                    value=_text(
                        task.get("project")
                    ),
                )

                edit_assignee = st.text_input(
                    "Assigned To",
                    value=_text(
                        task.get("assignee")
                    ),
                )

                current_priority = _text(
                    task.get(
                        "priority",
                        "Medium",
                    )
                )

                edit_priority = st.selectbox(
                    "Priority",
                    TASK_PRIORITIES,
                    index=(
                        TASK_PRIORITIES.index(
                            current_priority
                        )
                        if current_priority
                        in TASK_PRIORITIES
                        else 1
                    ),
                )

                current_status = _text(
                    task.get(
                        "status",
                        "Not Started",
                    )
                )

                edit_status = st.selectbox(
                    "Status",
                    TASK_STATUSES,
                    index=(
                        TASK_STATUSES.index(
                            current_status
                        )
                        if current_status
                        in TASK_STATUSES
                        else 0
                    ),
                )

                edit_description = st.text_area(
                    "Description",
                    value=_text(
                        task.get("description")
                    ),
                )

                save = st.form_submit_button(
                    "Save Changes",
                    use_container_width=True,
                )

                if save:

                    update_record(
                        database,
                        "tasks",
                        task_id,
                        {
                            "title": edit_title.strip(),
                            "project": edit_project.strip(),
                            "assignee": edit_assignee.strip(),
                            "priority": edit_priority,
                            "status": edit_status,
                            "description": (
                                edit_description.strip()
                            ),
                        },
                    )

                    st.success(
                        "Task updated."
                    )

                    st.rerun()

            if st.button(
                "Delete Task",
                key=f"delete_task_{task_id}",
            ):

                delete_record(
                    database,
                    "tasks",
                    task_id,
                )

                st.success(
                    "Task deleted."
                )

                st.rerun()