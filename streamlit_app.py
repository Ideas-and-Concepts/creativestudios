import streamlit as st
from modules import (
    documents,
    architecture,
    engineering,
    drawings,
    mep,
    projects
)
from modules.database import load_memory

# ============================================================
# MAIN APP
# ============================================================

def main():
    st.sidebar.title("Creative Studios")
    navigation = [
        "Projects",
        "Documents",
        "Architecture",
        "Engineering",
        "Drawings",
        "MEP"
    ]

    choice = st.sidebar.radio("Go to", navigation)

    # Load database
    database = load_memory()

    # Route to selected module
    if choice == "Projects":
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