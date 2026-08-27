import streamlit as st
from modules import (
    database,
    architecture,
    engineering,
    boq,
    team,
    mep,
    spaces,
    documents,
    drawings,
    approvals,
    rfis,
    site_logs,
    tasks,
    branding,
    projects,
    search_dashboard,
    portfolio_dashboard,
)

def main():
    st.set_page_config(page_title="Creative Studios", layout="wide")
    st.title("Creative Studios Workspace")
    st.caption("Integrated AEC lifecycle management: Architecture, Engineering, Construction, MEP, Spaces, Documents, Drawings, Approvals, and Portfolio KPIs.")

    # Load database
    database_state = database.load_memory()

    # Sidebar navigation
    navigation = [
        "Overview", "Projects", "Architecture", "Engineering", "Construction",
        "BOQ", "Team", "MEP", "Spaces", "Documents", "Drawings",
        "RFIs", "Tasks", "Approvals", "Site Logs", "Branding",
        "Search", "Portfolio"
    ]
    module_name = st.sidebar.radio("Navigate", navigation)

    # Router
    if module_name == "Overview":
        st.header("Overview")
        st.write("Creative Studios integrates Architecture, Engineering, Construction, and MEP phases.")
    elif module_name == "Projects":
        projects.render_projects_module(database_state)
    elif module_name == "Architecture":
        architecture.render_architecture_module(database_state)
    elif module_name == "Engineering":
        engineering.render_engineering_module(database_state)
    elif module_name == "Construction":
        st.header("Construction Phase")
        st.write("Includes BOQ, Team, RFIs, Site Logs, Approvals, Tasks.")
    elif module_name == "BOQ":
        boq.render_boq_module(database_state)
    elif module_name == "Team":
        team.render_team_module(database_state)
    elif module_name == "MEP":
        mep.render_mep_module(database_state)
    elif module_name == "Spaces":
        spaces.render_spaces_module(database_state)
    elif module_name == "Documents":
        documents.render_documents_module(database_state)
    elif module_name == "Drawings":
        drawings.render_drawings_module(database_state)
    elif module_name == "RFIs":
        rfis.render_rfis_module(database_state)
    elif module_name == "Tasks":
        tasks.render_tasks_module(database_state)
    elif module_name == "Approvals":
        approvals.render_approvals_module(database_state)
    elif module_name == "Site Logs":
        site_logs.render_site_logs_module(database_state)
    elif module_name == "Branding":
        branding.render_branding_module(database_state)
    elif module_name == "Search":
        search_dashboard.render_search_dashboard(database_state)
    elif module_name == "Portfolio":
        portfolio_dashboard.render_portfolio_dashboard(database_state)

if __name__ == "__main__":
    main()