"""Creative Studios Documents Module.

Documents use the shared workspace database so metadata is persisted through
Neon PostgreSQL when DATABASE_URL is configured. Uploaded file bytes remain in
Streamlit's local workspace storage.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st

from modules.database import delete_record, get_records, next_id
from modules.module_utils import now_iso, project_label, project_options, save_new_record

BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "storage" / "documents"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

DOCUMENT_STATUSES = ["Draft", "Under Review", "Approved", "Superseded", "Archived"]
DOCUMENT_TYPES = ["PDF", "Word", "Excel", "Image", "Other"]


def _document_type(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        return "PDF"
    if suffix == ".docx":
        return "Word"
    if suffix == ".xlsx":
        return "Excel"
    if suffix in {".png", ".jpg", ".jpeg"}:
        return "Image"
    return "Other"


def _save_uploaded_file(uploaded_file: Any, document_id: int, version: int) -> str:
    extension = Path(uploaded_file.name).suffix.lower()
    filename = f"doc_{document_id}_v{version}{extension}"
    file_path = STORAGE_DIR / filename
    with file_path.open("wb") as handle:
        handle.write(uploaded_file.getbuffer())
    return str(file_path.relative_to(BASE_DIR))


def _file_path(relative_path: str) -> Path:
    """Resolve a stored path while preventing traversal outside the workspace."""
    candidate = (BASE_DIR / relative_path).resolve()
    storage_root = STORAGE_DIR.resolve()
    if candidate != storage_root and storage_root not in candidate.parents:
        raise ValueError("Invalid document storage path.")
    return candidate


def _project_index(database: dict[str, Any], project_id: int | None) -> int:
    projects = project_options(database)
    if project_id is None:
        return 0
    for index, project in enumerate(projects):
        if str(project.get("id")) == str(project_id):
            return index
    return 0


def render_documents_module(database: dict[str, Any]) -> None:
    st.title("Documents")
    st.caption("Controlled project documents, file uploads, revisions and document status.")

    projects = project_options(database)
    project_labels = ["Unassigned"] + [project_label(project) for project in projects]

    st.subheader("Register Document")
    with st.form("upload_doc_form", clear_on_submit=True):
        title = st.text_input("Document Title")
        project_choice = st.selectbox("Project", project_labels)
        discipline = st.text_input("Discipline")
        status = st.selectbox("Status", DOCUMENT_STATUSES)
        uploaded_file = st.file_uploader(
            "File",
            type=["pdf", "docx", "xlsx", "png", "jpg", "jpeg"],
        )
        submitted = st.form_submit_button("Upload Document", use_container_width=True)

    if submitted:
        if not title.strip() or uploaded_file is None:
            st.error("Document title and file are required.")
        else:
            project_id: int | None = None
            if project_choice != "Unassigned":
                selected_project = projects[project_labels.index(project_choice) - 1]
                project_id = int(selected_project["id"])

            document_id = next_id("documents", database)
            version = 1
            file_path = _save_uploaded_file(uploaded_file, document_id, version)
            timestamp = now_iso()
            document = {
                "id": document_id,
                "project_id": project_id,
                "title": title.strip(),
                "project": project_choice if project_choice != "Unassigned" else "",
                "discipline": discipline.strip(),
                "status": status,
                "document_type": _document_type(uploaded_file.name),
                "version": version,
                "file_name": uploaded_file.name,
                "file_path": file_path,
                "created_at": timestamp,
                "updated_at": timestamp,
            }
            version_record = {
                "id": next_id("document_versions", database),
                "document_id": document_id,
                "version": version,
                "file_name": uploaded_file.name,
                "file_path": file_path,
                "uploaded_at": timestamp,
            }

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
                st.error("Unable to save the document metadata.")
                with st.expander("Technical details"):
                    st.exception(exc)

    documents = get_records("documents", database)
    if not documents:
        st.info("No documents have been registered yet.")
        return

    st.divider()
    st.subheader("Document Library")
    search = st.text_input("Search Documents", key="documents_search").strip().lower()
    visible = [
        document
        for document in documents
        if not search or search in str(document).lower()
    ]

    if not visible:
        st.info("No documents match the current search.")
        return

    for document in list(visible):
        document_id = document.get("id")
        version = document.get("version", 1)
        with st.expander(
            f"{document.get('title', 'Untitled')} | v{version} | {document.get('status', 'Draft')}"
        ):
            with st.form(f"document_edit_{document_id}"):
                title = st.text_input("Document Title", value=str(document.get("title", "")))
                project_id_value = document.get("project_id")
                current_project = "Unassigned"
                for project in projects:
                    if str(project.get("id")) == str(project_id_value):
                        current_project = project_label(project)
                        break
                project_index = project_labels.index(current_project) if current_project in project_labels else 0
                project_choice = st.selectbox("Project", project_labels, index=project_index)
                discipline = st.text_input("Discipline", value=str(document.get("discipline", "")))
                status = st.selectbox(
                    "Status",
                    DOCUMENT_STATUSES,
                    index=DOCUMENT_STATUSES.index(document.get("status", "Draft"))
                    if document.get("status") in DOCUMENT_STATUSES
                    else 0,
                )
                save = st.form_submit_button("Save Changes", use_container_width=True)

            if save:
                from modules.database import update_record

                selected_project_id: int | None = None
                if project_choice != "Unassigned":
                    selected_project = projects[project_labels.index(project_choice) - 1]
                    selected_project_id = int(selected_project["id"])

                try:
                    saved = update_record(
                        "documents",
                        document_id,
                        {
                            "title": title.strip(),
                            "project_id": selected_project_id,
                            "project": project_choice if project_choice != "Unassigned" else "",
                            "discipline": discipline.strip(),
                            "status": status,
                            "updated_at": now_iso(),
                        },
                        database,
                    )
                    if saved is None:
                        st.error("The document could not be found.")
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
                        st.download_button(
                            "Download Current File",
                            data=handle.read(),
                            file_name=str(document.get("file_name") or stored_file.name),
                            key=f"document_download_{document_id}",
                            use_container_width=True,
                        )
                else:
                    st.warning("The document metadata exists, but its uploaded file is not available in this workspace.")

            if st.button("Delete Document", key=f"document_delete_{document_id}", use_container_width=True):
                try:
                    versions = get_records("document_versions", database)
                    version_records = [
                        version_record
                        for version_record in versions
                        if str(version_record.get("document_id")) == str(document_id)
                    ]
                    for version_record in version_records:
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
