"""
Creative Studios
Documents Module
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from modules.database import save_memory
from modules.document_storage import (
    delete_file,
    get_file_bytes,
    list_module_files,
    render_module_files,
)


MODULES = [
    "Projects",
    "Architecture",
    "Engineering",
    "Drawings",
    "BOQ",
    "MEP",
]


def _all_documents(
    database: dict[str, Any],
) -> list[dict[str, Any]]:

    value = database.get(
        "documents",
        [],
    )

    if not isinstance(value, list):
        value = []

    return [
        dict(item)
        for item in value
        if isinstance(item, dict)
    ]


def render_documents_module(
    database: dict[str, Any],
) -> None:

    st.title("Documents")

    st.caption(
        "Central document library for Creative Studios."
    )

    documents = _all_documents(
        database
    )

    upload, library, module_library = st.tabs(
        [
            "Add Document",
            "Document Library",
            "Module Libraries",
        ]
    )

    with upload:

        selected_module = st.selectbox(
            "Module",
            MODULES,
        )

        render_module_files(
            database,
            selected_module,
        )

    with library:

        search = st.text_input(
            "Search documents"
        ).strip().lower()

        filtered = documents

        if search:

            filtered = [
                document
                for document in documents
                if search in " ".join(
                    [
                        str(
                            document.get(
                                "title",
                                "",
                            )
                        ),
                        str(
                            document.get(
                                "original_name",
                                "",
                            )
                        ),
                        str(
                            document.get(
                                "project",
                                "",
                            )
                        ),
                        str(
                            document.get(
                                "module",
                                "",
                            )
                        ),
                        str(
                            document.get(
                                "document_type",
                                "",
                            )
                        ),
                    ]
                ).lower()
            ]

        if not filtered:

            st.info(
                "No documents found."
            )

        else:

            st.write(
                f"{len(filtered)} document(s)"
            )

            for document in filtered:

                document_id = document.get(
                    "id"
                )

                with st.expander(
                    str(
                        document.get(
                            "title",
                            "Untitled",
                        )
                    ),
                    expanded=False,
                ):

                    st.write(
                        f"**Module:** "
                        f"{document.get('module', '')}"
                    )

                    st.write(
                        f"**File:** "
                        f"{document.get('original_name', '')}"
                    )

                    st.write(
                        f"**Project:** "
                        f"{document.get('project', '') or 'General'}"
                    )

                    st.write(
                        f"**Type:** "
                        f"{document.get('document_type', 'General')}"
                    )

                    st.write(
                        f"**Revision:** "
                        f"{document.get('revision', 'A')}"
                    )

                    st.write(
                        f"**Status:** "
                        f"{document.get('status', 'Draft')}"
                    )

                    file_bytes = get_file_bytes(
                        document
                    )

                    if file_bytes is not None:

                        st.download_button(
                            "Download",
                            data=file_bytes,
                            file_name=str(
                                document.get(
                                    "original_name",
                                    "file",
                                )
                            ),
                            mime=document.get(
                                "mime_type",
                                "application/octet-stream",
                            ),
                            key=f"documents_download_{document_id}",
                            use_container_width=True,
                        )

                    if st.button(
                        "Delete",
                        key=f"documents_delete_{document_id}",
                        use_container_width=True,
                    ):

                        delete_file(
                            database,
                            document_id,
                        )

                        st.rerun()

    with module_library:

        for module_name in MODULES:

            files = list_module_files(
                database,
                module_name,
            )

            with st.expander(
                f"{module_name} ({len(files)})",
                expanded=False,
            ):

                if not files:

                    st.info(
                        "No documents."
                    )

                else:

                    for document in files:

                        st.write(
                            f"**{document.get('title', 'Untitled')}** "
                            f"— "
                            f"{document.get('original_name', '')}"
                        )