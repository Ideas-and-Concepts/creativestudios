"""
Creative Studios
Documents Module (simplified)
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
    return {"documents": [], "document_versions": []}


def _save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, default=str)


def _get_collection(collection, db):
    if collection not in db:
        db[collection] = []
    return db[collection]


def _next_id(collection, db):
    records = _get_collection(collection, db)
    highest = 0
    for rec in records:
        if isinstance(rec, dict) and "id" in rec:
            try:
                highest = max(highest, int(rec["id"]))
            except:
                pass
    return highest + 1


def _save_uploaded_file(uploaded_file, doc_id, version):
    if uploaded_file is None:
        return ""
    file_ext = Path(uploaded_file.name).suffix
    filename = f"doc_{doc_id}_v{version}{file_ext}"
    file_path = STORAGE_DIR / filename
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return str(file_path.relative_to(BASE_DIR))


def render_documents_module(database):
    st.header("Documents")
    db = database

    # Upload form
    with st.form("upload_doc_form"):
        title = st.text_input("Document Title")
        project = st.text_input("Project")
        discipline = st.text_input("Discipline")
        status = st.selectbox("Status", DOCUMENT_STATUSES)
        uploaded_file = st.file_uploader("File", type=["pdf", "docx", "xlsx", "png", "jpg"])
        submitted = st.form_submit_button("Upload")

    if submitted:
        if not title.strip() or uploaded_file is None:
            st.error("Title and file required.")
        else:
            documents = _get_collection("documents", db)
            doc_id = _next_id("documents", db)
            file_path = _save_uploaded_file(uploaded_file, doc_id, 1)
            doc = {
                "id": doc_id,
                "title": title.strip(),
                "project": project.strip(),
                "discipline": discipline.strip(),
                "status": status,
                "version": 1,
                "file_path": file_path,
                "created_at": datetime.now().isoformat(),
            }
            documents.append(doc)
            # Also store version record
            versions = _get_collection("document_versions", db)
            versions.append({
                "id": _next_id("document_versions", db),
                "document_id": doc_id,
                "version": 1,
                "file_path": file_path,
                "uploaded_at": datetime.now().isoformat(),
            })
            _save_db(db)
            st.success("Document uploaded.")
            st.rerun()

    # List documents
    documents = _get_collection("documents", db)
    if not documents:
        st.info("No documents.")
        return

    st.subheader("Document Library")
    for i, doc in enumerate(documents):
        if not isinstance(doc, dict):
            continue
        with st.expander(f"{doc.get('title','Untitled')} (v{doc.get('version',1)})"):
            st.write(f"**Project:** {doc.get('project','')}")
            st.write(f"**Discipline:** {doc.get('discipline','')}")
            st.write(f"**Status:** {doc.get('status','')}")
            st.write(f"**File:** {doc.get('file_path','')}")
            # Download current file if exists
            if doc.get("file_path"):
                fpath = BASE_DIR / doc["file_path"]
                if fpath.exists():
                    with open(fpath, "rb") as f:
                        st.download_button(
                            label="Download",
                            data=f,
                            file_name=fpath.name,
                            key=f"down_{i}"
                        )
            if st.button("Delete", key=f"del_doc_{i}"):
                # Remove file
                if doc.get("file_path"):
                    fpath = BASE_DIR / doc["file_path"]
                    if fpath.exists():
                        fpath.unlink()
                documents.pop(i)
                _save_db(db)
                st.success("Deleted.")
                st.rerun()