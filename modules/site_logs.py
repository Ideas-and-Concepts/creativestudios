"""Creative Studios Site Progress / Field Reporting module."""
from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd
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

INSPECTION_STATUSES = ["Not recorded", "Pending", "Passed", "Rejected"]


def _date(value: Any) -> date:
    if value:
        try:
            return date.fromisoformat(str(value)[:10])
        except ValueError:
            pass
    return date.today()


def _number(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _activity_label(activity: dict[str, Any]) -> str:
    code = str(activity.get("activity_code") or "Activity")
    name = str(activity.get("name") or "Construction Activity")
    return f"{code} · {name}"


def render_site_logs_module(database: dict[str, Any]) -> None:
    st.title("Site Progress Logs")
    st.caption("Daily field reporting linked directly to canonical construction activities in Neon PostgreSQL.")

    project_id, _ = project_selector(database, "site_progress_project")
    if project_id is None:
        return

    activities = project_records(ensure_collection(database, "construction"), project_id)
    logs = project_records(ensure_collection(database, "site_progress_logs"), project_id)

    activity_map = {str(activity.get("id")): activity for activity in activities if activity.get("id")}
    activity_options = list(activity_map)
    activity_labels = {activity_id: _activity_label(activity_map[activity_id]) for activity_id in activity_options}

    total_quantity = sum(_number(log.get("quantity_completed")) for log in logs)
    total_delay = sum(_number(log.get("delay_hours")) for log in logs)
    avg_workforce = sum(_number(log.get("workforce_count")) for log in logs) / len(logs) if logs else 0
    inspected = sum(str(log.get("inspection_status", "Not recorded")) == "Passed" for log in logs)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Daily Logs", len(logs))
    c2.metric("Quantity Completed", f"{total_quantity:,.2f}")
    c3.metric("Delay Hours", f"{total_delay:,.1f}")
    c4.metric("Inspections Passed", inspected)

    if logs:
        chart_rows = []
        for log in logs:
            chart_rows.append({
                "Date": str(log.get("log_date", ""))[:10],
                "Quantity": _number(log.get("quantity_completed")),
                "Delay Hours": _number(log.get("delay_hours")),
            })
        chart_df = pd.DataFrame(chart_rows)
        if not chart_df.empty:
            st.subheader("Field Reporting Trend")
            st.line_chart(chart_df.set_index("Date")[["Quantity", "Delay Hours"]], use_container_width=True)

    st.subheader("Daily Logs")
    if not logs:
        st.info("No site progress logs have been recorded for this project yet.")
    else:
        table = []
        for log in logs:
            activity = activity_map.get(str(log.get("activity_id")), {})
            table.append({
                "Date": str(log.get("log_date", ""))[:10],
                "Activity": _activity_label(activity) if activity else str(log.get("activity_id", "")),
                "Work": str(log.get("work_description", "")),
                "Qty": _number(log.get("quantity_completed")),
                "Unit": str(log.get("unit") or ""),
                "Workforce": int(_number(log.get("workforce_count"))),
                "Delay h": _number(log.get("delay_hours")),
                "Inspection": str(log.get("inspection_status") or "Not recorded"),
            })
        st.dataframe(pd.DataFrame(table), use_container_width=True, hide_index=True)

    for record in list(logs):
        rid = record.get("id")
        activity = activity_map.get(str(record.get("activity_id")), {})
        title = f"{str(record.get('log_date', ''))[:10]} · {_activity_label(activity)}"
        with st.expander(title):
            if not activity_options:
                st.warning("This project has no construction activities. Create an activity before editing a site log.")
                continue
            with st.form(f"site_log_edit_{rid}"):
                activity_id = st.selectbox(
                    "Construction Activity",
                    activity_options,
                    index=activity_options.index(str(record.get("activity_id"))) if str(record.get("activity_id")) in activity_options else 0,
                    format_func=lambda value: activity_labels[value],
                )
                log_date = st.date_input("Log Date", value=_date(record.get("log_date")))
                work_description = st.text_area("Work Description", value=str(record.get("work_description", "")))
                a, b, c = st.columns(3)
                quantity_completed = a.number_input("Quantity Completed", min_value=0.0, value=_number(record.get("quantity_completed")), step=0.001)
                unit = b.text_input("Unit", value=str(record.get("unit", "")))
                workforce_count = c.number_input("Workforce Count", min_value=0, value=int(_number(record.get("workforce_count"))), step=1)
                equipment = st.text_input("Equipment", value=str(record.get("equipment", "")))
                site_conditions = st.text_area("Site Conditions", value=str(record.get("site_conditions", "")))
                a, b = st.columns(2)
                delay_hours = a.number_input("Delay Hours", min_value=0.0, value=_number(record.get("delay_hours")), step=0.5)
                inspection_status = b.selectbox("Inspection Status", INSPECTION_STATUSES, index=INSPECTION_STATUSES.index(str(record.get("inspection_status"))) if str(record.get("inspection_status")) in INSPECTION_STATUSES else 0)
                delay_reason = st.text_input("Delay Reason", value=str(record.get("delay_reason", "")))
                notes = st.text_area("Notes", value=str(record.get("notes", "")))
                submitted = st.form_submit_button("Save Changes", use_container_width=True)

            if submitted:
                if not work_description.strip():
                    st.error("Work Description is required.")
                elif delay_hours > 0 and not delay_reason.strip():
                    st.error("Provide a Delay Reason when delay hours are greater than zero.")
                else:
                    try:
                        saved = save_updated_record(
                            database,
                            "site_progress_logs",
                            rid,
                            {
                                "project_id": project_id,
                                "activity_id": activity_id,
                                "log_date": log_date.isoformat(),
                                "work_description": work_description.strip(),
                                "quantity_completed": round(float(quantity_completed), 3),
                                "unit": unit.strip(),
                                "workforce_count": int(workforce_count),
                                "equipment": equipment.strip(),
                                "site_conditions": site_conditions.strip(),
                                "delay_hours": round(float(delay_hours), 2),
                                "delay_reason": delay_reason.strip(),
                                "inspection_status": inspection_status,
                                "notes": notes.strip(),
                                "updated_at": now_iso(),
                            },
                        )
                        if not saved:
                            st.error("The site progress log could not be found.")
                        else:
                            st.success("Site progress log updated.")
                            st.rerun()
                    except Exception as exc:
                        st.error("Unable to update the site progress log.")
                        with st.expander("Technical details"):
                            st.exception(exc)

            if st.button("Delete Log", key=f"site_log_delete_{rid}", use_container_width=True):
                try:
                    if remove_record(database, "site_progress_logs", rid):
                        st.success("Site progress log deleted.")
                        st.rerun()
                    else:
                        st.warning("The site progress log was already removed.")
                except Exception as exc:
                    st.error("Unable to delete the site progress log.")
                    with st.expander("Technical details"):
                        st.exception(exc)

    st.divider()
    st.subheader("Add Daily Site Progress")
    if not activity_options:
        st.info("No construction activities exist for this project. Add a Construction Activity first.")
        return

    with st.form("site_log_add", clear_on_submit=True):
        activity_id = st.selectbox("Construction Activity", activity_options, format_func=lambda value: activity_labels[value])
        log_date = st.date_input("Log Date", value=date.today())
        work_description = st.text_area("Work Description", placeholder="Describe the work completed on site today.")
        a, b, c = st.columns(3)
        quantity_completed = a.number_input("Quantity Completed", min_value=0.0, value=0.0, step=0.001)
        unit = b.text_input("Unit", placeholder="m³, m², t, nr")
        workforce_count = c.number_input("Workforce Count", min_value=0, value=0, step=1)
        equipment = st.text_input("Equipment", placeholder="Excavator, crane, mixer...")
        site_conditions = st.text_area("Site Conditions", placeholder="Weather, access, ground conditions, etc.")
        a, b = st.columns(2)
        delay_hours = a.number_input("Delay Hours", min_value=0.0, value=0.0, step=0.5)
        inspection_status = b.selectbox("Inspection Status", INSPECTION_STATUSES)
        delay_reason = st.text_input("Delay Reason")
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Add Site Progress Log", type="primary", use_container_width=True)

    if submitted:
        if not work_description.strip():
            st.error("Work Description is required.")
        elif delay_hours > 0 and not delay_reason.strip():
            st.error("Provide a Delay Reason when delay hours are greater than zero.")
        else:
            try:
                save_new_record(
                    database,
                    "site_progress_logs",
                    {
                        "project_id": project_id,
                        "activity_id": activity_id,
                        "log_date": log_date.isoformat(),
                        "work_description": work_description.strip(),
                        "quantity_completed": round(float(quantity_completed), 3),
                        "unit": unit.strip(),
                        "workforce_count": int(workforce_count),
                        "equipment": equipment.strip(),
                        "site_conditions": site_conditions.strip(),
                        "delay_hours": round(float(delay_hours), 2),
                        "delay_reason": delay_reason.strip(),
                        "inspection_status": inspection_status,
                        "notes": notes.strip(),
                        "created_at": now_iso(),
                        "updated_at": now_iso(),
                    },
                )
                st.success("Site progress log added.")
                st.rerun()
            except Exception as exc:
                st.error("Unable to add the site progress log.")
                with st.expander("Technical details"):
                    st.exception(exc)
