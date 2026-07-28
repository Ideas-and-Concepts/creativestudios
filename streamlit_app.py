import streamlit as st
import json, uuid
from pathlib import Path
from datetime import datetime
import pandas as pd

import os
import json
from pathlib import Path
from sqlalchemy import create_engine, text

# ---------------------------------------------------------
# Database Engine & Connection Setup
# ---------------------------------------------------------
DATABASE_URL = os.environ.get("DATABASE_URL")

# Fix Render URL compatibility (SQLAlchemy requires postgresql:// instead of postgres://)
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def get_engine():
    """Creates database engine if DATABASE_URL is set."""
    if DATABASE_URL:
        return create_engine(DATABASE_URL, pool_pre_ping=True)
    return None

def init_db():
    """Ensures the app_state table exists in PostgreSQL."""
    engine = get_engine()
    if engine:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS app_state (
                    id INT PRIMARY KEY,
                    data JSONB
                );
            """))

# ---------------------------------------------------------
# Memory Persistence Functions (PostgreSQL with Local Fallback)
# ---------------------------------------------------------
MEMORY_FILE = Path("creativestudios_db.json")

def load_memory():
    """Loads state from Render PostgreSQL. Falls back to local JSON if no DB URL."""
    engine = get_engine()
    
    # --- Local JSON Fallback (for offline testing) ---
    if not engine:
        if MEMORY_FILE.exists():
            try:
                return json.loads(MEMORY_FILE.read_text())
            except Exception:
                pass
        return DEFAULT_MEMORY.copy()

    # --- PostgreSQL Storage ---
    try:
        init_db()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT data FROM app_state WHERE id = 1;")).fetchone()
            if result and result[0]:
                data = result[0]
                return json.loads(data) if isinstance(data, str) else data
        
        # Initialize default memory in DB if table is empty
        save_memory(DEFAULT_MEMORY)
        return DEFAULT_MEMORY.copy()
    except Exception as e:
        st.error(f"Database Read Error: {e}")
        return DEFAULT_MEMORY.copy()

def save_memory(mem):
    """Saves state to Render PostgreSQL. Falls back to local JSON if no DB URL."""
    engine = get_engine()

    # --- Local JSON Fallback (for offline testing) ---
    if not engine:
        MEMORY_FILE.write_text(json.dumps(mem, indent=2))
        return

    # --- PostgreSQL Storage ---
    try:
        init_db()
        with engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO app_state (id, data)
                    VALUES (1, :data::jsonb)
                    ON CONFLICT (id) DO UPDATE
                    SET data = EXCLUDED.data;
                """),
                {"data": json.dumps(mem)}
            )
    except Exception as e:
        st.error(f"Database Write Error: {e}")


# Look for this line near the top of streamlit_app.py:
# MEMORY_FILE = Path("creativestudios_db.json")

# Replace it with:
MEMORY_DIR = Path("/var/data")
MEMORY_DIR.mkdir(parents=True, exist_ok=True)  # Creates directory if it doesn't exist
MEMORY_FILE = MEMORY_DIR / "creativestudios_db.json"


# ---------------------------------------------------------
# Page Configuration & Memory Initialization
# ---------------------------------------------------------
st.set_page_config(
    page_title="Creative Studios - Architectural & MEP Management System",
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
            "discipline": "Mechanical (HVAC)",
            "title": "HVAC Duct Layout & Chiller Specs",
            "version": "v1.0",
            "file_name": "M-101_HVAC_Ducts.pdf",
            "status": "Pending Review",
            "uploaded_by": "Eng. Mark Miller",
            "uploaded_at": "2026-01-21T11:00:00"
        },
        {
            "id": "DWG-103",
            "project_id": "PRJ-001",
            "discipline": "Electrical",
            "title": "Single-Line Diagram & Circuit Distribution",
            "version": "v1.0",
            "file_name": "E-101_Electrical_SLD.pdf",
            "status": "Approved",
            "uploaded_by": "Eng. Sarah Watts",
            "uploaded_at": "2026-01-22T09:45:00"
        },
        {
            "id": "DWG-104",
            "project_id": "PRJ-001",
            "discipline": "Plumbing",
            "title": "Drainage, Waste & Vent (DWV) System",
            "version": "v1.1",
            "file_name": "P-101_Plumbing_Riser.pdf",
            "status": "Pending Review",
            "uploaded_by": "Eng. Alex Rivers",
            "uploaded_at": "2026-01-23T16:20:00"
        }
    ],
    "procurement_approvals": [
        {
            "id": "APP-001",
            "project_id": "PRJ-001",
            "item_name": "Main Electrical Panel & Transformers",
            "arch_status": "Approved",
            "mep_status": "Approved",
            "eng_status": "Approved",
            "procurement_status": "Ready for Release",
            "notes": "Electrical load calculations verified by MEP engineer."
        }
    ],
    "boq": [
        {
            "id": "BOQ-001",
            "project_id": "PRJ-001",
            "category": "Plumbing",
            "item": "PEX Water Supply Piping & Valves",
            "quantity": 500.0,
            "unit": "Meters",
            "unit_cost": 18.5,
            "total": 9250.0
        },
        {
            "id": "BOQ-002",
            "project_id": "PRJ-001",
            "category": "Mechanical (HVAC)",
            "item": "Central Air Handling Unit (AHU) 15 TON",
            "quantity": 2.0,
            "unit": "Units",
            "unit_cost": 8500.0,
            "total": 17000.0
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

def get_project_name(project_id):
    proj = next((p for p in db["projects"] if p["id"] == project_id), None)
    return proj["name"] if proj else "Unknown"

# ---------------------------------------------------------
# Sidebar Navigation
# ---------------------------------------------------------
st.sidebar.title("📐 Creative Studios")
st.sidebar.caption("Architectural, Structural & MEP Management")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Project Directory",
        "Drawing Vault (Arch & MEP)",
        "Procurement & Approvals",
        "BoQ (Materials, Labor & MEP)"
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
    st.markdown("Real-time project tracking across Architectural, Structural, and MEP engineering.")

    col1, col2, col3, col4 = st.columns(4)
    total_budget = sum(p.get("budget", 0) for p in db["projects"])
    pending_approvals = sum(
        1 for a in db["procurement_approvals"] 
        if a.get("procurement_status") != "Ready for Release"
    )

    col1.metric("Total Projects", len(db["projects"]))
    col2.metric("Total Vault Documents", len(db["drawings"]))
    col3.metric("Pending Approvals", pending_approvals)
    col4.metric("Total Portfolio Budget", f"${total_budget:,.2f}")

    st.markdown("---")
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Drawings by Discipline")
        if db["drawings"]:
            df_d = pd.DataFrame(db["drawings"])
            discipline_counts = df_d["discipline"].value_counts().reset_index()
            discipline_counts.columns = ["Discipline", "Count"]
            st.dataframe(discipline_counts, use_container_width=True)
        else:
            st.info("No drawings available.")

    with col_b:
        st.subheader("Latest Vault Submissions")
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
    st.markdown("Manage both **New Builds** and **Renovations / Retrofits**.")

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
            p_type = st.selectbox("Project Classification", [
                "New Construction", 
                "Renovation / MEP Overhaul", 
                "Structural Upgrade",
                "Fit-out & MEP Retrofit"
            ])
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
# MODULE 3: DRAWING VAULT (ARCH & MEP)
# ---------------------------------------------------------
elif page == "Drawing Vault (Arch & MEP)":
    st.title("📐 Drawing Vault & Version Control")
    st.markdown("Central storage for Architectural, Structural, and Mechanical/Electrical/Plumbing (MEP) plans.")

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
                discipline = st.selectbox("Discipline Classification", [
                    "Architectural",
                    "Structural Engineering",
                    "Mechanical (HVAC)",
                    "Electrical & Power",
                    "Plumbing & Sanitation",
                    "Fire Protection & Life Safety",
                    "Civil / Site Plan"
                ])
                title = st.text_input("Drawing Title (e.g., HVAC Duct Schematic / Electrical Riser)")
                version = st.text_input("Version Tag", value="v1.0")
                uploaded_by = st.text_input("Uploaded By", value="Lead Engineer / Architect")
                uploaded_file = st.file_uploader("Upload Drawing File (PDF, DWG, PNG)", type=["pdf", "dwg", "png", "jpg"])

                submitted = st.form_submit_button("Record Drawing in Vault")
                if submitted and title:
                    file_name = uploaded_file.name if uploaded_file else "Drawing_Plan.pdf"
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
    st.markdown("Multi-stage approval pipeline requiring **Architectural**, **Structural**, and **MEP Engineering** sign-offs.")

    if not db["projects"]:
        st.warning("Please create a project first.")
    else:
        tab1, tab2 = st.tabs(["Active Sign-off Pipeline", "Initiate Approval Request"])

        with tab1:
            st.subheader("Tri-Discipline Sign-off Matrix")
            if db["procurement_approvals"]:
                for idx, item in enumerate(db["procurement_approvals"]):
                    with st.expander(f"📦 {item['item_name']} (Project: {item['project_id']})"):
                        col1, col2, col3, col4 = st.columns(4)

                        # 1. Architectural Sign-off
                        with col1:
                            st.markdown("**1. Architectural**")
                            st.caption(f"Status: {item.get('arch_status', 'Pending')}")
                            if item.get('arch_status') != "Approved":
                                if st.button("Approve (Arch)", key=f"arch_{idx}"):
                                    item['arch_status'] = "Approved"
                                    save_memory(db)
                                    st.rerun()

                        # 2. Structural Sign-off
                        with col2:
                            st.markdown("**2. Structural**")
                            st.caption(f"Status: {item.get('eng_status', 'Pending')}")
                            if item.get('eng_status') != "Approved":
                                if st.button("Approve (Struct)", key=f"eng_{idx}"):
                                    item['eng_status'] = "Approved"
                                    save_memory(db)
                                    st.rerun()

                        # 3. MEP Sign-off
                        with col3:
                            st.markdown("**3. MEP Engineering**")
                            st.caption(f"Status: {item.get('mep_status', 'Pending')}")
                            if item.get('mep_status') != "Approved":
                                if st.button("Approve (MEP)", key=f"mep_{idx}"):
                                    item['mep_status'] = "Approved"
                                    save_memory(db)
                                    st.rerun()

                        # 4. Procurement Release Status
                        with col4:
                            st.markdown("**4. Procurement Release**")
                            arch_ok = item.get('arch_status') == "Approved"
                            eng_ok = item.get('eng_status') == "Approved"
                            mep_ok = item.get('mep_status') == "Approved"

                            if arch_ok and eng_ok and mep_ok:
                                item['procurement_status'] = "Ready for Release"
                                st.success("✅ Fully Approved")
                            else:
                                item['procurement_status'] = "Locked"
                                st.warning("🔒 Pending Approvals")

                        st.write(f"**Technical Notes:** {item.get('notes', 'N/A')}")
            else:
                st.info("No procurement approval requests currently in pipeline.")

        with tab2:
            st.subheader("Request Sign-off for Procurement Item")
            with st.form("new_approval_form"):
                proj_id = st.selectbox(
                    "Project",
                    options=[p["id"] for p in db["projects"]],
                    format_func=lambda x: f"{x} - {get_project_name(x)}"
                )
                item_name = st.text_input("Item Description (e.g., Main Distribution Panel, Chillers, DWV Pipe Batch)")
                notes = st.text_area("Engineering & Design Compliance Notes")

                submitted = st.form_submit_button("Submit into Approval Pipeline")
                if submitted and item_name:
                    app_id = f"APP-{len(db['procurement_approvals']) + 1:03d}"
                    db["procurement_approvals"].append({
                        "id": app_id,
                        "project_id": proj_id,
                        "item_name": item_name,
                        "arch_status": "Pending",
                        "eng_status": "Pending",
                        "mep_status": "Pending",
                        "procurement_status": "Locked",
                        "notes": notes
                    })
                    save_memory(db)
                    st.success(f"Approval pipeline item '{item_name}' created under ID: {app_id}")
                    st.rerun()

# ---------------------------------------------------------
# MODULE 5: BILL OF QUANTITIES (BOQ) INCLUDING MEP
# ---------------------------------------------------------
elif page == "BoQ (Materials, Labor & MEP)":
    st.title("🧱 Bill of Quantities (BoQ)")
    st.markdown("Track costs for Architectural, Structural, and **Mechanical, Electrical, & Plumbing (MEP)** assets.")

    if not db["projects"]:
        st.warning("Please create a project first.")
    else:
        tab1, tab2 = st.tabs(["Project BoQ Ledger", "Add BoQ Line Item"])

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
            st.subheader("Add Material, MEP, or Labor Entry")
            with st.form("boq_form"):
                p_id = st.selectbox(
                    "Project Target",
                    options=[p["id"] for p in db["projects"]],
                    format_func=lambda x: f"{x} - {get_project_name(x)}"
                )
                category = st.selectbox("Category", [
                    "Mechanical (HVAC)",
                    "Electrical & Wiring",
                    "Plumbing & Fixtures",
                    "Civil & Structural Materials",
                    "Architectural Finishes",
                    "MEP Labor & Subcontractors",
                    "General Labor"
                ])
                item = st.text_input("Item Description (e.g., 100A Busbars, 2-inch Copper Pipes, Ductwork)")
                quantity = st.number_input("Quantity", min_value=0.1, value=1.0)
                unit = st.text_input("Unit of Measure (e.g., Meters, Units, Hours, Sq Ft)", value="Units")
                unit_cost = st.number_input("Cost per Unit ($)", min_value=0.0, value=10.0)

                submitted = st.form_submit_button("Add to BoQ Ledger")
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
