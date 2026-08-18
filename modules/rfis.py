"""
Creative Studios
Requests for Information Module
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


RFI_STATUSES = [
    "Open",
    "Under Review",
    "Answered",
    "Closed",
]


def _text(value: Any) -> str:
    return str(value or "").strip()


def render_rfis_module(
    database: dict[str, Any],
) -> None:

    render_module_header(
        "RFIs",
        "Track requests for information across active projects.",
    )

    rfis = database.get(
        "rfis",
        [],
    )

    if not isinstance(
        rfis,
        list,
    ):
        rfis = []

    # ========================================================
    # SEARCH
    # ========================================================

    search = st.text_input(
        "Search RFIs",
        placeholder=(
            "Search RFI number, subject, project "
            "or requester..."
        ),
        key="rfis_search",
    )

    # ========================================================
    # NEW RFI
    # ========================================================

    if st.button(
        "New RFI",
        key="new_rfi",
    ):

        st.session_state[
            "show_rfi_form"
        ] = True

    # ========================================================
    # CREATE RFI
    # ========================================================

    if st.session_state.get(
        "show_rfi_form",
        False,
    ):

        with st.form(
            "rfi_form",
            clear_on_submit=True,
        ):

            subject = st.text_input(
                "Subject"
            )

            project = st.text_input(
                "Project"
            )

            requester = st.text_input(
                "Requested By"
            )

            question = st.text_area(
                "Question"
            )

            status = st.selectbox(
                "Status",
                RFI_STATUSES,
            )

            submitted = st.form_submit_button(
                "Create RFI",
                use_container_width=True,
            )

            if submitted:

                if not subject.strip():

                    st.error(
                        "RFI subject is required."
                    )

                else:

                    rfi = {
                        "id": next_id(
                            rfis
                        ),
                        "subject": subject.strip(),
                        "project": project.strip(),
                        "requester": requester.strip(),
                        "question": question.strip(),
                        "status": status,
                        "response": "",
                    }

                    add_record(
                        database,
                        "rfis",
                        rfi,
                    )

                    st.session_state[
                        "show_rfi_form"
                    ] = False

                    st.success(
                        "RFI created."
                    )

                    st.rerun()

    # ========================================================
    # FILTER
    # ========================================================

    search_value = search.lower().strip()

    filtered = []

    for rfi in rfis:

        if not isinstance(
            rfi,
            dict,
        ):
            continue

        searchable = " ".join(
            [
                _text(rfi.get("subject")),
                _text(rfi.get("project")),
                _text(rfi.get("requester")),
                _text(rfi.get("status")),
                _text(rfi.get("question")),
            ]
        ).lower()

        if (
            not search_value
            or search_value in searchable
        ):

            filtered.append(rfi)

    # ========================================================
    # SUMMARY
    # ========================================================

    cols = st.columns(4)

    metrics = [
        (
            "Total",
            len(rfis),
        ),
        (
            "Open",
            sum(
                1
                for rfi in rfis
                if _text(
                    rfi.get("status")
                ).lower()
                == "open"
            ),
        ),
        (
            "Under Review",
            sum(
                1
                for rfi in rfis
                if _text(
                    rfi.get("status")
                ).lower()
                == "under review"
            ),
        ),
        (
            "Closed",
            sum(
                1
                for rfi in rfis
                if _text(
                    rfi.get("status")
                ).lower()
                == "closed"
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
    # RFI LIST
    # ========================================================

    if not filtered:

        st.info(
            "No RFIs found."
        )

        return

    for rfi in filtered:

        rfi_id = rfi.get(
            "id"
        )

        subject = html.escape(
            _text(
                rfi.get(
                    "subject",
                    "Untitled RFI",
                )
            )
        )

        project = html.escape(
            _text(
                rfi.get("project")
            )
        )

        requester = html.escape(
            _text(
                rfi.get("requester")
            )
        )

        status = html.escape(
            _text(
                rfi.get(
                    "status",
                    "Open",
                )
            )
        )

        # ====================================================
        # RFI CARD
        # ====================================================

        st.markdown(
            f"""
            <div class="cs-card">

                <div class="cs-card-title">
                    RFI #{rfi_id} · {subject}
                </div>

                <div class="cs-card-subtitle">
                    Project: {project}
                    &nbsp; • &nbsp;
                    Requested by: {requester}
                    &nbsp; • &nbsp;
                    Status: {status}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        # ====================================================
        # EDIT / DELETE
        # ====================================================

        with st.expander(
            f"Manage RFI #{rfi_id}"
        ):

            with st.form(
                f"edit_rfi_{rfi_id}"
            ):

                edit_subject = st.text_input(
                    "Subject",
                    value=_text(
                        rfi.get("subject")
                    ),
                )

                edit_project = st.text_input(
                    "Project",
                    value=_text(
                        rfi.get("project")
                    ),
                )

                edit_requester = st.text_input(
                    "Requested By",
                    value=_text(
                        rfi.get("requester")
                    ),
                )

                edit_question = st.text_area(
                    "Question",
                    value=_text(
                        rfi.get("question")
                    ),
                )

                current_status = _text(
                    rfi.get(
                        "status",
                        "Open",
                    )
                )

                edit_status = st.selectbox(
                    "Status",
                    RFI_STATUSES,
                    index=(
                        RFI_STATUSES.index(
                            current_status
                        )
                        if current_status
                        in RFI_STATUSES
                        else 0
                    ),
                )

                response = st.text_area(
                    "Response",
                    value=_text(
                        rfi.get("response")
                    ),
                )

                save = st.form_submit_button(
                    "Save Changes",
                    use_container_width=True,
                )

                if save:

                    update_record(
                        database,
                        "rfis",
                        rfi_id,
                        {
                            "subject": (
                                edit_subject.strip()
                            ),
                            "project": (
                                edit_project.strip()
                            ),
                            "requester": (
                                edit_requester.strip()
                            ),
                            "question": (
                                edit_question.strip()
                            ),
                            "status": edit_status,
                            "response": (
                                response.strip()
                            ),
                        },
                    )

                    st.success(
                        "RFI updated."
                    )

                    st.rerun()

            if st.button(
                "Delete RFI",
                key=f"delete_rfi_{rfi_id}",
            ):

                delete_record(
                    database,
                    "rfis",
                    rfi_id,
                )

                st.success(
                    "RFI deleted."
                )

                st.rerun()