import streamlit as st
from utils import load_memory, save_memory, require_auth, hash_password, safe_dataframe

st.set_page_config(page_title="User Management", page_icon="👤", layout="wide")
require_auth()

db = load_memory()
current_user = st.session_state["user"]

st.title("👤 User Management")

if current_user["role"] != "Admin":
    st.error("🔒 Only Administrators can access User Management.")
else:
    tab1, tab2 = st.tabs(["Active Users Directory", "Provision New Account"])

    with tab1:
        df_users = safe_dataframe(db.get("users", []), ["username", "name", "role"])
        st.dataframe(df_users, use_container_width=True)

    with tab2:
        with st.form("new_user_form"):
            u_name = st.text_input("Full Name")
            u_username = st.text_input("Username")
            u_pass = st.text_input("Password", type="password")
            u_role = st.selectbox("Role", ["Architect", "Structural Engineer", "MEP Engineer", "Procurement Officer", "Admin"])

            if st.form_submit_button("Create User Account") and u_username and u_pass:
                if any(u["username"].lower() == u_username.lower() for u in db["users"]):
                    st.error("Username already exists.")
                else:
                    db["users"].append({
                        "username": u_username,
                        "password_hash": hash_password(u_pass),
                        "name": u_name,
                        "role": u_role
                    })
                    save_memory(db)
                    st.success(f"User account '{u_username}' created successfully!")
                    st.rerun()
