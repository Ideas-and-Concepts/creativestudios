import streamlit as st
import pandas as pd
from typing import Any
from modules.database import save_memory

# ============================================================
# RFIs MODULE
# ============================================================

def render_rfis_module(database: dict[str, Any]) -> None:
    """Render RFIs module for managing project queries."""

    st.header("Requests for Information (RFIs)")

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

    rfis = project.get("rfis", [])

    # Display RFIs
    st.subheader("Existing RFIs")
    if rfis:
        df = pd.DataFrame(rfis)
        st.dataframe(df)
    else:
        st.caption("No RFIs logged yet.")

    # Add new RFI form
    with st.form("add_rfi", clear_on_submit=True):
        subject = st.text_input("Subject")
        description = st.text_area("Description")
        requested_by = st.text_input("Requested By")
        assigned_to = st.text_input("Assigned To")
        status = st.selectbox("Status", ["Open", "In Review", "Closed"])
        submitted = st.form_submit_button("Log RFI")

        if submitted and subject and description:
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

    # Update RFI status
    if rfis:
        st.subheader("Update RFI Status")
        rfi_subjects = [r["subject"] for r in rfis]
        selected_rfi = st.selectbox("Select RFI", rfi_subjects)
        new_status = st.selectbox("New Status", ["Open", "In Review", "Closed"])
        if st.button("Update Status"):
            for r in rfis:
                if r["subject"] == selected_rfi:
                    r["status"] = new_status
                    save_memory(database)
                    st.success(f"Updated {selected_rfi} to {new_status}")