"""Creative Studios Settings module."""
from __future__ import annotations

import copy
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

PAGE_DEFINITIONS = [
    ("Dashboard", "Workspace overview"),
    ("Projects", "Project management"),
    ("Documents", "Document management"),
    ("Architecture", "Architecture"),
    ("Engineering", "Engineering"),
    ("Drawings", "Drawings"),
    ("MEP", "MEP"),
    ("BOQ", "Bill of Quantities"),
    ("Procurement", "Procurement"),
    ("Construction", "Construction"),
    ("Cost Control", "Cost Control"),
    ("Tasks", "Tasks"),
    ("RFIs", "RFIs"),
    ("Approvals", "Approvals"),
    ("Reports", "Reports"),
    ("Settings", "Settings"),
]
PAGE_KEYS = [key for key, _ in PAGE_DEFINITIONS]
PAGE_DESCRIPTIONS = dict(PAGE_DEFINITIONS)


def _page_config(settings: dict[str, Any]) -> tuple[list[str], dict[str, str]]:
    raw_order = settings.get("page_order", PAGE_KEYS)
    if not isinstance(raw_order, list):
        raw_order = PAGE_KEYS

    order: list[str] = []
    for page in raw_order:
        if isinstance(page, str) and page in PAGE_KEYS and page not in order:
            order.append(page)
    for page in PAGE_KEYS:
        if page not in order:
            order.append(page)

    raw_labels = settings.get("page_labels", {})
    if not isinstance(raw_labels, dict):
        raw_labels = {}
    labels = {
        page: str(raw_labels.get(page) or page).strip() or page
        for page in PAGE_KEYS
    }
    return order, labels


def get_page_configuration(database: dict[str, Any]) -> tuple[list[str], dict[str, str]]:
    settings = database.get("settings", {})
    if not isinstance(settings, dict):
        settings = {}
    return _page_config(settings)


def _save_settings(database: dict[str, Any], new_settings: dict[str, Any], message: str) -> bool:
    previous = copy.deepcopy(database.get("settings", {}))
    database["settings"] = new_settings
    try:
        if save_memory(database):
            st.success(message)
            st.rerun()
        database["settings"] = previous
        st.error("Unable to save settings to the shared database.")
        return False
    except Exception as exc:
        database["settings"] = previous
        st.error("Unable to save settings to the shared database.")
        with st.expander("Technical details"):
            st.exception(exc)
        return False


def render_page_editor(database: dict[str, Any]) -> None:
    settings = database.get("settings")
    if not isinstance(settings, dict):
        settings = {}

    order, labels = _page_config(settings)

    st.subheader("Pages and Navigation")
    st.caption("Edit page names and permanently change the order used by the Streamlit sidebar.")

    selected_page = st.selectbox(
        "Page",
        order,
        format_func=lambda page: labels.get(page, page),
        key="settings_page_editor_page",
    )
    position = order.index(selected_page)

    left, middle, right = st.columns([1.3, 1, 1])
    with left:
        new_label = st.text_input(
            "Display Name",
            value=labels.get(selected_page, selected_page),
            key="settings_page_editor_label",
        )
    with middle:
        st.metric("Position", f"{position + 1} / {len(order)}")
    with right:
        st.caption(PAGE_DESCRIPTIONS.get(selected_page, selected_page))

    move_left, move_right, save_col = st.columns(3)
    with move_left:
        move_up = st.button("Move Up", use_container_width=True, disabled=position == 0)
    with move_right:
        move_down = st.button("Move Down", use_container_width=True, disabled=position == len(order) - 1)
    with save_col:
        save_page = st.button("Save Page", type="primary", use_container_width=True)

    if move_up:
        order[position - 1], order[position] = order[position], order[position - 1]
        _save_settings(database, {**settings, "page_order": order, "page_labels": labels}, "Page order saved.")
        return

    if move_down:
        order[position + 1], order[position] = order[position], order[position + 1]
        _save_settings(database, {**settings, "page_order": order, "page_labels": labels}, "Page order saved.")
        return

    if save_page:
        labels[selected_page] = new_label.strip() or selected_page
        _save_settings(database, {**settings, "page_order": order, "page_labels": labels}, "Page name saved.")
        return

    if st.button("Reset Page Arrangement", use_container_width=True):
        _save_settings(
            database,
            {
                **settings,
                "page_order": PAGE_KEYS.copy(),
                "page_labels": {page: page for page in PAGE_KEYS},
            },
            "Page arrangement reset to the default.",
        )

    st.markdown("**Current order**")
    for index, page in enumerate(order, start=1):
        st.write(f"{index}. {labels.get(page, page)}")


def render_settings_module(database: dict[str, Any]) -> None:
    st.title("Settings")
    st.caption("Workspace configuration for the Streamlit environment.")

    settings = database.get("settings")
    if not isinstance(settings, dict):
        settings = {}
    values = {**DEFAULTS, **settings}

    with st.form("settings_form"):
        company_name = st.text_input("Company Name", value=str(values["company_name"]))
        platform_name = st.text_input("Platform Name", value=str(values["platform_name"]))
        timezone = st.text_input("Timezone", value=str(values["timezone"]))
        currency = st.text_input("Currency", value=str(values["currency"]))
        date_format = st.text_input("Date Format", value=str(values["date_format"]))
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
        new_settings = {
            **settings,
            "company_name": company_name.strip() or DEFAULTS["company_name"],
            "platform_name": platform_name.strip() or DEFAULTS["platform_name"],
            "timezone": timezone.strip() or DEFAULTS["timezone"],
            "currency": currency.strip().upper() or DEFAULTS["currency"],
            "date_format": date_format.strip() or DEFAULTS["date_format"],
            "default_project_status": default_project_status,
            "notifications_enabled": notifications_enabled,
            "compact_mode": compact_mode,
        }
        _save_settings(database, new_settings, "Settings saved successfully.")
        return

    st.divider()
    render_page_editor(database)

    st.divider()
    st.subheader("Workspace Information")
    backend = database_backend()
    st.write({
        "database": "Shared workspace state",
        "data_layer": "Neon PostgreSQL" if backend == "neon" else "Local JSON",
        "pwa": "Next.js",
        "persistence": "Changes are saved to the shared workspace before the page refreshes.",
        "sample_data": "No sample data is created by the Streamlit entry point.",
    })
