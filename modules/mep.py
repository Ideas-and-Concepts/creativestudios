import streamlit as st
from .database import save_memory

def render_mep_module(database):
    st.header("🔌 MEP")

    # Create
    system = st.text_input("New MEP System")
    if st.button("Add System"):
        database.setdefault("mep", []).append(system)
        save_memory(database)
        st.success(f"System '{system}' added!")

    # Read + Update + Delete
    if "mep" in database and database["mep"]:
        st.subheader("Manage Systems")
        for i, system in enumerate(database["mep"]):
            with st.expander(f"System: {system}"):
                new_system = st.text_input("Edit System", value=system, key=f"mep_{i}")
                if st.button("Update", key=f"update_mep_{i}"):
                    database["mep"][i] = new_system
                    save_memory(database)
                    st.success("System updated!")

                if st.button("Delete", key=f"delete_mep_{i}"):
                    database["mep"].pop(i)
                    save_memory(database)
                    st.warning("System deleted!")
                    st.experimental_rerun()