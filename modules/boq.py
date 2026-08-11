import streamlit as st
from .database import save_memory

def render_boq_module(db):
    st.title("Bill of Quantities & Cost Estimation")
    st.caption("Manage material quantities, unit costs, and project financial estimates.")

    projects = db.get("projects", [])
    if not projects:
        st.warning("Please create a project first.")
        return

    project_options = {p["name"]: p["id"] for p in projects}
    selected_proj_name = st.selectbox("Select Project Workspace", list(project_options.keys()), key="boq_proj_sel")
    selected_proj_id = project_options[selected_proj_name]

    tab1, tab2 = st.tabs(["Material Breakdown (BOQ)", "Add BOQ Item"])

    with tab1:
        boq_items = [b for b in db.get("boq", []) if b["project_id"] == selected_proj_id]
        if not boq_items:
            st.info("No bill of quantities items recorded for this project yet.")
        else:
            total_cost = 0
            for item in boq_items:
                item_total = item["quantity"] * item["unit_cost"]
                total_cost += item_total
                with st.expander(f"[{item['category']}] {item['item_name']} — Total: ${item_total:,.2f}"):
                    c1, c2, c3 = st.columns(3)
                    c1.markdown(f"**Quantity:** `{item['quantity']} {item['unit']}`")
                    c2.markdown(f"**Unit Cost:** `${item['unit_cost']:,.2f}`")
                    c3.markdown(f"**Calculated Total:** `${item_total:,.2f}`")

            st.markdown("---")
            st.markdown(f"### **Total Estimated BOQ Cost:** `${total_cost:,.2f}`")

    with tab2:
        st.subheader("Add Material / Work Item to BOQ")
        with st.form("new_boq_form"):
            category = st.selectbox("Category", ["Architectural Finishes", "Structural Concrete & Steel", "Electrical Systems", "Plumbing & Drainage", "HVAC & Mechanical"])
            item_name = st.text_input("Item Description (e.g., PEX Water Supply Piping)")
            quantity = st.number_input("Quantity", min_value=1.0, value=100.0, step=10.0)
            unit = st.text_input("Unit of Measurement (e.g., Meters, Units, Sq. Meters)", value="Meters")
            unit_cost = st.number_input("Unit Cost ($)", min_value=0.01, value=25.50, step=1.0)

            submitted = st.form_submit_button("Add BOQ Item", use_container_width=True)
            if submitted:
                if not item_name:
                    st.error("Item description is required.")
                else:
                    new_item = {
                        "id": f"BOQ-{len(db.get('boq', [])) + 1}",
                        "project_id": selected_proj_id,
                        "category": category,
                        "item_name": item_name,
                        "quantity": quantity,
                        "unit": unit,
                        "unit_cost": unit_cost
                    }
                    if "boq" not in db:
                        db["boq"] = []
                    db["boq"].append(new_item)
                    save_memory(db)
                    st.success("BOQ item added successfully!")
                    st.rerun()

