import streamlit as st
from .database import save_memory

def render_drawings_module(database):
    st.header("🖼️ Drawings")

    # Create
    drawing_name = st.text_input("New Drawing Name")
    if st.button("Add Drawing"):
        database.setdefault("drawings", []).append(drawing_name)
        save_memory(database)
        st.success(f"Drawing '{drawing_name}' added!")

    # Read + Update + Delete
    if "drawings" in database and database["drawings"]:
        st.subheader("Manage Drawings")
        for i, drawing in enumerate(database["drawings"]):
            with st.expander(f"Drawing: {drawing}"):
                new_name = st.text_input("Edit Name", value=drawing, key=f"drawing_{i}")
                if st.button("Update", key=f"update_drawing_{i}"):
                    database["drawings"][i] = new_name
                    save_memory(database)
                    st.success("Drawing updated!")

                if st.button("Delete", key=f"delete_drawing_{i}"):
                    database["drawings"].pop(i)
                    save_memory(database)
                    st.warning("Drawing deleted!")
                    st.experimental_rerun()