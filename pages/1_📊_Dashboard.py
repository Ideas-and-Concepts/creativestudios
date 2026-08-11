import pandas as pd
import streamlit as st
from utils import load_memory, require_auth, safe_dataframe

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
require_auth()

db = load_memory()

st.title("📊 Executive Dashboard")

col1, col2, col3, col4 = st.columns(4)
total_budget = sum(p.get("budget", 0) for p in db.get("projects", []))
pending_approvals = sum(
    1 for a in db.get("procurement_approvals", []) 
    if a.get("procurement_status") != "Ready for Release"
)

col1.metric("Total Projects", len(db.get("projects", [])))
col2.metric("Vault Documents", len(db.get("drawings", [])))
col3.metric("Pending Approvals", pending_approvals)
col4.metric("Portfolio Budget", f"${total_budget:,.2f}")

st.markdown("---")
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Drawings by Discipline")
    if db.get("drawings"):
        df_d = pd.DataFrame(db["drawings"])
        if "discipline" in df_d.columns:
            counts = df_d["discipline"].value_counts().reset_index()
            counts.columns = ["Discipline", "Count"]
            st.dataframe(counts, use_container_width=True)
    else:
        st.info("No drawings registered.")

with col_b:
    st.subheader("Recent Vault Submissions")
    if db.get("drawings"):
        df_recent = safe_dataframe(db["drawings"], ["discipline", "title", "version", "status", "uploaded_at"])
        st.dataframe(df_recent.tail(5), use_container_width=True)
    else:
        st.info("No drawings uploaded yet.")
