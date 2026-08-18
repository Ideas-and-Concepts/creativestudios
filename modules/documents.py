"""
Creative Studios
Documents Module
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


DOCUMENT_STATUSES = [
    "Draft",
    "Under Review",
    "Approved",
    "Superseded",
    "Archived",
]


def _text(value: Any) -> str:
    return str(value or "").strip()


def render_documents_module(
    database: dict[str, Any],
) -> None:

    render_module_header(
        "Documents",
        "Manage project documents, files and document records.",
    )

    documents = database.get(
        "documents",
        [],
    )

    if not isinstance(
        documents,
        list,
    ):
        documents = []

    search = st.text_input(
        "Search documents",
        placeholder="Search title, project, discipline or document number...",
        key="documents_search",
    )

    if st.button(
        "New Document",
        key="new_document",
        use_container_width=False,
    ):

        st.session_state[
            "show_document_form"
        ] = True

    if st.session_state.get(
        "show_document_form",
        False,
    ):

        with st.form(
            "document_form",
            clear_on_submit=True,
        ):

            title = st.text_input(
                "Document Title"
            )

            document_number = st.text_input(
                "Document Number"
            )

            project = st.text_input(
                "Project"
            )

            discipline = st.text_input(
                "Discipline"
            )

            status = st.selectbox(
                "Status",
                DOCUMENT_STATUSES,
            )

            description = st.text_area(
                "Description"
            )

            submitted = st.form_submit_button(
                "Create Document",
                use_container_width=True,
            )

            if submitted:

                if not title.strip():

                    st.error(
                        "Document title is required."
                    )

                else:

                    record = {
                        "id": next_id(
                            documents
                        ),
                        "title": title.strip(),
                        "document_number": document_number.strip(),
                        "project": project.strip(),
                        "discipline": discipline.strip(),
                        "status": status,
                        "description": description.strip(),
                    }

                    add_record(
                        database,
                        "documents",
                        record,
                    )

                    st.session_state[
                        "show_document_form"
                    ] = False

                    st.success(
                        "Document created."
                    )

                    st.rerun()

    search_value = search.lower().strip()

    filtered = []

    for document in documents:

        if not isinstance(
            document,
            dict,
        ):
            continue

        searchable = " ".join(
            [
                _text(document.get("title")),
                _text(document.get("document_number")),
                _text(document.get("project")),
                _text(document.get("discipline")),
                _text(document.get("status")),
            ]
        ).lower()

        if (
            not search_value
            or search_value in searchable
        ):

            filtered.append(document)

    st.metric(
        "Documents",
        len(documents),
    )

    st.write("")

    if not filtered:

        st.info(
            "No documents found."
        )

        return

    for document in filtered:

        document_id = document.get(
            "id"
        )

        title = html.escape(
            _text(
                document.get(
                    "title",
                    "Untitled Document",
                )
            )
        )

        number = html.escape(
            _text(
                document.get(
                    "document_number",
                    "",
                )
            )
        )

        project = html.escape(
            _text(
                document.get(
                    "project",
                    "",
                )
            )
        )

        status = html.escape(
            _text(
                document.get(
                    "status",
                    "Draft",
                )
            )
        )

        st.markdown(
            f"""
            <div class="cs-card">

                <div style="
                    color:#FFFFFF;
                    font-size:16px;
                    font-weight:850;
                ">
                    {title}
                </div>

                <div style="
                    color:#64748B;
                    font-size:12px;
                    margin-top:6px;
                ">
                    {number}
                    &nbsp; • &nbsp;
                    {project}
                    &nbsp; • &nbsp;
                    {status}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander(
            f"Edit Document #{document_id}"
        ):

            with st.form(
                f"edit_document_{document_id}"
            ):

                edit_title = st.text_input(
                    "Document Title",
                    value=_text(
                        document.get("title")
                    ),
                )

                edit_number = st.text_input(
                    "Document Number",
                    value=_text(
                        document.get(
                            "document_number"
                        )
                    ),
                )

                edit_project = st.text_input(
                    "Project",
                    value=_text(
                        document.get("project")
                    ),
                )

                edit_discipline = st.text_input(
                    "Discipline",
                    value=_text(
                        document.get("discipline")
                    ),
                )

                current_status = _text(
                    document.get(
                        "status",
                        "Draft",
                    )
                )

                edit_status = st.selectbox(
                    "Status",
                    DOCUMENT_STATUSES,
                    index=(
                        DOCUMENT_STATUSES.index(
                            current_status
                        )
                        if current_status
                        in DOCUMENT_STATUSES
                        else 0
                    ),
                )

                edit_description = st.text_area(
                    "Description",
                    value=_text(
                        document.get(
                            "description"
                        )
                    ),
                )

                save = st.form_submit_button(
                    "Save Changes",
                    use_container_width=True,
                )

                if save:

                    update_record(
                        database,
                        "documents",
                        document_id,
                        {
                            "title": edit_title.strip(),
                            "document_number": edit_number.strip(),
                            "project": edit_project.strip(),
                            "discipline": edit_discipline.strip(),
                            "status": edit_status,
                            "description": edit_description.strip(),
                        },
                    )

                    st.success(
                        "Document updated."
                    )

                    st.rerun()

            if st.button(
                "Delete Document",
                key=f"delete_document_{document_id}",
            ):

                delete_record(
                    database,
                    "documents",
                    document_id,
                )

                st.success(
                    "Document deleted."
                )

                st.rerun()