import streamlit as st
import pandas as pd
from typing import Any
from modules.database import save_memory

# ============================================================
# SITE LOGS MODULE
# ============================================================

def render_site_logs_module(database: dict[str, Any]) -> None:
    """Render Site Logs module for recording daily site activities."""

    st.header("Site Logs")

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

    site_logs = project.get("site_logs", [])

    # Display logs
    st.subheader("Existing Logs")
    if site_logs:
        df = pd.DataFrame(site_logs)
        st.dataframe(df)
    else:
        st.caption("No site logs recorded yet.")

    # Add new log form
    with st.form("add_site_log", clear_on_submit=True):
        date = st.date_input("Date")
        activity = st.text_area("Activity / Progress")
        issues = st.text_area("Issues / Observations")
        recorded_by = st.text_input("Recorded By")
        submitted = st.form_submit_button("Add Log")

        if submitted and activity:
            new_log = {
                "date": str(date),
                "activity": activity,
                "issues": issues,
                "recorded_by": recorded_by
            }
            site_logs.append(new_log)
            project["site_logs"] = site_logs
            save_memory(database)
            st.success(f"Added site log for {date}")

    # Filter logs by date
    if site_logs:
        st.subheader("Filter Logs")
        unique_dates = sorted({log["date"] for log in site_logs})
        selected_date = st.selectbox("Select Date", ["All"] + unique_dates)
        if selected_date != "All":
            filtered = [log for log in site_logs if log["date"] == selected_date]
            st.write(pd.DataFrame(filtered))