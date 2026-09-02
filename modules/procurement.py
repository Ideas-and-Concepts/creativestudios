"""Creative Studios Procurement module for Streamlit Cloud."""
from __future__ import annotations

from datetime import datetime
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

STATUSES = ["Draft", "Requested", "Approved", "Ordered", "Partially Received", "Received", "Cancelled"]


def _amount(record: dict[str, Any]) -> float:
    try:
        return float(record.get("amount", 0) or 0)
    except (TypeError, ValueError):
        return 0.0


def _index(options: list[str], value: Any) -> int:
    return options.index(value) if value in options else 0


def render_procurement_module(database: dict[str, Any]) -> None:
    st.title("Procurement")
    st.caption("Suppliers, purchase requests and purchase orders linked to project delivery.")

    records = ensure_collection(database, "procurement")
    project_id, _ = project_selector(database, "procurement_project")
    if project_id is None:
        return

    items = project_records(records, project_id)
    committed = sum(_amount(r) for r in items if r.get("status") not in {"Draft", "Cancelled"})
    ordered = sum(_amount(r) for r in items if r.get("status") == "Ordered")
    received = sum(_amount(r) for r in items if r.get("status") == "Received")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Procurement Records", len(items))
    c2.metric("Committed Value", f"{committed:,.2f}")
    c3.metric("Ordered Value", f"{ordered:,.2f}")
    c4.metric("Received Value", f"{received:,.2f}")

    query = st.text_input("Search Procurement", placeholder="PO number, supplier or description").strip().lower()
    status_filter = st.selectbox("Status", ["All"] + STATUSES)
    visible = [
        r for r in items
        if (not query or query in str(r).lower())
        and (status_filter == "All" or r.get("status") == status_filter)
    ]

    st.subheader("Procurement Register")
    if not visible:
        st.info("No procurement records match the selected project and filters.")
    for record in list(visible):
        rid = record.get("id")
        title = record.get("po_number") or record.get("reference") or "Procurement Record"
        with st.expander(f"{title} | {record.get('supplier', 'Supplier not set')} | {_amount(record):,.2f}"):
            with st.form(f"procurement_edit_{rid}"):
                reference = st.text_input("PO / Request Number", value=str(record.get("po_number", record.get("reference", ""))))
                supplier = st.text_input("Supplier", value=str(record.get("supplier", "")))
                description = st.text_input("Description", value=str(record.get("description", "")))
                quantity = st.number_input("Quantity", min_value=0.0, value=float(record.get("quantity", 0) or 0))
                unit = st.text_input("Unit", value=str(record.get("unit", "No.")))
                unit_price = st.number_input("Unit Price", min_value=0.0, value=float(record.get("unit_price", 0) or 0))
                amount = quantity * unit_price
                st.caption(f"Calculated amount: {amount:,.2f}")
                status = st.selectbox("Status", STATUSES, index=_index(STATUSES, record.get("status")))
                expected_date = st.text_input("Expected Delivery", value=str(record.get("expected_delivery", "")), placeholder="YYYY-MM-DD")
                notes = st.text_area("Notes", value=str(record.get("notes", "")))
                submitted = st.form_submit_button("Save Changes", use_container_width=True)
            if submitted:
                if not reference.strip() or not description.strip():
                    st.error("PO / Request Number and Description are required.")
                else:
                    try:
                        saved = save_updated_record(database, "procurement", rid, {
                            "project_id": project_id,
                            "po_number": reference.strip(),
                            "supplier": supplier.strip(),
                            "description": description.strip(),
                            "quantity": quantity,
                            "unit": unit.strip() or "No.",
                            "unit_price": unit_price,
                            "amount": round(amount, 2),
                            "status": status,
                            "expected_delivery": expected_date.strip(),
                            "notes": notes.strip(),
                            "updated_at": now_iso(),
                        })
                        if not saved:
                            st.error("The procurement record could not be found.")
                        else:
                            st.success("Procurement record updated.")
                            st.rerun()
                    except Exception as exc:
                        st.error("Unable to update the procurement record.")
                        with st.expander("Technical details"):
                            st.exception(exc)
            if st.button("Delete Record", key=f"procurement_delete_{rid}", use_container_width=True):
                try:
                    if remove_record(database, "procurement", rid):
                        st.success("Procurement record deleted.")
                        st.rerun()
                    else:
                        st.warning("The procurement record was already removed.")
                except Exception as exc:
                    st.error("Unable to delete the procurement record.")
                    with st.expander("Technical details"):
                        st.exception(exc)

    st.divider()
    st.subheader("Add Procurement Record")
    with st.form("procurement_add", clear_on_submit=True):
        reference = st.text_input("PO / Request Number")
        supplier = st.text_input("Supplier")
        description = st.text_input("Description")
        quantity = st.number_input("Quantity", min_value=0.0, value=1.0)
        unit = st.text_input("Unit", value="No.")
        unit_price = st.number_input("Unit Price", min_value=0.0, value=0.0)
        status = st.selectbox("Status", STATUSES)
        expected_date = st.text_input("Expected Delivery", placeholder="YYYY-MM-DD")
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Add Procurement Record", use_container_width=True)

    if submitted:
        if not reference.strip() or not description.strip():
            st.error("PO / Request Number and Description are required.")
        else:
            try:
                save_new_record(database, "procurement", {
                    "project_id": project_id,
                    "po_number": reference.strip(),
                    "supplier": supplier.strip(),
                    "description": description.strip(),
                    "quantity": quantity,
                    "unit": unit.strip() or "No.",
                    "unit_price": unit_price,
                    "amount": round(quantity * unit_price, 2),
                    "status": status,
                    "expected_delivery": expected_date.strip(),
                    "notes": notes.strip(),
                    "created_at": now_iso(),
                    "updated_at": now_iso(),
                })
                st.success("Procurement record added.")
                st.rerun()
            except Exception as exc:
                st.error("Unable to add the procurement record.")
                with st.expander("Technical details"):
                    st.exception(exc)
