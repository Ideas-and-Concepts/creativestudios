"""
Creative Studios
Construction Management Module

Tracks construction phases, timelines, and progress with project selection.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
from pathlib import Path
from datetime import datetime
from .database import save_memory
from .database import get_collection


BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
LOGO_PATH = ASSETS_DIR / "creative_studios.png"


def _log_activity(database, action: str, details: str = ""):
    """Record an activity in the global log."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details,
        "user": "System",  # No authentication
    }
    database.setdefault("activity_log", []).append(entry)
    save_memory(database)


def render_construction_module(database):
    st.header("Construction Management")

    # Project selection
    projects = get_collection("projects", database)
    if not projects:
        st.warning("No projects found. Create a project first in the Projects module.")
        return

    project_names = {p.get("name", f"Project {p.get('id')}"): p.get("id") for p in projects}
    selected_project_name = st.selectbox("Select Project", list(project_names.keys()))
    project_id = project_names[selected_project_name]

    # Get construction phases for selected project
    all_phases = get_collection("construction", database)
    phases = [p for p in all_phases if p.get("project_id") == project_id]

    # ==================== CREATE ====================
    st.subheader("Add New Construction Phase")
    with st.form("add_phase_form", clear_on_submit=True):
        phase_name = st.text_input("Phase Name", placeholder="e.g., Foundation, Columns")
        boq_item = st.text_input("BoQ Item Reference", placeholder="e.g., 02.01.001")
        status = st.selectbox("Status", ["Pending", "In Progress", "Completed"], index=0)
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")
        submitted = st.form_submit_button("Add Phase")

    if submitted:
        if not phase_name.strip():
            st.error("Phase name is required.")
        else:
            new_phase = {
                "id": len(all_phases) + 1,
                "project_id": project_id,
                "phase": phase_name.strip(),
                "boq": boq_item.strip(),
                "status": status,
                "start": str(start_date),
                "end": str(end_date),
                "created_at": datetime.now().isoformat(),
            }
            all_phases.append(new_phase)
            database["construction"] = all_phases
            save_memory(database)
            _log_activity(database, "Construction phase added", f"{phase_name} for project {selected_project_name}")
            st.success(f"Phase '{phase_name}' added!")
            st.rerun()

    # ==================== READ / UPDATE / DELETE ====================
    if phases:
        st.subheader("Manage Construction Phases")
        for i, phase in enumerate(phases):
            with st.expander(f"Phase: {phase['phase']} ({phase['status']})"):
                col1, col2 = st.columns(2)
                with col1:
                    new_phase = st.text_input("Phase Name", value=phase["phase"], key=f"phase_{phase['id']}")
                    new_boq = st.text_input("BoQ Reference", value=phase["boq"], key=f"boq_{phase['id']}")
                    status_options = ["Pending", "In Progress", "Completed"]
                    idx = status_options.index(phase["status"]) if phase["status"] in status_options else 0
                    new_status = st.selectbox("Status", status_options, index=idx, key=f"status_{phase['id']}")
                with col2:
                    new_start = st.date_input("Start Date", value=pd.to_datetime(phase["start"]).date(), key=f"start_{phase['id']}")
                    new_end = st.date_input("End Date", value=pd.to_datetime(phase["end"]).date(), key=f"end_{phase['id']}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Update", key=f"update_phase_{phase['id']}"):
                        phase["phase"] = new_phase.strip()
                        phase["boq"] = new_boq.strip()
                        phase["status"] = new_status
                        phase["start"] = str(new_start)
                        phase["end"] = str(new_end)
                        save_memory(database)
                        _log_activity(database, "Construction phase updated", f"{new_phase}")
                        st.success("Phase updated!")
                        st.rerun()
                with col2:
                    if st.button("Delete", key=f"delete_phase_{phase['id']}"):
                        all_phases = [p for p in all_phases if p.get("id") != phase["id"]]
                        database["construction"] = all_phases
                        save_memory(database)
                        _log_activity(database, "Construction phase deleted", f"{phase['phase']}")
                        st.warning("Phase deleted!")
                        st.rerun()

        # ==================== GANTT CHART ====================
        st.subheader("Construction Timeline (Gantt Chart)")
        if phases:
            df = pd.DataFrame(phases)
            df["start"] = pd.to_datetime(df["start"])
            df["end"] = pd.to_datetime(df["end"])
            fig = px.timeline(
                df,
                x_start="start",
                x_end="end",
                y="phase",
                color="status",
                title=f"Construction Timeline: {selected_project_name}",
                color_discrete_map={
                    "Pending": "gray",
                    "In Progress": "blue",
                    "Completed": "green",
                }
            )
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig, use_container_width=True)

            # ==================== SUMMARY TABLE ====================
            st.subheader("Phase Summary")
            st.dataframe(df[["phase", "boq", "status", "start", "end"]], use_container_width=True)

            # ==================== EXPORT CSV ====================
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Construction Schedule as CSV",
                data=csv,
                file_name="construction_schedule.csv",
                mime="text/csv",
            )

            # ==================== EXPORT PDF ====================
            if st.button("Generate PDF Report"):
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
                pdf.cell(200, 10, f"Project: {selected_project_name}", ln=True, align="C")
                pdf.cell(200, 10, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="C")

                # Table page
                pdf.add_page()
                pdf.set_font("Arial", "B", 14)
                pdf.cell(200, 10, "Phase Details", ln=True, align="C")
                pdf.ln(10)

                # Table header
                pdf.set_font("Arial", "B", 10)
                headers = ["Phase", "BoQ", "Status", "Start", "End"]
                col_widths = [40, 40, 30, 40, 40]
                for i, header in enumerate(headers):
                    pdf.cell(col_widths[i], 8, header, border=1)
                pdf.ln()

                # Table rows
                pdf.set_font("Arial", size=10)
                for _, row in df.iterrows():
                    pdf.cell(col_widths[0], 8, str(row["phase"]), border=1)
                    pdf.cell(col_widths[1], 8, str(row["boq"]), border=1)
                    pdf.cell(col_widths[2], 8, str(row["status"]), border=1)
                    pdf.cell(col_widths[3], 8, str(row["start"].date()), border=1)
                    pdf.cell(col_widths[4], 8, str(row["end"].date()), border=1)
                    pdf.ln()

                pdf_bytes = pdf.output(dest="S").encode("latin-1")
                st.download_button(
                    label="Download Construction Schedule as PDF",
                    data=pdf_bytes,
                    file_name="construction_schedule.pdf",
                    mime="application/pdf",
                )
    else:
        st.info("No construction phases for this project yet.")