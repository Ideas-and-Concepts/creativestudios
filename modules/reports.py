"""Creative Studios Reports module."""
from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from modules.database import get_records


def _count(database: dict[str, Any], collection: str) -> int:
    return len(get_records(collection, database))


def _cost_total(database: dict[str, Any], cost_type: str | None = None) -> float:
    total = 0.0
    for record in get_records("cost_control", database):
        if cost_type and record.get("cost_type") != cost_type:
            continue
        try:
            total += float(record.get("amount", 0) or 0)
        except (TypeError, ValueError):
            pass
    return total


def render_reports_module(database: dict[str, Any]) -> None:
    st.title("Reports")
    st.caption("Portfolio and project-control reporting from the legacy workspace database.")

    projects = get_records("projects", database)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Projects", len(projects))
    c2.metric("Drawings", _count(database, "drawings"))
    c3.metric("Tasks", _count(database, "tasks"))
    c4.metric("Open RFIs", sum(r.get("status") in {"Open", "Under Review"} for r in get_records("rfis", database)))

    st.subheader("Delivery Controls")
    status_rows = []
    for status in ["planning", "active", "on_hold", "completed", "cancelled"]:
        status_rows.append({"Project Status": status.replace("_", " ").title(), "Projects": sum(p.get("status") == status for p in projects)})
    st.dataframe(pd.DataFrame(status_rows), use_container_width=True, hide_index=True)

    st.subheader("Cost Summary")
    cost_rows = [
        {"Cost Type": label, "Amount": _cost_total(database, label)}
        for label in ["Budget", "Committed Cost", "Actual Cost", "Forecast", "Variation"]
    ]
    st.dataframe(pd.DataFrame(cost_rows), use_container_width=True, hide_index=True)

    st.subheader("Module Record Counts")
    collections = ["documents", "architecture", "engineering", "drawings", "mep", "boq", "construction", "tasks", "rfis", "approvals"]
    rows = [{"Module": collection.replace("_", " ").title(), "Records": _count(database, collection)} for collection in collections]
    st.bar_chart(pd.DataFrame(rows).set_index("Module"), use_container_width=True)

    st.info("Reports use the Streamlit legacy database. Production reporting will use the Neon-backed Next.js application.")
