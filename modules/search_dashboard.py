import streamlit as st
import pandas as pd
from typing import Any

def render_search_dashboard(database: dict[str, Any]) -> None:
    """Render dashboard to search/filter documents and drawings across projects."""

    st.header("Search & Filter Dashboard")

    projects = database.get("projects", [])
    if not projects:
        st.info("No projects available.")
        return

    # Collect all files
    records = []
    for project in projects:
        pname = project.get("name", "Unnamed Project")

        # Project-level documents
        for doc in project.get("documents", []):
            records.append({
                "Project": pname,
                "Type": "Document",
                "Title": doc["title"],
                "Phase": doc["phase"],
                "Version": doc["version"],
                "Author": doc["author"],
                "Filename": doc["filename"],
                "Space": None
            })

        # Project-level drawings
        for dr in project.get("drawings", []):
            records.append({
                "Project": pname,
                "Type": "Drawing",
                "Title": dr["title"],
                "Phase": dr["phase"],
                "Version": dr["version"],
                "Author": dr["author"],
                "Filename": dr["filename"],
                "Space": None
            })

        # Space-level files
        for space in project.get("spaces", []):
            sname = space.get("name")
            for doc in space.get("documents", []):
                records.append({
                    "Project": pname,
                    "Type": "Document",
                    "Title": doc["title"],
                    "Phase": doc.get("phase",""),
                    "Version": doc["version"],
                    "Author": doc["author"],
                    "Filename": doc["filename"],
                    "Space": sname
                })
            for dr in space.get("drawings", []):
                records.append({
                    "Project": pname,
                    "Type": "Drawing",
                    "Title": dr["title"],
                    "Phase": dr.get("phase",""),
                    "Version": dr["version"],
                    "Author": dr["author"],
                    "Filename": dr["filename"],
                    "Space": sname
                })

    if not records:
        st.caption("No files found.")
        return

    df = pd.DataFrame(records)

    # Filters
    st.subheader("Filters")
    project_filter = st.selectbox("Project", ["All"] + df["Project"].unique().tolist())
    type_filter = st.selectbox("Type", ["All", "Document", "Drawing"])
    phase_filter = st.selectbox("Phase", ["All"] + df["Phase"].unique().tolist())
    space_filter = st.selectbox("Space", ["All"] + [s for s in df["Space"].dropna().unique().tolist()])

    filtered = df.copy()
    if project_filter != "All":
        filtered = filtered[filtered["Project"] == project_filter]
    if type_filter != "All":
        filtered = filtered[filtered["Type"] == type_filter]
    if phase_filter != "All":
        filtered = filtered[filtered["Phase"] == phase_filter]
    if space_filter != "All":
        filtered = filtered[filtered["Space"] == space_filter]

    st.subheader("Results")
    st.dataframe(filtered)

    # Quick metrics
    st.metric("Total Files", len(filtered))
    st.metric("Documents", len(filtered[filtered["Type"]=="Document"]))
    st.metric("Drawings", len(filtered[filtered["Type"]=="Drawing"]))