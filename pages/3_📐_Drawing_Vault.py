import streamlit as st
from datetime import datetime
from utils import load_memory, save_memory, require_auth, safe_dataframe, get_project_name

st.set_page_config(page_title="Drawing Vault", page_icon="📐", layout="wide")
require_auth()

db = load_memory()
current_user = st.session_state["user"]

st.title("📐 Drawing Vault & Version Control")

if not db.get("projects"):
    st.warning("Please create a project first.")
else:
    tab1, tab2 = st.tabs(["Document Repository", "Upload New Drawing / Revision"])

    with tab1:
        project_filter = st.selectbox(
            "Filter by Project",
            options=["All"] + [p["id"] for p in db["projects"]],
            format_func=lambda x: "All Projects" if x == "All" else f"{x} - {get_project_name(db, x)}"
        )

        drawings_list = db.get("drawings", [])
        if project_filter != "All":
            drawings_list = [d for d in drawings_list if d.get("project_id") == project_filter]

        if drawings_list:
            df_drawings = safe_dataframe(
                drawings_list, 
                ["id", "project_id", "discipline", "title", "version", "status", "file_name", "uploaded_by"]
            )
            st.dataframe(df_drawings, use_container_width=True)
        else:
            st.info("No drawings recorded for this selection.")

    with tab2:
        st.subheader("Upload Plan Document")
        with st.form("upload_drawing_form"):
            proj_id = st.selectbox(
                "Target Project",
                options=[p["id"] for p in db["projects"]],
                format_func=lambda x: f"{x} - {get_project_name(db, x)}"
            )
            discipline = st.selectbox("Discipline Classification", [
                "Architectural", "Structural Engineering", "Mechanical (HVAC)",
                "Electrical & Power", "Plumbing & Sanitation", "Civil / Site Plan"
            ])
            title = st.text_input("Drawing Title")
            version = st.text_input("Version Tag", value="v1.0")
            uploaded_file = st.file_uploader("Upload Drawing File", type=["pdf", "dwg", "png", "jpg"])

            submitted = st.form_submit_button("Record Drawing in Vault")
            if submitted and title:
                file_name = uploaded_file.name if uploaded_file else "Drawing_Plan.pdf"
                dwg_id = f"DWG-{len(db['drawings']) + 1:03d}"
                db["drawings"].append({
                    "id": dwg_id, "project_id": proj_id, "discipline": discipline,
                    "title": title, "version": version, "file_name": file_name,
                    "status": "Pending Review", "uploaded_by": current_user["name"],
                    "uploaded_at": datetime.now().isoformat()
                })
                save_memory(db)
                st.success(f"Drawing registered as ID: {dwg_id}")
                st.rerun()
