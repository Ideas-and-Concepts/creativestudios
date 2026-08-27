import streamlit as st
from .database import save_memory

def render_engineering_module(database):
    st.header("⚙️ Engineering")

    # Create
    detail = st.text_area("New Engineering Detail")
    if st.button("Add Detail"):
        database.setdefault("engineering", []).append(detail)
        save_memory(database)
        st.success("Detail added!")

    # Read + Update + Delete
    if "engineering" in database and database["engineering"]:
        st.subheader("Manage Details")
        for i, detail in enumerate(database["engineering"]):
            with st.expander(f"Detail {i+1}"):
                new_detail = st.text_area("Edit Detail", value=detail, key=f"eng_{i}")
                if st.button("Update", key=f"update_eng_{i}"):
                    database["engineering"][i] = new_detail
                    save_memory(database)
                    st.success("Detail updated!")

                if st.button("Delete", key=f"delete_eng_{i}"):
                    database["engineering"].pop(i)
                    save_memory(database)
                    st.warning("Detail deleted!")
                    st.experimental_rerun()