import pandas as pd
import plotly.express as px
import streamlit as st

def render_dashboard(database):
    st.header("Dashboard")

    # --- KPI Cards ---
    total_projects = len(database.get("projects", []))
    total_docs = sum(len(p.get("documents", [])) for p in database.get("projects", []))
    total_drawings = sum(len(p.get("drawings", [])) for p in database.get("projects", []))
    total_mep = sum(len(p.get("mep", [])) for p in database.get("projects", []))

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Projects", total_projects)
    col2.metric("Documents", total_docs)
    col3.metric("Drawings", total_drawings)
    col4.metric("MEP Systems", total_mep)

    # --- Timeline Chart ---
    doc_data = []
    for p in database.get("projects", []):
        for d in p.get("documents", []):
            if isinstance(d, dict) and "date" in d:
                doc_data.append({"project": p["name"], "date": d["date"]})

    if doc_data:
        df = pd.DataFrame(doc_data)
        df["date"] = pd.to_datetime(df["date"])
        df_grouped = df.groupby("date").size().reset_index(name="count")

        fig = px.line(df_grouped, x="date", y="count", title="Documents Added Over Time")
        st.plotly_chart(fig, use_container_width=True)