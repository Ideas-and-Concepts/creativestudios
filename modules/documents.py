import streamlit as st
from .database import save_memory

def render_documents_module(database):
    st.header("📄 Documents")

    # Create
    uploaded_file = st.file_uploader("Upload Document")
    if uploaded_file and st.button("Add Document"):
        database.setdefault("documents", []).append(uploaded_file.name)
        save_memory(database)
        st.success(f"Document '{uploaded_file.name}' added!")

    # Read + Update + Delete
    if "documents" in database and database["documents"]:
        st.subheader("Manage Documents")
        for i, doc in enumerate(database["documents"]):
            with st.expander(f"Document: {doc}"):
                new_name = st.text_input("Edit Name", value=doc, key=f"doc_{i}")
                if st.button("Update", key=f"update_doc_{i}"):
                    database["documents"][i] = new_name
                    save_memory(database)
                    st.success("Document updated!")

                if st.button("Delete", key=f"delete_doc_{i}"):
                    database["documents"].pop(i)
                    save_memory(database)
                    st.warning("Document deleted!")
                    st.experimental_rerun()