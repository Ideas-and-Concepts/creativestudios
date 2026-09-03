from __future__ import annotations
from typing import Any
import streamlit as st
from modules.module_utils import ensure_collection, project_records, project_selector

def render_audit_log_module(database: dict[str, Any]) -> None:
    st.title("Audit Trail")
    st.caption("Chronological record of project workflow activity.")
    records = ensure_collection(database, "activity_log")
    project_id, _ = project_selector(database, "audit_project")
    if project_id is None:
        return
    items = project_records(records, project_id)
    st.metric("Events", len(items))
    if not items:
        st.info("No audit events have been recorded for this project yet.")
        return
    for record in sorted(items, key=lambda r: str(r.get("created_at", r.get("timestamp", ""))), reverse=True):
        actor = record.get("actor", record.get("user", "System"))
        action = record.get("action", record.get("event", "Activity"))
        entity = record.get("entity_type", record.get("module", "Workspace"))
        label = record.get("entity_label", record.get("description", ""))
        st.write(f"**{action}** · {entity} · {label}")
        st.caption(f"{actor} · {record.get('created_at', record.get('timestamp', ''))}")
