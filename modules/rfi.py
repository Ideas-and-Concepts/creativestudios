import streamlit as st
from datetime import datetime
from .database import save_memory

def render_rfi_module(db):
    st.title("💬 RFI & Technical Query Tracker")
    st.caption("Track, assign, and resolve Requests for Information (RFIs) across architectural and engineering disciplines.")

    projects = db.get("projects", [])
    if not projects:
        st.warning("Please create a project first.")
        return

    project_options = {p["name"]: p["id"] for p in projects}
    selected_proj_name = st.selectbox("Select Project Workspace", list(project_options.keys()), key="rfi_proj_sel")
    selected_proj_id = project_options[selected_proj_name]

    tab1, tab2 = st.tabs(["📂 Active RFIs", "➕ Raise New RFI"])

    with tab1:
        rfis = [r for r in db.get("rfis", []) if r["project_id"] == selected_proj_id]

        status_filter = st.selectbox("Filter by Status", ["All Statuses", "Open", "In Review", "Resolved", "Closed"])
        if status_filter != "All Statuses":
            rfis = [r for r in rfis if r["status"] == status_filter]

        if not rfis:
            st.info("No RFIs recorded for this project under the selected filter.")
        else:
            for rfi in rfis:
                with st.expander(f"📌 [{rfi['priority']}] RFI-{rfi['id']}: {rfi['subject']} — Status: `{rfi['status']}`"):
                    c1, c2, c3 = st.columns(3)
                    c1.markdown(f"**Raised By:** {rfi['raised_by']}")
                    c2.markdown(f"**Assigned Discipline:** `{rfi['discipline']}`")
                    c3.markdown(f"**Date:** {rfi['created_at'][:10]}")

                    st.markdown(f"**Description / Query:** {rfi['description']}")
                    resolution_text = rfi.get('resolution', '') or '*Pending resolution...*'
                    st.markdown(f"**Resolution / Answer:** {resolution_text}")
                    st.markdown("---")

                    current_user = st.session_state.get("user", {})
                    with st.form(f"update_rfi_{rfi['id']}"):
                        valid_statuses = ["Open", "In Review", "Resolved", "Closed"]
                        current_status = rfi.get("status", "Open")
                        if current_status in valid_statuses:
                            default_idx = valid_statuses.index(current_status)
                        else:
                            default_idx = 0
                        new_status = st.selectbox("Update Status", valid_statuses, index=default_idx)
                        new_resolution = st.text_area("Add / Update Resolution Notes", value=rfi.get("resolution", ""))
                        update_btn = st.form_submit_button("Save RFI Update", use_container_width=True)

                        if update_btn:
                            rfi["status"] = new_status
                            rfi["resolution"] = new_resolution
                            rfi["updated_by"] = current_user.get("name", "Unknown User")
                            rfi["updated_at"] = datetime.now().isoformat()
                            save_memory(db)
                            st.success("RFI updated successfully!")
                            st.rerun()

    with tab2:
        st.subheader("Raise a Request for Information (RFI)")
        with st.form("new_rfi_form"):
            subject = st.text_input("RFI Subject (e.g., Clarification on Column Rebar Size at Grid Line B-4)")
            discipline = st.selectbox("Target Discipline for Answer", ["Architectural", "Structural Engineering", "Electrical Engineering", "Plumbing & Mechanical", "General Contractor"])
            priority = st.selectbox("Priority Level", ["Low", "Medium", "High", "Urgent"])
            description = st.text_area("Detailed Query / Specification Issue Description")

            submitted = st.form_submit_button("Submit RFI", use_container_width=True)
            if submitted:
                if not subject or not description:
                    st.error("Subject and description are required fields.")
                else:
                    current_user = st.session_state.get("user", {})
                    # Robust ID generation: find max existing ID + 1, start at 1 if none
                    existing_ids = [r["id"] for r in db.get("rfis", []) if isinstance(r.get("id"), int)]
                    new_id = max(existing_ids, default=0) + 1
                    new_rfi = {
                        "id": new_id,
                        "project_id": selected_proj_id,
                        "subject": subject,
                        "discipline": discipline,
                        "priority": priority,
                        "status": "Open",
                        "raised_by": current_user.get("name", "Unknown User"),
                        "created_at": datetime.now().isoformat(),
                        "description": description,
                        "resolution": ""
                    }
                    if "rfis" not in db:
                        db["rfis"] = []
                    db["rfis"].append(new_rfi)
                    save_memory(db)
                    st.success("RFI successfully raised and logged!")
                    st.rerun()