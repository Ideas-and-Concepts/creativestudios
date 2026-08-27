import streamlit as st
from typing import Any
from modules.database import save_memory

def render_team_module(database: dict[str, Any]) -> None:
    """Render Team module with BOQ assignments."""

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
    boq_items = project.get("boq", [])

    st.subheader("Team Members")
    if team:
        for member in team:
            name = member.get("name")
            role = member.get("role")

            # Find BOQ items assigned to this member
            assigned_items = [
                item for item in boq_items if item.get("responsible") == name
            ]

            st.markdown(f"**{name}** ({role})")
            if assigned_items:
                for item in assigned_items:
                    st.write(f"• {item['description']} (${item['total']:,.2f})")
            else:
                st.caption("No BOQ items assigned.")
            st.write("---")
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
            st.success(f"Added {name} as {role}")