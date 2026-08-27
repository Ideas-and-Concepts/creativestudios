"""
Creative Studios
Dashboard Module

Main AEC collaboration dashboard.

The dashboard provides:
    - Creative Studios branding
    - Project overview
    - Live module statistics
    - Architecture statistics
    - Engineering statistics
    - MEP statistics
    - BOQ statistics
    - Document statistics
    - Quick navigation actions
    - Recent project/work information

The dashboard does not own the database.
It receives the shared database dictionary from streamlit_app.py.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

ASSETS_DIR = BASE_DIR / "assets"

LOGO_CANDIDATES = [
    ASSETS_DIR / "creative_studios.png",
    ASSETS_DIR / "creative_studios_logo.png",
    ASSETS_DIR / "logo.png",
]


def _find_logo() -> Path | None:
    """Return the first available Creative Studios logo."""

    for path in LOGO_CANDIDATES:
        if path.exists():
            return path

    return None


# ============================================================
# SAFE DATA HELPERS
# ============================================================

def _records(
    database: dict[str, Any],
    key: str,
) -> list[Any]:
    """
    Return a database collection safely as a list.

    Older database versions may contain strings, dictionaries,
    or missing collections. This helper prevents dashboard
    rendering errors.
    """

    value = database.get(key, [])

    if isinstance(value, list):
        return value

    return []


def _count(
    database: dict[str, Any],
    key: str,
) -> int:
    """Return the number of records in a database collection."""

    return len(
        _records(
            database,
            key,
        )
    )


def _count_matching(
    database: dict[str, Any],
    key: str,
    field: str,
    value: str,
) -> int:
    """Count dictionary records matching a field value."""

    records = _records(
        database,
        key,
    )

    total = 0

    for record in records:

        if not isinstance(record, dict):
            continue

        current = str(
            record.get(
                field,
                "",
            )
        ).strip().lower()

        if current == value.strip().lower():
            total += 1

    return total


def _safe_text(
    value: Any,
    fallback: str = "",
) -> str:
    """Convert a value safely to display text."""

    if value is None:
        return fallback

    text = str(value).strip()

    return text if text else fallback


# ============================================================
# BRANDING
# ============================================================

def render_branding() -> None:
    """Render the centered Creative Studios dashboard branding."""

    logo = _find_logo()

    st.markdown(
        """
        <div class="cs-dashboard-brand">
        """,
        unsafe_allow_html=True,
    )

    if logo is not None:

        left, center, right = st.columns(
            [1, 1, 1]
        )

        with center:

            st.image(
                str(logo),
                width=130,
            )

    else:

        left, center, right = st.columns(
            [1, 1, 1]
        )

        with center:

            st.markdown(
                """
                <div class="cs-dashboard-logo-fallback">
                    CS
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        """
        <div class="cs-dashboard-title">
            Creative Studios
        </div>

        <div class="cs-dashboard-subtitle">
            AEC Collaboration Platform
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


# ============================================================
# DASHBOARD CSS
# ============================================================

def inject_dashboard_css() -> None:
    """Inject dashboard-specific styling."""

    st.markdown(
        """
        <style>

        .cs-dashboard-brand {
            width: 100%;
            text-align: center;
            padding: 0.5rem 0 1.75rem 0;
        }

        .cs-dashboard-brand
        [data-testid="stImage"] {
            display: flex;
            justify-content: center;
        }

        .cs-dashboard-title {
            text-align: center;
            font-size: 34px;
            font-weight: 800;
            line-height: 1.15;
            margin-top: 0.35rem;
        }

        .cs-dashboard-subtitle {
            text-align: center;
            font-size: 15px;
            opacity: 0.65;
            margin-top: 0.4rem;
        }

        .cs-dashboard-logo-fallback {
            width: 130px;
            height: 130px;
            margin: 0 auto;
            border-radius: 22px;
            border: 1px solid rgba(128,128,128,0.25);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 38px;
            font-weight: 800;
        }

        .cs-dashboard-section {
            font-size: 21px;
            font-weight: 750;
            margin: 1.5rem 0 0.75rem 0;
        }

        .cs-dashboard-section-description {
            font-size: 13px;
            opacity: 0.65;
            margin-bottom: 1rem;
        }

        .cs-dashboard-card {
            border: 1px solid rgba(128,128,128,0.20);
            border-radius: 12px;
            padding: 1rem;
            min-height: 115px;
        }

        .cs-dashboard-card-title {
            font-size: 16px;
            font-weight: 700;
        }

        .cs-dashboard-card-value {
            font-size: 28px;
            font-weight: 800;
            margin-top: 0.4rem;
        }

        .cs-dashboard-card-description {
            font-size: 12px;
            opacity: 0.60;
            margin-top: 0.25rem;
        }

        .cs-dashboard-status {
            border: 1px solid rgba(128,128,128,0.20);
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 0.75rem;
        }

        .cs-dashboard-status-title {
            font-weight: 700;
            font-size: 15px;
        }

        .cs-dashboard-status-text {
            font-size: 13px;
            opacity: 0.65;
            margin-top: 0.25rem;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# OVERVIEW STATISTICS
# ============================================================

def render_overview_metrics(
    database: dict[str, Any],
) -> None:
    """Render high-level application statistics."""

    projects = _count(
        database,
        "projects",
    )

    documents = _count(
        database,
        "documents",
    )

    architecture = _count(
        database,
        "architecture",
    )

    engineering = _count(
        database,
        "engineering",
    )

    mep = _count(
        database,
        "mep",
    )

    boq = _count(
        database,
        "boq",
    )

    drawings = (
        _count_matching(
            database,
            "architecture",
            "type",
            "Architectural Drawing",
        )
        + _count_matching(
            database,
            "engineering",
            "type",
            "Structural Drawing",
        )
        + _count_matching(
            database,
            "engineering",
            "type",
            "Engineering Drawing",
        )
    )

    st.markdown(
        """
        <div class="cs-dashboard-section">
            Project Overview
        </div>

        <div class="cs-dashboard-section-description">
            Live information from the Creative Studios project database.
        </div>
        """,
        unsafe_allow_html=True,
    )

    columns = st.columns(4)

    metrics = [
        (
            columns[0],
            "Projects",
            projects,
            "Active project records",
        ),
        (
            columns[1],
            "Documents",
            documents,
            "Project documents",
        ),
        (
            columns[2],
            "Design Records",
            architecture + engineering,
            "Architecture and engineering",
        ),
        (
            columns[3],
            "BOQ Items",
            boq,
            "Construction quantity records",
        ),
    ]

    for column, label, value, description in metrics:

        with column:

            st.markdown(
                f"""
                <div class="cs-dashboard-card">
                    <div class="cs-dashboard-card-title">
                        {label}
                    </div>

                    <div class="cs-dashboard-card-value">
                        {value}
                    </div>

                    <div class="cs-dashboard-card-description">
                        {description}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.caption(
        f"Architecture: {architecture} · "
        f"Engineering: {engineering} · "
        f"MEP: {mep} · "
        f"Drawing records: {drawings}"
    )


# ============================================================
# DISCIPLINE SUMMARY
# ============================================================

def render_discipline_summary(
    database: dict[str, Any],
) -> None:
    """Render Architecture, Engineering, MEP and BOQ summaries."""

    st.markdown(
        """
        <div class="cs-dashboard-section">
            Construction Workspaces
        </div>
        """,
        unsafe_allow_html=True,
    )

    columns = st.columns(4)

    architecture_count = _count(
        database,
        "architecture",
    )

    engineering_count = _count(
        database,
        "engineering",
    )

    mep_count = _count(
        database,
        "mep",
    )

    boq_count = _count(
        database,
        "boq",
    )

    workspace_data = [
        (
            columns[0],
            "Architecture",
            architecture_count,
            "Design, architectural drawings, schedules and revisions",
        ),
        (
            columns[1],
            "Engineering",
            engineering_count,
            "Structural, civil, calculations and engineering drawings",
        ),
        (
            columns[2],
            "MEP",
            mep_count,
            "Mechanical, electrical and plumbing work",
        ),
        (
            columns[3],
            "BOQ",
            boq_count,
            "Construction quantities and cost elements",
        ),
    ]

    for column, title, count, description in workspace_data:

        with column:

            st.markdown(
                f"""
                <div class="cs-dashboard-card">

                    <div class="cs-dashboard-card-title">
                        {title}
                    </div>

                    <div class="cs-dashboard-card-value">
                        {count}
                    </div>

                    <div class="cs-dashboard-card-description">
                        {description}
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# STATUS SUMMARY
# ============================================================

def render_status_summary(
    database: dict[str, Any],
) -> None:
    """Render useful project/design status information."""

    st.markdown(
        """
        <div class="cs-dashboard-section">
            Work Status
        </div>
        """,
        unsafe_allow_html=True,
    )

    architecture_issued = _count_matching(
        database,
        "architecture",
        "status",
        "Issued",
    )

    architecture_review = _count_matching(
        database,
        "architecture",
        "status",
        "In Review",
    )

    engineering_issued = _count_matching(
        database,
        "engineering",
        "status",
        "Issued",
    )

    engineering_review = _count_matching(
        database,
        "engineering",
        "status",
        "In Review",
    )

    columns = st.columns(4)

    values = [
        (
            columns[0],
            "Architecture In Review",
            architecture_review,
        ),
        (
            columns[1],
            "Architecture Issued",
            architecture_issued,
        ),
        (
            columns[2],
            "Engineering In Review",
            engineering_review,
        ),
        (
            columns[3],
            "Engineering Issued",
            engineering_issued,
        ),
    ]

    for column, title, value in values:

        with column:

            st.metric(
                title,
                value,
            )


# ============================================================
# RECENT RECORDS
# ============================================================

def render_recent_records(
    database: dict[str, Any],
) -> None:
    """Render recent records from the main workspaces."""

    st.markdown(
        """
        <div class="cs-dashboard-section">
            Recent Work
        </div>
        """,
        unsafe_allow_html=True,
    )

    architecture = _records(
        database,
        "architecture",
    )

    engineering = _records(
        database,
        "engineering",
    )

    projects = _records(
        database,
        "projects",
    )

    recent_items: list[dict[str, str]] = []

    for record in projects[-5:]:

        if isinstance(record, dict):

            recent_items.append(
                {
                    "area": "Project",
                    "title": _safe_text(
                        record.get(
                            "name",
                            record.get(
                                "title",
                                "Untitled Project",
                            ),
                        ),
                        "Untitled Project",
                    ),
                }
            )

    for record in architecture[-5:]:

        if isinstance(record, dict):

            recent_items.append(
                {
                    "area": "Architecture",
                    "title": _safe_text(
                        record.get(
                            "title",
                            record.get(
                                "name",
                                "Architecture Work",
                            ),
                        ),
                        "Architecture Work",
                    ),
                }
            )

    for record in engineering[-5:]:

        if isinstance(record, dict):

            recent_items.append(
                {
                    "area": "Engineering",
                    "title": _safe_text(
                        record.get(
                            "title",
                            record.get(
                                "name",
                                "Engineering Work",
                            ),
                        ),
                        "Engineering Work",
                    ),
                }
            )

    if not recent_items:

        st.info(
            "No project or design activity has been recorded yet."
        )

        return

    # Show the most recent records first.
    recent_items = recent_items[-10:][::-1]

    for item in recent_items:

        st.markdown(
            f"""
            <div class="cs-dashboard-status">

                <div class="cs-dashboard-status-title">
                    {item["title"]}
                </div>

                <div class="cs-dashboard-status-text">
                    {item["area"]}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# QUICK ACTIONS
# ============================================================

def render_quick_actions() -> None:
    """Render dashboard quick navigation actions."""

    st.markdown(
        """
        <div class="cs-dashboard-section">
            Quick Actions
        </div>
        """,
        unsafe_allow_html=True,
    )

    columns = st.columns(4)

    actions = [
        (
            columns[0],
            "Projects",
            "Open project management",
        ),
        (
            columns[1],
            "Architecture",
            "Open architectural workspace",
        ),
        (
            columns[2],
            "Engineering",
            "Open engineering workspace",
        ),
        (
            columns[3],
            "BOQ",
            "Open bill of quantities",
        ),
    ]

    for column, module_name, description in actions:

        with column:

            st.caption(description)

            if st.button(
                module_name,
                key=f"dashboard_action_{module_name.lower()}",
                use_container_width=True,
            ):

                st.session_state.active_module = (
                    module_name
                )

                st.rerun()


# ============================================================
# MAIN RENDERER
# ============================================================

def render_dashboard(
    database: dict[str, Any],
) -> None:
    """
    Render the Creative Studios dashboard.

    This function is intentionally named render_dashboard()
    because streamlit_app.py uses it as the Dashboard renderer.
    """

    if not isinstance(database, dict):
        database = {}

    inject_dashboard_css()

    render_branding()

    render_overview_metrics(
        database
    )

    render_discipline_summary(
        database
    )

    render_status_summary(
        database
    )

    render_recent_records(
        database
    )

    render_quick_actions()