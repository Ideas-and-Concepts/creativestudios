import streamlit as st
import json, uuid
from pathlib import Path
from datetime import datetime
import pandas as pd

# ---------------------------------------------------------
# Page Configuration & Memory Initialization
# ---------------------------------------------------------
st.set_page_config(
    page_title="Creative Studios - Architectural Management System",
    page_icon="📐",
    layout="wide"
)

MEMORY_FILE = Path("creativestudios_db.json")

DEFAULT_MEMORY = {
    "projects": [
        {
            "id": "PRJ-001",
            "name": "Skyline Commercial Hub",
            "type": "New Construction",
            "status": "In Review",
            "created": "2026-01-15T09:00:00",
            "budget": 250000.0,
            "description": "5-story commercial complex with subterranean parking."
        }
    ],
    "drawings": [
        {
            "id": "DWG-101",
            "project_id": "PRJ-001",
            "discipline": "Architectural",
            "title": "Ground Floor Plan & Layout",
            "version": "v1.2",
            "file_name": "A-101_Ground_Floor.pdf",
            "status": "Approved",
            "uploaded_by": "Arch. Jane Doe",
            "uploaded_at": "2026-01-18T10:30:00"
        },
        {
            "id": "DWG-102",
            "project_id": "PRJ-001",
            "discipline": "Engineering",
            "title": "Foundation & Structural Beams",
            "version": "v1.0",
            "file_name": "S-101_Foundation.pdf",
            "status": "Pending Review",
            "uploaded_by": "Eng. John Smith",
            "uploaded_at": "2026-01-20T14:15:00"
        }
    ],
    "procurement_approvals": [
        {
            "id": "APP-001",
            "project_id": "PRJ-001",
            "item_name": "Concrete Foundation Phase 1",
            "arch_status": "Approved",
            "eng_status": "Pending",
            "procurement_status": "Locked",
            "notes": "Awaiting structural engineer validation on rebar load specs."
        }
    ],
    "boq": [
        {
            "id": "BOQ-001",
            "project_id": "PRJ-001",
            "category": "Materials",
            "item": "Ready-Mix Concrete (30 MPa)",
            "quantity": 150.0,
            "unit": "m³",
            "unit_cost": 120.0,
            "total": 18000.0
        },
        {
            "id": "BOQ-002",
            "project_id": "PRJ-001",
            "category": "Labor",
            "item": "Structural Steelworkers",
            "quantity": 320.0,
            "unit": "Hours",
            "unit_cost": 45.0,
            "total": 14400.0
        }
    ]
}

def load_memory():
    if MEMORY_FILE.exists():
        try:
            return json.loads(MEMORY_FILE.read_text())
        except Exception:
            pass
    return DEFAULT_MEMORY.copy()

def save_memory(mem):
    MEMORY_FILE.write_text(json.dumps(mem, indent=2))

db = load_memory()

# Helper function to find project name by ID
def get_project_name(project_id):
    proj = next((p for p in db["projects"] if p["id"] == project_id), None)
    return proj["name"] if proj else "Unknown"

# ---------------------------------------------------------
# Sidebar Navigation & Quick Metrics
# ---------------------------------------------------------
st.sidebar.title("📐 Creative Studios")
st.sidebar.caption("Architectural & Construction Management System")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Project Directory",
        "Drawing Vault",
        "Procurement & Approvals",
        "BoQ (Materials & Labor)"
    ]
)

st.sidebar.markdown("---")
st.sidebar.write("**System Quick Summary**")
st.sidebar.caption(f"Active Projects: {len(db['projects'])}")
st.sidebar.caption(f"Vault Drawings: {len(db['drawings'])}")

# ---------------------------------------------------------
# MODULE 1: DASHBOARD
# ---------------------------------------------------------
if page == "Dashboard":
    st.title("📊 Executive Dashboard")
    st.markdown("Real-time summary of drawings, active approvals, and budget allocations.")

    col1, col2, col3, col4 = st.columns(4)
    total_budget = sum(p.get("budget", 0) for p in db["projects"])
    pending_approvals = sum(
        1 for a in db["procurement_approvals"] 
        if a["procurement_status"] != "Approved"
    )

    col1.metric("Total Projects", len(db["projects"]))
    col2.metric("Total Vault Documents", len(db["drawings"]))
    col3.metric("Pending Approvals", pending_approvals)
    col4.metric("Total Portfolio Budget", f"${total_budget:,.2f}")

    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Project Type Overview")
        if db["projects"]:
            df_p = pd.DataFrame(db["projects"])
            type_counts = df_p["type"].value_counts().reset_index()
            type_counts.columns = ["Project Type", "Count"]
            st.dataframe(type_counts, use_container_width=True)
        else:
            st.info("No project data available.")

    with col_b:
        st.subheader("Latest Vault Uploads")
        if db["drawings"]:
            df_d = pd.DataFrame(db["drawings"])[["discipline", "title", "version", "status", "uploaded_at"]]
            st.dataframe(df_d.tail(5), use_container_width=True)
        else:
            st.info("No drawings uploaded yet.")

# ---------------------------------------------------------
# MODULE 2: PROJECT DIRECTORY
# ---------------------------------------------------------
elif page == "Project Directory":
    st.title("📁 Project Directory")
    st.markdown("Manage both **New Construction** and **Renovation/Retrofit** initiatives.")

    tab1, tab2 = st.tabs(["View Projects", "Register New Project"])

    with tab1:
        if db["projects"]:
            df_projects = pd.DataFrame(db["projects"])
            st.dataframe(
                df_projects[["id", "name", "type", "status", "budget", "created", "description"]],
                use_container_width=True
            )
        else:
            st.info("No active projects found.")

    with tab2:
        st.subheader("Register a Project")
        with st.form("new_project_form"):
            p_name = st.text_input("Project Title")
            p_type = st.selectbox("Project Classification", ["New Construction", "Renovation / Restructuring", "Structural Upgrade"])
            p_status = st.selectbox("Initial Status", ["Planning", "In Review", "Active Execution", "Completed"])
            p_budget = st.number_input("Estimated Budget ($)", min_value=0.0, step=1000.0)
            p_desc = st.text_area("Scope & Description")

            submitted = st.form_submit_button("Create Project Entry")
            if submitted and p_name:
                new_id = f"PRJ-{len(db['projects']) + 1:03d}"
                db["projects"].append({
                    "id": new_id,
                    "name": p_name,
                    "type": p_type,
                    "status": p_status,
                    "created": datetime.now().isoformat(),
                    "budget": p_budget,
                    "description": p_desc
                })
                save_memory(db)
                st.success(f"Project '{p_name}' successfully created with ID: {new_id}")
                st.rerun()

# ---------------------------------------------------------
# MODULE 3: DRAWING VAULT
# ---------------------------------------------------------
elif page == "Drawing Vault":
    st.title("📐 Drawing Vault & Version Control")
    st.markdown("Central repository for **Architectural** and **Engineering** drawings.")

    if not db["projects"]:
        st.warning("Please create at least one project before managing drawings.")
    else:
        tab1, tab2 = st.tabs(["Document Repository", "Upload New Drawing / Revision"])

        with tab1:
            project_filter = st.selectbox(
                "Filter by Project",
                options=["All"] + [p["id"] for p in db["projects"]],
                format_func=lambda x: "All Projects" if x == "All" else f"{x} - {get_project_name(x)}"
            )

            drawings_list = db["drawings"]
            if project_filter != "All":
                drawings_list = [d for d in drawings_list if d["project_id"] == project_filter]

            if drawings_list:
                df_drawings = pd.DataFrame(drawings_list)
                st.dataframe(
                    df_drawings[["id", "project_id", "discipline", "title", "version", "status", "file_name", "uploaded_by"]],
                    use_container_width=True
                )
            else:
                st.info("No drawings recorded for this selection.")

        with tab2:
            st.subheader("Upload Plan Document")
            with st.form("upload_drawing_form"):
                proj_id = st.selectbox(
                    "Target Project",
                    options=[p["id"] for p in db["projects"]],
                    format_func=lambda x: f"{x} - {get_project_name(x)}"
                )
                discipline = st.selectbox("Discipline", ["Architectural", "Structural Engineering", "MEP Engineering", "Civil/Site Plan"])
                title = st.text_input("Drawing Title (e.g., Section A-A Elevation)")
                version = st.text_input("Version Tag", value="v1.0")
                uploaded_by = st.text_input("Uploaded By", value="Architect/Engineer Name")
                uploaded_file = st.file_uploader("Upload File (PDF, DWG, PNG)", type=["pdf", "dwg", "png", "jpg"])

                submitted = st.form_submit_button("Record Drawing")
                if submitted and title:
                    file_name = uploaded_file.name if uploaded_file else "Simulated_Drawing.pdf"
                    dwg_id = f"DWG-{len(db['drawings']) + 1:03d}"
                    db["drawings"].append({
                        "id": dwg_id,
                        "project_id": proj_id,
                        "discipline": discipline,
                        "title": title,
                        "version": version,
                        "file_name": file_name,
                        "status": "Pending Review",
                        "uploaded_by": uploaded_by,
                        "uploaded_at": datetime.now().isoformat()
                    })
                    save_memory(db)
                    st.success(f"Drawing '{title}' registered in vault as ID: {dwg_id}")
                    st.rerun()

# ---------------------------------------------------------
# MODULE 4: PROCUREMENT & APPROVAL WORKFLOW
# ---------------------------------------------------------
elif page == "Procurement & Approvals":
    st.title("🛡 Approval & Procurement Engine")
    st.markdown("Dual sign-off chain required before procurement releases materials or labor.")

    if not db["projects"]:
        st.warning("Please create a project first.")
    else:
        tab1, tab2 = tab1, tab2 = st.tabs(["Active Sign-off Pipeline", "Initiate Approval Request"])

        with tab1:
            st.subheader("Sign-off Management Matrix")
            if db["procurement_approvals"]:
                for idx, item in enumerate(db["procurement_approvals"]):
                    with st.expander(f"📦 {item['item_name']} (Project: {item['project_id']})"):
                        col1, col2, col3 = st.columns(3)

                        # Architectural Sign-off
                        with col1:
                            st.markdown("**1. Architectural Sign-off**")
                            st.caption(f"Status: {item['arch_status']}")
                            if item['arch_status'] != "Approved":
                                if st.button("Approve (Architect)", key=f"arch_{idx}"):
                                    item['arch_status'] = "Approved"
                                    save_memory(db)
                                    st.rerun()

                        # Engineering Sign-off
                        with col2:
                            st.markdown("**2. Engineering Sign-off**")
                            st.caption(f"Status: {item['eng_status']}")
                            if item['eng_status'] != "Approved":
                                if st.button("Approve (Engineer)", key=f"eng_{idx}"):
                                    item['eng_status'] = "Approved"
                                    save_memory(db)
                                    st.rerun()

                        # Procurement Status Update
                        with col3:
                            st.markdown("**3. Procurement Authorization**")
                            if item['arch_status'] == "Approved" and item['eng_status'] == "Approved":
                                item['procurement_status'] = "Ready for Release"
                                st.success("✅ Fully Approved for Procurement")
                            else:
                                item['procurement_status'] = "Locked (Awaiting Approvals)"
                                st.warning("🔒 Sign-offs Pending")

                        st.write(f"**Technical Notes:** {item.get('notes', 'N/A')}")
            else:
                st.info("No approval requests currently in pipeline.")

        with tab2:
            st.subheader("Request Sign-off for Procurement Item")
            with st.form("new_approval_form"):
                proj_id = st.selectbox(
                    "Project",
                    options=[p["id"] for p in db["projects"]],
                    format_func=lambda x: f"{x} - {get_project_name(x)}"
                )
                item_name = st.text_input("Item / Phase Description (e.g., Roof Truss Structural Steel)")
                notes = st.text_area("Specification Notes for Reviewers")

                submitted = st.form_submit_button("Submit into Pipeline")
                if submitted and item_name:
                    app_id = f"APP-{len(db['procurement_approvals']) + 1:03d}"
                    db["procurement_approvals"].append({
                        "id": app_id,
                        "project_id": proj_id,
                        "item_name": item_name,
                        "arch_status": "Pending",
                        "eng_status": "Pending",
                        "procurement_status": "Locked",
                        "notes": notes
                    })
                    save_memory(db)
                    st.success(f"Approval pipeline item '{item_name}' created under ID: {app_id}")
                    st.rerun()

# ---------------------------------------------------------
# MODULE 5: BILL OF QUANTITIES (BOQ) & RESOURCE ESTIMATOR
# ---------------------------------------------------------
elif page == "BoQ (Materials & Labor)":
    st.title("🧱 Bill of Quantities (BoQ)")
    st.markdown("Track estimated and actual expenditures for **Materials** and **Labor**.")

    if not db["projects"]:
        st.warning("Please create a project first.")
    else:
        tab1, tab2 = st.tabs(["Project BoQ Ledger", "Add Line Item"])

        with tab1:
            proj_id = st.selectbox(
                "Select Project",
                options=[p["id"] for p in db["projects"]],
                format_func=lambda x: f"{x} - {get_project_name(x)}"
            )

            boq_items = [b for b in db["boq"] if b["project_id"] == proj_id]

            if boq_items:
                df_boq = pd.DataFrame(boq_items)
                st.dataframe(
                    df_boq[["id", "category", "item", "quantity", "unit", "unit_cost", "total"]],
                    use_container_width=True
                )
                total_cost = df_boq["total"].sum()
                st.metric("Total Calculated BoQ Cost", f"${total_cost:,.2f}")
            else:
                st.info("No items in BoQ for this project yet.")

        with tab2:
            st.subheader("Add Material / Labor Entry")
            with st.form("boq_form"):
                p_id = st.selectbox(
                    "Project Target",
                    options=[p["id"] for p in db["projects"]],
                    format_func=lambda x: f"{x} - {get_project_name(x)}"
                )
                category = st.selectbox("Category", ["Materials", "Labor", "Equipment Rental", "Permits & Legal"])
                item = st.text_input("Item / Role Description")
                quantity = st.number_input("Quantity", min_value=0.1, value=1.0)
                unit = st.text_input("Unit of Measure (e.g., m³, Hours, Bags, Sq Ft)", value="Units")
                unit_cost = st.number_input("Cost per Unit ($)", min_value=0.0, value=10.0)

                submitted = st.form_submit_button("Add to BoQ")
                if submitted and item:
                    boq_id = f"BOQ-{len(db['boq']) + 1:03d}"
                    total = quantity * unit_cost
                    db["boq"].append({
                        "id": boq_id,
                        "project_id": p_id,
                        "category": category,
                        "item": item,
                        "quantity": quantity,
                        "unit": unit,
                        "unit_cost": unit_cost,
                        "total": total
                    })
                    save_memory(db)
                    st.success(f"Added '{item}' to BoQ with calculated total of ${total:,.2f}")
                    st.rerun()
