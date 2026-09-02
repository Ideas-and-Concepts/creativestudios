"""Creative Studios Settings module."""
from __future__ import annotations

from typing import Any

import streamlit as st

from modules.database import save_memory

DEFAULTS = {
    "company_name": "Creative Studios",
    "platform_name": "Creative Studios",
    "timezone": "Africa/Juba",
    "currency": "USD",
    "date_format": "YYYY-MM-DD",
    "default_project_status": "planning",
    "notifications_enabled": True,
    "compact_mode": False,
}


def render_settings_module(database: dict[str, Any]) -> None:
    st.title("Settings")
    st.caption("Workspace configuration for the legacy Streamlit environment.")

    settings = database.get("settings")
    if not isinstance(settings, dict):
        settings = {}
        database["settings"] = settings

    values = {**DEFAULTS, **settings}
    with st.form("settings_form"):
        company_name = st.text_input("Company Name", value=str(values["company_name"]))
        platform_name = st.text_input("Platform Name", value=str(values["platform_name"]))
        timezone = st.text_input("Timezone", value=str(values["timezone"]))
        currency = st.text_input("Currency", value=str(values["currency"]))
        date_format = st.text_input("Date Format", value=str(values["date_format"]))
        default_project_status = st.selectbox("Default Project Status", ["planning", "active", "on_hold", "completed", "cancelled"], index=["planning", "active", "on_hold", "completed", "cancelled"].index(values["default_project_status"]) if values["default_project_status"] in ["planning", "active", "on_hold", "completed", "cancelled"] else 0)
        notifications_enabled = st.checkbox("Notifications Enabled", value=bool(values["notifications_enabled"]))
        compact_mode = st.checkbox("Compact Mode", value=bool(values["compact_mode"]))
        submitted = st.form_submit_button("Save Settings", use_container_width=True)

    if submitted:
        database["settings"] = {
            "company_name": company_name.strip() or DEFAULTS["company_name"],
            "platform_name": platform_name.strip() or DEFAULTS["platform_name"],
            "timezone": timezone.strip() or DEFAULTS["timezone"],
            "currency": currency.strip().upper() or DEFAULTS["currency"],
            "date_format": date_format.strip() or DEFAULTS["date_format"],
            "default_project_status": default_project_status,
            "notifications_enabled": notifications_enabled,
            "compact_mode": compact_mode,
        }
        if save_memory(database):
            st.success("Settings saved.")
            st.rerun()
        else:
            st.error("Unable to save settings.")

    st.divider()
    st.subheader("Workspace Information")
    st.write({"database": "Legacy JSON workspace", "production_database": "Neon PostgreSQL", "pwa": "Next.js"})
