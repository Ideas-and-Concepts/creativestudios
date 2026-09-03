"""Creative Studios Drawings Module."""
from __future__ import annotations
from datetime import datetime
from typing import Any
import streamlit as st
from modules.database import (database_backend, create_relational_drawing, delete_relational_drawing, delete_record, get_records, get_relational_drawings, next_id, save_memory, update_relational_drawing, update_record)
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
            records.append({"id": index,"project_id": None,"drawing_number":"","title":item,"discipline":"Architectural","drawing_type":"Plan","revision":"A","status":"Draft","scale":"1:100","created_at":""})
    database["drawings"] = records
    return records

def _load(database: dict[str, Any], project_id: str) -> list[dict[str, Any]]:
    if database_backend() == "neon":
        return get_relational_drawings(project_id)
    return filter_project_records(_normalize(database), project_id)

def _project_id(projects: list[dict[str, Any]], label: str) -> str:
    return str(projects[[project_label(p) for p in projects].index(label)]["id"])

def render_drawings_module(database: dict[str, Any]) -> None:
    st.title("Drawings")
    st.caption("Project-linked drawing register for architectural, structural, civil and MEP documentation.")
    projects = project_options(database)
    if not projects:
        st.warning("Create a project first in Projects."); return
    labels = [project_label(p) for p in projects]
    selected = st.selectbox("Project", labels, key="drawings_project")
    project_id = _project_id(projects, selected)
    records = _load(database, project_id)

    tab_arch, tab_struct, tab_all, tab_add = st.tabs(["Architectural Drawings", "Structural Drawings", "All Drawings", "Register Drawing"])

    def render_list(items: list[dict[str, Any]], key_prefix: str) -> None:
        if not items: st.info("No drawings registered for this project."); return
        for drawing in list(items):
            rid = drawing.get("id")
            heading = f"{drawing.get('drawing_number', '')} | {drawing.get('title', 'Untitled')}".strip(" |")
            with st.expander(heading):
                with st.form(f"drawing_edit_{key_prefix}_{rid}"):
                    number = st.text_input("Drawing Number", value=str(drawing.get("drawing_number", "")))
                    title = st.text_input("Drawing Title", value=str(drawing.get("title", "")))
                    discipline = st.selectbox("Discipline", DISCIPLINES, index=DISCIPLINES.index(drawing.get("discipline", "Architectural")) if drawing.get("discipline", "Architectural") in DISCIPLINES else 0)
                    dtype = st.selectbox("Drawing Type", DRAWING_TYPES, index=DRAWING_TYPES.index(drawing.get("drawing_type", "Plan")) if drawing.get("drawing_type", "Plan") in DRAWING_TYPES else 0)
                    revision = st.text_input("Revision", value=str(drawing.get("revision", "A")))
                    status = st.selectbox("Status", STATUSES, index=STATUSES.index(drawing.get("status", "Draft")) if drawing.get("status", "Draft") in STATUSES else 0)
                    scale = st.text_input("Scale", value=str(drawing.get("scale", "1:100")))
                    file_url = st.text_input("Drawing file URL", value=str(drawing.get("file_url") or ""), help="Optional shared file reference. Local Streamlit uploads are not assumed to be globally available.")
                    save = st.form_submit_button("Save Changes", use_container_width=True)
                if save:
                    if not number.strip() or not title.strip(): st.error("Drawing number and title are required.")
                    else:
                        values = {"drawing_number": number.strip(), "title": title.strip(), "discipline": discipline, "drawing_type": dtype, "revision": revision.strip() or "A", "status": status, "scale": scale.strip() or "1:100", "file_url": file_url.strip() or None}
                        try:
                            if database_backend() == "neon": update_relational_drawing(str(rid), values)
                            else: update_record("drawings", rid, {**values, "updated_at": datetime.now().isoformat(timespec="seconds")}, database)
                            st.success("Drawing updated."); st.rerun()
                        except Exception as exc:
                            st.error("Unable to update the drawing."); st.exception(exc)
                if st.button("Delete Drawing", key=f"drawing_delete_{key_prefix}_{rid}", use_container_width=True):
                    try:
                        if database_backend() == "neon": delete_relational_drawing(str(rid))
                        else: delete_record("drawings", rid, database)
                        st.success("Drawing deleted."); st.rerun()
                    except Exception as exc:
                        st.error("Unable to delete the drawing."); st.exception(exc)

    with tab_arch: render_list([r for r in records if r.get("discipline") == "Architectural"], "arch")
    with tab_struct: render_list([r for r in records if r.get("discipline") == "Structural"], "struct")
    with tab_all: render_list(records, "all")
    with tab_add:
        with st.form("drawing_add", clear_on_submit=True):
            number = st.text_input("Drawing Number")
            title = st.text_input("Drawing Title")
            discipline = st.selectbox("Discipline", DISCIPLINES)
            dtype = st.selectbox("Drawing Type", DRAWING_TYPES)
            revision = st.text_input("Revision", value="A")
            status = st.selectbox("Status", STATUSES)
            scale = st.text_input("Scale", value="1:100")
            file_url = st.text_input("Drawing file URL", help="Optional shared file reference.")
            submitted = st.form_submit_button("Register Drawing", use_container_width=True)
        if submitted:
            if not number.strip() or not title.strip(): st.error("Drawing number and title are required.")
            else:
                try:
                    values = {"project_id": project_id, "drawing_number": number.strip(), "title": title.strip(), "discipline": discipline, "drawing_type": dtype, "revision": revision.strip() or "A", "status": status, "scale": scale.strip() or "1:100", "file_url": file_url.strip() or None}
                    if database_backend() == "neon": create_relational_drawing(values)
                    else:
                        records_all = _normalize(database); records_all.append({"id": next_id("drawings", database), **values, "created_at": datetime.now().isoformat(timespec="seconds"), "updated_at": datetime.now().isoformat(timespec="seconds")}); save_memory(database)
                    st.success("Drawing registered."); st.rerun()
                except Exception as exc:
                    st.error("Unable to register the drawing."); st.exception(exc)
