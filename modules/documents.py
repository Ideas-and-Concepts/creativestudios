"""
Creative Studios
Documents Module
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st


def _documents(
    database: dict[str, Any],
) -> list[dict[str, Any]]:
    value = database.setdefault(
        "documents",
        [],
    )

    if not isinstance(value, list):
        database["documents"] = []
        return database["documents"]

    return value


def _next_id(records: list[dict[str, Any]]) -> int:
    ids = []

    for record in records:
        try:
            ids.append(int(record.get("id", 0)))
        except (TypeError, ValueError):
            continue

    return max(ids, default=0) + 1


def render_documents_module(
    database: dict[str, Any],
) -> None:
    """Render document management."""

    st.title("Documents")
    st.caption(
        "Manage project documentation and records."
    )

    documents = _documents(database)

    tab_library, tab_create = st.tabs(
        ["Document Library", "Add Document"]
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

            search_value = search.strip().lower()

            filtered = []

            for document in documents:

                searchable = " ".join(
                    str(
                        document.get(field, "")
                    )
                    for field in (
                        "name",
                        "title",
                        "document_number",
                        "category",
                        "project",
                    )
                ).lower()

                if (
                    not search_value
                    or search_value in searchable
                ):
                    filtered.append(document)

            for document in filtered:

                title = document.get(
                    "title",
                    document.get(
                        "name",
                        "Untitled Document",
                    ),
                )

                with st.container(border=True):

                    st.subheader(str(title))

                    columns = st.columns(4)

                    columns[0].write(
                        f"**Document Number**  \n"
                        f"{document.get('document_number', '-')}"
                    )

                    columns[1].write(
                        f"**Category**  \n"
                        f"{document.get('category', '-')}"
                    )

                    columns[2].write(
                        f"**Project**  \n"
                        f"{document.get('project', '-')}"
                    )

                    columns[3].write(
                        f"**Status**  \n"
                        f"{document.get('status', '-')}"
                    )

    with tab_create:

        with st.form(
            "create_document_form",
            clear_on_submit=True,
        ):

            title = st.text_input(
                "Document Title",
            )

            document_number = st.text_input(
                "Document Number",
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
                "Project",
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
                "Description",
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
                    "id": _next_id(documents),
                    "title": title.strip(),
                    "name": title.strip(),
                    "document_number": (
                        document_number.strip()
                    ),
                    "category": category,
                    "project": project.strip(),
                    "status": status,
                    "description": description.strip(),
                    "created_at": datetime.now().isoformat(
                        timespec="seconds"
                    ),
                }
            )

            st.success(
                "Document added successfully."
            )

            st.rerun()