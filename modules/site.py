import streamlit as st
import pandas as pd
from typing import Any
from modules.database import save_memory

# ============================================================
# SITE MODULE (RFIs + Logs + Approvals)
# ============================================================

def render_site_module(database: dict[str, Any]) -> None:
    """Render Site module combining RFIs, Site Logs, and Approvals."""

    st.header("Site Management")

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

    # Tabs for RFIs, Logs, Approvals
    tab_rfis, tab_logs, tab_approvals = st.tabs(["RFIs", "Site Logs", "Approvals"])

    # ---------------- RFIs ----------------
    with tab_rfis:
        rfis = project.get("rfis", [])
        st.subheader("Requests for Information")
        if rfis:
            st.dataframe(pd.DataFrame(rfis))
        else:
            st.caption("No RFIs yet.")

        with st.form("add_rfi", clear_on_submit=True):
            subject = st.text_input("Subject")
            description = st.text_area("Description")
            requested_by = st.text_input("Requested By")
            assigned_to = st.text_input("Assigned To")
            status = st.selectbox("Status", ["Open", "In Review", "Closed"])
            submitted = st.form_submit_button("Log RFI")

            if submitted and subject:
                new_rfi = {
                    "subject": subject,
                    "description": description,
                    "requested_by": requested_by,
                    "assigned_to": assigned_to,
                    "status": status
                }
                rfis.append(new_rfi)
                project["rfis"] = rfis
                save_memory(database)
                st.success(f"Logged RFI: {subject}")

    # ---------------- Site Logs ----------------
    with tab_logs:
        site_logs = project.get("site_logs", [])
        st.subheader("Daily Site Logs")
        if site_logs:
            st.dataframe(pd.DataFrame(site_logs))
        else:
            st.caption("No site logs yet.")

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

    # ---------------- Approvals ----------------
    with tab_approvals:
        approvals = project.get("pending_approvals", [])
        st.subheader("Pending Approvals")
        if approvals:
            for idx, req in enumerate(approvals):
                st.write(f"{req['type']} → {req['item']}")
                st.caption(f"{req['change']} (by {req['requested_by']}) — Status: {req['status']}")

                col1, col2 = st.columns([1, 1])
                if col1.button(f"Approve {idx}", key=f"approve_{project['id']}_{idx}"):
                    req["status"] = "Approved"
                    save_memory(database)
                    st.success(f"Approved request for {req['item']}")
                if col2.button(f"Reject {idx}", key=f"reject_{project['id']}_{idx}"):
                    req["status"] = "Rejected"
                    save_memory(database)
                    st.warning(f"Rejected request for {req['item']}")
        else:
            st.caption("No pending approvals.")