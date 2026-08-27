"""
Sign-Off & Approvals Module
Manages multi-disciplinary document sign-offs, material submittals, and milestone approvals.
"""

from __future__ import annotations
import datetime
import streamlit as st


def render_approvals_module(db: dict) -> None:
    st.markdown("## Sign-Off & Approvals")
    st.caption("Track formal approval requests, material sample sign-offs, and design approvals across project stakeholders.")

    if "approvals" not in db:
        db["approvals"] = []

    # Summary Metrics
    total_approvals = len(db["approvals"])
    pending = sum(1 for a in db["approvals"] if a.get("status") in ["Pending Review", "Under Review"])
    approved = sum(1 for a in db["approvals"] if a.get("status") == "Approved")
    rejected = sum(1 for a in db["approvals"] if a.get("status") == "Rejected")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Requests", total_approvals)
    col2.metric("Pending Sign-Off", pending)
    col3.metric("Approved", approved)
    col4.metric("Rejected / Revise", rejected)

    st.markdown("---")

    tab1, tab2 = st.tabs(["Approval Register", "Request Sign-Off"])

    with tab1:
        if not db["approvals"]:
            st.info("No approval requests logged yet.")
        else:
            c1, c2 = st.columns([2, 1])
            status_filter = c1.selectbox(
                "Filter Status",
                ["All", "Pending Review", "Approved", "Conditional Approval", "Rejected"]
            )
            category_filter = c2.selectbox(
                "Category",
                ["All", "Architectural", "Structural", "MEP", "Material Submittal", "Method Statement"]
            )

            filtered = db["approvals"]
            if status_filter != "All":
                filtered = [a for a in filtered if a.get("status") == status_filter]
            if category_filter != "All":
                filtered = [a for a in filtered if a.get("category") == category_filter]

            if not filtered:
                st.info("No approval requests match the selected filters.")
            else:
                for item in filtered:
                    status_badge = {
                        "Approved": "🟢 Approved",
                        "Conditional Approval": "🟡 Conditional",
                        "Pending Review": "🔵 Pending Review",
                        "Rejected": "🔴 Rejected"
                    }.get(item.get("status", ""), item.get("status", "Pending"))

                    title_label = f"**[{item.get('doc_code', 'N/A')}]** {item.get('title', 'Untitled')} — {status_badge}"

                    with st.expander(title_label):
                        ac1, ac2, ac3 = st.columns(3)
                        ac1.write(f"**Category:** {item.get('category', '-')}")
                        ac2.write(f"**Assigned Approver:** {item.get('approver', 'Unassigned')}")
                        ac3.write(f"**Requested Date:** {item.get('date_requested', '-')}")

                        st.markdown(f"**Scope / Details:**\n{item.get('description', 'No details provided.')}")

                        if item.get("review_comments"):
                            st.markdown("---")
                            st.markdown(f"**Approver Comments:**\n{item.get('review_comments')}")

                        # Action form to update approval status
                        current_user = st.session_state.get("user", {})
                        st.markdown("---")
                        st.caption("Update Approval Status")

                        with st.form(f"update_approval_{item.get('id')}"):
                            new_status = st.selectbox(
                                "Action Status",
                                ["Pending Review", "Approved", "Conditional Approval", "Rejected"],
                                index=["Pending Review", "Approved", "Conditional Approval", "Rejected"].index(
                                    item.get("status", "Pending Review")
                                ) if item.get("status") in ["Pending Review", "Approved", "Conditional Approval", "Rejected"] else 0,
                                key=f"status_select_{item.get('id')}"
                            )
                            comments = st.text_area(
                                "Review Comments / Conditions",
                                value=item.get("review_comments", ""),
                                key=f"comments_text_{item.get('id')}"
                            )
                            update_btn = st.form_submit_button("Save Decision", use_container_width=True)

                            if update_btn:
                                item["status"] = new_status
                                item["review_comments"] = comments.strip()
                                item["reviewed_by"] = current_user.get("full_name", "Admin")
                                item["date_reviewed"] = datetime.date.today().isoformat()
                                st.success("Approval status updated successfully!")
                                st.rerun()

    with tab2:
        st.markdown("### Create Approval Request")
        with st.form("create_approval_form", clear_on_submit=True):
            a1, a2 = st.columns(2)
            doc_code = a1.text_input("Document / Submittal Ref Code*", placeholder="e.g. SUB-ARC-014")
            title = a2.text_input("Title / Subject*", placeholder="e.g. Exterior Glazing Material Spec")

            a3, a4 = st.columns(2)
            category = a3.selectbox(
                "Category*",
                ["Architectural", "Structural", "MEP", "Material Submittal", "Method Statement", "Site Mockup"]
            )
            approver = a4.selectbox(
                "Assigned Approver Role*",
                ["Lead Architect", "Structural Engineer", "MEP Consultant", "Project Director", "Client Representative"]
            )

            description = st.text_area("Request Details & Specifications*", placeholder="Describe what requires sign-off...")

            submitted = st.form_submit_button("Submit Sign-Off Request", use_container_width=True)

            if submitted:
                if not doc_code or not title or not description:
                    st.error("Please fill in all required fields marked with *.")
                else:
                    new_approval = {
                        "id": len(db["approvals"]) + 1,
                        "doc_code": doc_code.strip(),
                        "title": title.strip(),
                        "category": category,
                        "approver": approver,
                        "description": description.strip(),
                        "status": "Pending Review",
                        "requested_by": st.session_state.get("user", {}).get("full_name", "Admin"),
                        "date_requested": datetime.date.today().isoformat(),
                        "review_comments": "",
                        "reviewed_by": "",
                        "date_reviewed": ""
                    }
                    db["approvals"].append(new_approval)
                    st.success(f"Submitted approval request {doc_code}!")
                    st.rerun()


# ============================================================