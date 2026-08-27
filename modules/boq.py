"""
Bill of Quantities (BOQ) Module
Manages itemized material takeoffs, line-item pricing, and total cost tracking.
"""

from __future__ import annotations
import streamlit as st


def render_boq_module(db: dict) -> None:
    st.markdown("## Bill of Quantities (BOQ)")
    st.caption("Itemized financial takeoffs, material specifications, and cost tracking.")

    if "boq" not in db:
        db["boq"] = []

    # Calculate Totals
    total_items = len(db["boq"])
    grand_total = sum(
        (item.get("quantity", 0) * item.get("unit_price", 0)) 
        for item in db["boq"]
    )

    c1, c2 = st.columns(2)
    c1.metric("Total Line Items", total_items)
    c2.metric("Estimated Grand Total", f"${grand_total:,.2f}")

    st.markdown("---")

    tab1, tab2 = st.tabs(["Quantity Takeoff Schedule", "Add BOQ Line Item"])

    with tab1:
        if not db["boq"]:
            st.info("No BOQ line items recorded yet.")
        else:
            category_filter = st.selectbox(
                "Filter Category",
                ["All"] + sorted(list({i.get("category", "General") for i in db["boq"]}))
            )

            filtered_boq = db["boq"]
            if category_filter != "All":
                filtered_boq = [i for i in filtered_boq if i.get("category") == category_filter]

            table_data = []
            for idx, item in enumerate(filtered_boq, 1):
                qty = float(item.get("quantity", 0))
                rate = float(item.get("unit_price", 0))
                total = qty * rate
                table_data.append({
                    "#": idx,
                    "Code": item.get("item_code", "-"),
                    "Description": item.get("description", "N/A"),
                    "Category": item.get("category", "General"),
                    "Qty": f"{qty:,.2f}",
                    "Unit": item.get("unit", "pcs"),
                    "Rate ($)": f"${rate:,.2f}",
                    "Total ($)": f"${total:,.2f}",
                })

            st.dataframe(table_data, use_container_width=True)

    with tab2:
        st.markdown("### Add New Line Item")
        with st.form("add_boq_item_form", clear_on_submit=True):
            b1, b2 = st.columns(2)
            item_code = b1.text_input("Item Code*", placeholder="e.g. CONC-001")
            category = b2.selectbox(
                "Category*",
                ["Substructure", "Superstructure", "Finishes", "MEP Services", "External Works", "General"]
            )

            description = st.text_input("Item Description*", placeholder="e.g. Ready-mix concrete C30/37")

            b3, b4, b5 = st.columns(3)
            quantity = b3.number_input("Quantity*", min_value=0.0, step=1.0)
            unit = b4.text_input("Unit*", placeholder="e.g. m³, kg, m²")
            unit_price = b5.number_input("Unit Rate ($)*", min_value=0.0, step=0.50)

            submitted = st.form_submit_button("Add Line Item", use_container_width=True)

            if submitted:
                if not item_code or not description or not unit:
                    st.error("Please fill in all required fields marked with *.")
                else:
                    new_boq = {
                        "id": len(db["boq"]) + 1,
                        "item_code": item_code.strip(),
                        "category": category,
                        "description": description.strip(),
                        "quantity": quantity,
                        "unit": unit.strip(),
                        "unit_price": unit_price,
                    }
                    db["boq"].append(new_boq)
                    st.success(f"Added BOQ item: {item_code}")
                    st.rerun()


# ============================================================