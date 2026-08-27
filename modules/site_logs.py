"""
Daily Site Logs Module
Records daily construction site activity, weather conditions, workforce headcounts, and safety incidents.
"""

from __future__ import annotations
import datetime
import streamlit as st


def render_site_logs_module(db: dict) -> None:
    st.markdown("## Daily Site Logs")
    st.caption("Record daily site activity, weather logs, contractor manpower, equipment utilization, and field issues.")

    if "site_logs" not in db:
        db["site_logs"] = []

    # Summary Metrics
    total_logs = len(db["site_logs"])
    latest_manpower = db["site_logs"][-1].get("total_headcount", 0) if db["site_logs"] else 0
    total_incidents = sum(1 for log in db["site_logs"] if log.get("has_incident"))

    col1, col2, col3 = st.columns(3)
    col1.metric("Logs Recorded", total_logs)
    col2.metric("Latest Site Headcount", f"{latest_manpower} Workers" if latest_manpower else "N/A")
    col3.metric("Incidents Logged", total_incidents)

    st.markdown("---")

    tab1, tab2 = st.tabs(["Daily Logs History", "Record Daily Log"])

    with tab1:
        if not db["site_logs"]:
            st.info("No daily site logs recorded yet.")
        else:
            sorted_logs = sorted(db["site_logs"], key=lambda x: x.get("log_date", ""), reverse=True)

            for log in sorted_logs:
                date_str = log.get("log_date", "Unknown Date")
                incident_flag = "⚠️ Incident Reported" if log.get("has_incident") else "✅ Normal Site Operations"
                header = f"**Site Log — {date_str}** ({incident_flag})"

                with st.expander(header):
                    lc1, lc2, lc3, lc4 = st.columns(4)
                    lc1.write(f"**Weather:** {log.get('weather', '-')}")
                    lc2.write(f"**Main Contractor:** {log.get('main_contractor_count', 0)} workers")
                    lc3.write(f"**Subcontractors:** {log.get('subcontractor_count', 0)} workers")
                    lc4.write(f"**Total Headcount:** {log.get('total_headcount', 0)}")

                    st.markdown("---")
                    st.markdown(f"**Work Progress Completed:**\n{log.get('work_completed', 'No description entered.')}")

                    if log.get("equipment_on_site"):
                        st.markdown(f"**Equipment Active:** {log.get('equipment_on_site')}")

                    if log.get("has_incident") and log.get("incident_details"):
                        st.error(f"**Safety / Delay Note:**\n{log.get('incident_details')}")

                    st.caption(f"Logged by: {log.get('logged_by', 'N/A')}")

    with tab2:
        st.markdown("### Record New Daily Site Log")
        with st.form("record_site_log_form", clear_on_submit=True):
            s1, s2 = st.columns(2)
            log_date = s1.date_input("Log Date*", value=datetime.date.today())
            weather = s2.selectbox(
                "Weather Condition*",
                ["Clear / Sunny", "Partly Cloudy", "Overcast", "Light Rain / Drizzle", "Heavy Rain (Site Stoppage)", "Windy"]
            )

            s3, s4 = st.columns(2)
            main_contractor_count = s3.number_input("Main Contractor Headcount*", min_value=0, step=1, value=10)
            subcontractor_count = s4.number_input("Subcontractor Headcount*", min_value=0, step=1, value=5)

            equipment_on_site = st.text_input("Active Heavy Equipment", placeholder="e.g. 1x Tower Crane, 2x Excavators, 1x Concrete Pump")

            work_completed = st.text_area(
                "Summary of Work Performed Today*",
                placeholder="Detail key structural, MEP, or architectural progress completed on site today..."
            )

            has_incident = st.checkbox("Report Delay, Safety Incident, or Inspection Issue")
            incident_details = ""
            if has_incident:
                incident_details = st.text_area(
                    "Incident / Issue Details*",
                    placeholder="Describe safety incidents, material delivery delays, or weather stoppages..."
                )

            submitted = st.form_submit_button("Submit Site Log", use_container_width=True)

            if submitted:
                if not work_completed:
                    st.error("Please provide a summary of work performed today.")
                elif has_incident and not incident_details:
                    st.error("Please describe the incident or issue details.")
                else:
                    new_log = {
                        "id": len(db["site_logs"]) + 1,
                        "log_date": log_date.isoformat(),
                        "weather": weather,
                        "main_contractor_count": int(main_contractor_count),
                        "subcontractor_count": int(subcontractor_count),
                        "total_headcount": int(main_contractor_count + subcontractor_count),
                        "equipment_on_site": equipment_on_site.strip(),
                        "work_completed": work_completed.strip(),
                        "has_incident": has_incident,
                        "incident_details": incident_details.strip() if has_incident else "",
                        "logged_by": st.session_state.get("user", {}).get("full_name", "Admin")
                    }
                    db["site_logs"].append(new_log)
                    st.success(f"Daily site log for {log_date.isoformat()} successfully saved!")
                    st.rerun()


# ============================================================