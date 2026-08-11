import streamlit as st
from utils import load_memory, save_memory, require_auth, get_project_name

st.set_page_config(page_title="Procurement Approvals", page_icon="🛡", layout="wide")
require_auth()

db = load_memory()
current_user = st.session_state["user"]

st.title("🛡 Approval & Procurement Engine")

if not db.get("projects"):
    st.warning("Please create a project first.")
else:
    tab1, tab2 = st.tabs(["Active Sign-off Pipeline", "Initiate Approval Request"])

    with tab1:
        approvals = db.get("procurement_approvals", [])
        if approvals:
            for item in approvals:
                item_id = item.get("id", "APP-UNKNOWN")
                with st.expander(f"📦 {item.get('item_name', 'Item')} (Project: {item.get('project_id')})"):
                    col1, col2, col3, col4 = st.columns(4)

                    # 1. Architectural
                    with col1:
                        st.markdown("**1. Architectural**")
                        st.caption(f"Status: `{item.get('arch_status', 'Pending')}`")
                        if item.get('arch_status') != "Approved":
                            can_arch = current_user["role"] in ["Architect", "Admin"]
                            if st.button("Approve (Arch)", key=f"arch_{item_id}", disabled=not can_arch):
                                item['arch_status'] = "Approved"
                                item['arch_approved_by'] = current_user["name"]
                                save_memory(db)
                                st.rerun()

                    # 2. Structural
                    with col2:
                        st.markdown("**2. Structural**")
                        st.caption(f"Status: `{item.get('eng_status', 'Pending')}`")
                        if item.get('eng_status') != "Approved":
                            can_struct = current_user["role"] in ["Structural Engineer", "Admin"]
                            if st.button("Approve (Struct)", key=f"eng_{item_id}", disabled=not can_struct):
                                item['eng_status'] = "Approved"
                                item['eng_approved_by'] = current_user["name"]
                                save_memory(db)
                                st.rerun()

                    # 3. MEP
                    with col3:
                        st.markdown("**3. MEP Engineering**")
                        st.caption(f"Status: `{item.get('mep_status', 'Pending')}`")
                        if item.get('mep_status') != "Approved":
                            can_mep = current_user["role"] in ["MEP Engineer", "Admin"]
                            if st.button("Approve (MEP)", key=f"mep_{item_id}", disabled=not can_mep):
                                item['mep_status'] = "Approved"
                                item['mep_approved_by'] = current_user["name"]
                                save_memory(db)
                                st.rerun()

                    # 4. Status
                    with col4:
                        st.markdown("**4. Procurement Release**")
                        if item.get('arch_status') == "Approved" and item.get('eng_status') == "Approved" and item.get('mep_status') == "Approved":
                            item['procurement_status'] = "Ready for Release"
                            st.success("✅ Fully Approved")
                        else:
                            item['procurement_status'] = "Locked"
                            st.warning("🔒 Sign-offs Pending")

                    st.write(f"**Notes:** {item.get('notes', 'N/A')}")
        else:
            st.info("No approval requests active.")

    with tab2:
        with st.form("new_approval_form"):
            proj_id = st.selectbox("Project", options=[p["id"] for p in db["projects"]], format_func=lambda x: f"{x} - {get_project_name(db, x)}")
            item_name = st.text_input("Item Description")
            notes = st.text_area("Compliance Notes")
            if st.form_submit_button("Submit Request") and item_name:
                app_id = f"APP-{len(db['procurement_approvals']) + 1:03d}"
                db["procurement_approvals"].append({
                    "id": app_id, "project_id": proj_id, "item_name": item_name,
                    "arch_status": "Pending", "eng_status": "Pending", "mep_status": "Pending",
                    "procurement_status": "Locked", "notes": notes
                })
                save_memory(db)
                st.success(f"Approval pipeline item created under ID: {app_id}")
                st.rerun()
