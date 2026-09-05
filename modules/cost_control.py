"""Creative Studios Cost Control and Earned Value Management module."""
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
from modules.project_controls import calculate_evm

COST_TYPES = ["Budget", "Committed Cost", "Actual Cost", "Forecast", "Variation"]
STATUSES = ["Draft", "Active", "Approved", "Closed"]


def _amount(record: dict[str, Any]) -> float:
    try:
        return float(record.get("amount", 0) or 0)
    except (TypeError, ValueError):
        return 0.0


def _index(options: list[str], value: Any, default: int = 0) -> int:
    return options.index(value) if value in options else default


def _performance_label(value: float | None) -> str:
    if value is None:
        return "No baseline"
    return "On target" if value >= 1.0 else "Needs attention"


def _render_evm(
    boq: list[dict[str, Any]],
    construction: list[dict[str, Any]],
    costs: list[dict[str, Any]],
    site_logs: list[dict[str, Any]],
) -> None:
    evm = calculate_evm(boq, construction, costs, site_logs)
    st.divider()
    st.subheader("Earned Value Management")
    st.caption("Project Controls: BOQ baseline → construction activity → site progress → actual cost.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("BAC · Budget at Completion", f"{evm['bac']:,.2f}")
    c2.metric("PV · Planned Value", f"{evm['pv']:,.2f}")
    c3.metric("EV · Earned Value", f"{evm['ev']:,.2f}")
    c4.metric("AC · Actual Cost", f"{evm['ac']:,.2f}")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("CV · Cost Variance", f"{evm['cv']:,.2f}")
    c2.metric("SV · Schedule Variance", f"{evm['sv']:,.2f}")
    c3.metric("CPI", "N/A" if evm["cpi"] is None else f"{evm['cpi']:.3f}", _performance_label(evm["cpi"]))
    c4.metric("SPI", "N/A" if evm["spi"] is None else f"{evm['spi']:.3f}", _performance_label(evm["spi"]))
    c5.metric("VAC · Variance at Completion", f"{evm['vac']:,.2f}")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("EAC · Estimate at Completion", f"{evm['eac']:,.2f}")
    c2.metric("ETC · Estimate to Complete", f"{evm['etc']:,.2f}")
    c3.metric("TCPI · BAC", "N/A" if evm["tcpi_bac"] is None else f"{evm['tcpi_bac']:.3f}")
    c4.metric("TCPI · EAC", "N/A" if evm["tcpi_eac"] is None else f"{evm['tcpi_eac']:.3f}")
    c5.metric("Site Logs", f"{evm['site_logs']:,}")

    c1, c2, c3 = st.columns(3)
    c1.metric("Physical Progress", f"{evm['physical']:.1f}%")
    c2.metric("Financial Progress", f"{evm['financial']:.1f}%")
    c3.metric("Baseline Coverage", f"{evm['covered']} / {evm['baseline_items']}")
    st.progress(min(1.0, max(0.0, evm["physical"] / 100.0)), text=f"Physical progress {evm['physical']:.1f}%")
    st.caption(
        f"{evm['covered']} BOQ-linked baselines have usable planned start/finish dates. "
        "Each BOQ item is valued once, preventing duplicate earned value when several activities share one BOQ item. "
        "Site logs can update physical progress when activity quantities and units are usable."
    )


def render_cost_control_module(database: dict[str, Any]) -> None:
    st.title("Cost Control")
    st.caption("Project budgets, commitments, actual costs, forecasts, variations and earned value performance.")

    records = ensure_collection(database, "cost_control")
    project_id, _ = project_selector(database, "cost_control_project")
    if project_id is None:
        return

    items = project_records(records, project_id)
    boq = project_records(ensure_collection(database, "boq"), project_id)
    construction = project_records(ensure_collection(database, "construction"), project_id)
    site_logs = project_records(ensure_collection(database, "site_progress_logs"), project_id)
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

    _render_evm(boq, construction, items, site_logs)

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
            with st.expander(f"{record.get('cost_code', 'Cost')} | {record.get('description', 'Cost item')} | {_amount(record):,.2f}"):
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
                            saved = save_updated_record(database, "cost_control", record_id, {
                                "project_id": project_id, "cost_code": code.strip(), "description": description.strip(),
                                "cost_type": cost_type, "amount": round(float(amount), 2), "status": status,
                                "notes": notes.strip(), "updated_at": now_iso(),
                            })
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
                save_new_record(database, "cost_control", {
                    "project_id": project_id, "cost_code": code.strip(), "description": description.strip(),
                    "cost_type": cost_type, "amount": round(float(amount), 2), "status": status,
                    "notes": notes.strip(), "created_at": now_iso(), "updated_at": now_iso(),
                })
                st.success("Cost record added.")
                st.rerun()
            except Exception as exc:
                st.error("Unable to add the cost record.")
                with st.expander("Technical details"):
                    st.exception(exc)
