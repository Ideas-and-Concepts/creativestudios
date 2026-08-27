import streamlit as st
from typing import Any

def render_boq_module(database: dict[str, Any]) -> None:
    st.header("Bill of Quantities")

    project = database.get("projects", [])[0]  # Example: first project
    boq_items = project.get("boq", [])

    st.subheader("Line Items")
    for item in boq_items:
        st.write(
            f"{item['description']} - {item['quantity']} {item['unit']} "
            f"@ ${item['unit_rate']:.2f} = ${item['total']:.2f}"
        )

    subtotal = sum(item["total"] for item in boq_items)
    overheads = project.get("overheads", 0)
    contingency = project.get("contingency", 0)
    grand_total = subtotal + overheads + contingency

    st.metric("Subtotal", f"${subtotal:,.2f}")
    st.metric("Overheads", f"${overheads:,.2f}")
    st.metric("Contingency", f"${contingency:,.2f}")
    st.metric("Grand Total", f"${grand_total:,.2f}")

    if st.button("Add Item"):
        st.info("Form for adding new BOQ line item goes here.")