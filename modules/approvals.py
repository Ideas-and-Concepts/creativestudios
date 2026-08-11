import streamlit as st
from datetime import datetime
from .database import save_memory

def render_approvals_module(db):
    st.title("✍️ Cross-Disciplinary Sign-Off & Approvals")
    st.caption("Review, track, and validate project milestones across architectural and engineering leads.")

    projects = db.get("projects", [])
    if not projects:
        st.warning("No projects available for review.")
        return

    project_options = {p["name"]: p["id"] for p in projects}
    selected_proj_name = st.selectbox("Select Project for Review", list(project_options.keys()), key="app_proj_sel")
    selected_proj_id = project_options[selected_proj_name]

    tab1, tab2 = st.tabs(["📋 Review Workflows", "➕ Initialize Approval Request"])

    with tab1:
        approvals = [a for a in db.get("approvals", []) if a["project_id"] == selected_proj_id]
        if not approvals:
            st.info("No approval workflows initiated for this project yet.")
        else:
            for app in approvals:
                with st.expander(f"📌 {app['item_name']} — Overall Status: `{app['overall_status']}`"):
                    c1, c2, c3, c4 = st.columns(4)
                    c1.markdown(f"**Architect:** `{app['arch_status']}`")
                    c2.markdown(f"**Structural:** `{app['struct_status']}`")
                    c3.markdown(f"**Electrical:** `{app['elec_status']}`")
                    c4.markdown(f"**Plumbing:** `{app['plum_status']}`")
                    
                    st.markdown(f"**Notes:** {app['notes']}")
                    st.markdown("---")
                    
                    current_user = st.session_state.get("user", {})
                    user_role = current_user.get("role", "")
                    
                    col_act1, col_act2 = st.columns([2, 1])
                    with col_act1:
                        action_comment = st.text_input("Review Comment / Sign-off note", key=f"cmt_{app['id']}")
                    with col_act2:
                        st.write("")
                        st.write("")
                        if st.button("✅ Approve Item", key=f"app_{app['id']}", use_container_width=True):
                            if user_role == "Architect":
                                app["arch_status"] = "Approved"
                            elif user_role == "Structural Engineer":
                                app["struct_status"] = "Approved"
                            elif user_role == "Electrical Engineer":
                                app["elec_status"] = "Approved"
                            elif user_role == "Plumber":
                                app["plum_status"] = "Approved"
                            elif user_role == "Admin":
                                app["arch_status"] = "Approved"
                                app["struct_status"] = "Approved"
                                app["elec_status"] = "Approved"
                                app["plum_status"] = "Approved"
                            
                            if all(app[k] == "Approved" for k in ["arch_status", "struct_status", "elec_status", "plum_status"]):
                                app["overall_status"] = "Fully Approved"
                            else:
                                app["overall_status"] = "Pending Review"
                                
                            app["notes"] += f" | [{current_user.get('name', 'User')}] Approved on {datetime.now().strftime('%Y-%m-%d')}."
                            save_memory(db)
                            st.success("Approval status updated successfully!")
                            st.rerun()

    with tab2:
        st.subheader("Create New Sign-Off Milestone")
        with st.form("new_approval_form"):
            item_name = st.text_input("Milestone / Deliverable Name (e.g., Foundation & Utility Schematic Package)")
            initial_notes = st.text_area("Initial Specification Notes")
            
            submitted = st.form_submit_button("Initiate Sign-Off Workflow", use_container_width=True)
            if submitted:
                if not item_name:
                    st.error("Deliverable name is required.")
                else:
                    new_app = {
                        "id": f"APP-{len(db.get('approvals', [])) + 1}",
                        "project_id": selected_proj_id,
                        "item_name": item_name,
                        "arch_status": "Pending",
                        "struct_status": "Pending",
                        "elec_status": "Pending",
                        "plum_status": "Pending",
                        "overall_status": "Pending Review",
                        "notes": initial_notes
                    }
                    if "approvals" not in db:
                        db["approvals"] = []
                    db["approvals"].append(new_app)
                    save_memory(db)
                    st.success("Approval workflow initialized!")
                    st.rerun()
