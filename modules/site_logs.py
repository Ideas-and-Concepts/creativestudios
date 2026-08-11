import streamlit as st
from datetime import date
from .database import save_memory

def render_site_logs_module(db):
    st.title("📝 Daily Site Progress Logs")
    st.caption("Record site conditions, workforce headcounts, major daily milestones, and safety notes.")

    projects = db.get("projects", [])
    if not projects:
        st.warning("Please create a project first.")
        return

    project_options = {p["name"]: p["id"] for p in projects}
    selected_proj_name = st.selectbox("Select Project Workspace", list(project_options.keys()), key="logs_proj_sel")
    selected_proj_id = project_options[selected_proj_name]

    tab1, tab2 = st.tabs(["📂 View Site Logs", "➕ Add Daily Log"])

    with tab1:
        logs = [l for l in db.get("site_logs", []) if l["project_id"] == selected_proj_id]
        if not logs:
            st.info("No daily site logs recorded for this project yet.")
        else:
            for log in sorted(logs, key=lambda x: x["log_date"], reverse=True):
                with st.expander(f"📅 Log Date: {log['log_date']} — Weather: {log['weather']} | Workers: {log['workforce']}"):
                    c1, c2 = st.columns(2)
                    c1.markdown(f"**Logged By:** {log['logged_by']}")
                    c2.markdown(f"**Workforce Count:** {log['workforce']} personnel")
                    st.markdown(f"**Major Activities Completed:**\n{log['activities']}")
                    st.markdown(f"**Safety / Site Issues:**\n{log['safety_notes']}")

    with tab2:
        st.subheader("Submit Today's Site Progress Log")
        with st.form("new_site_log_form"):
            log_date = st.date_input("Log Date", value=date.today())
            weather = st.selectbox("Weather Condition", ["Sunny / Clear", "Partly Cloudy", "Rainy / Wet", "Windy / Stormy", "Extreme Heat"])
            workforce = st.number_input("Total Workers on Site", min_value=1, value=25, step=1)
            activities = st.text_area("Major Activities / Milestones Completed Today")
            safety_notes = st.text_area("Safety Incidents or Site Notes (Leave blank if none)", value="None reported.")
            
            submitted = st.form_submit_button("Submit Daily Log", use_container_width=True)
            if submitted:
                if not activities:
                    st.error("Activities description is required.")
                else:
                    current_user = st.session_state.get("user", {})
                    new_log = {
                        "id": f"LOG-{len(db.get('site_logs', [])) + 1}",
                        "project_id": selected_proj_id,
                        "log_date": str(log_date),
                        "weather": weather,
                        "workforce": workforce,
                        "activities": activities,
                        "safety_notes": safety_notes,
                        "logged_by": current_user.get("name", "Unknown User")
                    }
                    if "site_logs" not in db:
                        db["site_logs"] = []
                    db["site_logs"].append(new_log)
                    save_memory(db)
                    st.success("Daily site log successfully submitted!")
                    st.rerun()
