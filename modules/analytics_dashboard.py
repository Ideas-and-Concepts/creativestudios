import streamlit as st
import pandas as pd
from typing import Any

def render_analytics_dashboard(database: dict[str, Any]) -> None:
    """Render analytics dashboard with portfolio trends and workload distribution."""

    st.header("Analytics Dashboard")

    projects = database.get("projects", [])
    if not projects:
        st.info("No projects available.")
        return

    # Collect data
    records = []
    for project in projects:
        pname = project.get("name", "Unnamed Project")
        spaces = project.get("spaces", [])
        boq_items = project.get("boq", [])
        team = project.get("team", [])

        subtotal = sum(item.get("total", 0) for item in boq_items)
        grand_total = subtotal + project.get("overheads", 0) + project.get("contingency", 0)

        records.append({
            "Project": pname,
            "Spaces": len(spaces),
            "BOQ Items": len(boq_items),
            "Team Members": len(team),
            "Estimated Cost": grand_total
        })

    df = pd.DataFrame(records)

    # Portfolio trends
    st.subheader("Portfolio Trends")
    st.line_chart(df.set_index("Project")[["Estimated Cost"]])

    # Workload distribution
    st.subheader("Workload Distribution")
    workload = []
    for project in projects:
        pname = project.get("name", "Unnamed Project")
        for member in project.get("team", []):
            assigned = sum(1 for item in project.get("boq", []) if item.get("responsible") == member["name"])
            workload.append({"Project": pname, "Member": member["name"], "Assigned Items": assigned})
    if workload:
        wdf = pd.DataFrame(workload)
        st.bar_chart(wdf.set_index("Member")["Assigned Items"])
    else:
        st.caption("No workload data yet.")