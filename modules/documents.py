"""
Creative Studios
Documents Module
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st

from modules.database import save_memory


def _normalize_documents(
    database: dict[str, Any],
) -> list[dict[str, Any]]:
    """Normalize legacy and current document records."""

    value = database.get("documents", [])

    if not isinstance(value, list):
        value = []

    normalized = []

    for index, item in enumerate(
        value,
        start=1,
    ):

        if isinstance(item, dict):

            record = dict(item)

            if not record.get("id"):
                record["id"] = index

            normalized.append(record)

        elif isinstance(item, str):

            normalized.append(
                {
                    "id": index,
                    "title": item,
                    "name": item,
                    "document_number": "",
                    "category": "General",
                    "project": "",
                    "status": "Draft",
                    "description": "",
                    "created_at": "",
                }
            )

    database["documents"] = normalized

    return normalized


def _next_id(
    records: list[dict[str, Any]],
) -> int:

    ids = []

    for record in records:
        try:
            ids.append(
                int(record.get("id", 0))
            )
        except (
            TypeError,
            ValueError,
        ):
            continue

    return max(ids, default=0) + 1


def _save(
    database: dict[str, Any],
) -> None:
    save_memory(database)


def render_documents_module(
    database: dict[str, Any],
) -> None:
    """Render editable document management."""

    st.title("Documents")
    st.caption(
        "Create, edit and manage project documentation and records."
    )

    documents = _normalize_documents(
        database
    )

    tab_library, tab_create = st.tabs(
        [
            "Document Library",
            "Add Document",
        ]
    )

    with tab_library:

        if not documents:

            st.info(
                "No documents have been registered yet."
            )

        else:

            search = st.text_input(
                "Search documents",
                key="document_search",
            )

            search_value = (
                search.strip().lower()
            )

            filtered = []

            for document in documents:

                searchable = " ".join(
                    str(
                        document.get(
                            field,
                            "",
                        )
                        or ""
                    )
                    for field in (
                        "name",
                        "title",
                        "document_number",
                        "category",
                        "project",
                        "status",
                        "description",
                    )
                ).lower()

                if (
                    not search_value
                    or search_value
                    in searchable
                ):
                    filtered.append(
                        document
                    )

            if not filtered:

                st.info(
                    "No documents match your search."
                )

            for index, document in enumerate(
                filtered
            ):

                document_id = document.get(
                    "id",
                    index + 1,
                )

                title = document.get(
                    "title",
                    document.get(
                        "name",
                        "Untitled Document",
                    ),
                )

                with st.expander(
                    str(title),
                    expanded=False,
                ):

                    with st.form(
                        f"edit_document_{document_id}"
                    ):

                        edited_title = st.text_input(
                            "Document Title",
                            value=str(
                                title or ""
                            ),
                        )

                        edited_number = st.text_input(
                            "Document Number",
                            value=str(
                                document.get(
                                    "document_number",
                                    "",
                                )
                                or ""
                            ),
                        )

                        categories = [
                            "General",
                            "Contract",
                            "Specification",
                            "Report",
                            "Correspondence",
                            "Technical",
                            "Other",
                        ]

                        current_category = str(
                            document.get(
                                "category",
                                "General",
                            )
                        )

                        category_index = (
                            categories.index(
                                current_category
                            )
                            if current_category
                            in categories
                            else 0
                        )

                        edited_category = st.selectbox(
                            "Category",
                            categories,
                            index=category_index,
                        )

                        edited_project = st.text_input(
                            "Project",
                            value=str(
                                document.get(
                                    "project",
                                    "",
                                )
                                or ""
                            ),
                        )

                        statuses = [
                            "Draft",
                            "Issued",
                            "Approved",
                            "Archived",
                        ]

                        current_status = str(
                            document.get(
                                "status",
                                "Draft",
                            )
                        )

                        status_index = (
                            statuses.index(
                                current_status
                            )
                            if current_status
                            in statuses
                            else 0
                        )

                        edited_status = st.selectbox(
                            "Status",
                            statuses,
                            index=status_index,
                        )

                        edited_description = st.text_area(
                            "Description",
                            value=str(
                                document.get(
                                    "description",
                                    "",
                                )
                                or ""
                            ),
                        )

                        submitted = st.form_submit_button(
                            "Save Changes",
                            use_container_width=True,
                        )

                    if submitted:

                        if not edited_title.strip():
                            st.error(
                                "Document title is required."
                            )
                        else:

                            document["title"] = (
                                edited_title.strip()
                            )

                            document["name"] = (
                                edited_title.strip()
                            )

                            document[
                                "document_number"
                            ] = edited_number.strip()

                            document[
                                "category"
                            ] = edited_category

                            document[
                                "project"
                            ] = edited_project.strip()

                            document[
                                "status"
                            ] = edited_status

                            document[
                                "description"
                            ] = edited_description.strip()

                            _save(database)

                            st.success(
                                "Document updated successfully."
                            )

                            st.rerun()

                    if st.button(
                        "Delete Document",
                        key=f"delete_document_{document_id}",
                        use_container_width=True,
                    ):

                        documents.remove(
                            document
                        )

                        _save(database)

                        st.success(
                            "Document deleted successfully."
                        )

                        st.rerun()

    with tab_create:

        with st.form(
            "create_document_form",
            clear_on_submit=True,
        ):

            title = st.text_input(
                "Document Title"
            )

            document_number = st.text_input(
                "Document Number"
            )

            category = st.selectbox(
                "Category",
                [
                    "General",
                    "Contract",
                    "Specification",
                    "Report",
                    "Correspondence",
                    "Technical",
                    "Other",
                ],
            )

            project = st.text_input(
                "Project"
            )

            status = st.selectbox(
                "Status",
                [
                    "Draft",
                    "Issued",
                    "Approved",
                    "Archived",
                ],
            )

            description = st.text_area(
                "Description"
            )

            submitted = st.form_submit_button(
                "Add Document",
                use_container_width=True,
            )

        if submitted:

            if not title.strip():
                st.error(
                    "Document title is required."
                )
                return

            documents.append(
                {
                    "id": _next_id(
                        documents
                    ),
                    "title": title.strip(),
                    "name": title.strip(),
                    "document_number": (
                        document_number.strip()
                    ),
                    "category": category,
                    "project": project.strip(),
                    "status": status,
                    "description": (
                        description.strip()
                    ),
                    "created_at": datetime.now().isoformat(
                        timespec="seconds"
                    ),
                }
            )

            _save(database)

            st.success(
                "Document added successfully."
            )

            st.rerun()