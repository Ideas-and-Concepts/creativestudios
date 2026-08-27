import streamlit as st
import pandas as pd
from typing import Any

# ============================================================
# BOQ MODULE
# ============================================================

def render_boq_module(database: dict[str, Any]) -> None:
    """Render Bill of Quantities module for a single project."""

    st.header("Bill of Quantities")

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

    boq_items = project.get("boq", [])

    # Display line items
    st.subheader("Line Items")
    if boq_items:
        df = pd.DataFrame(boq_items)
        st.dataframe(df)
    else:
        st.caption("No BOQ items yet.")

    # Add new item form
    with st.form("add_boq_item", clear_on_submit=True):
        description = st.text_input("Description")
        quantity = st.number_input("Quantity", min_value=0.0, step=1.0)
        unit = st.text_input("Unit")
        unit_rate = st.number_input("Unit Rate ($)", min_value=0.0, step=0.01)
        submitted = st.form_submit_button("Add Item")

        if submitted and description and unit:
            total = quantity * unit_rate
            new_item = {
                "description": description,
                "quantity": quantity,
                "unit": unit,
                "unit_rate": unit_rate,
                "total": total,
            }
            boq_items.append(new_item)
            project["boq"] = boq_items
            st.success(f"Added item: {description} (${total:,.2f})")

    # Totals
    subtotal = sum(item["total"] for item in boq_items)
    overheads = project.get("overheads", 0)
    contingency = project.get("contingency", 0)
    grand_total = subtotal + overheads + contingency

    st.metric("Subtotal", f"${subtotal:,.2f}")
    st.metric("Overheads", f"${overheads:,.2f}")
    st.metric("Contingency", f"${contingency:,.2f}")
    st.metric("Grand Total", f"${grand_total:,.2f}")


# ============================================================
# BOQ DASHBOARD
# ============================================================

def render_boq_dashboard(database: dict[str, Any]) -> None:
    """Render multi-project BOQ dashboard with charts."""

    st.header("BOQ Dashboard")

    projects = database.get("projects", [])
    if not projects:
        st.info("No projects available.")
        return

    data = [
        {
            "Project": p.get("name", "Unnamed"),
            "Status": p.get("status", "unknown").capitalize(),
            "Estimated": p.get("grand_total", 0),
            "Actual": p.get("actual_total", 0),
        }
        for p in projects
    ]
    df = pd.DataFrame(data)

    # Status filter
    status_options = df["Status"].unique().tolist()
    selected_status = st.selectbox("Filter by Status", ["All"] + status_options)
    if selected_status != "All":
        df = df[df["Status"] == selected_status]

    # Portfolio metrics
    portfolio_total = df["Estimated"].sum()
    st.metric("Portfolio Estimated Total", f"${portfolio_total:,.2f}")

    # Charts
    st.subheader("Project Cost Comparison")
    st.bar_chart(df.set_index("Project")[["Estimated", "Actual"]])

    st.subheader("Portfolio Distribution")
    st.write(df.set_index("Project")["Estimated"].plot.pie(autopct="%1.1f%%"))


# ============================================================
# BOQ COMPARISON
# ============================================================

def render_boq_comparison(database: dict[str, Any]) -> None:
    """Render estimated vs actual cost comparison."""

    st.header("BOQ Cost Comparison")

    projects = database.get("projects", [])
    if not projects:
        st.info("No projects available.")
        return

    data = []
    for p in projects:
        name = p.get("name", "Unnamed")
        estimated = p.get("grand_total", 0)
        actual = p.get("actual_total", 0)
        variance = actual - estimated
        variance_pct = (variance / estimated * 100) if estimated else 0

        data.append({
            "Project": name,
            "Estimated": estimated,
            "Actual": actual,
            "Variance": variance,
            "Variance %": variance_pct,
        })

    df = pd.DataFrame(data)
    st.dataframe(df)

    st.subheader("Variance Chart")
    st.bar_chart(df.set_index("Project")[["Estimated", "Actual"]])