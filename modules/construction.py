import streamlit as st
import pandas as pd
import plotly.express as px
from .database import save_memory

def render_construction_module(database):
    st.header("Construction Management")

    # Create
    phase = st.text_input("New Construction Phase")
    boq_item = st.text_input("BoQ Item")
    status = st.selectbox("Status", ["Pending", "In Progress", "Completed"])
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")

    if st.button("Add Phase"):
        new_phase = {
            "phase": phase,
            "boq": boq_item,
            "status": status,
            "start": str(start_date),
            "end": str(end_date),
        }
        database.setdefault("construction", []).append(new_phase)
        save_memory(database)
        st.success(f"Phase '{phase}' added!")

    # Read + Update + Delete
    if "construction" in database and database["construction"]:
        st.subheader("Manage Construction Phases")
        for i, phase in enumerate(database["construction"]):
            with st.expander(f"Phase: {phase['phase']}"):
                new_phase = st.text_input("Edit Phase", value=phase["phase"], key=f"phase_{i}")
                new_boq = st.text_input("Edit BoQ", value=phase["boq"], key=f"boq_{i}")
                new_status = st.selectbox("Status", ["Pending", "In Progress", "Completed"],
                                          index=["Pending","In Progress","Completed"].index(phase["status"]),
                                          key=f"status_{i}")
                new_start = st.date_input("Start Date", value=pd.to_datetime(phase["start"]), key=f"start_{i}")
                new_end = st.date_input("End Date", value=pd.to_datetime(phase["end"]), key=f"end_{i}")

                if st.button("Update", key=f"update_phase_{i}"):
                    phase["phase"] = new_phase
                    phase["boq"] = new_boq
                    phase["status"] = new_status
                    phase["start"] = str(new_start)
                    phase["end"] = str(new_end)
                    save_memory(database)
                    st.success("Phase updated!")

                if st.button("Delete", key=f"delete_phase_{i}"):
                    database["construction"].pop(i)
                    save_memory(database)
                    st.warning("Phase deleted!")
                    st.experimental_rerun()

        # --- Gantt Chart ---
        st.subheader("Construction Timeline")
        df = pd.DataFrame(database["construction"])
        if not df.empty:
            df["start"] = pd.to_datetime(df["start"])
            df["end"] = pd.to_datetime(df["end"])
            fig = px.timeline(df, x_start="start", x_end="end", y="phase", color="status", title="Construction Phases Timeline")
            fig.update_yaxes(autorange="reversed")  # Gantt style
            st.plotly_chart(fig, use_container_width=True)