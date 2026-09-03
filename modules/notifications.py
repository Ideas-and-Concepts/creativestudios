from __future__ import annotations
from datetime import date
from typing import Any
import streamlit as st
from modules.module_utils import ensure_collection, now_iso, project_records, project_selector, remove_record, save_new_record, save_updated_record

TYPES = ["Info", "RFI", "Approval", "Construction", "Cost", "Task"]
SEVERITIES = ["Normal", "Attention", "Urgent"]

def render_notifications_module(database: dict[str, Any]) -> None:
    st.title("Notifications & Activity")
    st.caption("Project alerts and operational workflow notifications.")
    records = ensure_collection(database, "notifications")
    project_id, _ = project_selector(database, "notifications_project")
    if project_id is None:
        return
    items = project_records(records, project_id)
    unread = [r for r in items if not r.get("is_read", False)]
    urgent = [r for r in items if str(r.get("severity", "")).lower() == "urgent"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Notifications", len(items)); c2.metric("Unread", len(unread)); c3.metric("Urgent", len(urgent))
    for record in sorted(items, key=lambda r: str(r.get("created_at", "")), reverse=True):
        rid = record.get("id")
        with st.expander(f"{record.get('title', 'Notification')} · {'Unread' if not record.get('is_read', False) else 'Read'}"):
            st.write(record.get("message", ""))
            st.caption(f"{record.get('type', 'Info')} · {record.get('severity', 'Normal')} · {record.get('created_at', '')}")
            if record.get("action_url"):
                st.link_button("Open related item", str(record["action_url"]))
            if not record.get("is_read", False) and st.button("Mark as read", key=f"notification_read_{rid}"):
                save_updated_record(database, "notifications", rid, {"is_read": True, "read_at": now_iso()}); st.rerun()
            if st.button("Delete notification", key=f"notification_delete_{rid}"):
                if remove_record(database, "notifications", rid): st.rerun()
    st.divider(); st.subheader("Add Notification")
    with st.form("notification_add", clear_on_submit=True):
        a, b = st.columns(2); title = a.text_input("Title"); notification_type = b.selectbox("Type", TYPES)
        a, b = st.columns(2); severity = a.selectbox("Severity", SEVERITIES); recipient = b.text_input("Recipient")
        message = st.text_area("Message"); source_type = st.text_input("Source Type"); source_id = st.text_input("Source ID"); action_url = st.text_input("Action URL")
        submitted = st.form_submit_button("Add Notification", use_container_width=True)
    if submitted:
        if not title.strip() or not message.strip():
            st.error("Title and Message are required.")
        else:
            save_new_record(database, "notifications", {"project_id": project_id, "title": title.strip(), "message": message.strip(), "type": notification_type, "severity": severity, "recipient": recipient.strip(), "source_type": source_type.strip(), "source_id": source_id.strip(), "action_url": action_url.strip(), "is_read": False, "created_at": now_iso(), "updated_at": now_iso()})
            st.success("Notification added."); st.rerun()
