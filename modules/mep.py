import streamlit as st
import pandas as pd
from typing import Any
from modules.database import save_memory

# ============================================================
# MEP MODULE
# ============================================================

def render_mep_module(database: dict[str, Any]) -> None:
    """Render MEP module for mechanical, electrical, and plumbing details."""

    st.header("MEP (Mechanical, Electrical, Plumbing)")

    projects = database.get("projects", [])
    if not projects:
        st.info("No projects available.")
        return

    # Select project
    project_names = [p.get("name", "Unnamed Project") for p in projects]
    selected_project = st.selectbox("Select Project", project_names)

    project = next((p for p in projects if p.get("name") == selected_project), None)
    if not project:
        st.warning("Project not found.")
        return

    mep_items = project.get("mep", [])

    # Display MEP items
    st.subheader("MEP Items")
    if mep_items:
        df = pd.DataFrame(mep_items)
        st.dataframe(df)
    else:
        st.caption("No MEP items recorded yet.")

    # Add new MEP item form
    with st.form("add_mep_item", clear_on_submit=True):
        system_type = st.selectbox("System Type", ["Mechanical", "Electrical", "Plumbing"])
        description = st.text_input("Description")
        number = st.number_input("Number of Units", min_value=0, step=1)
        length = st.number_input("Length (m)", min_value=0.0, step=0.1)
        cost = st.number_input("Cost", min_value=0.0, step=0.01)
        submitted = st.form_submit_button("Add MEP Item")

        if submitted and description:
            new_item = {
                "system_type": system_type,
                "description": description,
                "number": number,
                "length": length,
                "cost": cost
            }
            mep_items.append(new_item)
            project["mep"] = mep_items
            save_memory(database)
            st.success(f"Added MEP item: {description} ({system_type})")

    # Update BOQ integration
    if mep_items:
        st.subheader("MEP BOQ Integration")
        total_cost = sum(item.get("cost", 0) for item in mep_items)
        st.metric("Total MEP Cost", f"${total_cost:,.2f}")