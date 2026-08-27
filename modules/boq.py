import streamlit as st
import pandas as pd

def render_boq_dashboard(database: dict[str, Any]) -> None:
    st.header("BOQ Dashboard")

    projects = database.get("projects", [])
    if not projects:
        st.info("No projects available.")
        return

    # Build DataFrame
    data = [
        {
            "Project": p.get("name", "Unnamed"),
            "Status": p.get("status", "unknown").capitalize(),
            "Grand Total": p.get("grand_total", 0)
        }
        for p in projects
    ]
    df = pd.DataFrame(data)

    # Status filter
    status_options = df["Status"].unique().tolist()
    selected_status = st.selectbox("Filter by Status", ["All"] + status_options)

    if selected_status != "All":
        df = df[df["Status"] == selected_status]

    # Portfolio metrics
    portfolio_total = df["Grand Total"].sum()
    st.metric("Portfolio Total", f"${portfolio_total:,.2f}")

    # Bar Chart
    st.subheader("Project Cost Comparison")
    st.bar_chart(df.set_index("Project")["Grand Total"])

    # Pie Chart
    st.subheader("Portfolio Distribution")
    st.write(df.set_index("Project")["Grand Total"].plot.pie(autopct="%1.1f%%"))