"""Creative Studios Settings module."""
from __future__ import annotations

from typing import Any

import streamlit as st

from modules.database import database_backend, save_memory

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
PROJECT_STATUSES = ["planning", "active", "on_hold", "completed", "cancelled"]


def render_settings_module(database: dict[str, Any]) -> None:
    st.title("Settings")
    st.caption("Workspace configuration for the Streamlit environment.")

    settings = database.get("settings")
    if not isinstance(settings, dict):
        settings = {}
    values = {**DEFAULTS, **settings}

    with st.form("settings_form"):
        company_name = st.text_input("Company Name", value=str(values.get("company_name", DEFAULTS["company_name"])))
        platform_name = st.text_input("Platform Name", value=str(values.get("platform_name", DEFAULTS["platform_name"])))
        timezone = st.text_input("Timezone", value=str(values.get("timezone", DEFAULTS["timezone"])))
        currency = st.text_input("Currency", value=str(values.get("currency", DEFAULTS["currency"])))
        date_format = st.text_input("Date Format", value=str(values.get("date_format", DEFAULTS["date_format"])))
        default_status = str(values.get("default_project_status", DEFAULTS["default_project_status"]))
        default_project_status = st.selectbox(
            "Default Project Status",
            PROJECT_STATUSES,
            index=PROJECT_STATUSES.index(default_status) if default_status in PROJECT_STATUSES else 0,
        )
        notifications_enabled = st.checkbox("Notifications Enabled", value=bool(values.get("notifications_enabled", True)))
        compact_mode = st.checkbox("Compact Mode", value=bool(values.get("compact_mode", False)))
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
        try:
            if save_memory(database):
                st.success("Settings saved.")
                st.rerun()
            else:
                st.error("Unable to save settings.")
        except Exception as exc:
            st.error("Unable to save settings to the shared database.")
            with st.expander("Technical details"):
                st.exception(exc)

    st.divider()
    st.subheader("Workspace Information")
    backend = database_backend()
    st.write(
        {
            "database": "Shared workspace state",
            "data_layer": "Neon PostgreSQL" if backend == "neon" else "Local JSON",
            "pwa": "Next.js",
        }
    )
