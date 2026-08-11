import os
import json
import base64
import hashlib
import pandas as pd
import streamlit as st
from pathlib import Path
from sqlalchemy import create_engine, text

MEMORY_FILE = "creativestudios_db.json"
LOGO_FILE = "logo.svg"

def ensure_logo_svg():
    """Generates the transparent Pisces-inspired vector SVG logo."""
    svg_content = """<svg width="500" height="500" viewBox="0 0 500 500" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="piscesGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#2563EB"/>
            <stop offset="100%" stop-color="#06B6D4"/>
        </linearGradient>
    </defs>
    <path d="M150 250H350" stroke="url(#piscesGrad)" stroke-width="32" stroke-linecap="round"/>
    <path d="M190 150C135 205 135 295 190 350" stroke="url(#piscesGrad)" stroke-width="32" stroke-linecap="round" fill="none"/>
    <path d="M310 150C365 205 365 295 310 350" stroke="url(#piscesGrad)" stroke-width="32" stroke-linecap="round" fill="none"/>
</svg>"""
    Path(LOGO_FILE).write_text(svg_content)

def get_logo_html(width=130):
    ensure_logo_svg()
    if Path(LOGO_FILE).exists():
        encoded = base64.b64encode(Path(LOGO_FILE).read_bytes()).decode()
        return f"""
        <div style="display: flex; justify-content: center; align-items: center; width: 100%; margin-bottom: 20px;">
            <img src="data:image/svg+xml;base64,{encoded}" width="{width}" style="display: block;" />
        </div>
        """
    return ""

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# Defined AEC Roles
DEFAULT_USERS = [
    {"username": "admin", "password_hash": hash_password("admin123"), "name": "System Administrator", "role": "Admin"},
    {"username": "arch_lead", "password_hash": hash_password("arch123"), "name": "Lead Architect", "role": "Architect"},
    {"username": "struct_eng", "password_hash": hash_password("struct123"), "name": "Structural Specialist", "role": "Structural Engineer"},
    {"username": "elec_eng", "password_hash": hash_password("elec123"), "name": "Electrical Systems Lead", "role": "Electrical Engineer"},
    {"username": "plumber_lead", "password_hash": hash_password("plum123"), "name": "Master Plumber", "role": "Plumber"}
]

DEFAULT_MEMORY = {
    "users": DEFAULT_USERS,
    "projects": [],
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
    ensure_logo_svg()
    engine = get_engine()
    if not engine:
        if Path(MEMORY_FILE).exists():
            try:
                data = json.loads(Path(MEMORY_FILE).read_text())
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

def render_sidebar():
    st.sidebar.markdown(get_logo_html(width=100), unsafe_allow_html=True)
    current_user = st.session_state.get("user")
    if current_user:
        st.sidebar.markdown(f"👤 **{current_user['name']}**")
        st.sidebar.caption(f"Role: `{current_user['role']}`")
        if st.sidebar.button("🚪 Sign Out", use_container_width=True):
            st.session_state["authenticated"] = False
            st.session_state["user"] = None
            st.rerun()
    st.sidebar.markdown("---")

def require_auth():
    if not st.session_state.get("authenticated", False):
        st.warning("Please sign in from the main login screen to access Creative Studios.")
        st.stop()
    render_sidebar()
