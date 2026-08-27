import streamlit as st
from typing import Any
from modules.database import save_memory

# ============================================================
# APPROVALS MODULE
# ============================================================

def render_approvals_module(database: dict[str, Any]) -> None:
    """Render Approvals module for pending BOQ changes."""

    st.header("Approvals")

    projects = database.get("projects", [])
    if not projects:
        st.info("No projects available.")
        return

    for project in projects:
        approvals = project.get("pending_approvals", [])
        if approvals:
            st.subheader(project.get("name", "Unnamed Project"))
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
            st.caption(f"No pending approvals for {project.get('name', 'Unnamed Project')}.")