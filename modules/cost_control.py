"""Creative Studios Cost Control module."""
from __future__ import annotations

from typing import Any

import streamlit as st

from modules.module_utils import (
    ensure_collection,
    now_iso,
    project_records,
    project_selector,
    remove_record,
    save_new_record,
    save_updated_record,
)

COST_TYPES = ["Budget", "Committed Cost", "Actual Cost", "Forecast", "Variation"]
STATUSES = ["Draft", "Active", "Approved", "Closed"]


def _amount(record: dict[str, Any]) -> float:
    try:
        return float(record.get("amount", 0) or 0)
    except (TypeError, ValueError):
        return 0.0


def _index(options: list[str], value: Any, default: int = 0) -> int:
    return options.index(value) if value in options else default


def render_cost_control_module(database: dict[str, Any]) -> None:
    st.title("Cost Control")
    st.caption("Project budgets, commitments, actual costs, forecasts and variations.")

    records = ensure_collection(database, "cost_control")
    project_id, _ = project_selector(database, "cost_control_project")
    if project_id is None:
        return

    items = project_records(records, project_id)
    totals = {
        cost_type: sum(_amount(record) for record in items if record.get("cost_type") == cost_type)
        for cost_type in COST_TYPES
    }

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Budget", f"{totals['Budget']:,.2f}")
    c2.metric("Committed", f"{totals['Committed Cost']:,.2f}")
    c3.metric("Actual", f"{totals['Actual Cost']:,.2f}")
    c4.metric("Forecast", f"{totals['Forecast']:,.2f}")
    c5.metric("Variation", f"{totals['Variation']:,.2f}")
    st.caption(f"Budget remaining after actual cost: {totals['Budget'] - totals['Actual Cost']:,.2f}")

    search = st.text_input("Search costs", placeholder="Cost code or description", key="cost_control_search")
    status_filter = st.selectbox("Status", ["All"] + STATUSES, key="cost_control_status_filter")
    type_filter = st.selectbox("Cost Type", ["All"] + COST_TYPES, key="cost_control_type_filter")
    query = search.strip().lower()
    visible = [
        record for record in items
        if (not query or query in str(record.get("cost_code", "")).lower() or query in str(record.get("description", "")).lower())
        and (status_filter == "All" or record.get("status") == status_filter)
        and (type_filter == "All" or record.get("cost_type") == type_filter)
    ]

    st.subheader("Cost Register")
    if not visible:
        st.info("No matching cost records exist for this project.")
    else:
        for record in list(visible):
            record_id = record.get("id")
            with st.expander(
                f"{record.get('cost_code', 'Cost')} | {record.get('description', 'Cost item')} | {_amount(record):,.2f}"
            ):
                with st.form(f"cost_edit_{record_id}"):
                    code = st.text_input("Cost Code", value=str(record.get("cost_code", "")))
                    description = st.text_input("Description", value=str(record.get("description", "")))
                    cost_type = st.selectbox("Cost Type", COST_TYPES, index=_index(COST_TYPES, record.get("cost_type")))
                    amount = st.number_input("Amount", min_value=0.0, value=max(0.0, _amount(record)), step=100.0)
                    status = st.selectbox("Status", STATUSES, index=_index(STATUSES, record.get("status")))
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
                        if remove_record(database, "cost_control", record_id):
                            st.success("Cost record deleted.")
                            st.rerun()
                        else:
                            st.warning("The cost record was already removed.")
                    except Exception as exc:
                        st.error("Unable to delete the cost record.")
                        with st.expander("Technical details"):
                            st.exception(exc)

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
