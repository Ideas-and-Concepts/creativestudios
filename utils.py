import os
import json
import hashlib
import pandas as pd
import streamlit as st
from pathlib import Path
from sqlalchemy import create_engine, text

MEMORY_FILE = Path("creativestudios_db.json")

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

DEFAULT_USERS = [
    {"username": "admin", "password_hash": hash_password("admin123"), "name": "System Admin", "role": "Admin"},
    {"username": "jane_arch", "password_hash": hash_password("arch123"), "name": "Arch. Jane Doe", "role": "Architect"},
    {"username": "john_struct", "password_hash": hash_password("struct123"), "name": "Eng. John Smith", "role": "Structural Engineer"},
    {"username": "mark_mep", "password_hash": hash_password("mep123"), "name": "Eng. Mark Miller", "role": "MEP Engineer"},
    {"username": "sam_proc", "password_hash": hash_password("proc123"), "name": "Sam Procurement", "role": "Procurement Officer"}
]

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

@st.cache_resource
def get_engine():
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        return create_engine(db_url, pool_pre_ping=True, pool_size=5, max_overflow=10)
    return None

def init_db():
    engine = get_engine()
    if engine:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS app_state (
                    id INT PRIMARY KEY,
                    data JSONB
                );
            """))

def load_memory():
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
    except Exception:
        return DEFAULT_MEMORY.copy()

def save_memory(mem):
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

def get_project_name(db, project_id):
    proj = next((p for p in db.get("projects", []) if p["id"] == project_id), None)
    return proj["name"] if proj else "Unknown"

def safe_dataframe(data_list, preferred_columns):
    if not data_list:
        return pd.DataFrame()
    df = pd.DataFrame(data_list)
    available_cols = [col for col in preferred_columns if col in df.columns]
    return df[available_cols]

def render_sidebar_logo():
    """Injects the logo into the sidebar cleanly without text app titles."""
    if Path("logo.jpg").exists():
        st.sidebar.image("logo.jpg", use_container_width=True)
    st.sidebar.markdown("---")

def require_auth():
    """Guard function placed at top of every page script with logo branding."""
    if not st.session_state.get("authenticated", False):
        st.warning("Please sign in from the main Login page to access this system.")
        st.stop()
    
    render_sidebar_logo()
    
    current_user = st.session_state["user"]
    st.sidebar.markdown(f"👤 **{current_user['name']}**")
    st.sidebar.caption(f"Role: `{current_user['role']}`")
    if st.sidebar.button("🚪 Sign Out"):
        st.session_state["authenticated"] = False
        st.session_state["user"] = None
        st.rerun()
    st.sidebar.markdown("---")
