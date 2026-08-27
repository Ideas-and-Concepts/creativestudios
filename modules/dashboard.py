"""
Creative Studios
Dashboard Module
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from modules.document_storage import (
    list_module_files,
)


def _count(
    database: dict[str, Any],
    key: str,
) -> int:

    value = database.get(
        key,
        [],
    )

    return (
        len(value)
        if isinstance(value, list)
        else 0
    )


def render_dashboard(
    database: dict[str, Any],
) -> None:

    st.title("Creative Studios")

    st.caption(
        "AEC Collaboration Platform"
    )

    projects = _count(
        database,
        "projects",
    )

    architecture = _count(
        database,
        "architecture",
    )

    engineering = _count(
        database,
        "engineering",
    )

    drawings = _count(
        database,
        "drawings",
    )

    boq = _count(
        database,
        "boq",
    )

    mep = _count(
        database,
        "mep",
    )

    documents = _count(
        database,
        "documents",
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Projects",
        projects,
    )

    c2.metric(
        "Architecture",
        architecture,
    )

    c3.metric(
        "Engineering",
        engineering,
    )

    c4.metric(
        "Drawings",
        drawings,
    )

    c5, c6, c7, c8 = st.columns(4)

    c5.metric(
        "BOQ Items",
        boq,
    )

    c6.metric(
        "MEP Records",
        mep,
    )

    c7.metric(
        "Documents",
        documents,
    )

    total_files = sum(
        len(
            list_module_files(
                database,
                module,
            )
        )
        for module in [
            "Projects",
            "Architecture",
            "Engineering",
            "Drawings",
            "BOQ",
            "MEP",
        ]
    )

    c8.metric(
        "Stored Files",
        total_files,
    )

    st.divider()

    st.subheader(
        "Construction Information Flow"
    )

    st.write(
        "Projects → Architecture → Engineering → "
        "Drawings → BOQ → MEP → Documents"
    )

    st.info(
        "Each module now has its own editable records "
        "and shared file/document repository."
    )

    st.subheader(
        "Workspace"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(
            """
            **Architecture**

            Building planning, design development,
            construction documentation and architectural drawings.
            """
        )

    with col2:

        st.markdown(
            """
            **Engineering**

            Structural, civil, geotechnical and
            infrastructure engineering coordination.
            """
        )

    with col3:

        st.markdown(
            """
            **Construction Information**

            Drawings, BOQ, MEP records, project files
            and technical documentation.
            """
        )