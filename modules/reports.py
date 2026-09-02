"""Creative Studios Reports module."""
from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from modules.database import get_records

COST_TYPES = ["Budget", "Committed Cost", "Actual Cost", "Forecast", "Variation"]
COLLECTIONS = [
    "documents", "architecture", "engineering", "drawings", "mep", "boq",
    "construction", "procurement", "tasks", "rfis", "approvals", "cost_control",
]


def _count(database: dict[str, Any], collection: str) -> int:
    try:
        return len(get_records(collection, database))
    except Exception:
        return 0


def _amount(record: dict[str, Any]) -> float:
    try:
        return float(record.get("amount", 0) or 0)
    except (TypeError, ValueError):
        return 0.0


def _status_key(value: Any) -> str:
    return str(value or "").strip().lower().replace(" ", "_")


def _cost_total(database: dict[str, Any], cost_type: str | None = None) -> float:
    records = get_records("cost_control", database)
    return sum(
        _amount(record)
        for record in records
        if cost_type is None or str(record.get("cost_type", "")) == cost_type
    )


def render_reports_module(database: dict[str, Any]) -> None:
    st.title("Reports")
    st.caption("Portfolio and project-control reporting from the shared workspace database.")

    try:
        projects = get_records("projects", database)
        tasks = get_records("tasks", database)
        rfis = get_records("rfis", database)
    except Exception as exc:
        st.error("Unable to load report data from the shared database.")
        with st.expander("Technical details"):
            st.exception(exc)
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Projects", len(projects))
    c2.metric("Drawings", _count(database, "drawings"))
    c3.metric("Tasks", len(tasks))
    c4.metric("Open RFIs", sum(_status_key(r.get("status")) in {"open", "under_review"} for r in rfis))

    st.subheader("Delivery Controls")
    status_rows = [
        {"Project Status": label, "Projects": sum(_status_key(p.get("status")) == key for p in projects)}
        for key, label in [
            ("planning", "Planning"),
            ("active", "Active"),
            ("on_hold", "On Hold"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ]
    ]
    st.dataframe(pd.DataFrame(status_rows), use_container_width=True, hide_index=True)

    st.subheader("Cost Summary")
    try:
        cost_rows = [{"Cost Type": label, "Amount": _cost_total(database, label)} for label in COST_TYPES]
    except Exception as exc:
        st.error("Unable to calculate the cost summary.")
        with st.expander("Technical details"):
            st.exception(exc)
        cost_rows = []
    st.dataframe(pd.DataFrame(cost_rows), use_container_width=True, hide_index=True)

    st.subheader("Module Record Counts")
    counts_df = pd.DataFrame([
        {"Module": collection.replace("_", " ").title(), "Records": _count(database, collection)}
        for collection in COLLECTIONS
    ])
    if counts_df.empty:
        st.info("No module records are available yet.")
    else:
        st.bar_chart(counts_df.set_index("Module"), use_container_width=True)

    st.caption("Reports read the same shared workspace state used by the Streamlit modules.")
