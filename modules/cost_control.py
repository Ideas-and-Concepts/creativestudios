"""Creative Studios Cost Control module."""
from __future__ import annotations

from typing import Any

import streamlit as st

from modules.database import get_records
from modules.module_utils import now_iso, project_records, project_selector, save_new_record, save_updated_record, ensure_collection

COST_TYPES = ["Budget", "Committed Cost", "Actual Cost", "Forecast", "Variation"]
STATUSES = ["Draft", "Active", "Approved", "Closed"]


def _amount(record: dict[str, Any], field: str) -> float:
    try:
        return float(record.get(field, 0) or 0)
    except (TypeError, ValueError):
        return 0.0


def render_cost_control_module(database: dict[str, Any]) -> None:
    st.title("Cost Control")
    st.caption("Project budgets, commitments, actual costs, forecasts and variations.")

    records = ensure_collection(database, "cost_control")
    project_id, _ = project_selector(database, "cost_control_project")
    if project_id is None:
        return

    project_records_list = project_records(records, project_id)
    total_budget = sum(_amount(r, "amount") for r in project_records_list if r.get("cost_type") == "Budget")
    committed = sum(_amount(r, "amount") for r in project_records_list if r.get("cost_type") == "Committed Cost")
    actual = sum(_amount(r, "amount") for r in project_records_list if r.get("cost_type") == "Actual Cost")
    forecast = sum(_amount(r, "amount") for r in project_records_list if r.get("cost_type") == "Forecast")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Budget", f"{total_budget:,.2f}")
    c2.metric("Committed", f"{committed:,.2f}")
    c3.metric("Actual", f"{actual:,.2f}")
    c4.metric("Forecast", f"{forecast:,.2f}")

    st.subheader("Cost Register")
    for record in list(project_records_list):
        rid = record.get("id")
        with st.expander(f"{record.get('cost_code', 'Cost')} | {record.get('description', 'Cost item')}"):
            with st.form(f"cost_edit_{rid}"):
                code = st.text_input("Cost Code", value=str(record.get("cost_code", "")))
                description = st.text_input("Description", value=str(record.get("description", "")))
                cost_type = st.selectbox("Cost Type", COST_TYPES, index=COST_TYPES.index(record.get("cost_type", "Budget")) if record.get("cost_type") in COST_TYPES else 0)
                amount = st.number_input("Amount", min_value=0.0, value=_amount(record, "amount"), step=100.0)
                status = st.selectbox("Status", STATUSES, index=STATUSES.index(record.get("status", "Draft")) if record.get("status") in STATUSES else 0)
                notes = st.text_area("Notes", value=str(record.get("notes", "")))
                submitted = st.form_submit_button("Save Changes", use_container_width=True)
            if submitted:
                if not code.strip() or not description.strip():
                    st.error("Cost Code and Description are required.")
                else:
                    save_updated_record(database, "cost_control", rid, {"cost_code": code.strip(), "description": description.strip(), "cost_type": cost_type, "amount": round(amount, 2), "status": status, "notes": notes.strip(), "updated_at": now_iso()})
                    st.success("Cost record updated.")
                    st.rerun()
            if st.button("Delete Record", key=f"cost_delete_{rid}", use_container_width=True):
                from modules.database import delete_record
                delete_record("cost_control", rid, database)
                st.rerun()

    st.divider()
    with st.form("cost_add", clear_on_submit=True):
        code = st.text_input("Cost Code")
        description = st.text_input("Description")
        cost_type = st.selectbox("Cost Type", COST_TYPES)
        amount = st.number_input("Amount", min_value=0.0, step=100.0)
        status = st.selectbox("Status", STATUSES)
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Add Cost Record", use_container_width=True)
    if submitted:
        if not code.strip() or not description.strip():
            st.error("Cost Code and Description are required.")
        else:
            save_new_record(database, "cost_control", {"project_id": project_id, "cost_code": code.strip(), "description": description.strip(), "cost_type": cost_type, "amount": round(amount, 2), "status": status, "notes": notes.strip(), "created_at": now_iso(), "updated_at": now_iso()})
            st.success("Cost record added.")
            st.rerun()
