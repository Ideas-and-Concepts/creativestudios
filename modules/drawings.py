"""
Drawing Repository Module
Handles document versioning, discipline filtering, and file status tracking.
"""

from __future__ import annotations
import streamlit as st


def render_drawings_module(db: dict) -> None:
    st.markdown("## Drawing Repository")
    st.caption("Manage architectural, structural, MEP, and site construction drawings.")

    if "drawings" not in db:
        db["drawings"] = []

    # Summary Metrics
    total_drawings = len(db["drawings"])
    pending_approval = sum(1 for d in db["drawings"] if d.get("status") == "Pending Review")
    approved_drawings = sum(1 for d in db["drawings"] if d.get("status") == "Approved")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Sheets", total_drawings)
    col2.metric("Pending Review", pending_approval)
    col3.metric("Approved", approved_drawings)

    st.markdown("---")

    tab1, tab2 = st.tabs(["Sheet Directory", "Upload / Register Sheet"])

    with tab1:
        c1, c2, c3 = st.columns([2, 1, 1])
        search = c1.text_input("Search drawing title or code", placeholder="e.g. A-101")
        discipline_filter = c2.selectbox(
            "Discipline",
            ["All", "Architectural", "Structural", "Electrical", "Plumbing", "HVAC", "Civil"]
        )
        status_filter = c3.selectbox(
            "Status",
            ["All", "Approved", "Pending Review", "Superceded", "Rejected"]
        )

        filtered = db["drawings"]
        if search:
            s_lower = search.lower()
            filtered = [
                d for d in filtered 
                if s_lower in d.get("code", "").lower() or s_lower in d.get("title", "").lower()
            ]
        if discipline_filter != "All":
            filtered = [d for d in filtered if d.get("discipline") == discipline_filter]
        if status_filter != "All":
            filtered = [d for d in filtered if d.get("status") == status_filter]

        if not filtered:
            st.info("No drawing sheets found matching the active criteria.")
        else:
            for item in filtered:
                with st.expander(f"**[{item.get('code', 'N/A')}]** {item.get('title', 'Untitled Sheet')}"):
                    d_col1, d_col2, d_col3, d_col4 = st.columns(4)
                    d_col1.write(f"**Discipline:** {item.get('discipline', '-')}")
                    d_col2.write(f"**Revision:** Rev {item.get('revision', '0')}")
                    d_col3.write(f"**Status:** {item.get('status', 'Draft')}")
                    d_col4.write(f"**Author:** {item.get('author', 'N/A')}")
                    
                    if item.get("notes"):
                        st.caption(f"**Notes:** {item.get('notes')}")

    with tab2:
        st.markdown("### Register New Drawing Sheet")
        with st.form("add_drawing_form", clear_on_submit=True):
            f1, f2 = st.columns(2)
            code = f1.text_input("Sheet Code*", placeholder="e.g. S-201")
            title = f2.text_input("Sheet Title*", placeholder="e.g. Foundation Framing Plan")

            f3, f4, f5 = st.columns(3)
            discipline = f3.selectbox(
                "Discipline*",
                ["Architectural", "Structural", "Electrical", "Plumbing", "HVAC", "Civil"]
            )
            revision = f4.text_input("Revision", value="0")
            status = f5.selectbox("Initial Status", ["Pending Review", "Approved", "Draft"])

            notes = st.text_area("Revision Notes / Scope", placeholder="Describe changes or sheet coverage...")
            submitted = st.form_submit_button("Register Sheet", use_container_width=True)

            if submitted:
                if not code or not title:
                    st.error("Sheet Code and Title are required.")
                else:
                    new_doc = {
                        "id": len(db["drawings"]) + 1,
                        "code": code.strip(),
                        "title": title.strip(),
                        "discipline": discipline,
                        "revision": revision.strip(),
                        "status": status,
                        "author": st.session_state.get("user", {}).get("full_name", "Admin"),
                        "notes": notes.strip(),
                    }
                    db["drawings"].append(new_doc)
                    st.success(f"Registered sheet {code} successfully!")
                    st.rerun()


# ============================================================