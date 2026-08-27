import streamlit as st
import pandas as pd
from typing import Any

def render_portfolio_dashboard(database: dict[str, Any]) -> None:
    """Render portfolio dashboard aggregating KPIs across all projects."""

    st.header("Portfolio Dashboard")

    projects = database.get("projects", [])
    if not projects:
        st.info("No projects available.")
        return

    # Collect KPIs
    data = []
    for project in projects:
        pname = project.get("name", "Unnamed Project")
        ptype = project.get("type", "Unknown")
        spaces = project.get("spaces", [])
        boq_items = project.get("boq", [])
        documents = project.get("documents", [])
        drawings = project.get("drawings", [])

        subtotal = sum(item.get("total", 0) for item in boq_items)
        grand_total = subtotal + project.get("overheads", 0) + project.get("contingency", 0)

        data.append({
            "Project": pname,
            "Type": ptype,
            "Spaces": len(spaces),
            "BOQ Items": len(boq_items),
            "Documents": len(documents),
            "Drawings": len(drawings),
            "Estimated Cost": grand_total
        })

    df = pd.DataFrame(data)

    # Filters
    st.subheader("Filters")
    type_filter = st.selectbox("Project Type", ["All"] + df["Type"].unique().tolist())
    filtered = df.copy()
    if type_filter != "All":
        filtered = filtered[filtered["Type"] == type_filter]

    st.subheader("Portfolio KPIs")
    st.dataframe(filtered)

    # Metrics
    st.metric("Total Projects", len(filtered))
    st.metric("Total Spaces", filtered["Spaces"].sum())
    st.metric("Total BOQ Items", filtered["BOQ Items"].sum())
    st.metric("Total Documents", filtered["Documents"].sum())
    st.metric("Total Drawings", filtered["Drawings"].sum())
    st.metric("Portfolio Estimated Cost", f"${filtered['Estimated Cost'].sum():,.2f}")

    # Charts
    st.subheader("Cost by Project")
    st.bar_chart(filtered.set_index("Project")["Estimated Cost"])

    st.subheader("Documents vs Drawings")
    st.bar_chart(filtered.set_index("Project")[["Documents", "Drawings"]])