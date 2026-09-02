"""
Creative Studios
Documents Module

Supports document upload, metadata, and versioning.
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
import shutil
import os
from .database import (
    get_collection,
    add_record,
    update_record,
    delete_record,
    next_id,
    save_memory,
)


DOCUMENT_STATUSES = ["Draft", "Under Review", "Approved", "Superseded", "Archived"]

BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "storage" / "documents"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def _log_activity(database, action, details=""):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details,
        "user": "System",
    }
    database.setdefault("activity_log", []).append(entry)
    save_memory(database)


def _save_uploaded_file(uploaded_file, document_id, version):
    """Save uploaded file to storage directory and return relative path."""
    if uploaded_file is None:
        return ""
    file_ext = Path(uploaded_file.name).suffix
    filename = f"doc_{document_id}_v{version}{file_ext}"
    file_path = STORAGE_DIR / filename
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return str(file_path.relative_to(BASE_DIR))


def render_documents_module(database):
    st.header("Documents")

    documents = get_collection("documents", database)

    # -------- Upload / Create Document --------
    with st.expander("New Document", expanded=False):
        with st.form("document_upload_form", clear_on_submit=True):
            title = st.text_input("Document Title")
            project = st.text_input("Project")
            discipline = st.text_input("Discipline")
            status = st.selectbox("Status", DOCUMENT_STATUSES, index=0)
            version_note = st.text_input("Version Note (optional)")
            uploaded_file = st.file_uploader("Choose file", type=["pdf", "docx", "xlsx", "png", "jpg", "dwg", "rvt"])
            submitted = st.form_submit_button("Upload Document")

        if submitted:
            if not title.strip():
                st.error("Title is required.")
            elif uploaded_file is None:
                st.error("Please select a file.")
            else:
                # Check if title already exists (versioning)
                existing = next((d for d in documents if d.get("title", "").lower() == title.lower()), None)
                if existing:
                    # Create new version
                    new_version = existing.get("version", 1) + 1
                    doc_id = existing["id"]
                    file_path = _save_uploaded_file(uploaded_file, doc_id, new_version)
                    # Add version record
                    version_record = {
                        "id": next_id("document_versions", database),
                        "document_id": doc_id,
                        "version": new_version,
                        "file_path": file_path,
                        "uploaded_at": datetime.now().isoformat(),
                        "version_note": version_note,
                    }
                    add_record("document_versions", version_record, database)
                    # Update main document record
                    update_record(
                        "documents",
                        doc_id,
                        {
                            "version": new_version,
                            "file_path": file_path,
                            "status": status,
                        },
                        database,
                    )
                    _log_activity(database, "Document version uploaded", f"{title} v{new_version}")
                    st.success(f"Version {new_version} uploaded for '{title}'.")
                else:
                    # New document
                    doc_id = next_id("documents", database)
                    file_path = _save_uploaded_file(uploaded_file, doc_id, 1)
                    document = {
                        "id": doc_id,
                        "title": title.strip(),
                        "project": project.strip(),
                        "discipline": discipline.strip(),
                        "status": status,
                        "version": 1,
                        "file_path": file_path,
                        "created_at": datetime.now().isoformat(),
                    }
                    add_record("documents", document, database)
                    version_record = {
                        "id": next_id("document_versions", database),
                        "document_id": doc_id,
                        "version": 1,
                        "file_path": file_path,
                        "uploaded_at": datetime.now().isoformat(),
                        "version_note": version_note,
                    }
                    add_record("document_versions", version_record, database)
                    _log_activity(database, "Document uploaded", title)
                    st.success(f"Document '{title}' uploaded.")
                st.rerun()

    # -------- Document List --------
    if not documents:
        st.info("No documents found.")
        return

    st.subheader("Document Library")
    for doc in documents:
        with st.expander(f"{doc.get('title', 'Untitled')} (v{doc.get('version', 1)})"):
            st.write(f"**Project:** {doc.get('project', 'N/A')}")
            st.write(f"**Discipline:** {doc.get('discipline', 'N/A')}")
            st.write(f"**Status:** {doc.get('status', 'N/A')}")
            st.write(f"**File:** {doc.get('file_path', 'N/A')}")

            # Download current version
            if doc.get("file_path"):
                file_path = BASE_DIR / doc["file_path"]
                if file_path.exists():
                    with open(file_path, "rb") as f:
                        st.download_button(
                            label="Download Current Version",
                            data=f,
                            file_name=file_path.name,
                            mime="application/octet-stream",
                        )

            # Version history
            versions = [v for v in get_collection("document_versions", database) if v.get("document_id") == doc["id"]]
            if versions:
                st.markdown("**Version History:**")
                for v in sorted(versions, key=lambda x: x["version"], reverse=True):
                    st.write(f"- v{v['version']} ({v['uploaded_at']}) - {v.get('version_note','')}")
                    if v.get("file_path"):
                        fpath = BASE_DIR / v["file_path"]
                        if fpath.exists():
                            with open(fpath, "rb") as f:
                                st.download_button(
                                    label=f"Download v{v['version']}",
                                    data=f,
                                    file_name=fpath.name,
                                    key=f"download_{v['id']}",
                                )

            # Edit/Delete
            edit_col, del_col = st.columns(2)
            with edit_col:
                if st.button("Edit", key=f"edit_doc_{doc['id']}"):
                    st.session_state["edit_doc_id"] = doc["id"]
            with del_col:
                if st.button("Delete", key=f"del_doc_{doc['id']}"):
                    # Delete file from storage
                    if doc.get("file_path"):
                        fpath = BASE_DIR / doc["file_path"]
                        if fpath.exists():
                            fpath.unlink()
                    delete_record("documents", doc["id"], database)
                    _log_activity(database, "Document deleted", doc.get("title", ""))
                    st.success("Document deleted.")
                    st.rerun()

    # -------- Edit Document (inline) --------
    if "edit_doc_id" in st.session_state:
        doc_id = st.session_state["edit_doc_id"]
        doc = next((d for d in documents if d["id"] == doc_id), None)
        if doc:
            st.subheader(f"Edit Document: {doc['title']}")
            with st.form("edit_doc_form"):
                title = st.text_input("Title", value=doc.get("title", ""))
                project = st.text_input("Project", value=doc.get("project", ""))
                discipline = st.text_input("Discipline", value=doc.get("discipline", ""))
                status_idx = DOCUMENT_STATUSES.index(doc.get("status", "Draft")) if doc.get("status") in DOCUMENT_STATUSES else 0
                status = st.selectbox("Status", DOCUMENT_STATUSES, index=status_idx)
                update = st.form_submit_button("Update Document")

            if update:
                update_record(
                    "documents",
                    doc_id,
                    {
                        "title": title.strip(),
                        "project": project.strip(),
                        "discipline": discipline.strip(),
                        "status": status,
                    },
                    database,
                )
                _log_activity(database, "Document updated", title)
                st.success("Document updated.")
                del st.session_state["edit_doc_id"]
                st.rerun()