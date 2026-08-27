import streamlit as st
import pandas as pd
from typing import Any

# ============================================================
# LANDING PAGE MODULE
# ============================================================

def render_landing_page(database: dict[str, Any]) -> None:
    """Render landing page with intro text, quick stats, and links."""

    st.title("🏗️ Creative Studios")
    st.markdown("Welcome to your streamlined AEC platform — manage projects, documents, drawings, and MEP all in one place.")

    projects = database.get("projects", [])
    docs = [doc for p in projects for doc in p.get("documents", [])]
    arch_drawings = [d for p in projects for d in p.get("architecture_drawings", [])]
    eng_drawings = [d for p in projects for d in p.get("engineering_drawings", [])]
    mep_items = [m for p in projects for m in p.get("mep", [])]

    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Projects", len(projects))
    col2.metric("Documents", len(docs))
    col3.metric("Drawings", len(arch_drawings) + len(eng_drawings))
    col4.metric("MEP Items", len(mep_items))

    # Quick links
    st.subheader("Quick Access")
    st.markdown("- 📂 Go to **Dashboard** for analytics")
    st.markdown("- 📑 Manage **Documents** (Approved/Pending)")
    st.markdown("- 🏛️ Upload **Architecture Drawings** & Suggestions")
    st.markdown("- 🏗️ Upload **Engineering Drawings** & Suggestions")
    st.markdown("- 📐 View all **Drawings** in one place")
    st.markdown("- ⚙️ Track **MEP** items and BOQ")