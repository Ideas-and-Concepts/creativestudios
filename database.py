import os
import json
import streamlit as st
from pathlib import Path
from sqlalchemy import create_engine, text
from utils import hash_password

MEMORY_FILE = "creativestudios_db.json"

DEFAULT_USERS = [
    {"username": "admin", "password_hash": hash_password("admin123"), "name": "System Administrator", "role": "Admin"},
    {"username": "arch_lead", "password_hash": hash_password("arch123"), "name": "Lead Architect", "role": "Architect"},
    {"username": "struct_eng", "password_hash": hash_password("struct123"), "name": "Structural Specialist", "role": "Structural Engineer"},
    {"username": "elec_eng", "password_hash": hash_password("elec123"), "name": "Electrical Systems Lead", "role": "Electrical Engineer"},
    {"username": "plumber_lead", "password_hash": hash_password("plum123"), "name": "Master Plumber", "role": "Plumber"}
]

DEFAULT_MEMORY = {
    "users": DEFAULT_USERS,
    "projects": [
        {
            "id": "PRJ-001",
            "name": "Grand Horizon Commercial Complex",
            "type": "Commercial",
            "phase": "Schematic Design",
            "budget": 1250000.0,
            "created_at": "2026-02-10",
            "description": "10-story mixed-use commercial space with basement parking and green roofing."
        }
    ],
    "drawings": [],
    "approvals": [],
    "boq": []
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
        if Path(MEMORY_FILE).exists():
            try:
                data = json.loads(Path(MEMORY_FILE).read_text())
                if "users" not in data:
                    data["users"] = DEFAULT_USERS
                if "projects" not in data:
                    data["projects"] = DEFAULT_MEMORY["projects"]
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
                if "projects" not in data_dict:
                    data_dict["projects"] = DEFAULT_MEMORY["projects"]
                return data_dict
        
        save_memory(DEFAULT_MEMORY)
        return DEFAULT_MEMORY.copy()
    except Exception:
        return DEFAULT_MEMORY.copy()

def save_memory(mem):
    engine = get_engine()
    if not engine:
        Path(MEMORY_FILE).write_text(json.dumps(mem, indent=2))
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
