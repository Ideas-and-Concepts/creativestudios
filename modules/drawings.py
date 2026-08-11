import streamlit as st
from datetime import datetime
from .database import save_memory

def render_drawings_module(db):
    st.title("📐 Drawing & Document Repository")
    st.caption("Store, manage, and version-control engineering & architectural drawings by discipline.")
    
    projects = db.get("projects", [])
    if not projects:
        st.warning("Please create at least one project in the Project Directory before uploading drawings.")
        return

    project_options = {p["name"]: p["id"] for p in projects}
    selected_proj_name = st.selectbox("Select Project Workspace", list(project_options.keys()))
    selected_proj_id = project_options[selected_proj_name]

    tab1, tab2 = st.tabs(["📂 Browse Drawings", "📤 Upload / Add Drawing"])

    with tab1:
        drawings = [d for d in db.get("drawings", []) if d["project_id"] == selected_proj_id]
        
        discipline_filter = st.selectbox("Filter by Discipline", ["All Disciplines", "Architectural", "Structural", "Electrical", "Plumbing"])
        
        if discipline_filter != "All Disciplines":
            drawings = [d for d in drawings if d["discipline"] == discipline_filter]

        if not drawings:
            st.info(f"No drawings found for '{selected_proj_name}' under this filter.")
        else:
            for d in drawings:
                with st.expander(f"📄 [{d['discipline']}] {d['title']} ({d['version']}) — Status: {d['status']}"):
                    col1, col2, col3 = st.columns(3)
                    col1.markdown(f"**File Name:** `{d['file_name']}`")
                    col2.markdown(f"**Uploaded By:** {d['uploaded_by']}")
                    col3.markdown(f"**Date:** {d['uploaded_at'][:10]}")
                    st.markdown(f"**Description / Notes:** {d['notes']}")

    with tab2:
        st.subheader(f"Upload Drawing for: {selected_proj_name}")
        with st.form("upload_drawing_form"):
            d_title = st.text_input("Drawing Title (e.g., Ground Floor Power Layout)")
            d_discipline = st.selectbox("Discipline Category", ["Architectural", "Structural", "Electrical", "Plumbing"])
            d_version = st.text_input("Version Tag", value="v1.0")
            d_file_name = st.text_input("File Name (e.g., E-101_Lighting.pdf)")
            d_notes = st.text_area("Revision Notes / Description")
            
            submitted = st.form_submit_button("Upload & Register Drawing", use_container_width=True)
            if submitted:
                if not d_title or not d_file_name:
                    st.error("Drawing title and file name are required.")
                else:
                    current_user = st.session_state.get("user", {})
                    new_drawing = {
                        "id": f"DWG-{len(db.get('drawings', [])) + 101}",
                        "project_id": selected_proj_id,
                        "title": d_title,
                        "discipline": d_discipline,
                        "version": d_version,
                        "file_name": d_file_name,
                        "status": "In Review",
                        "uploaded_by": current_user.get("name", "Unknown User"),
                        "uploaded_at": datetime.now().isoformat(),
                        "notes": d_notes
                    }
                    if "drawings" not in db:
                        db["drawings"] = []
                    db["drawings"].append(new_drawing)
                    save_memory(db)
                    st.success("Drawing successfully registered in repository!")
                    st.rerun()
