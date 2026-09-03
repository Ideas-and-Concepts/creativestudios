"""Creative Studios Cost Control and Earned Value Management module."""
from __future__ import annotations

from datetime import datetime, timezone
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


def _number(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _value(record: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in record and record.get(key) not in (None, ""):
            return record.get(key)
    return None


def _date(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    text = str(value or "").strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _index(options: list[str], value: Any, default: int = 0) -> int:
    return options.index(value) if value in options else default


def _planned_value(amount: float, start: datetime | None, end: datetime | None, as_of: datetime) -> float:
    if amount <= 0 or start is None or end is None or end <= start:
        return 0.0
    if as_of <= start:
        return 0.0
    if as_of >= end:
        return amount
    return amount * ((as_of - start).total_seconds() / (end - start).total_seconds())


def _earned_value(project_boq: list[dict[str, Any]], project_construction: list[dict[str, Any]], actual_cost: float) -> dict[str, Any]:
    """Calculate a transparent EVM snapshot from the existing project data spine.

    BAC comes from BOQ amounts. EV uses BOQ-linked construction activity value and
    physical progress. PV uses a linear time-phased baseline for activities with
    BOQ value plus planned start/finish dates. Actual Cost is explicitly sourced
    from Actual Cost records, never procurement commitments.
    """
    as_of = datetime.now(timezone.utc)
    bac = sum(_number(_value(item, "amount")) for item in project_boq)
    pv = 0.0
    ev = 0.0
    covered = 0

    boq_by_id = {str(_value(item, "id")): _number(_value(item, "amount")) for item in project_boq if _value(item, "id") is not None}
    boq_by_code = {str(_value(item, "item_code", "itemCode")): _number(_value(item, "amount")) for item in project_boq if _value(item, "item_code", "itemCode")}

    for activity in project_construction:
        boq_id = _value(activity, "boq_item_id", "boqItemId")
        activity_amount = boq_by_id.get(str(boq_id), 0.0) if boq_id is not None else 0.0
        if activity_amount <= 0:
            code = _value(activity, "boq_item_code", "boqItemCode", "item_code", "itemCode")
            activity_amount = boq_by_code.get(str(code), 0.0) if code else 0.0
        if activity_amount <= 0:
            continue
        progress = max(0.0, min(100.0, _number(_value(activity, "progress"))))
        ev += activity_amount * progress / 100.0
        start = _date(_value(activity, "planned_start", "plannedStart"))
        end = _date(_value(activity, "planned_end", "plannedEnd"))
        if start and end and end > start:
            pv += _planned_value(activity_amount, start, end, as_of)
            covered += 1

    cv = ev - actual_cost
    sv = ev - pv
    cpi = ev / actual_cost if actual_cost > 0 else None
    spi = ev / pv if pv > 0 else None
    eac = bac / cpi if cpi and cpi > 0 else bac
    etc = max(0.0, eac - actual_cost)
    vac = bac - eac
    physical = min(100.0, max(0.0, ev / bac * 100.0)) if bac > 0 else 0.0
    financial = min(100.0, max(0.0, actual_cost / bac * 100.0)) if bac > 0 else 0.0

    return {
        "bac": bac, "pv": pv, "ev": ev, "ac": actual_cost,
        "cv": cv, "sv": sv, "cpi": cpi, "spi": spi,
        "eac": eac, "etc": etc, "vac": vac,
        "physical": physical, "financial": financial,
        "covered": covered, "activities": len(project_construction),
        "as_of": as_of,
    }


def _performance_label(value: float | None) -> str:
    if value is None:
        return "No baseline"
    return "On target" if value >= 1.0 else "Needs attention"


def _render_evm(boq: list[dict[str, Any]], construction: list[dict[str, Any]], actual_cost: float) -> None:
    evm = _earned_value(boq, construction, actual_cost)
    st.divider()
    st.subheader("Earned Value Management")
    st.caption("Project Controls: BAC, PV, EV and AC connect the BOQ baseline, construction programme and recorded actual costs.")

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

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("EAC · Estimate at Completion", f"{evm['eac']:,.2f}")
    c2.metric("ETC · Estimate to Complete", f"{evm['etc']:,.2f}")
    c3.metric("Physical Progress", f"{evm['physical']:.1f}%")
    c4.metric("Financial Progress", f"{evm['financial']:.1f}%")

    st.progress(min(1.0, max(0.0, evm["physical"] / 100.0)), text=f"Physical progress {evm['physical']:.1f}%")
    st.caption(
        f"PV baseline coverage: {evm['covered']} of {evm['activities']} construction activities have both a BOQ value and planned start/finish dates. "
        "PV is linearly time-phased between those dates. Procurement commitments are not treated as actual cost."
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

    _render_evm(boq, construction, totals["Actual Cost"])

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
