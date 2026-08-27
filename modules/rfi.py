"""
RFI & Technical Queries Module
Tracks engineering clarifications, design adjustments, and site queries.
"""

from __future__ import annotations
import streamlit as st


def render_rfi_module(db: dict) -> None:
    st.markdown("## RFI & Technical Queries")
    st.caption("Submit, track, and resolve Request for Information (RFI) tickets across disciplines.")

    if "rfis" not in db:
        db["rfis"] = []

    # Summary Statistics
    total_rfis = len(db["rfis"])
    open_rfis = sum(1 for r in db["rfis"] if r.get("status") in ["Open", "Under Review"])
    closed_rfis = sum(1 for r in db["rfis"] if r.get("status") == "Closed")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total RFIs", total_rfis)
    col2.metric("Open / Under Review", open_rfis)
    col3.metric("Resolved / Closed", closed_rfis)

    st.markdown("---")

    tab1, tab2 = st.tabs(["Active RFI Log", "Submit New RFI"])

    with tab1:
        if not db["rfis"]:
            st.info("No RFI entries logged yet.")
        else:
            status_filter = st.selectbox("Filter Status", ["All", "Open", "Under Review", "Answered", "Closed"])
            
            rfis = db["rfis"]
            if status_filter != "All":
                rfis = [r for r in rfis if r.get("status") == status_filter]

            for rfi in rfis:
                badge_color = "🔴" if rfi.get("priority") == "High" else ("🟡" if rfi.get("priority") == "Medium" else "🟢")
                title_str = f"**{rfi.get('rfi_number', 'RFI-???')}**: {rfi.get('subject', 'No Subject')} {badge_color}"
                
                with st.expander(title_str):
                    rc1, rc2, rc3 = st.columns(3)
                    rc1.write(f"**Status:** {rfi.get('status', 'Open')}")
                    rc2.write(f"**Priority:** {rfi.get('priority', 'Normal')}")
                    rc3.write(f"**Assigned To:** {rfi.get('assigned_to', 'Unassigned')}")

                    st.markdown(f"**Question / Clarification:**\n{rfi.get('question', 'N/A')}")

                    if rfi.get("response"):
                        st.markdown("---")
                        st.markdown(f"**Official Response:**\n{rfi.get('response')}")
                    else:
                        st.caption("No official resolution response posted yet.")

    with tab2:
        st.markdown("### Raise a Request for Information")
        with st.form("submit_rfi_form", clear_on_submit=True):
            r1, r2 = st.columns(2)
            rfi_number = r1.text_input("RFI Number*", value=f"RFI-{len(db['rfis']) + 101:03d}")
            subject = r2.text_input("Subject / Query Title*", placeholder="e.g. Beam Rebar Conflict at Axis C-4")

            r3, r4 = st.columns(2)
            priority = r3.selectbox("Priority Level", ["Low", "Medium", "High", "Critical"])
            assigned_to = r4.selectbox(
                "Assign Discipline / Engineer*",
                ["Architectural Team", "Structural Engineer", "MEP Consultant", "Site Manager"]
            )

            question = st.text_area("Detailed Technical Description*", placeholder="Explain the field query or clarification required...")

            submitted = st.form_submit_button("Submit RFI Ticket", use_container_width=True)

            if submitted:
                if not subject or not question:
                    st.error("Please provide both a subject and question description.")
                else:
                    new_rfi = {
                        "id": len(db["rfis"]) + 1,
                        "rfi_number": rfi_number.strip(),
                        "subject": subject.strip(),
                        "priority": priority,
                        "assigned_to": assigned_to,
                        "question": question.strip(),
                        "status": "Open",
                        "response": "",
                        "raised_by": st.session_state.get("user", {}).get("full_name", "Admin")
                    }
                    db["rfis"].append(new_rfi)
                    st.success(f"Submitted {rfi_number} successfully!")
                    st.rerun()


# ============================================================