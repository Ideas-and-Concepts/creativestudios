import streamlit as st
from pathlib import Path
from modules.utils import ensure_logo_svg, get_logo_html, LOGO_FILE
from modules.database import load_memory
from modules.auth import login_user, require_auth
from modules.projects import render_projects_module
from modules.drawings import render_drawings_module
from modules.approvals import render_approvals_module
from modules.boq import render_boq_module
from modules.rfi import render_rfi_module
from modules.site_logs import render_site_logs_module

# Ensure the logo SVG exists before setting page config
ensure_logo_svg()

st.set_page_config(
    page_title="Creative Studios — AEC Platform",
    page_icon=LOGO_FILE,
    layout="wide"
)

# ---------- Custom CSS for a unique, simple UI ----------
def inject_custom_css():
    st.markdown("""
    <style>
        /* Import clean font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Hide Streamlit default header and footer */
        header {visibility: hidden;}
        footer {visibility: hidden;}

        /* Main background */
        .main {
            background-color: #f8fafc;
        }

        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e2e8f0;
        }
        [data-testid="stSidebar"] > div:first-child {
            padding-top: 2rem;
        }

        /* All cards / containers */
        .stContainer, .stExpander {
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            border: 1px solid #e2e8f0;
        }

        /* Expanders – clean header */
        .stExpander > div:first-child {
            background: transparent;
            border-bottom: 1px solid #f1f5f9;
        }

        /* Buttons */
        .stButton > button {
            border-radius: 8px;
            font-weight: 500;
            background-color: #1e3a8a;
            color: white;
            border: none;
            padding: 0.5rem 1.25rem;
            transition: all 0.2s;
        }
        .stButton > button:hover {
            background-color: #1e40af;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        /* Inputs */
        .stTextInput > div > div > input,
        .stTextArea > div > textarea,
        .stSelectbox > div > div > div {
            border-radius: 8px;
            border: 1px solid #cbd5e1;
        }

        /* Titles and captions */
        h1, h2, h3 {
            color: #0f172a;
            font-weight: 600;
        }
        .stCaption {
            color: #64748b;
        }

        /* Metric-like boxes (for status displays) */
        .metric-box {
            background: white;
            border-radius: 12px;
            padding: 1.25rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            border: 1px solid #e2e8f0;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
            border-bottom: 1px solid #e2e8f0;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 4px 4px 0 0;
            padding: 0.75rem 1rem;
            font-weight: 500;
            color: #475569;
        }
        .stTabs [aria-selected="true"] {
            color: #1e3a8a;
            border-bottom: 2px solid #1e3a8a;
        }

        /* Login page special styles */
        .login-container {
            max-width: 400px;
            margin: 0 auto;
        }

        /* Hide hamburger menu & "Made with Streamlit" */
        [data-testid="stToolbar"] {visibility: hidden;}
        .viewerBadge_container__1QSob {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

inject_custom_css()

db = load_memory()

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["user"] = None

if not st.session_state["authenticated"]:
    # -------- LOGIN PAGE (refined) --------
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(get_logo_html(width=100), unsafe_allow_html=True)
        st.markdown(
            "<h2 style='text-align: center; color: #0F172A; font-weight: 700;'>Creative Studios</h2>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='text-align: center; color: #64748B;'>Architectural, Engineering & Construction Collaboration</p><br>",
            unsafe_allow_html=True,
        )

        with st.form("login_form"):
            user_input = st.text_input("Username")
            pass_input = st.text_input("Password", type="password")
            submit_btn = st.form_submit_button("Sign In", use_container_width=True)

            if submit_btn:
                if login_user(db, user_input, pass_input):
                    st.success("Authentication successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

        with st.expander("Default Test Credentials"):
            st.markdown("""
            * **Lead Architect**: `arch_lead` / `arch123`
            * **Structural Engineer**: `struct_eng` / `struct123`
            * **Electrical Engineer**: `elec_eng` / `elec123`
            * **Master Plumber**: `plumber_lead` / `plum123`
            * **System Admin**: `admin` / `admin123`
            """)
else:
    require_auth()

    # -------- SIDEBAR WITH LOGO + NAVIGATION --------
    with st.sidebar:
        st.markdown(get_logo_html(width=70), unsafe_allow_html=True)
        st.markdown("---")
        app_mode = st.radio(
            "Navigation",
            [
                "Project Directory",
                "Drawing Repository",
                "Sign-Off & Approvals",
                "Bill of Quantities (BOQ)",
                "RFI & Technical Queries",
                "Daily Site Logs",
            ],
            label_visibility="collapsed",
        )

    # -------- MAIN CONTENT --------
    if app_mode == "Project Directory":
        render_projects_module(db)
    elif app_mode == "Drawing Repository":
        render_drawings_module(db)
    elif app_mode == "Sign-Off & Approvals":
        render_approvals_module(db)
    elif app_mode == "Bill of Quantities (BOQ)":
        render_boq_module(db)
    elif app_mode == "RFI & Technical Queries":
        render_rfi_module(db)
    elif app_mode == "Daily Site Logs":
        render_site_logs_module(db)