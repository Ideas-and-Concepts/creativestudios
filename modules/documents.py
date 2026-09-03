"""Creative Studios document register and document analytics."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

from modules.database import delete_record, get_records, next_id, update_record
from modules.module_utils import now_iso, project_label, project_options, save_new_record

BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "storage" / "documents"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

DOCUMENT_STATUSES = ["Draft", "Under Review", "Approved", "Superseded", "Archived"]
ALLOWED_TYPES = ["pdf", "docx", "xlsx", "png", "jpg", "jpeg"]
CHART_COLORS = ["#2563EB", "#111827", "#64748B", "#CBD5E1", "#94A3B8"]


def _document_type(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    return {".pdf": "PDF", ".docx": "Word", ".xlsx": "Excel", ".png": "Image", ".jpg": "Image", ".jpeg": "Image"}.get(suffix, "Other")


def _save_uploaded_file(uploaded_file: Any, document_id: int, version: int) -> str:
    extension = Path(uploaded_file.name).suffix.lower()
    file_path = STORAGE_DIR / f"doc_{document_id}_v{version}{extension}"
    with file_path.open("wb") as handle:
        handle.write(uploaded_file.getbuffer())
    return str(file_path.relative_to(BASE_DIR))


def _file_path(relative_path: str) -> Path:
    candidate = (BASE_DIR / relative_path).resolve()
    root = STORAGE_DIR.resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError("Invalid document storage path.")
    return candidate


def _project_id(project_choice: str, projects: list[dict[str, Any]], labels: list[str]) -> int | None:
    if project_choice == "Unassigned":
        return None
    selected = projects[labels.index(project_choice) - 1]
    return int(selected["id"])


def _analytics(documents: list[dict[str, Any]]) -> None:
    frame = pd.DataFrame(documents)
    if frame.empty:
        return
    frame["status"] = frame.get("status", "Draft").fillna("Draft")
    frame["document_type"] = frame.get("document_type", "Other").fillna("Other")
    frame["discipline"] = frame.get("discipline", "Unspecified").replace("", "Unspecified").fillna("Unspecified")

    total = len(frame)
    approved = int((frame["status"] == "Approved").sum())
    review = int((frame["status"] == "Under Review").sum())
    archived = int((frame["status"] == "Archived").sum())
    project_count = int(frame.get("project_id", pd.Series(dtype=object)).replace("", pd.NA).dropna().nunique())
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total documents", total)
    c2.metric("Approved", approved)
    c3.metric("Under review", review)
    c4.metric("Projects represented", project_count)

    left, right = st.columns(2)
    with left:
        st.caption("Documents by status")
        status_counts = frame["status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Documents"]
        fig = px.pie(status_counts, names="Status", values="Documents", hole=.62, color_discrete_sequence=CHART_COLORS)
        fig.update_traces(textinfo="none", marker_line_width=0)
        fig.update_layout(height=260, margin=dict(l=5, r=5, t=5, b=5), paper_bgcolor="rgba(0,0,0,0)", font=dict(size=9, color="#111827"))
        fig.add_annotation(text=f"<b>{total}</b><br><span style='font-size:9px'>Total</span>", showarrow=False, font=dict(size=15, color="#111827"))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    with right:
        st.caption("Documents by file type")
        type_counts = frame["document_type"].value_counts().reset_index()
        type_counts.columns = ["Type", "Documents"]
        fig = px.bar(type_counts, x="Type", y="Documents", color="Type", color_discrete_sequence=CHART_COLORS)
        fig.update_layout(height=260, margin=dict(l=5, r=5, t=5, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False, font=dict(size=9, color="#111827"))
        fig.update_xaxes(showgrid=False, title=None)
        fig.update_yaxes(showgrid=True, gridcolor="#E5E7EB", title=None)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.caption("Document register")
    columns = ["id", "title", "project", "discipline", "document_type", "version", "status", "file_name", "updated_at"]
    available = [column for column in columns if column in frame.columns]
    display = frame[available].copy()
    display.columns = [column.replace("_", " ").title() for column in available]
    st.dataframe(display, use_container_width=True, hide_index=True)

    discipline_counts = frame["discipline"].value_counts().rename("Documents").head(10)
    if len(discipline_counts) > 1:
        st.caption("Top disciplines")
        discipline_df = discipline_counts.reset_index()
        discipline_df.columns = ["Discipline", "Documents"]
        fig = px.bar(discipline_df, x="Discipline", y="Documents", color_discrete_sequence=["#2563EB"])
        fig.update_layout(height=180, margin=dict(l=5, r=5, t=5, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False, font=dict(size=9, color="#111827"))
        fig.update_xaxes(showgrid=False, title=None)
        fig.update_yaxes(showgrid=True, gridcolor="#E5E7EB", title=None)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_documents_module(database: dict[str, Any]) -> None:
    st.title("Documents")
    st.caption("Controlled project documents, revisions, status and searchable project records.")

    projects = project_options(database)
    project_labels = ["Unassigned"] + [project_label(project) for project in projects]

    with st.expander("Register document", expanded=True):
        with st.form("upload_doc_form", clear_on_submit=True):
            title = st.text_input("Document title", max_chars=200)
            project_choice = st.selectbox("Project", project_labels)
            discipline = st.text_input("Discipline", max_chars=100)
            status = st.selectbox("Status", DOCUMENT_STATUSES)
            uploaded_file = st.file_uploader("File", type=ALLOWED_TYPES)
            submitted = st.form_submit_button("Upload document", use_container_width=True)

        if submitted:
            if not title.strip() or uploaded_file is None:
                st.error("Document title and file are required.")
            else:
                document_id = next_id("documents", database)
                file_path = _save_uploaded_file(uploaded_file, document_id, 1)
                timestamp = now_iso()
                document = {
                    "id": document_id,
                    "project_id": _project_id(project_choice, projects, project_labels),
                    "title": title.strip(),
                    "project": project_choice if project_choice != "Unassigned" else "",
                    "discipline": discipline.strip(),
                    "status": status,
                    "document_type": _document_type(uploaded_file.name),
                    "version": 1,
                    "file_name": uploaded_file.name,
                    "file_path": file_path,
                    "created_at": timestamp,
                    "updated_at": timestamp,
                }
                version_record = {"id": next_id("document_versions", database), "document_id": document_id, "version": 1, "file_name": uploaded_file.name, "file_path": file_path, "uploaded_at": timestamp}
                try:
                    save_new_record(database, "documents", document)
                    save_new_record(database, "document_versions", version_record)
                    st.success("Document uploaded and registered.")
                    st.rerun()
                except Exception as exc:
                    try:
                        stored = _file_path(file_path)
                        if stored.exists():
                            stored.unlink()
                    except Exception:
                        pass
                    st.error("Unable to save document metadata.")
                    with st.expander("Technical details"):
                        st.exception(exc)

    documents = get_records("documents", database)
    if not documents:
        st.info("No documents have been registered yet.")
        return

    st.divider()
    _analytics(documents)

    st.divider()
    st.subheader("Manage documents")
    search = st.text_input("Search documents", key="documents_search", placeholder="Title, project, discipline, status or filename").strip().lower()
    visible = [document for document in documents if not search or search in str(document).lower()]
    if not visible:
        st.info("No documents match the current search.")
        return

    for document in visible:
        document_id = document.get("id")
        version = document.get("version", 1)
        with st.expander(f"{document.get('title', 'Untitled')} · v{version} · {document.get('status', 'Draft')}"):
            with st.form(f"document_edit_{document_id}"):
                edit_title = st.text_input("Document title", value=str(document.get("title", "")))
                current_project = "Unassigned"
                for project in projects:
                    if str(project.get("id")) == str(document.get("project_id")):
                        current_project = project_label(project)
                        break
                edit_project = st.selectbox("Project", project_labels, index=project_labels.index(current_project) if current_project in project_labels else 0)
                edit_discipline = st.text_input("Discipline", value=str(document.get("discipline", "")))
                current_status = document.get("status", "Draft")
                edit_status = st.selectbox("Status", DOCUMENT_STATUSES, index=DOCUMENT_STATUSES.index(current_status) if current_status in DOCUMENT_STATUSES else 0)
                save = st.form_submit_button("Save changes", use_container_width=True)
            if save:
                try:
                    saved = update_record("documents", document_id, {"title": edit_title.strip(), "project_id": _project_id(edit_project, projects, project_labels), "project": edit_project if edit_project != "Unassigned" else "", "discipline": edit_discipline.strip(), "status": edit_status, "updated_at": now_iso()}, database)
                    if saved is None:
                        st.error("Document not found.")
                    else:
                        st.success("Document updated.")
                        st.rerun()
                except Exception as exc:
                    st.error("Unable to update the document.")
                    with st.expander("Technical details"):
                        st.exception(exc)

            file_path_value = str(document.get("file_path", ""))
            if file_path_value:
                try:
                    stored_file = _file_path(file_path_value)
                except ValueError:
                    stored_file = None
                if stored_file and stored_file.exists():
                    with stored_file.open("rb") as handle:
                        st.download_button("Download current file", handle.read(), file_name=str(document.get("file_name") or stored_file.name), key=f"document_download_{document_id}", use_container_width=True)
                else:
                    st.warning("The document metadata exists, but its uploaded file is not available in this workspace.")

            if st.button("Delete document", key=f"document_delete_{document_id}", use_container_width=True):
                try:
                    versions = get_records("document_versions", database)
                    for version_record in [v for v in versions if str(v.get("document_id")) == str(document_id)]:
                        version_path = str(version_record.get("file_path", ""))
                        if version_path:
                            try:
                                stored_file = _file_path(version_path)
                                if stored_file.exists():
                                    stored_file.unlink()
                            except ValueError:
                                pass
                        delete_record("document_versions", version_record.get("id"), database)
                    if delete_record("documents", document_id, database):
                        st.success("Document deleted.")
                        st.rerun()
                    else:
                        st.warning("The document was already removed.")
                except Exception as exc:
                    st.error("Unable to delete the document.")
                    with st.expander("Technical details"):
                        st.exception(exc)
