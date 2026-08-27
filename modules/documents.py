import streamlit as st
from .database import save_memory
def render_documents_module(database): ...

# ============================================================
# DOCUMENTS MODULE
# ============================================================

def render_documents_module(database: dict[str, Any]) -> None:
    """Render Documents module for managing project files and approvals."""

    st.header("Documents")

    projects = database.get("projects", [])
    if not projects:
        st.info("No projects available.")
        return

    # Select project
    project_names = [p.get("name", "Unnamed Project") for p in projects]
    selected_project = st.selectbox("Select Project", project_names)

    project = next((p for p in projects if p.get("name") == selected_project), None)
    if not project:
        st.warning("Project not found.")
        return

    documents = project.get("documents", [])

    # Display documents
    st.subheader("Project Documents")
    if documents:
        df = pd.DataFrame(documents)
        st.dataframe(df)
    else:
        st.caption("No documents uploaded yet.")

    # Add new document form
    with st.form("add_document", clear_on_submit=True):
        title = st.text_input("Document Title")
        filename = st.text_input("Filename")
        phase = st.selectbox("Phase", ["Planning", "Design", "Construction"])
        status = st.selectbox("Status", ["Pending", "Approved"])
        author = st.text_input("Author")
        submitted = st.form_submit_button("Add Document")

        if submitted and title and filename:
            new_doc = {
                "title": title,
                "filename": filename,
                "phase": phase,
                "status": status,
                "author": author
            }
            documents.append(new_doc)
            project["documents"] = documents
            save_memory(database)
            st.success(f"Added document: {title} ({status})")

    # Update document status
    if documents:
        st.subheader("Update Document Status")
        doc_titles = [d["title"] for d in documents]
        selected_doc = st.selectbox("Select Document", doc_titles)
        new_status = st.selectbox("New Status", ["Pending", "Approved"])
        if st.button("Update Status"):
            for d in documents:
                if d["title"] == selected_doc:
                    d["status"] = new_status
                    save_memory(database)
                    st.success(f"Updated {selected_doc} to {new_status}")