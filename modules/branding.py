import streamlit as st
from typing import Any
from modules.database import save_memory

# ============================================================
# BRANDING MODULE
# ============================================================

def render_branding_module(database: dict[str, Any]) -> None:
    """Render Branding module for managing logos, colors, and fonts."""

    st.header("Branding")

    projects = database.get("projects", [])
    if not projects:
        st.info("No projects available.")
        return

    # Select project
    project_names = [p.get("name", "Unnamed Project") for p in projects]
    selected_project = st.selectbox("Select Project", project_names)

    project = next((p for p in projects if p.get("name") == selected_project), None)
    if not project:
        st.warning("Project not found.")
        return

    branding = project.get("branding", {})

    # Display current branding
    st.subheader("Current Branding")
    st.write(branding if branding else "No branding set yet.")

    # Update branding form
    with st.form("update_branding", clear_on_submit=True):
        logo_url = st.text_input("Logo URL", branding.get("logo_url", ""))
        primary_color = st.color_picker("Primary Color", branding.get("primary_color", "#000000"))
        secondary_color = st.color_picker("Secondary Color", branding.get("secondary_color", "#FFFFFF"))
        font_family = st.text_input("Font Family", branding.get("font_family", "Arial"))
        submitted = st.form_submit_button("Save Branding")

        if submitted:
            branding.update({
                "logo_url": logo_url,
                "primary_color": primary_color,
                "secondary_color": secondary_color,
                "font_family": font_family
            })
            project["branding"] = branding
            save_memory(database)
            st.success("Branding updated successfully!")

    # Preview branding
    if branding:
        st.subheader("Preview")
        st.markdown(
            f"""
            <div style="background-color:{branding['primary_color']}; color:{branding['secondary_color']}; font-family:{branding['font_family']}; padding:10px;">
                <h3>Project Branding Preview</h3>
                <p>This is how your branding looks in the app.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if branding.get("logo_url"):
            st.image(branding["logo_url"], caption="Project Logo")