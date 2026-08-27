import streamlit as st
import pandas as pd
from typing import Any
from modules.database import save_memory

# ============================================================
# TEAM MODULE
# ============================================================

def render_team_module(database: dict[str, Any]) -> None:
    """Render Team module for managing project members and roles."""

    st.header("Project Team")

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

    team = project.get("team", [])

    # Display team members
    st.subheader("Team Members")
    if team:
        df = pd.DataFrame(team)
        st.dataframe(df)
    else:
        st.caption("No team members yet.")

    # Add new member form
    with st.form("add_team_member", clear_on_submit=True):
        name = st.text_input("Name")
        role = st.text_input("Role")
        submitted = st.form_submit_button("Add Member")

        if submitted and name and role:
            new_member = {"name": name, "role": role}
            team.append(new_member)
            project["team"] = team
            save_memory(database)
            st.success(f"Added team member: {name} ({role})")

    # Assign responsibilities
    st.subheader("Assign Responsibilities")
    boq_items = project.get("boq", [])
    if boq_items and team:
        item_names = [item.get("description", item.get("item", "Unnamed")) for item in boq_items]
        member_names = [m["name"] for m in team]

        selected_item = st.selectbox("Select BOQ Item", item_names)
        selected_member = st.selectbox("Assign to Member", member_names)
        if st.button("Assign Responsibility"):
            for item in boq_items:
                if item.get("description") == selected_item or item.get("item") == selected_item:
                    item["responsible"] = selected_member
                    save_memory(database)
                    st.success(f"Assigned {selected_item} to {selected_member}")
    else:
        st.caption("Add BOQ items and team members to assign responsibilities.")