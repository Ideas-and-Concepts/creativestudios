import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
from pathlib import Path
from datetime import datetime
from .database import save_memory

# Locate logo
BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
LOGO_PATH = ASSETS_DIR / "creative_studios.png"

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
            fig = px.timeline(
                df,
                x_start="start",
                x_end="end",
                y="phase",
                color="status",
                title="Construction Phases Timeline",
                color_discrete_map={
                    "Pending": "gray",
                    "In Progress": "blue",
                    "Completed": "green",
                }
            )
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig, use_container_width=True)

            # --- Summary Table ---
            st.subheader("Phase Summary")
            st.dataframe(df[["phase", "boq", "status", "start", "end"]])

            # --- Export to CSV ---
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Construction Schedule as CSV",
                data=csv,
                file_name="construction_schedule.csv",
                mime="text/csv",
            )

            # --- Export to PDF with Cover Page ---
            pdf = FPDF()
            pdf.add_page()

            # Cover page
            if LOGO_PATH.exists():
                pdf.image(str(LOGO_PATH), x=80, y=30, w=50)
            pdf.set_font("Arial", "B", 18)
            pdf.ln(90)
            pdf.cell(200, 10, "Creative Studios", ln=True, align="C")
            pdf.set_font("Arial", "I", 14)
            pdf.cell(200, 10, "Construction Schedule Report", ln=True, align="C")
            pdf.ln(10)
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="C")

            # New page for table
            pdf.add_page()
            pdf.set_font("Arial", "B", 14)
            pdf.cell(200, 10, "Phase Details", ln=True, align="C")
            pdf.ln(10)

            # Table header
            pdf.set_font("Arial", "B", 10)
            for col in ["Phase", "BoQ", "Status", "Start", "End"]:
                pdf.cell(38, 8, col, border=1)
            pdf.ln()

            # Table rows
            pdf.set_font("Arial", size=10)
            for _, row in df.iterrows():
                pdf.cell(38, 8, str(row["phase"]), border=1)
                pdf.cell(38, 8, str(row["boq"]), border=1)
                pdf.cell(38, 8, str(row["status"]), border=1)
                pdf.cell(38, 8, str(row["start"].date()), border=1)
                pdf.cell(38, 8, str(row["end"].date()), border=1)
                pdf.ln()

            pdf_bytes = pdf.output(dest="S").encode("latin-1")
            st.download_button(
                label="Download Construction Schedule as PDF",
                data=pdf_bytes,
                file_name="construction_schedule.pdf",
                mime="application/pdf",
            )