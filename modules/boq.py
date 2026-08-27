import streamlit as st
import pandas as pd
from typing import Any
from modules.database import save_memory

def render_boq_module(database: dict[str, Any]) -> None:
    st.header("Bill of Quantities")

    projects = database.get("projects", [])
    if not projects:
        st.info("No projects available.")
        return

    project_names = [p.get("name", "Unnamed Project") for p in projects]
    selected_project = st.selectbox("Select Project", project_names)
    project = next((p for p in projects if p.get("name") == selected_project), None)
    if not project:
        st.warning("Project not found.")
        return

    boq_items = project.get("boq", [])
    team = project.get("team", [])

    st.subheader("Line Items")
    if boq_items:
        for idx, item in enumerate(boq_items):
            st.write(
                f"**{item['description']}** "
                f"({item['quantity']} {item['unit']} @ ${item['unit_rate']:.2f}) "
                f"= ${item['total']:,.2f} → {item.get('responsible','Unassigned')}"
            )

            col1, col2 = st.columns([1,1])
            with col1:
                if st.button(f"Edit {idx}", key=f"edit_{idx}"):
                    with st.form(f"edit_form_{idx}", clear_on_submit=True):
                        description = st.text_input("Description", item["description"])
                        quantity = st.number_input("Quantity", value=item["quantity"])
                        unit = st.text_input("Unit", item["unit"])
                        unit_rate = st.number_input("Unit Rate ($)", value=item["unit_rate"])
                        responsible = st.selectbox(
                            "Responsible",
                            ["Unassigned"] + [m.get("name") for m in team],
                            index=(["Unassigned"] + [m.get("name") for m in team]).index(item.get("responsible","Unassigned"))
                        )
                        submitted = st.form_submit_button("Save Changes")
                        if submitted:
                            item.update({
                                "description": description,
                                "quantity": quantity,
                                "unit": unit,
                                "unit_rate": unit_rate,
                                "total": quantity * unit_rate,
                                "responsible": responsible,
                            })
                            save_memory(database)
                            st.success("Item updated!")

            with col2:
                if st.button(f"Delete {idx}", key=f"delete_{idx}"):
                    boq_items.pop(idx)
                    project["boq"] = boq_items
                    save_memory(database)
                    st.warning("Item deleted.")
    else:
        st.caption("No BOQ items yet.")