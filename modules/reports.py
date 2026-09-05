"""Creative Studios portfolio and project-control reports."""
from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from modules.database import database_backend, get_records, get_relational_documents, get_relational_drawings, get_relational_projects
from modules.boq_repository import get_relational_boq_items
from modules.procurement_repository import get_relational_purchase_orders

COST_TYPES = ["Budget", "Committed Cost", "Actual Cost", "Forecast", "Variation"]
WORKSPACE_COLLECTIONS = ["architecture", "engineering", "mep", "construction", "tasks", "rfis", "approvals", "cost_control"]


def _records(database: dict[str, Any], collection: str) -> list[dict[str, Any]]:
    if database_backend() == "neon":
        relational = {
            "projects": get_relational_projects,
            "documents": get_relational_documents,
            "drawings": get_relational_drawings,
            "boq": get_relational_boq_items,
            "procurement": get_relational_purchase_orders,
        }.get(collection)
        if relational:
            return relational()
    rows = get_records(collection, database)
    return rows if isinstance(rows, list) else []


def _amount(record: dict[str, Any]) -> float:
    try:
        return float(record.get("amount", 0) or 0)
    except (TypeError, ValueError):
        return 0.0


def _status_key(value: Any) -> str:
    return str(value or "").strip().lower().replace(" ", "_")


def _cost_total(database: dict[str, Any], cost_type: str | None = None) -> float:
    records = _records(database, "cost_control")
    return sum(_amount(record) for record in records if cost_type is None or str(record.get("cost_type", "")) == cost_type)


def render_reports_module(database: dict[str, Any]) -> None:
    st.title("Reports")
    st.caption("Portfolio and project-control reporting from the shared workspace database.")

    try:
        projects = _records(database, "projects")
        documents = _records(database, "documents")
        drawings = _records(database, "drawings")
        boq = _records(database, "boq")
        procurement = _records(database, "procurement")
        tasks = _records(database, "tasks")
        rfis = _records(database, "rfis")
    except Exception as exc:
        st.error("Unable to load report data from the shared database.")
        with st.expander("Technical details", expanded=True):
            st.exception(exc)
        return

    project_labels = ["All Projects", *[f"{p.get('code') or p.get('id')} | {p.get('name') or 'Unnamed Project'}" for p in projects]]
    selected = st.selectbox("Project", project_labels, key="reports_project_filter")
    selected_project = next((p for p in projects if f"{p.get('code') or p.get('id')} | {p.get('name') or 'Unnamed Project'}" == selected), None)
    project_id = str(selected_project.get("id")) if selected_project else None

    def scope(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not project_id:
            return rows
        return [row for row in rows if str(row.get("project_id")) == project_id]

    documents, drawings, boq, procurement, tasks, rfis = map(scope, [documents, drawings, boq, procurement, tasks, rfis])
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Projects", len([selected_project] if selected_project else projects))
    c2.metric("Drawings", len(drawings))
    c3.metric("Documents", len(documents))
    c4.metric("Tasks", len(tasks))
    c5.metric("Open RFIs", sum(_status_key(r.get("status")) not in {"closed", "completed"} for r in rfis))

    st.subheader("Delivery Controls")
    status_rows = [
        {"Project Status": label, "Projects": sum(_status_key(p.get("status")) == key for p in ([selected_project] if selected_project else projects))}
        for key, label in [("planning", "Planning"), ("active", "Active"), ("on_hold", "On Hold"), ("completed", "Completed"), ("cancelled", "Cancelled")]
    ]
    st.dataframe(pd.DataFrame(status_rows), use_container_width=True, hide_index=True)

    st.subheader("Commercial Summary")
    boq_value = sum(_amount(r) if r.get("amount") is not None else _amount({"amount": float(r.get("quantity", 0) or 0) * float(r.get("rate", 0) or 0)}) for r in boq)
    procurement_value = sum(float(r.get("total") or r.get("grand_total") or r.get("amount") or 0) for r in procurement)
    commercial = pd.DataFrame({"Metric": ["BOQ value", "Procurement value"], "Amount": [boq_value, procurement_value]})
    st.dataframe(commercial, use_container_width=True, hide_index=True)

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
    counts = [("Architecture", "architecture"), ("Engineering", "engineering"), ("MEP", "mep"), ("Construction", "construction"), ("Tasks", "tasks"), ("RFIs", "rfis"), ("Approvals", "approvals"), ("Cost Control", "cost_control")]
    counts_df = pd.DataFrame([{"Module": label, "Records": len(scope(_records(database, key)))} for label, key in counts])
    st.bar_chart(counts_df.set_index("Module"), use_container_width=True)

    st.caption(f"Data source: {'Neon PostgreSQL' if database_backend() == 'neon' else 'Local JSON'}. Reports use canonical relational records where available.")
