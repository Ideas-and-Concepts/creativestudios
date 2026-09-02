"""Creative Studios Drawings Module."""
from __future__ import annotations
from datetime import datetime
from typing import Any
import streamlit as st
from modules.database import next_id, save_memory
from modules.project_context import filter_project_records, project_label, project_options

DISCIPLINES = ["Architectural", "Structural", "Civil", "Electrical", "Mechanical", "Plumbing", "Other"]
DRAWING_TYPES = ["Plan", "Elevation", "Section", "Detail", "Schedule", "Site Plan", "Structural Detail", "MEP Drawing", "Other"]
STATUSES = ["Draft", "In Review", "Approved", "Issued", "Superseded"]


def _normalize(database: dict[str, Any]) -> list[dict[str, Any]]:
    raw = database.get("drawings", []); records: list[dict[str, Any]] = []
    if not isinstance(raw, list): raw = []
    for index, item in enumerate(raw, 1):
        if isinstance(item, dict):
            r = dict(item); r.setdefault("id", index); r.setdefault("project_id", None); records.append(r)
        elif isinstance(item, str):
            records.append({"id": index, "project_id": None, "drawing_number": "", "title": item, "discipline": "Architectural", "drawing_type": "Plan", "revision": "A", "status": "Draft", "scale": "1:100", "created_at": ""})
    database["drawings"] = records
    return records


def render_drawings_module(database: dict[str, Any]) -> None:
    st.title("Drawings")
    st.caption("Project-linked drawing register for architectural, structural, civil and MEP documentation.")
    records = _normalize(database)
    projects = project_options(database)
    if not projects:
        st.warning("Create a project first in Projects."); return
    labels = [project_label(p) for p in projects]
    selected = st.selectbox("Project", labels, key="drawings_project")
    project_id = int(projects[labels.index(selected)]["id"])
    project_records = filter_project_records(records, project_id)

    tab_arch, tab_struct, tab_all, tab_add = st.tabs(["Architectural Drawings", "Structural Drawings", "All Drawings", "Register Drawing"])

    def render_list(items: list[dict[str, Any]], key_prefix: str) -> None:
        if not items:
            st.info("No drawings registered for this project."); return
        for drawing in list(items):
            rid = drawing.get("id")
            heading = f"{drawing.get('drawing_number', '')} | {drawing.get('title', 'Untitled') }".strip(" |")
            with st.expander(heading):
                with st.form(f"drawing_edit_{key_prefix}_{rid}"):
                    number = st.text_input("Drawing Number", value=str(drawing.get("drawing_number", "")))
                    title = st.text_input("Drawing Title", value=str(drawing.get("title", "")))
                    discipline = st.selectbox("Discipline", DISCIPLINES, index=DISCIPLINES.index(drawing.get("discipline", "Architectural")) if drawing.get("discipline", "Architectural") in DISCIPLINES else 0)
                    dtype = st.selectbox("Drawing Type", DRAWING_TYPES, index=DRAWING_TYPES.index(drawing.get("drawing_type", "Plan")) if drawing.get("drawing_type", "Plan") in DRAWING_TYPES else 0)
                    revision = st.text_input("Revision", value=str(drawing.get("revision", "A")))
                    status = st.selectbox("Status", STATUSES, index=STATUSES.index(drawing.get("status", "Draft")) if drawing.get("status", "Draft") in STATUSES else 0)
                    scale = st.text_input("Scale", value=str(drawing.get("scale", "1:100")))
                    save = st.form_submit_button("Save Changes", use_container_width=True)
                if save:
                    if not number.strip() or not title.strip(): st.error("Drawing number and title are required.")
                    else:
                        drawing.update({"drawing_number": number.strip(), "title": title.strip(), "discipline": discipline, "drawing_type": dtype, "revision": revision.strip(), "status": status, "scale": scale.strip(), "updated_at": datetime.now().isoformat(timespec="seconds")})
                        save_memory(database); st.success("Drawing updated."); st.rerun()
                if st.button("Delete Drawing", key=f"drawing_delete_{key_prefix}_{rid}", use_container_width=True):
                    records.remove(drawing); save_memory(database); st.rerun()

    with tab_arch:
        render_list([r for r in project_records if r.get("discipline") == "Architectural"], "arch")
    with tab_struct:
        render_list([r for r in project_records if r.get("discipline") == "Structural"], "struct")
    with tab_all:
        render_list(project_records, "all")
    with tab_add:
        with st.form("drawing_add", clear_on_submit=True):
            number = st.text_input("Drawing Number")
            title = st.text_input("Drawing Title")
            discipline = st.selectbox("Discipline", DISCIPLINES)
            dtype = st.selectbox("Drawing Type", DRAWING_TYPES)
            revision = st.text_input("Revision", value="A")
            status = st.selectbox("Status", STATUSES)
            scale = st.text_input("Scale", value="1:100")
            submitted = st.form_submit_button("Register Drawing", use_container_width=True)
        if submitted:
            if not number.strip() or not title.strip(): st.error("Drawing number and title are required.")
            else:
                records.append({"id": next_id("drawings", database), "project_id": project_id, "drawing_number": number.strip(), "title": title.strip(), "discipline": discipline, "drawing_type": dtype, "revision": revision.strip(), "status": status, "scale": scale.strip(), "created_at": datetime.now().isoformat(timespec="seconds")})
                save_memory(database); st.success("Drawing registered."); st.rerun()
