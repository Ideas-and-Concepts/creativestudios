import streamlit as st
from .database import save_memory

def render_architecture_module(database):
    st.header("🏛️ Architecture")

    # Create
    note = st.text_area("New Architecture Note")
    if st.button("Add Note"):
        database.setdefault("architecture", []).append(note)
        save_memory(database)
        st.success("Note added!")

    # Read + Update + Delete
    if "architecture" in database and database["architecture"]:
        st.subheader("Manage Notes")
        for i, note in enumerate(database["architecture"]):
            with st.expander(f"Note {i+1}"):
                new_note = st.text_area("Edit Note", value=note, key=f"arch_{i}")
                if st.button("Update", key=f"update_arch_{i}"):
                    database["architecture"][i] = new_note
                    save_memory(database)
                    st.success("Note updated!")

                if st.button("Delete", key=f"delete_arch_{i}"):
                    database["architecture"].pop(i)
                    save_memory(database)
                    st.warning("Note deleted!")
                    st.experimental_rerun()