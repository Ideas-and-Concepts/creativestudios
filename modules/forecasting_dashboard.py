import streamlit as st
import pandas as pd
from typing import Any
import math

def render_forecasting_dashboard(database: dict[str, Any]) -> None:
    """Render forecasting dashboard with cost escalation, risk analysis, and completion estimates."""

    st.header("Forecasting Dashboard")

    projects = database.get("projects", [])
    if not projects:
        st.info("No projects available.")
        return

    records = []
    for project in projects:
        pname = project.get("name", "Unnamed Project")
        estimated = project.get("grand_total", 0)
        actual = project.get("actual_total", 0)
        status = project.get("status", "Unknown")

        # Forecast escalation (e.g., 5% per quarter)
        escalation_rate = 0.05
        forecast_cost = estimated * (1 + escalation_rate)

        # Risk analysis (simple variance check)
        variance = actual - estimated
        risk_level = "Low"
        if variance > 0.2 * estimated:
            risk_level = "High"
        elif variance > 0.1 * estimated:
            risk_level = "Medium"

        # Completion estimate (dummy % based on actual vs estimated)
        completion_pct = min(100, math.floor((actual / estimated * 100))) if estimated else 0

        records.append({
            "Project": pname,
            "Status": status,
            "Estimated": estimated,
            "Actual": actual,
            "Forecast Cost": forecast_cost,
            "Risk Level": risk_level,
            "Completion %": completion_pct
        })

    df = pd.DataFrame(records)
    st.dataframe(df)

    # Charts
    st.subheader("Forecasted Costs")
    st.bar_chart(df.set_index("Project")[["Estimated", "Forecast Cost"]])

    st.subheader("Completion Estimates")
    st.bar_chart(df.set_index("Project")[["Completion %"]])