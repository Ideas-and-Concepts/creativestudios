import os
import json
import hashlib
import pandas as pd
import streamlit as st
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine, text

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Creative Studios - Architectural & MEP Management",
    page_icon="📐",
    layout="wide"
)

# ---------------------------------------------------------
# Helper Functions for Security & Passwords
# ---------------------------------------------------------
def hash_password(password: str) -> str:
    """Hashes passwords using SHA-256 for secure comparison."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# Default default user credentials
DEFAULT_USERS = [
    {"username": "admin", "password_hash": hash_password("admin123"), "name": "System Admin", "role": "Admin"},
    {"username": "jane_arch", "password_hash": hash_password("arch123"), "name": "Arch. Jane Doe", "role": "Architect"},
    {"username": "john_struct", "password_hash": hash_password("struct123"), "name": "Eng. John Smith", "role": "Structural Engineer"},
    {"username": "mark_mep", "password_hash": hash_password("mep123"), "name": "Eng. Mark Miller", "role": "MEP Engineer"},
    {"username": "sam_proc", "password_hash": hash_password("proc123"), "name": "Sam Procurement", "role": "Procurement Officer"}
]

# ---------------------------------------------------------
# Database Connection & Engine Caching
# ---------------------------------------------------------
@st.cache_resource
def get_engine():
    """Creates a cached, pooled database connection engine."""
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        return create_engine(db_url, pool_pre_ping=True, pool_size=5, max_overflow=10)
    return None

def init_db():
    """Initializes PostgreSQL table schema if missing."""
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
# Memory Persistence Engine (PostgreSQL with Local Fallback)
# ---------------------------------------------------------
MEMORY_FILE = Path("creativestudios_db.json")

DEFAULT_MEMORY = {
    "users": DEFAULT_USERS,
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
        }
    ],
    "procurement_approvals": [
        {
            "id": "APP-001",
            "project_id": "PRJ-001",
            "item_name": "Main Electrical Panel & Transformers",
            "arch_status": "Approved",
            "arch_approved_by": "Arch. Jane Doe",
            "eng_status": "Approved",
            "eng_approved_by": "Eng. John Smith",
            "mep_status": "Pending",
            "mep_approved_by": None,
            "procurement_status": "Locked",
            "notes": "Awaiting MEP sign-off on breaker panel ratings."
        }
    ],
    "boq": [
        {
            "id": "BOQ-001",
            "project_id": "PRJ-001",
            "category": "Plumbing & Fixtures",
            "item": "PEX Water Supply Piping & Valves",
            "quantity": 500.0,
            "unit": "Meters",
            "unit_cost": 18.5,
            "total": 9250.0
        }
    ]
}

def load_memory():
    """Loads state from PostgreSQL or local JSON file."""
    engine = get_engine()
    
    if not engine:
        if MEMORY_FILE.exists():
            try:
                data = json.loads(MEMORY_FILE.read_text())
                if "users" not in data:
                    data["users"] = DEFAULT_USERS
                return data
            except Exception:
                pass
        return DEFAULT_MEMORY.copy()

    try:
        init_db()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT data FROM app_state WHERE id = 1;")).fetchone()
            if result and result[0] is not None:
                data = result[0]
                data_dict = data if isinstance(data, dict) else json.loads(data)
                if "users" not in data_dict:
                    data_dict["users"] = DEFAULT_USERS
                return data_dict
        
        save_memory(DEFAULT_MEMORY)
        return DEFAULT_MEMORY.copy()
    except Exception as e:
        st.warning(f"Database connection warning: {e}. Falling back to default state.")
        return DEFAULT_MEMORY.copy()

def save_memory(mem):
    """Persists state to PostgreSQL or local disk."""
    engine = get_engine()

    if not engine:
        MEMORY_FILE.write_text(json.dumps(mem, indent=2))
        return

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
        st.error(f"Failed to save changes to Database: {e}")

db = load_memory()

def get_project_name(project_id):
    proj = next((p for p in db.get("projects", []) if p["id"] == project_id), None)
    return proj["name"] if proj else "Unknown"

def safe_dataframe(data_list, preferred_columns):
    """Safely builds a pandas DataFrame avoiding missing column exceptions."""
    if not data_list:
        return pd.DataFrame()
    df = pd.DataFrame(data_list)
    available_cols = [col for col in preferred_columns if col in df.columns]
    return df[available_cols]

# ---------------------------------------------------------
# AUTHENTICATION & SESSION MANAGEMENT
# ---------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["user"] = None

def login(username, password):
    user = next((u for u in db.get("users", []) if u["username"].lower() == username.lower()), None)
    if user and user["password_hash"] == hash_password(password):
        st.session_state["authenticated"] = True
        st.session_state["user"] = user
        return True
    return False

def logout():
    st.session_state["authenticated"] = False
    st.session_state["user"] = None
    st.rerun()

# --- LOGIN SCREEN ---
if not st.session_state["authenticated"]:
    st.title("🔐 Creative Studios Login")
    st.markdown("Sign in to access Architectural, Structural, and MEP workflows.")

    col_login, col_demo = st.columns([1, 1])

    with col_login:
        with st.form("login_form"):
            user_input = st.text_input("Username")
            pass_input = st.text_input("Password", type="password")
            submit_btn = st.form_submit_button("Sign In")

            if submit_btn:
                if login(user_input, pass_input):
                    st.success("Authentication successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

    with col_demo:
        st.subheader("💡 Demo Accounts Quick Switch")
        st.caption("Click any account below to pre-fill credentials for testing:")
        
        for u in db.get("users", []):
            role_badge = f"**{u['name']}** ({u['role']})"
            if st.button(f"Login as {u['name']} [{u['role']}]", key=f"quick_{u['username']}"):
                # Password mapping for demo
                pwd_map = {
                    "admin": "admin123",
                    "jane_arch": "arch123",
                    "john_struct": "struct123",
                    "mark_mep": "mep123",
                    "sam_proc": "proc123"
                }
                login(u['username'], pwd_map.get(u['username'], "admin123"))
                st.rerun()

    st.stop()  # Stop execution here until logged in

# ---------------------------------------------------------
# SIDEBAR PROFILE & NAVIGATION
# ---------------------------------------------------------
current_user = st.session_state["user"]

st.sidebar.title("📐 Creative Studios")
st.sidebar.markdown(f"👤 **{current_user['name']}**")
st.sidebar.caption(f"Role: `{current_user['role']}`")

if st.sidebar.button("🚪 Sign Out"):
    logout()

st.sidebar.markdown("---")

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
st.sidebar.write("**System Status**")
st.sidebar.caption(f"Active Projects: {len(db.get('projects', []))}")
st.sidebar.caption(f"Vault Drawings: {len(db.get('drawings', []))}")

# ---------------------------------------------------------
# MODULE 1: DASHBOARD
# ---------------------------------------------------------
if page == "Dashboard":
    st.title("📊 Executive Dashboard")
    st.markdown(f"Welcome back, **{current_user['name']}**.")

    col1, col2, col3, col4 = st.columns(4)
    total_budget = sum(p.get("budget", 0) for p in db.get("projects", []))
    pending_approvals = sum(
        1 for a in db.get("procurement_approvals", []) 
        if a.get("procurement_status") != "Ready for Release"
    )

    col1.metric("Total Projects", len(db.get("projects", [])))
    col2.metric("Vault Documents", len(db.get("drawings", [])))
    col3.metric("Pending Approvals", pending_approvals)
    col4.metric("Total Portfolio Budget", f"${total_budget:,.2f}")

    st.markdown("---")
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Drawings by Discipline")
        if db.get("drawings"):
            df_d = pd.DataFrame(db["drawings"])
            if "discipline" in df_d.columns:
                discipline_counts = df_d["discipline"].value_counts().reset_index()
                discipline_counts.columns = ["Discipline", "Count"]
                st.dataframe(discipline_counts, use_container_width=True)
        else:
            st.info("No drawing entries registered.")

    with col_b:
        st.subheader("Recent Vault Submissions")
        if db.get("drawings"):
            df_recent = safe_dataframe(db["drawings"], ["discipline", "title", "version", "status", "uploaded_at"])
            st.dataframe(df_recent.tail(5), use_container_width=True)
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
        if db.get("projects"):
            df_projects = safe_dataframe(
                db["projects"], 
                ["id", "name", "type", "status", "budget", "created", "description"]
            )
            st.dataframe(df_projects, use_container_width=True)
        else:
            st.info("No active projects found.")

    with tab2:
        st.subheader("Register a Project")
        if current_user["role"] in ["Admin", "Architect", "Procurement Officer"]:
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
                    st.success(f"Project '{p_name}' created with ID: {new_id}")
                    st.rerun()
        else:
            st.warning("🔒 Only Project Managers, Architects, or Procurement Officers can register new projects.")

# ---------------------------------------------------------
# MODULE 3: DRAWING VAULT (ARCH & MEP)
# ---------------------------------------------------------
elif page == "Drawing Vault (Arch & MEP)":
    st.title("📐 Drawing Vault & Version Control")
    st.markdown("Central storage for Architectural, Structural, and MEP plans.")

    if not db.get("projects"):
        st.warning("Please create at least one project before managing drawings.")
    else:
        tab1, tab2 = st.tabs(["Document Repository", "Upload New Drawing / Revision"])

        with tab1:
            project_filter = st.selectbox(
                "Filter by Project",
                options=["All"] + [p["id"] for p in db["projects"]],
                format_func=lambda x: "All Projects" if x == "All" else f"{x} - {get_project_name(x)}"
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
                uploaded_by = st.text_input("Uploaded By", value=current_user["name"], disabled=True)
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
                        "uploaded_by": current_user["name"],
                        "uploaded_at": datetime.now().isoformat()
                    })
                    save_memory(db)
                    st.success(f"Drawing '{title}' registered in vault as ID: {dwg_id}")
                    st.rerun()

# ---------------------------------------------------------
# MODULE 4: PROCUREMENT & APPROVAL WORKFLOW (RBAC ENFORCED)
# ---------------------------------------------------------
elif page == "Procurement & Approvals":
    st.title("🛡 Approval & Procurement Engine")
    st.markdown("Role-enforced sign-off matrix across **Architectural**, **Structural**, and **MEP Engineering**.")

    if not db.get("projects"):
        st.warning("Please create a project first.")
    else:
        tab1, tab2 = st.tabs(["Active Sign-off Pipeline", "Initiate Approval Request"])

        with tab1:
            st.subheader("Role-Gated Sign-off Matrix")
            approvals = db.get("procurement_approvals", [])
            if approvals:
                for item in approvals:
                    item_id = item.get("id", "APP-UNKNOWN")
                    with st.expander(f"📦 {item.get('item_name', 'Item')} (Project: {item.get('project_id')})"):
                        col1, col2, col3, col4 = st.columns(4)

                        # --- 1. Architectural Sign-off ---
                        with col1:
                            st.markdown("**1. Architectural**")
                            arch_status = item.get('arch_status', 'Pending')
                            st.caption(f"Status: `{arch_status}`")
                            if item.get('arch_approved_by'):
                                st.caption(f"By: {item['arch_approved_by']}")
                            
                            if arch_status != "Approved":
                                can_approve_arch = current_user["role"] in ["Architect", "Admin"]
                                if st.button("Approve (Arch)", key=f"arch_{item_id}", disabled=not can_approve_arch):
                                    item['arch_status'] = "Approved"
                                    item['arch_approved_by'] = current_user["name"]
                                    save_memory(db)
                                    st.rerun()
                                if not can_approve_arch:
                                    st.caption("🔒 Requires Architect role")

                        # --- 2. Structural Sign-off ---
                        with col2:
                            st.markdown("**2. Structural**")
                            eng_status = item.get('eng_status', 'Pending')
                            st.caption(f"Status: `{eng_status}`")
                            if item.get('eng_approved_by'):
                                st.caption(f"By: {item['eng_approved_by']}")

                            if eng_status != "Approved":
                                can_approve_struct = current_user["role"] in ["Structural Engineer", "Admin"]
                                if st.button("Approve (Struct)", key=f"eng_{item_id}", disabled=not can_approve_struct):
                                    item['eng_status'] = "Approved"
                                    item['eng_approved_by'] = current_user["name"]
                                    save_memory(db)
                                    st.rerun()
                                if not can_approve_struct:
                                    st.caption("🔒 Requires Structural Eng. role")

                        # --- 3. MEP Sign-off ---
                        with col3:
                            st.markdown("**3. MEP Engineering**")
                            mep_status = item.get('mep_status', 'Pending')
                            st.caption(f"Status: `{mep_status}`")
                            if item.get('mep_approved_by'):
                                st.caption(f"By: {item['mep_approved_by']}")

                            if mep_status != "Approved":
                                can_approve_mep = current_user["role"] in ["MEP Engineer", "Admin"]
                                if st.button("Approve (MEP)", key=f"mep_{item_id}", disabled=not can_approve_mep):
                                    item['mep_status'] = "Approved"
                                    item['mep_approved_by'] = current_user["name"]
                                    save_memory(db)
                                    st.rerun()
                                if not can_approve_mep:
                                    st.caption("🔒 Requires MEP Eng. role")

                        # --- 4. Final Procurement Release ---
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
                                st.warning("🔒 Sign-offs Pending")

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
                        "arch_approved_by": None,
                        "eng_status": "Pending",
                        "eng_approved_by": None,
                        "mep_status": "Pending",
                        "mep_approved_by": None,
                        "procurement_status": "Locked",
                        "notes": notes
                    })
                    save_memory(db)
                    st.success(f"Approval pipeline item '{item_name}' created under ID: {app_id}")
                    st.rerun()

# ---------------------------------------------------------
# MODULE 5: BILL OF QUANTITIES (BOQ)
# ---------------------------------------------------------
elif page == "BoQ (Materials, Labor & MEP)":
    st.title("🧱 Bill of Quantities (BoQ)")
    st.markdown("Track costs for Architectural, Structural, and **Mechanical, Electrical, & Plumbing (MEP)** assets.")

    if not db.get("projects"):
        st.warning("Please create a project first.")
    else:
        tab1, tab2 = st.tabs(["Project BoQ Ledger", "Add BoQ Line Item"])

        with tab1:
            proj_id = st.selectbox(
                "Select Project",
                options=[p["id"] for p in db["projects"]],
                format_func=lambda x: f"{x} - {get_project_name(x)}"
            )

            boq_items = [b for b in db.get("boq", []) if b.get("project_id") == proj_id]

            if boq_items:
                df_boq = safe_dataframe(
                    boq_items,
                    ["id", "category", "item", "quantity", "unit", "unit_cost", "total"]
                )
                st.dataframe(df_boq, use_container_width=True)
                total_cost = sum(b.get("total", 0) for b in boq_items)
                st.metric("Total Calculated BoQ Cost", f"${total_cost:,.2f}")
            else:
                st.info("No items in BoQ for this project yet.")

        with tab2:
            st.subheader("Add Material, MEP, or Labor Entry")
            if current_user["role"] in ["Procurement Officer", "Admin", "Architect", "MEP Engineer", "Structural Engineer"]:
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
