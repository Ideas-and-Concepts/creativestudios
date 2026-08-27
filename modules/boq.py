lfrom modules.database import save_memory

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
        st.dataframe(pd.DataFrame(boq_items))
    else:
        st.caption("No BOQ items yet.")

    with st.form("add_boq_item", clear_on_submit=True):
        description = st.text_input("Description")
        quantity = st.number_input("Quantity", min_value=0.0, step=1.0)
        unit = st.text_input("Unit")
        unit_rate = st.number_input("Unit Rate ($)", min_value=0.0, step=0.01)

        # New: assign responsibility
        team_names = [m.get("name") for m in team] if team else []
        responsible = st.selectbox("Responsible", ["Unassigned"] + team_names)

        submitted = st.form_submit_button("Add Item")

        if submitted and description and unit:
            total = quantity * unit_rate
            new_item = {
                "description": description,
                "quantity": quantity,
                "unit": unit,
                "unit_rate": unit_rate,
                "total": total,
                "responsible": responsible,
            }
            boq_items.append(new_item)
            project["boq"] = boq_items
            save_memory(database)
            st.success(f"Added item: {description} (${total:,.2f}) → {responsible}")