import streamlit as st
from modules.audit_log import render_audit_log_module
from modules.database import load_memory
st.set_page_config(page_title="Audit Trail · Creative Studios", layout="wide")
render_audit_log_module(load_memory())
