import streamlit as st
from utils import load_memory, save_memory, require_auth, safe_dataframe, get_project_name

st.set_page_config(page_title="BoQ Ledger", page_icon="🧱", layout="wide")
require_auth()

db = load_memory()

st.title("🧱 Bill of Quantities (BoQ)")

if not db.get("projects"):
    st.warning("Please create a project first.")
else:
    tab1, tab2 = st.tabs(["Project BoQ Ledger", "Add BoQ Line Item"])

    with tab1:
        proj_id = st.selectbox("Select Project", options=[p["id"] for p in db["projects"]], format_func=lambda x: f"{x} - {get_project_name(db, x)}")
        boq_items = [b for b in db.get("boq", []) if b.get("project_id") == proj_id]

        if boq_items:
            df_boq = safe_dataframe(boq_items, ["id", "category", "item", "quantity", "unit", "unit_cost", "total"])
            st.dataframe(df_boq, use_container_width=True)
            st.metric("Total Calculated Cost", f"${sum(b.get('total', 0) for b in boq_items):,.2f}")
        else:
            st.info("No items in BoQ for this project yet.")

    with tab2:
        with st.form("boq_form"):
            p_id = st.selectbox("Project Target", options=[p["id"] for p in db["projects"]], format_func=lambda x: f"{x} - {get_project_name(db, x)}")
            category = st.selectbox("Category", [
                "Mechanical (HVAC)", "Electrical & Wiring", "Plumbing & Fixtures",
                "Civil & Structural Materials", "Architectural Finishes", "General Labor"
            ])
            item = st.text_input("Item Description")
            quantity = st.number_input("Quantity", min_value=0.1, value=1.0)
            unit = st.text_input("Unit", value="Units")
            unit_cost = st.number_input("Unit Cost ($)", min_value=0.0, value=10.0)

            if st.form_submit_button("Add Entry") and item:
                boq_id = f"BOQ-{len(db['boq']) + 1:03d}"
                total = quantity * unit_cost
                db["boq"].append({
                    "id": boq_id, "project_id": p_id, "category": category,
                    "item": item, "quantity": quantity, "unit": unit,
                    "unit_cost": unit_cost, "total": total
                })
                save_memory(db)
                st.success(f"Added item with total ${total:,.2f}")
                st.rerun()
