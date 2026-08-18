"""
Creative Studios
AEC Collaboration Platform

RFIs Module
-----------
Request for Information management with:

- RFI creation
- RFI search/filter
- RFI viewing
- RFI editing
- RFI deletion
- Project linking
- Task linking
- Missing Task-assignee detection
- Task-assignee repair
- Assignment repair audit logging

Database contract:
    modules.database.py
"""

from modules.branding import render_module_header

from __future__ import annotations

from datetime import datetime

import streamlit as st

from modules.database import (
    add_record,
    delete_record,
    get_record,
    get_records,
    next_id,
    update_record,
)


# ============================================================
# USER HELPERS
# ============================================================

def _get_users(db):
    """Return valid users."""

    return [
        user
        for user in get_records(
            "users",
            db,
        )
        if isinstance(
            user,
            dict,
        )
    ]


def _get_user_by_id(
    db,
    user_id,
):
    """
    Find a user by ID.

    assigned_to remains authoritative for Tasks.
    """

    if user_id is None:
        return None

    for user in _get_users(db):

        if str(
            user.get("id")
        ) == str(user_id):

            return user

    return None


def _user_display_name(user):
    """Return a safe display name."""

    if not user:
        return "Unassigned"

    full_name = str(
        user.get(
            "full_name",
            "",
        )
    ).strip()

    username = str(
        user.get(
            "username",
            "",
        )
    ).strip()

    if full_name and username:

        return (
            f"{full_name} "
            f"(@{username})"
        )

    if full_name:
        return full_name

    if username:
        return f"@{username}"

    return (
        f"User #{user.get('id', '')}"
    )


def _get_current_user(db):
    """
    Get the currently authenticated user.

    The Streamlit session remains authoritative for the
    current login, while the users collection is used to
    resolve the latest user information.
    """

    session_user = (
        st.session_state.get(
            "user"
        )
    )

    if not isinstance(
        session_user,
        dict,
    ):
        return None

    user_id = session_user.get(
        "id"
    )

    if user_id is None:

        return session_user

    current_user = _get_user_by_id(
        db,
        user_id,
    )

    return (
        current_user
        or session_user
    )


# ============================================================
# TASK HELPERS
# ============================================================

def _get_linked_tasks(
    db,
    rfi_id,
):
    """Return Tasks linked to an RFI."""

    tasks = get_records(
        "tasks",
        db,
    )

    return [
        task
        for task in tasks
        if str(
            task.get(
                "rfi_id",
                "",
            )
        ) == str(rfi_id)
    ]


def _get_task_assignee_display(
    db,
    assigned_to,
):
    """
    Determine the current Task assignment state.

    States:

        assigned
        unassigned
        missing
    """

    if assigned_to in (
        None,
        "",
    ):

        return {
            "name": "Unassigned",
            "state": "unassigned",
        }

    user = _get_user_by_id(
        db,
        assigned_to,
    )

    if user is None:

        return {
            "name": (
                f"User #{assigned_to} "
                "no longer exists"
            ),
            "state": "missing",
        }

    return {
        "name": _user_display_name(
            user
        ),
        "state": "assigned",
    }


# ============================================================
# AUDIT LOG
# ============================================================

def _record_assignee_repair(
    db,
    task,
    old_assigned_to,
    new_assigned_to,
):
    """
    Record a Task-assignee repair.

    Uses the existing generic JSON database contract.
    """

    current_user = _get_current_user(
        db
    )

    repaired_by_id = (
        current_user.get("id")
        if current_user
        else None
    )

    repaired_by_name = (
        _user_display_name(
            current_user
        )
        if current_user
        else "Unknown user"
    )

    timestamp = (
        datetime.now().isoformat()
    )

    activity = {
        "id": next_id(
            "activity_log",
            db,
        ),

        "action": (
            "task_assignee_repaired"
        ),

        "entity_type": "task",

        "entity_id": task.get(
            "id"
        ),

        "task_id": task.get(
            "id"
        ),

        "project_id": task.get(
            "project_id"
        ),

        "rfi_id": task.get(
            "rfi_id"
        ),

        "old_assigned_to": (
            old_assigned_to
        ),

        "new_assigned_to": (
            new_assigned_to
        ),

        "repaired_by": (
            repaired_by_id
        ),

        "repaired_by_name": (
            repaired_by_name
        ),

        "timestamp": timestamp,
    }

    return add_record(
        "activity_log",
        activity,
        db,
    )


# ============================================================
# REPAIR UI
# ============================================================

def _render_missing_assignee_repair(
    db,
    task,
):
    """
    Render the repair control for a Task whose assigned_to
    value no longer exists in users.
    """

    task_id = task.get(
        "id"
    )

    old_assigned_to = task.get(
        "assigned_to"
    )

    st.markdown(
        f"""
        <div style="
            color:#F59E0B;
            font-size:11px;
            margin-top:7px;
            font-weight:700;
        ">
            ⚠ Assigned user:
            User #{old_assigned_to}
            no longer exists
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.warning(
        f"Task #{task_id} references "
        f"user #{old_assigned_to}, but that "
        "user no longer exists."
    )

    st.markdown(
        """
        <div style="
            color:#F59E0B;
            font-size:12px;
            font-weight:700;
            margin-bottom:8px;
        ">
            Repair the assignment by selecting
            a valid Creative Studios user.
        </div>
        """,
        unsafe_allow_html=True,
    )

    valid_users = _get_users(
        db
    )

    if not valid_users:

        st.error(
            "No valid users are available "
            "for reassignment."
        )

        return

    selected_user = st.selectbox(
        "Reassign Task to",
        [None] + valid_users,
        format_func=lambda user: (
            "Select a user..."
            if user is None
            else _user_display_name(
                user
            )
        ),
        key=(
            f"repair_assignee_"
            f"{task_id}"
        ),
    )

    if st.button(
        "Repair Assignment",
        key=(
            f"repair_task_"
            f"{task_id}"
        ),
        use_container_width=True,
    ):

        if selected_user is None:

            st.error(
                "Please select a valid user."
            )

            return

        new_assigned_to = (
            selected_user.get("id")
        )

        if new_assigned_to is None:

            st.error(
                "Selected user has no valid ID."
            )

            return

        # ----------------------------------------------------
        # UPDATE TASK
        # ----------------------------------------------------

        try:

            updated_task = update_record(
                "tasks",
                task_id,
                {
                    "assigned_to": (
                        new_assigned_to
                    ),
                    "updated_at": (
                        datetime.now().isoformat()
                    ),
                },
                db,
            )

            if updated_task is None:

                st.error(
                    "Task could not be found."
                )

                return

        except Exception as exc:

            st.error(
                "Unable to repair Task assignment."
            )

            st.code(
                f"{type(exc).__name__}: "
                f"{exc}"
            )

            return

        # ----------------------------------------------------
        # AUDIT RECORD
        # ----------------------------------------------------

        try:

            _record_assignee_repair(
                db=db,
                task=updated_task,
                old_assigned_to=old_assigned_to,
                new_assigned_to=new_assigned_to,
            )

        except Exception as audit_exc:

            # The Task has already been successfully repaired.
            # Do not claim that the repair failed.
            st.warning(
                "The Task was reassigned successfully, "
                "but the repair audit could not be saved."
            )

            st.code(
                f"{type(audit_exc).__name__}: "
                f"{audit_exc}"
            )

            return

        st.success(
            "Task assignment repaired successfully."
        )

        st.rerun()


# ============================================================
# LINKED TASK VIEW
# ============================================================

def _render_linked_task(
    db,
    task,
):
    """Render one Task linked to an RFI."""

    task_id = task.get(
        "id"
    )

    assigned_to = task.get(
        "assigned_to"
    )

    assignee = (
        _get_task_assignee_display(
            db,
            assigned_to,
        )
    )

    assigned_name = assignee[
        "name"
    ]

    assigned_state = assignee[
        "state"
    ]

    st.markdown(
        f"""
        <div class="cs-card"
             style="margin-bottom:10px;">

            <div style="
                color:#FFFFFF;
                font-size:15px;
                font-weight:800;
            ">
                {task.get(
                    "title",
                    "Untitled Task"
                )}
            </div>

            <div style="
                color:#64748B;
                font-size:11px;
                margin-top:6px;
            ">
                Task #{task_id}
                &nbsp; • &nbsp;
                Status:
                {task.get(
                    "status",
                    "Open"
                )}
                &nbsp; • &nbsp;
                Priority:
                {task.get(
                    "priority",
                    "Normal"
                )}
            </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # ASSIGNEE
    # --------------------------------------------------------

    if assigned_state == "assigned":

        st.markdown(
            f"""
            <div style="
                color:#60A5FA;
                font-size:11px;
                margin-top:7px;
            ">
                Assigned to:
                {assigned_name}
            </div>
            """,
            unsafe_allow_html=True,
        )

    elif assigned_state == "unassigned":

        st.markdown(
            """
            <div style="
                color:#94A3B8;
                font-size:11px;
                margin-top:7px;
            ">
                Assigned to:
                Unassigned
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        _render_missing_assignee_repair(
            db,
            task,
        )

    # --------------------------------------------------------
    # DESCRIPTION
    # --------------------------------------------------------

    description = str(
        task.get(
            "description",
            "",
        )
    ).strip()

    if description:

        st.markdown(
            f"""
            <div style="
                color:#94A3B8;
                font-size:12px;
                margin-top:8px;
            ">
                {description}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


# ============================================================
# RFI VIEW
# ============================================================

def render_rfi_tasks(
    db,
    rfi,
):
    """
    Render Tasks linked to the supplied RFI.
    """

    rfi_id = rfi.get(
        "id"
    )

    st.markdown(
        """
        <div class="cs-card">
            <div style="
                color:#FFFFFF;
                font-size:18px;
                font-weight:850;
            ">
                Linked Tasks
            </div>

            <div style="
                color:#64748B;
                font-size:12px;
                margin-top:6px;
                margin-bottom:14px;
            ">
                Tasks connected to this Request
                for Information.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    linked_tasks = _get_linked_tasks(
        db,
        rfi_id,
    )

    if not linked_tasks:

        st.info(
            "No Tasks are currently linked to this RFI."
        )

        return

    for task in linked_tasks:

        _render_linked_task(
            db,
            task,
        )


# ============================================================
# SIMPLE RFI VIEW
# ============================================================

def render_rfi_detail(
    db,
    rfi_id,
):
    """Display a single RFI."""

    rfi = get_record(
        "rfis",
        rfi_id,
        db,
    )

    if rfi is None:

        st.error(
            "RFI could not be found."
        )

        return

    st.markdown(
        f"""
        <div class="cs-page-title">
            {rfi.get(
                "title",
                "Request for Information"
            )}
        </div>

        <div class="cs-page-subtitle">
            RFI #{rfi.get("id")}
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_rfi_tasks(
        db,
        rfi,
    )


# ============================================================
# MAIN MODULE
# ============================================================

def render_rfis_module(
    db,
):
    """
    Main RFIs module entry point.

    Existing RFI CRUD can remain around this workflow.
    """

    st.markdown(
        '<div class="cs-page-title">RFIs</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="cs-page-subtitle">'
        "Manage Requests for Information and "
        "linked project Tasks."
        "</div>",
        unsafe_allow_html=True,
    )

    rfis = get_records(
        "rfis",
        db,
    )

    if not rfis:

        st.info(
            "No RFIs have been created yet."
        )

        return

    options = {
        (
            f"RFI #{rfi.get('id')} - "
            f"{rfi.get('title', 'Untitled')}"
        ): rfi.get("id")
        for rfi in rfis
    }

    selected_label = st.selectbox(
        "Select RFI",
        list(options.keys()),
    )

    selected_rfi_id = options[
        selected_label
    ]

    render_rfi_detail(
        db,
        selected_rfi_id,
    )