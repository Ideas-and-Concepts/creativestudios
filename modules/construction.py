"""Creative Studios Construction Management Module."""
from __future__ import annotations

from datetime import date
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

STATUSES = ["planned", "in_progress", "completed", "on_hold"]
STATUS_LABELS = {
    "planned": "Planned",
    "in_progress": "In Progress",
    "completed": "Completed",
    "on_hold": "On Hold",
}


def _index(options: list[str], value: Any, default: int = 0) -> int:
    return options.index(value) if value in options else default


def _date(value: Any) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def _status_label(value: Any) -> str:
    return STATUS_LABELS.get(str(value), str(value or "Planned").replace("_", " ").title())


def render_construction_module(database: dict[str, Any]) -> None:
    st.title("Construction")
    st.caption("Execute project work against BOQ items using the canonical construction activity register.")

    records = ensure_collection(database, "construction")
    project_id, _ = project_selector(database, "construction_project")
    if project_id is None:
        return

    items = project_records(records, project_id)
    boq = project_records(ensure_collection(database, "boq"), project_id)
    boq_labels = ["None"] + [
        " · ".join(str(item.get(key, "")) for key in ("item_code", "description") if item.get(key))
        for item in boq
    ]
    boq_map = {boq_labels[index + 1]: str(item.get("id")) for index, item in enumerate(boq)}

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Activities", len(items))
    c2.metric("In Progress", sum(r.get("status") == "in_progress" for r in items))
    c3.metric("Completed", sum(r.get("status") == "completed" for r in items))
    avg_progress = sum(float(r.get("progress", 0) or 0) for r in items) / len(items) if items else 0
    c4.metric("Average Progress", f"{avg_progress:.1f}%")

    for record in list(items):
        rid = record.get("id")
        title = f"{record.get('activity_code', 'Activity')} · {record.get('name', 'Construction Activity')} · {_status_label(record.get('status'))}"
        with st.expander(title):
            with st.form(f"construction_edit_{rid}"):
                a, b = st.columns(2)
                activity_code = a.text_input("Activity Code", value=str(record.get("activity_code", "")))
                name = b.text_input("Activity Name", value=str(record.get("name", "")))
                a, b, c = st.columns(3)
                discipline = a.text_input("Discipline", value=str(record.get("discipline", "")))
                contractor = b.text_input("Contractor", value=str(record.get("contractor", "")))
                status = c.selectbox("Status", STATUSES, index=_index(STATUSES, record.get("status")))
                a, b, c = st.columns(3)
                progress = a.number_input("Progress %", min_value=0, max_value=100, value=int(float(record.get("progress", 0) or 0)))
                planned_quantity = b.number_input("Planned Quantity", min_value=0.0, value=float(record.get("planned_quantity", 0) or 0), step=1.0)
                actual_quantity = c.number_input("Actual Quantity", min_value=0.0, value=float(record.get("actual_quantity", 0) or 0), step=1.0)
                unit = st.text_input("Unit", value=str(record.get("unit", "")))
                boq_label = next((label for label, value in boq_map.items() if value == str(record.get("boq_item_id"))), "None")
                boq_item = st.selectbox("BOQ Item", boq_labels, index=_index(boq_labels, boq_label))
                a, b = st.columns(2)
                planned_start = a.date_input("Planned Start", value=_date(record.get("planned_start")) or date.today())
                planned_end = b.date_input("Planned End", value=_date(record.get("planned_end")) or date.today())
                a, b = st.columns(2)
                actual_start = a.date_input("Actual Start", value=_date(record.get("actual_start")))
                actual_end = b.date_input("Actual End", value=_date(record.get("actual_end")))
                notes = st.text_area("Notes", value=str(record.get("notes", "")))
                submitted = st.form_submit_button("Save Changes", use_container_width=True)

            if submitted:
                if not activity_code.strip() or not name.strip():
                    st.error("Activity Code and Activity Name are required.")
                elif planned_end < planned_start:
                    st.error("Planned End cannot be earlier than Planned Start.")
                else:
                    try:
                        saved = save_updated_record(
                            database,
                            "construction",
                            rid,
                            {
                                "project_id": project_id,
                                "boq_item_id": boq_map.get(boq_item),
                                "activity_code": activity_code.strip(),
                                "name": name.strip(),
                                "discipline": discipline.strip(),
                                "contractor": contractor.strip(),
                                "status": status,
                                "progress": int(progress),
                                "planned_quantity": round(float(planned_quantity), 3),
                                "actual_quantity": round(float(actual_quantity), 3),
                                "unit": unit.strip(),
                                "planned_start": planned_start.isoformat(),
                                "planned_end": planned_end.isoformat(),
                                "actual_start": actual_start.isoformat() if actual_start else None,
                                "actual_end": actual_end.isoformat() if actual_end else None,
                                "notes": notes.strip(),
                                "updated_at": now_iso(),
                            },
                        )
                        if not saved:
                            st.error("The construction activity could not be found.")
                        else:
                            st.success("Construction activity updated.")
                            st.rerun()
                    except Exception as exc:
                        st.error("Unable to update the construction activity.")
                        with st.expander("Technical details"):
                            st.exception(exc)

            if st.button("Delete Activity", key=f"construction_delete_{rid}", use_container_width=True):
                try:
                    if remove_record(database, "construction", rid):
                        st.success("Construction activity deleted.")
                        st.rerun()
                    else:
                        st.warning("The construction activity was already removed.")
                except Exception as exc:
                    st.error("Unable to delete the construction activity.")
                    with st.expander("Technical details"):
                        st.exception(exc)

    st.divider()
    st.subheader("Add Construction Activity")
    with st.form("construction_add", clear_on_submit=True):
        a, b = st.columns(2)
        activity_code = a.text_input("Activity Code", placeholder="CON-001")
        name = b.text_input("Activity Name", placeholder="Foundation excavation")
        a, b, c = st.columns(3)
        discipline = a.text_input("Discipline", placeholder="Civil")
        contractor = b.text_input("Contractor")
        status = c.selectbox("Status", STATUSES, format_func=_status_label)
        a, b, c = st.columns(3)
        progress = a.number_input("Progress %", min_value=0, max_value=100, value=0)
        planned_quantity = b.number_input("Planned Quantity", min_value=0.0, value=0.0, step=1.0)
        actual_quantity = c.number_input("Actual Quantity", min_value=0.0, value=0.0, step=1.0)
        unit = st.text_input("Unit")
        boq_item = st.selectbox("BOQ Item", boq_labels)
        a, b = st.columns(2)
        planned_start = a.date_input("Planned Start", value=date.today())
        planned_end = b.date_input("Planned End", value=date.today())
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Add Construction Activity", use_container_width=True)

    if submitted:
        if not activity_code.strip() or not name.strip():
            st.error("Activity Code and Activity Name are required.")
        elif planned_end < planned_start:
            st.error("Planned End cannot be earlier than Planned Start.")
        else:
            try:
                save_new_record(
                    database,
                    "construction",
                    {
                        "project_id": project_id,
                        "boq_item_id": boq_map.get(boq_item),
                        "activity_code": activity_code.strip(),
                        "name": name.strip(),
                        "discipline": discipline.strip(),
                        "contractor": contractor.strip(),
                        "status": status,
                        "progress": int(progress),
                        "planned_quantity": round(float(planned_quantity), 3),
                        "actual_quantity": round(float(actual_quantity), 3),
                        "unit": unit.strip(),
                        "planned_start": planned_start.isoformat(),
                        "planned_end": planned_end.isoformat(),
                        "notes": notes.strip(),
                        "created_at": now_iso(),
                        "updated_at": now_iso(),
                    },
                )
                st.success("Construction activity added.")
                st.rerun()
            except Exception as exc:
                st.error("Unable to add the construction activity.")
                with st.expander("Technical details"):
                    st.exception(exc)
