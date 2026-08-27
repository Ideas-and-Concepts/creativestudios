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
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "creative_studios.png")

    # Custom CSS for background styling
    st.markdown(
        """
        <style>
        .sidebar-logo {
            background-color: #2C3E50; /* Dark theme color */
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        .sidebar-logo img {
            max-width: 100%;
            height: auto;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    try:
        if os.path.exists(logo_path):
            st.sidebar.markdown(
                f"""
                <div class="sidebar-logo">
                    <img src="assets/creative_studios.png" alt="Creative Studios Logo">
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.sidebar.header("Creative Studios")
    except Exception:
        st.sidebar.header("Creative Studios")
        st.sidebar.write("⚠️ Logo not available")

def main():
    render_sidebar_logo()

    st.sidebar.title("Navigation")
    choice = st.sidebar.radio(
        "Go to",
        ["Dashboard", "Projects", "Documents", "Architecture", "Engineering", "Drawings", "MEP"]
    )

    database = load_memory()

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