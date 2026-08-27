import os
import streamlit as st
from modules import (
    dashboard,
    projects,
    documents,
    architecture,
    engineering,
    drawings,
    mep
)
from modules.database import load_memory

def render_sidebar_logo():
    # Path to logo inside assets folder
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "creative_studios.png")

    try:
        if os.path.exists(logo_path):
            st.sidebar.image(logo_path, use_column_width=True)
        else:
            st.sidebar.header("Creative Studios")
    except Exception:
        st.sidebar.header("Creative Studios")
        st.sidebar.write("⚠️ Logo not available")

def main():
    # Sidebar branding
    render_sidebar_logo()

    # Navigation
    st.sidebar.title("Navigation")
    choice = st.sidebar.radio(
        "Go to",
        ["Dashboard", "Projects", "Documents", "Architecture", "Engineering", "Drawings", "MEP"]
    )

    # Load database
    database = load_memory()

    # Route to modules
    if choice == "Dashboard":
        dashboard.render_dashboard(database)
    elif choice == "Projects":
        projects.render_projects_module(database)
    elif choice == "Documents":
        documents.render_documents_module(database)
    elif choice == "Architecture":
        architecture.render_architecture_module(database)
    elif choice == "Engineering":
        engineering.render_engineering_module(database)
    elif choice == "Drawings":
        drawings.render_drawings_module(database)
    elif choice == "MEP":
        mep.render_mep_module(database)

if __name__ == "__main__":
    main()
