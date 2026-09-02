"""
Creative Studios
Documents Module (self-contained)
"""

import json
import streamlit as st
from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "creativestudios_db.json"
STORAGE_DIR = BASE_DIR / "storage" / "documents"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
DOCUMENT_STATUSES = ["Draft", "Under Review", "Approved", "Superseded", "Archived"]


def _load_db():
    if DB_FILE.exists():
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"documents": [], "document_versions": [], "activity_log": []}


def _save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, default=str)


def _get_collection(collection, db):
    if collection not in db:
        db[collection] = []
    if not isinstance(db[collection], list):
        db[collection] = []
    return db[collection]


def _next_id(collection, db):
    records = _get_collection(collection, db)
    highest = 0
    for rec in records:
        if isinstance(rec, dict) and "id" in rec:
            try:
                highest = max(highest, int(rec["id"]))
            except (ValueError, TypeError):
                pass
    return highest + 1


def _add_record(collection, record, db):
    records = _get_collection(collection, db)
    record = dict(record)
    if "id" not in record or record["id"] is None:
        record["id"] = _next_id(collection, db)
    records.append(record)
    _save_db(db)
    return record


def _update_record(collection, record_id, updates, db):
    records = _get_collection(collection, db)
    for idx, rec in enumerate(records):
        if isinstance(rec, dict) and str(rec.get("id")) == str(record_id):
            rec.update(updates)
            _save_db(db)
            return rec
    return None


def _delete_record(collection, record_id, db):
    records = _get_collection(collection, db)
    for idx, rec in enumerate(records):
        if isinstance(rec, dict) and str(rec.get("id")) == str(record_id):
            records.pop(idx)
            _save_db(db)
            return True
    return False


def _log_activity(db, action, details=""):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details,
        "user": "System",
    }
    _get_collection("activity_log", db).append(entry)
    _save_db(db)


def _save_uploaded_file(uploaded_file, document_id, version):
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
    db = database

    documents = _get_collection("documents", db)

    # Upload form
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
                existing = next((d for d in documents if isinstance(d, dict) and d.get("title", "").lower() == title.lower()), None)
                if existing:
                    new_version = existing.get("version", 1) + 1
                    doc_id = existing["id"]
                    file_path = _save_uploaded_file(uploaded_file, doc_id, new_version)
                    version_record = {
                        "id": _next_id("document_versions", db),
                        "document_id": doc_id,
                        "version": new_version,
                        "file_path": file_path,
                        "uploaded_at": datetime.now().isoformat(),
                        "version_note": version_note,
                    }
                    _add_record("document_versions", version_record, db)
                    _update_record("documents", doc_id, {"version": new_version, "file_path": file_path, "status": status}, db)
                    _log_activity(db, "Document version uploaded", f"{title} v{new_version}")
                    st.success(f"Version {new_version} uploaded for '{title}'.")
                else:
                    doc_id = _next_id("documents", db)
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
                    _add_record("documents", document, db)
                    version_record = {
                        "id": _next_id("document_versions", db),
                        "document_id": doc_id,
                        "version": 1,
                        "file_path": file_path,
                        "uploaded_at": datetime.now().isoformat(),
                        "version_note": version_note,
                    }
                    _add_record("document_versions", version_record, db)
                    _log_activity(db, "Document uploaded", title)
                    st.success(f"Document '{title}' uploaded.")
                st.rerun()

    # List documents: filter only dicts
    valid_documents = [d for d in documents if isinstance(d, dict)]
    if not valid_documents:
        st.info("No documents found.")
        return

    st.subheader("Document Library")
    for idx, doc in enumerate(valid_documents):
        doc_id = doc.get("id")
        with st.expander(f"{doc.get('title', 'Untitled')} (v{doc.get('version', 1)})"):
            st.write(f"**Project:** {doc.get('project', 'N/A')}")
            st.write(f"**Discipline:** {doc.get('discipline', 'N/A')}")
            st.write(f"**Status:** {doc.get('status', 'N/A')}")
            st.write(f"**File:** {doc.get('file_path', 'N/A')}")

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

            versions = [v for v in _get_collection("document_versions", db) if isinstance(v, dict) and v.get("document_id") == doc_id]
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
                                    key=f"download_{v['id']}_{idx}",
                                )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Edit", key=f"edit_doc_{doc_id}_{idx}"):
                    st.session_state["edit_doc_id"] = doc_id
            with col2:
                if st.button("Delete", key=f"del_doc_{doc_id}_{idx}"):
                    if doc.get("file_path"):
                        fpath = BASE_DIR / doc["file_path"]
                        if fpath.exists():
                            fpath.unlink()
                    _delete_record("documents", doc_id, db)
                    _log_activity(db, "Document deleted", doc.get("title", ""))
                    st.success("Document deleted.")
                    st.rerun()

    # Edit form
    if "edit_doc_id" in st.session_state:
        edit_doc_id = st.session_state["edit_doc_id"]
        doc = next((d for d in valid_documents if d.get("id") == edit_doc_id), None)
        if doc:
            st.subheader(f"Edit Document: {doc.get('title', '')}")
            with st.form("edit_doc_form"):
                title = st.text_input("Title", value=doc.get("title", ""))
                project = st.text_input("Project", value=doc.get("project", ""))
                discipline = st.text_input("Discipline", value=doc.get("discipline", ""))
                status_idx = DOCUMENT_STATUSES.index(doc.get("status", "Draft")) if doc.get("status") in DOCUMENT_STATUSES else 0
                status = st.selectbox("Status", DOCUMENT_STATUSES, index=status_idx)
                update = st.form_submit_button("Update Document")

            if update:
                _update_record(
                    "documents",
                    edit_doc_id,
                    {
                        "title": title.strip(),
                        "project": project.strip(),
                        "discipline": discipline.strip(),
                        "status": status,
                    },
                    db,
                )
                _log_activity(db, "Document updated", title)
                st.success("Document updated.")
                del st.session_state["edit_doc_id"]
                st.rerun()