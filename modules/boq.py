"""Creative Studios Bill of Quantities Module."""
from __future__ import annotations
from datetime import datetime
from typing import Any
import streamlit as st
from modules.database import next_id, save_memory
from modules.project_context import filter_project_records, project_label, project_options

CATEGORIES = ["Preliminaries", "Earthworks", "Foundations", "Concrete", "Reinforcement", "Formwork", "Columns", "Beams", "Slabs", "Masonry", "Walls", "Doors", "Windows", "Roofing", "Finishes", "Civil Works", "Plumbing", "Electrical", "Mechanical", "External Works", "Other"]
UNITS = ["item", "m", "m2", "m3", "kg", "ton", "No.", "set", "lot"]


def _normalize(database: dict[str, Any]) -> list[dict[str, Any]]:
    raw = database.get("boq", []); records: list[dict[str, Any]] = []
    if not isinstance(raw, list): raw = []
    for index, item in enumerate(raw, 1):
        if isinstance(item, dict):
            r = dict(item); r.setdefault("id", index); r.setdefault("project_id", None); records.append(r)
    database["boq"] = records
    return records


def _num(value: Any) -> float:
    try: return float(value or 0)
    except (TypeError, ValueError): return 0.0


def render_boq_module(database: dict[str, Any]) -> None:
    st.title("Bill of Quantities")
    st.caption("Project-linked quantities, construction elements and cost planning.")
    records = _normalize(database)
    projects = project_options(database)
    if not projects:
        st.warning("Create a project first in Projects."); return
    labels = [project_label(p) for p in projects]
    selected = st.selectbox("Project", labels, key="boq_project")
    project_id = int(projects[labels.index(selected)]["id"])
    project_records = filter_project_records(records, project_id)
    total = sum(_num(r.get("quantity")) * _num(r.get("rate")) for r in project_records)
    c1, c2, c3 = st.columns(3)
    c1.metric("BOQ Items", len(project_records)); c2.metric("Total Quantity", f"{sum(_num(r.get('quantity')) for r in project_records):,.2f}"); c3.metric("Estimated Amount", f"{total:,.2f}")

    st.subheader("BOQ Register")
    search = st.text_input("Search BOQ").strip().lower()
    visible = [r for r in project_records if not search or search in str(r).lower()]
    for record in list(visible):
        rid = record.get("id")
        with st.expander(f"{record.get('item_code', '')} | {record.get('description', 'BOQ Item')} | {record.get('category', 'Other')}"):
            with st.form(f"boq_edit_{rid}"):
                code = st.text_input("Item Code", value=str(record.get("item_code", "")))
                description = st.text_input("Description", value=str(record.get("description", "")))
                category = st.selectbox("Construction Element", CATEGORIES, index=CATEGORIES.index(record.get("category", "Other")) if record.get("category", "Other") in CATEGORIES else len(CATEGORIES)-1)
                unit = st.selectbox("Unit", UNITS, index=UNITS.index(record.get("unit", "item")) if record.get("unit", "item") in UNITS else 0)
                quantity = st.number_input("Quantity", min_value=0.0, value=_num(record.get("quantity")))
                rate = st.number_input("Rate", min_value=0.0, value=_num(record.get("rate")))
                source = st.text_input("Design / Drawing Reference", value=str(record.get("source_reference", "")))
                notes = st.text_area("Notes", value=str(record.get("notes", "")))
                save = st.form_submit_button("Save Changes", use_container_width=True)
            if save:
                if not description.strip(): st.error("Description is required.")
                else:
                    record.update({"item_code": code.strip(), "description": description.strip(), "category": category, "unit": unit, "quantity": quantity, "rate": rate, "amount": quantity * rate, "source_reference": source.strip(), "notes": notes.strip(), "updated_at": datetime.now().isoformat(timespec="seconds")})
                    save_memory(database); st.success("BOQ item updated."); st.rerun()
            if st.button("Delete Item", key=f"boq_delete_{rid}", use_container_width=True):
                records.remove(record); save_memory(database); st.rerun()

    st.divider()
    with st.form("boq_add", clear_on_submit=True):
        code = st.text_input("Item Code")
        description = st.text_input("Description")
        category = st.selectbox("Construction Element", CATEGORIES)
        unit = st.selectbox("Unit", UNITS)
        quantity = st.number_input("Quantity", min_value=0.0, value=1.0)
        rate = st.number_input("Rate", min_value=0.0, value=0.0)
        source = st.text_input("Design / Drawing Reference")
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Add BOQ Item", use_container_width=True)
    if submitted:
        if not description.strip(): st.error("Description is required.")
        else:
            records.append({"id": next_id("boq", database), "project_id": project_id, "item_code": code.strip(), "description": description.strip(), "category": category, "unit": unit, "quantity": quantity, "rate": rate, "amount": quantity * rate, "source_reference": source.strip(), "notes": notes.strip(), "created_at": datetime.now().isoformat(timespec="seconds")})
            save_memory(database); st.success("BOQ item added."); st.rerun()
