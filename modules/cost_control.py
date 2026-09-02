"""Creative Studios Cost Control module."""
from __future__ import annotations

from typing import Any

import streamlit as st

from modules.database import delete_record
from modules.module_utils import (
    ensure_collection,
    now_iso,
    project_records,
    project_selector,
    save_new_record,
    save_updated_record,
)

COST_TYPES = ["Budget", "Committed Cost", "Actual Cost", "Forecast", "Variation"]
STATUSES = ["Draft", "Active", "Approved", "Closed"]


def _amount(record: dict[str, Any], field: str = "amount") -> float:
    try:
        return float(record.get(field, 0) or 0)
    except (TypeError, ValueError):
        return 0.0


def _cost_type_index(record: dict[str, Any]) -> int:
    value = record.get("cost_type", "Budget")
    return COST_TYPES.index(value) if value in COST_TYPES else 0


def _status_index(record: dict[str, Any]) -> int:
    value = record.get("status", "Draft")
    return STATUSES.index(value) if value in STATUSES else 0


def render_cost_control_module(database: dict[str, Any]) -> None:
    st.title("Cost Control")
    st.caption("Project budgets, commitments, actual costs, forecasts and variations.")

    records = ensure_collection(database, "cost_control")
    project_id, _ = project_selector(database, "cost_control_project")
    if project_id is None:
        return

    project_records_list = project_records(records, project_id)
    total_budget = sum(_amount(record) for record in project_records_list if record.get("cost_type") == "Budget")
    committed = sum(_amount(record) for record in project_records_list if record.get("cost_type") == "Committed Cost")
    actual = sum(_amount(record) for record in project_records_list if record.get("cost_type") == "Actual Cost")
    forecast = sum(_amount(record) for record in project_records_list if record.get("cost_type") == "Forecast")
    variation = sum(_amount(record) for record in project_records_list if record.get("cost_type") == "Variation")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Budget", f"{total_budget:,.2f}")
    c2.metric("Committed", f"{committed:,.2f}")
    c3.metric("Actual", f"{actual:,.2f}")
    c4.metric("Forecast", f"{forecast:,.2f}")
    c5.metric("Variation", f"{variation:,.2f}")

    remaining = total_budget - actual
    st.caption(f"Budget remaining after actual cost: {remaining:,.2f}")

    st.subheader("Cost Register")
    if project_records_list:
        for record in list(project_records_list):
            record_id = record.get("id")
            with st.expander(
                f"{record.get('cost_code', 'Cost')} | {record.get('description', 'Cost item')} | {_amount(record):,.2f}"
            ):
                with st.form(f"cost_edit_{record_id}"):
                    code = st.text_input("Cost Code", value=str(record.get("cost_code", "")))
                    description = st.text_input("Description", value=str(record.get("description", "")))
                    cost_type = st.selectbox("Cost Type", COST_TYPES, index=_cost_type_index(record))
                    amount = st.number_input(
                        "Amount",
                        min_value=0.0,
                        value=max(0.0, _amount(record)),
                        step=100.0,
                    )
                    status = st.selectbox("Status", STATUSES, index=_status_index(record))
                    notes = st.text_area("Notes", value=str(record.get("notes", "")))
                    submitted = st.form_submit_button("Save Changes", use_container_width=True)

                if submitted:
                    if not code.strip() or not description.strip():
                        st.error("Cost Code and Description are required.")
                    else:
                        try:
                            saved = save_updated_record(
                                database,
                                "cost_control",
                                record_id,
                                {
                                    "project_id": project_id,
                                    "cost_code": code.strip(),
                                    "description": description.strip(),
                                    "cost_type": cost_type,
                                    "amount": round(float(amount), 2),
                                    "status": status,
                                    "notes": notes.strip(),
                                    "updated_at": now_iso(),
                                },
                            )
                            if not saved:
                                st.error("The cost record could not be found.")
                            else:
                                st.success("Cost record updated.")
                                st.rerun()
                        except Exception as exc:
                            st.error("Unable to save the cost record.")
                            with st.expander("Technical details"):
                                st.exception(exc)

                if st.button("Delete Record", key=f"cost_delete_{record_id}", use_container_width=True):
                    try:
                        if delete_record("cost_control", record_id, database):
                            st.success("Cost record deleted.")
                            st.rerun()
                        else:
                            st.warning("The cost record was already removed.")
                    except Exception as exc:
                        st.error("Unable to delete the cost record.")
                        with st.expander("Technical details"):
                            st.exception(exc)
    else:
        st.info("No cost records exist for this project yet.")

    st.divider()
    st.subheader("Add Cost Record")
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
            try:
                save_new_record(
                    database,
                    "cost_control",
                    {
                        "project_id": project_id,
                        "cost_code": code.strip(),
                        "description": description.strip(),
                        "cost_type": cost_type,
                        "amount": round(float(amount), 2),
                        "status": status,
                        "notes": notes.strip(),
                        "created_at": now_iso(),
                        "updated_at": now_iso(),
                    },
                )
                st.success("Cost record added.")
                st.rerun()
            except Exception as exc:
                st.error("Unable to add the cost record.")
                with st.expander("Technical details"):
                    st.exception(exc)
