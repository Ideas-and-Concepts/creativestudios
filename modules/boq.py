"""Creative Studios - Bill of Quantities Module."""
from __future__ import annotations

from typing import Any

import streamlit as st

from modules.database import save_memory

CATEGORIES = ["Preliminaries", "Substructure", "Structural", "Walls", "Openings", "Roofing", "Architectural Finishes", "Civil Works", "Electrical", "Mechanical", "Plumbing", "External Works", "Other"]
ELEMENTS_BY_CATEGORY = {
    "Preliminaries": ["Site Establishment", "Mobilisation", "Demobilisation", "Setting Out", "Temporary Works", "Health and Safety", "Site Supervision", "Other"],
    "Substructure": ["Excavation", "Backfilling", "Blinding Concrete", "Pad Foundation", "Strip Foundation", "Raft Foundation", "Ground Beam", "Foundation Wall", "Damp Proof Membrane", "Other"],
    "Structural": ["Column", "Beam", "Slab", "Structural Wall", "Staircase", "Lintel", "Reinforcement", "Formwork", "Structural Concrete", "Other"],
    "Walls": ["External Wall", "Internal Wall", "Block Wall", "Brick Wall", "Partition Wall", "Retaining Wall", "Parapet Wall", "Other"],
    "Openings": ["Door", "Window", "Louver", "Glazed Screen", "Roller Shutter", "Fire Door", "Other"],
    "Roofing": ["Roof Structure", "Roof Covering", "Roof Truss", "Roof Sheet", "Roof Tile", "Gutter", "Downpipe", "Roof Insulation", "Other"],
    "Architectural Finishes": ["Plaster", "Rendering", "Screed", "Floor Tiling", "Wall Tiling", "Ceiling", "Painting", "Floor Finish", "Skirting", "Cladding", "Other"],
    "Civil Works": ["Road Works", "Drainage", "Kerbs", "Pavement", "Concrete Works", "Earthworks", "Stormwater Drain", "Manhole", "Other"],
    "Electrical": ["Lighting Point", "Socket Outlet", "Switch", "Distribution Board", "Cable", "Conduit", "Electrical Panel", "Earthing", "Generator Connection", "Other"],
    "Mechanical": ["Air Conditioning", "Ventilation", "Mechanical Equipment", "Ductwork", "Pump", "Fire Protection", "Other"],
    "Plumbing": ["Water Pipe", "Drainage Pipe", "Water Tank", "Pump", "Water Closet", "Wash Hand Basin", "Sink", "Shower", "Floor Drain", "Other"],
    "External Works": ["Paving", "Landscaping", "Boundary Wall", "Fence", "Gate", "External Drainage", "External Lighting", "Parking Area", "Other"],
    "Other": ["Construction Item", "Material", "Labour", "Equipment", "Other"],
}
UNITS = ["item", "m", "m²", "m³", "kg", "tonne", "No.", "set", "lot", "hour", "day"]
STATUSES = ["Draft", "Measured", "Priced", "Approved", "Issued"]


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(str(value).replace(",", "").replace(" ", "").strip())
    except (TypeError, ValueError):
        return default


def _text(value: Any, default: str = "") -> str:
    return default if value is None else str(value).strip()


def _normalize_records(database: dict[str, Any]) -> list[dict[str, Any]]:
    value = database.get("boq", [])
    if not isinstance(value, list):
        value = []
    defaults = {"item_number": "", "project": "", "category": "Other", "element": "Other", "description": "", "specification": "", "unit": "item", "quantity": 0.0, "rate": 0.0, "status": "Draft", "notes": ""}
    records: list[dict[str, Any]] = []
    for index, item in enumerate(value, 1):
        if isinstance(item, dict):
            record = {**defaults, **item}
            record["id"] = record.get("id") or index
            if not _text(record.get("item_number")):
                record["item_number"] = f"{index:03d}"
            record["quantity"] = _safe_float(record.get("quantity"))
            record["rate"] = _safe_float(record.get("rate"))
            records.append(record)
        elif isinstance(item, str):
            records.append({"id": index, **defaults, "item_number": f"{index:03d}", "description": item.strip(), "quantity": 1.0})
    database["boq"] = records
    return records


def _next_id(records: list[dict[str, Any]]) -> int:
    ids = []
    for r in records:
        try:
            ids.append(int(r.get("id", 0)))
        except (TypeError, ValueError):
            pass
    return max(ids, default=0) + 1


def _next_item_number(records: list[dict[str, Any]]) -> str:
    nums = []
    for r in records:
        try:
            nums.append(int(str(r.get("item_number", "")).strip()))
        except ValueError:
            pass
    return f"{max(nums, default=0) + 1:03d}"


def _amount(record: dict[str, Any]) -> float:
    return _safe_float(record.get("quantity")) * _safe_float(record.get("rate"))


def _save(database: dict[str, Any]) -> None:
    save_memory(database)
    st.session_state.database = database


def _index(options: list[str], value: Any, default: int = 0) -> int:
    value = _text(value)
    return options.index(value) if value in options else min(default, len(options) - 1)


def render_boq_module(database: dict[str, Any]) -> None:
    st.title("Bill of Quantities")
    st.caption("Measure, describe, price and manage construction work items.")
    records = _normalize_records(database)
    total_value = sum(_amount(r) for r in records)
    cols = st.columns(4)
    cols[0].metric("BOQ Items", len(records))
    cols[1].metric("Priced Items", sum(1 for r in records if _safe_float(r.get("rate")) > 0))
    cols[2].metric("Approved Items", sum(1 for r in records if _text(r.get("status")).lower() == "approved"))
    cols[3].metric("Total Value", f"{total_value:,.2f}")
    st.divider()

    tab_overview, tab_register, tab_add = st.tabs(["Overview", "BOQ Register", "Add Item"])
    with tab_overview:
        st.subheader("Construction Cost Summary")
        if not records:
            st.info("Add BOQ items to begin building the construction cost plan.")
        else:
            totals: dict[str, float] = {}
            counts: dict[str, int] = {}
            for r in records:
                category = _text(r.get("category"), "Other") or "Other"
                totals[category] = totals.get(category, 0.0) + _amount(r)
                counts[category] = counts.get(category, 0) + 1
            st.dataframe([{"Category": k, "Items": counts[k], "Value": totals[k]} for k in sorted(totals)], use_container_width=True, hide_index=True, column_config={"Value": st.column_config.NumberColumn("Value", format="%.2f")})

    with tab_register:
        st.subheader("BOQ Register")
        filters = st.columns(3)
        selected_category = filters[0].selectbox("Category", ["All Categories", *CATEGORIES])
        if selected_category == "All Categories":
            element_options = ["All Elements", *sorted({_text(r.get("element"), "Other") for r in records})]
        else:
            element_options = ["All Elements", *ELEMENTS_BY_CATEGORY.get(selected_category, ["Other"])]
        selected_element = filters[1].selectbox("Element", element_options)
        search = filters[2].text_input("Search", placeholder="Search BOQ...", key="boq_search")
        term = search.strip().lower()
        filtered = []
        for r in records:
            if selected_category != "All Categories" and r.get("category") != selected_category:
                continue
            if selected_element != "All Elements" and r.get("element") != selected_element:
                continue
            if term and term not in " ".join(_text(r.get(k)) for k in ("item_number", "project", "category", "element", "description", "specification")).lower():
                continue
            filtered.append(r)
        if filtered:
            st.dataframe([{"Item": r.get("item_number"), "Category": r.get("category"), "Element": r.get("element"), "Description": r.get("description"), "Unit": r.get("unit"), "Quantity": _safe_float(r.get("quantity")), "Rate": _safe_float(r.get("rate")), "Amount": _amount(r), "Status": r.get("status")} for r in filtered], use_container_width=True, hide_index=True, column_config={"Quantity": st.column_config.NumberColumn("Quantity", format="%.2f"), "Rate": st.column_config.NumberColumn("Rate", format="%.2f"), "Amount": st.column_config.NumberColumn("Amount", format="%.2f")})
        else:
            st.info("No BOQ items match the current filters.")
        st.divider()
        for index, record in enumerate(filtered):
            record_id = record.get("id", index + 1)
            with st.expander(f"{record.get('item_number', '')} — {_text(record.get('description'), 'BOQ Item')} ({_amount(record):,.2f})", expanded=False):
                with st.form(f"edit_boq_{record_id}"):
                    row = st.columns(2)
                    edited_project = row[0].text_input("Project", value=_text(record.get("project")))
                    edited_item_number = row[1].text_input("Item Number", value=_text(record.get("item_number")))
                    edited_category = st.selectbox("Category", CATEGORIES, index=_index(CATEGORIES, record.get("category"), len(CATEGORIES)-1))
                    elements = ELEMENTS_BY_CATEGORY.get(edited_category, ["Other"])
                    edited_element = st.selectbox("Construction Element", elements, index=_index(elements, record.get("element"), len(elements)-1))
                    edited_description = st.text_input("Description", value=_text(record.get("description")))
                    edited_specification = st.text_area("Specification", value=_text(record.get("specification")))
                    qrow = st.columns(3)
                    edited_unit = qrow[0].selectbox("Unit", UNITS, index=_index(UNITS, record.get("unit")))
                    edited_quantity = qrow[1].number_input("Quantity", min_value=0.0, value=_safe_float(record.get("quantity")), step=0.01)
                    edited_rate = qrow[2].number_input("Rate", min_value=0.0, value=_safe_float(record.get("rate")), step=0.01)
                    st.metric("Calculated Amount", f"{edited_quantity * edited_rate:,.2f}")
                    edited_status = st.selectbox("Status", STATUSES, index=_index(STATUSES, record.get("status")))
                    edited_notes = st.text_area("Notes", value=_text(record.get("notes")))
                    submitted = st.form_submit_button("Save Changes", use_container_width=True)
                if submitted:
                    if not edited_item_number.strip():
                        st.error("Item number is required.")
                    elif not edited_description.strip():
                        st.error("Description is required.")
                    else:
                        record.update(project=edited_project.strip(), item_number=edited_item_number.strip(), category=edited_category, element=edited_element, description=edited_description.strip(), specification=edited_specification.strip(), unit=edited_unit, quantity=edited_quantity, rate=edited_rate, status=edited_status, notes=edited_notes.strip())
                        _save(database)
                        st.success("BOQ item updated successfully.")
                        st.rerun()
                if st.button("Delete BOQ Item", key=f"delete_boq_{record_id}", use_container_width=True):
                    records[:] = [item for item in records if item is not record]
                    _save(database)
                    st.success("BOQ item deleted successfully.")
                    st.rerun()

    with tab_add:
        st.subheader("Add Construction Item")
        with st.form("add_boq_item_form", clear_on_submit=True):
            project = st.text_input("Project")
            category = st.selectbox("Category", CATEGORIES)
            element = st.selectbox("Construction Element", ELEMENTS_BY_CATEGORY.get(category, ["Other"]))
            description = st.text_input("Description", placeholder="Example: Reinforced concrete column")
            specification = st.text_area("Specification")
            row = st.columns(3)
            unit = row[0].selectbox("Unit", UNITS)
            quantity = row[1].number_input("Quantity", min_value=0.0, value=0.0, step=0.01)
            rate = row[2].number_input("Rate", min_value=0.0, value=0.0, step=0.01)
            status = st.selectbox("Status", STATUSES)
            notes = st.text_area("Notes")
            submitted = st.form_submit_button("Add BOQ Item", use_container_width=True)
        if submitted:
            if not description.strip():
                st.error("Description is required.")
            else:
                records.append({"id": _next_id(records), "item_number": _next_item_number(records), "project": project.strip(), "category": category, "element": element, "description": description.strip(), "specification": specification.strip(), "unit": unit, "quantity": quantity, "rate": rate, "status": status, "notes": notes.strip()})
                _save(database)
                st.success("BOQ item added successfully.")
                st.rerun()