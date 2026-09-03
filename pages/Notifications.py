import streamlit as st
from modules.database import load_memory
from modules.notifications import render_notifications_module
st.set_page_config(page_title="Notifications · Creative Studios", layout="wide")
render_notifications_module(load_memory())
