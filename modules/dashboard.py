limport streamlit as st
import plotly.express as px

def render_dashboard(database):
    st.header("📊 Dashboard")

    try:
        if "projects" in database and database["projects"]:
            # Example: bar chart of documents per project
            project_names = [p.get("name", "Unnamed") for p in database["projects"]]
            doc_counts = [len(p.get("documents", [])) for p in database["projects"]]

            fig = px.bar(
                x=project_names,
                y=doc_counts,
                labels={"x": "Projects", "y": "Documents"},
                title="Documents per Project"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No projects yet to display")
    except Exception as e:
        st.error(f"⚠️ Dashboard rendering failed: {e}")