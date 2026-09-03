"""Creative Studios document register.

Neon mode writes document metadata to the shared relational documents table.
JSON mode remains available for offline/local development. Uploaded binaries are
currently stored in the Streamlit workspace; shared object storage is a separate
production deployment concern and is intentionally not faked here.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

from modules.database import (
    database_backend,
    delete_record,
    delete_relational_document,
    get_records,
    get_relational_documents,
    next_id,
    create_relational_document,
    update_record,
    update_relational_document,
)
from modules.module_utils import now_iso, project_label, project_options, save_new_record

BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "storage" / "documents"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
DOCUMENT_STATUSES = ["Draft", "Under Review", "Approved", "Superseded", "Archived"]
ALLOWED_TYPES = ["pdf", "docx", "xlsx", "png", "jpg", "jpeg"]
CHART_COLORS = ["#2563EB", "#111827", "#64748B", "#CBD5E1", "#94A3B8"]


def _document_type(filename: str) -> str:
    return {".pdf": "PDF", ".docx": "Word", ".xlsx": "Excel", ".png": "Image", ".jpg": "Image", ".jpeg": "Image"}.get(Path(filename).suffix.lower(), "Other")


def _save_uploaded_file(uploaded_file: Any, document_id: Any, revision: str | int) -> str:
    extension = Path(uploaded_file.name).suffix.lower()
    safe_id = str(document_id).replace("/", "_")
    file_path = STORAGE_DIR / f"doc_{safe_id}_v{revision}{extension}"
    with file_path.open("wb") as handle:
        handle.write(uploaded_file.getbuffer())
    return str(file_path.relative_to(BASE_DIR))


def _file_path(relative_path: str) -> Path:
    candidate = (BASE_DIR / relative_path).resolve()
    root = STORAGE_DIR.resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError("Invalid document storage path.")
    return candidate


def _documents(database: dict[str, Any]) -> list[dict[str, Any]]:
    if database_backend() == "neon":
        return get_relational_documents()
    return get_records("documents", database)


def _projects(database: dict[str, Any]) -> list[dict[str, Any]]:
    # project_options uses the relational project store when DATABASE_URL is set.
    return project_options(database)


def _project_id(choice: str, projects: list[dict[str, Any]], labels: list[str]) -> Any | None:
    if choice == "Unassigned":
        return None
    return projects[labels.index(choice) - 1].get("id")


def _display_document(record: dict[str, Any], projects: list[dict[str, Any]]) -> dict[str, Any]:
    project = next((p for p in projects if str(p.get("id")) == str(record.get("project_id"))), None)
    return {
        "id": record.get("id"), "title": record.get("title", ""),
        "project": project_label(project) if project else "Unassigned",
        "discipline": record.get("discipline") or "Unspecified",
        "document_type": record.get("document_type") or "Other",
        "version": record.get("revision") or 1,
        "status": record.get("status") or ("Approved" if record.get("is_approved") else "Draft"),
        "file_name": record.get("file_name") or "",
        "file_path": record.get("file_url") or "",
        "created_at": record.get("created_at"), "updated_at": record.get("updated_at"),
    }


def _analytics(documents: list[dict[str, Any]]) -> None:
    frame = pd.DataFrame(documents)
    if frame.empty: return
    frame["status"] = frame.get("status", pd.Series("Draft", index=frame.index)).fillna("Draft")
    frame["document_type"] = frame.get("document_type", pd.Series("Other", index=frame.index)).fillna("Other")
    frame["discipline"] = frame.get("discipline", pd.Series("Unspecified", index=frame.index)).replace("", "Unspecified").fillna("Unspecified")
    total = len(frame); approved = int((frame["status"] == "Approved").sum()); review = int((frame["status"] == "Under Review").sum())
    project_count = int(frame["project_id"].replace("", pd.NA).dropna().nunique()) if "project_id" in frame.columns else 0
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total documents", total); c2.metric("Approved", approved); c3.metric("Under review", review); c4.metric("Projects represented", project_count)
    left, right = st.columns(2)
    with left:
        st.caption("Documents by status")
        counts = frame["status"].value_counts().reset_index(); counts.columns = ["Status", "Documents"]
        fig = px.pie(counts, names="Status", values="Documents", hole=.62, color_discrete_sequence=CHART_COLORS)
        fig.update_traces(textinfo="none", marker_line_width=0); fig.update_layout(height=260, margin=dict(l=5,r=5,t=5,b=5), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    with right:
        st.caption("Documents by file type")
        counts = frame["document_type"].value_counts().reset_index(); counts.columns = ["Type", "Documents"]
        fig = px.bar(counts, x="Type", y="Documents", color="Type", color_discrete_sequence=CHART_COLORS)
        fig.update_layout(height=260, margin=dict(l=5,r=5,t=5,b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.caption("Document register")
    columns = ["id", "title", "project", "discipline", "document_type", "version", "status", "file_name", "updated_at"]
    display = frame[[c for c in columns if c in frame.columns]].copy(); display.columns = [c.replace("_", " ").title() for c in display.columns]
    st.dataframe(display, use_container_width=True, hide_index=True)


def render_documents_module(database: dict[str, Any]) -> None:
    st.title("Documents")
    st.caption("Controlled project documents, revisions, status and searchable project records.")
    projects = _projects(database)
    if not projects:
        st.warning("Create a project first in Projects before registering a document.")
        return
    labels = [project_label(p) for p in projects]

    with st.expander("Register document", expanded=True):
        with st.form("upload_doc_form", clear_on_submit=True):
            title = st.text_input("Document title", max_chars=200)
            project_choice = st.selectbox("Project", labels)
            discipline = st.text_input("Discipline", max_chars=100)
            status = st.selectbox("Status", DOCUMENT_STATUSES)
            uploaded_file = st.file_uploader("File", type=ALLOWED_TYPES)
            submitted = st.form_submit_button("Upload document", use_container_width=True)
        if submitted:
            if not title.strip() or uploaded_file is None:
                st.error("Document title and file are required.")
            else:
                project_id = _project_id(project_choice, projects, ["Unassigned"] + labels)
                revision = "1"
                document_id: Any = next_id("documents", database) if database_backend() == "json" else "pending"
                file_path = ""
                try:
                    if database_backend() == "neon":
                        record = create_relational_document({"project_id": project_id, "title": title.strip(), "document_type": _document_type(uploaded_file.name), "discipline": discipline.strip() or None, "status": status, "file_name": uploaded_file.name, "revision": revision, "is_approved": status == "Approved"})
                        document_id = record["id"]
                        file_path = _save_uploaded_file(uploaded_file, document_id, revision)
                        update_relational_document(str(document_id), {"file_url": file_path})
                    else:
                        file_path = _save_uploaded_file(uploaded_file, document_id, revision)
                        timestamp = now_iso()
                        save_new_record(database, "documents", {"id": document_id, "project_id": project_id, "project": project_choice, "title": title.strip(), "discipline": discipline.strip(), "status": status, "document_type": _document_type(uploaded_file.name), "version": 1, "file_name": uploaded_file.name, "file_path": file_path, "created_at": timestamp, "updated_at": timestamp})
                    st.success("Document uploaded and registered."); st.rerun()
                except Exception as exc:
                    if file_path:
                        try:
                            path = _file_path(file_path)
                            if path.exists(): path.unlink()
                        except Exception: pass
                    st.error("Unable to save document metadata.")
                    with st.expander("Technical details"): st.exception(exc)

    raw_documents = _documents(database)
    if not raw_documents:
        st.info("No documents have been registered yet."); return
    documents = [_display_document(d, projects) for d in raw_documents]
    st.divider(); _analytics(documents); st.divider(); st.subheader("Manage documents")
    search = st.text_input("Search documents", key="documents_search", placeholder="Title, project, discipline, status or filename").strip().lower()
    visible = [d for d in documents if not search or search in str(d).lower()]
    if not visible:
        st.info("No documents match the current search."); return

    for document in visible:
        document_id = document.get("id"); version = document.get("version", 1)
        with st.expander(f"{document.get('title', 'Untitled')} · v{version} · {document.get('status', 'Draft')}"):
            with st.form(f"document_edit_{document_id}"):
                edit_title = st.text_input("Document title", value=str(document.get("title", "")))
                current_project = document.get("project", labels[0]); edit_project = st.selectbox("Project", labels, index=labels.index(current_project) if current_project in labels else 0)
                edit_discipline = st.text_input("Discipline", value=str(document.get("discipline", "")))
                current_status = document.get("status", "Draft"); edit_status = st.selectbox("Status", DOCUMENT_STATUSES, index=DOCUMENT_STATUSES.index(current_status) if current_status in DOCUMENT_STATUSES else 0)
                save = st.form_submit_button("Save changes", use_container_width=True)
            if save:
                try:
                    project_id = projects[labels.index(edit_project)].get("id")
                    if database_backend() == "neon":
                        saved = update_relational_document(str(document_id), {"project_id": project_id, "title": edit_title.strip(), "discipline": edit_discipline.strip() or None, "status": edit_status, "is_approved": edit_status == "Approved"})
                    else:
                        saved = update_record("documents", document_id, {"project_id": project_id, "project": edit_project, "title": edit_title.strip(), "discipline": edit_discipline.strip(), "status": edit_status, "updated_at": now_iso()}, database)
                    if saved is None: st.error("Document not found.")
                    else: st.success("Document updated."); st.rerun()
                except Exception as exc:
                    st.error("Unable to update the document.")
                    with st.expander("Technical details"): st.exception(exc)

            file_path_value = str(document.get("file_path", ""))
            if file_path_value:
                try: stored_file = _file_path(file_path_value)
                except ValueError: stored_file = None
                if stored_file and stored_file.exists():
                    with stored_file.open("rb") as handle: st.download_button("Download current file", handle.read(), file_name=str(document.get("file_name") or stored_file.name), key=f"document_download_{document_id}", use_container_width=True)
                else: st.warning("Metadata exists, but the uploaded file is not available in this Streamlit workspace.")

            if st.button("Delete document", key=f"document_delete_{document_id}", use_container_width=True):
                try:
                    if database_backend() == "neon":
                        deleted = delete_relational_document(str(document_id))
                    else:
                        deleted = delete_record("documents", document_id, database)
                        if deleted and file_path_value:
                            try:
                                stored = _file_path(file_path_value)
                                if stored.exists(): stored.unlink()
                            except ValueError: pass
                    if deleted: st.success("Document deleted."); st.rerun()
                    else: st.warning("The document was already removed.")
                except Exception as exc:
                    st.error("Unable to delete the document.")
                    with st.expander("Technical details"): st.exception(exc)
