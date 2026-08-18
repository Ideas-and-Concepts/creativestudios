"""
Creative Studios
Central branding utilities.

Single source of truth for:
- Creative Studios logo
- Branding CSS
- Module headers
"""

from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

LOGO_PATH = (
    BASE_DIR
    / "assets"
    / "creative_studios.png"
)


# ============================================================
# LOGO
# ============================================================

def logo_exists() -> bool:
    """Return True when the Creative Studios logo exists."""

    return (
        LOGO_PATH.exists()
        and LOGO_PATH.is_file()
    )


def _logo_data_uri() -> str | None:
    """
    Return the logo as a base64 data URI.

    This allows the logo to be used safely inside HTML
    without depending on Streamlit static-file serving.
    """

    if not logo_exists():
        return None

    try:

        encoded = base64.b64encode(
            LOGO_PATH.read_bytes()
        ).decode("ascii")

        return (
            "data:image/png;base64,"
            + encoded
        )

    except OSError:

        return None


# ============================================================
# NATIVE STREAMLIT LOGO
# ============================================================

def render_logo(
    width: int = 80,
) -> None:
    """
    Render the Creative Studios logo using Streamlit's
    native image renderer.
    """

    if not logo_exists():

        st.warning(
            "Creative Studios logo was not found: "
            f"{LOGO_PATH}"
        )

        return

    st.image(
        str(LOGO_PATH),
        width=width,
    )


# ============================================================
# BRANDING CSS
# ============================================================

def inject_branding_css() -> None:
    """
    Inject all Creative Studios branding CSS.

    This function is the single source of truth for
    application branding.
    """

    st.markdown(
        """
<style>

/* ==========================================================
   GLOBAL
   ========================================================== */

html,
body,
[data-testid="stAppViewContainer"] {
    background: #05070B !important;
    color: #F8FAFC !important;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(
            circle at top right,
            rgba(37,99,235,0.10),
            transparent 35%
        ),
        #05070B !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

[data-testid="stToolbar"] {
    background: transparent !important;
}

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
}

h1,
h2,
h3,
h4,
h5,
h6 {
    color: #F8FAFC !important;
}

p,
label,
span {
    color: #CBD5E1;
}


/* ==========================================================
   SIDEBAR
   ========================================================== */

[data-testid="stSidebar"] {
    background: #080B12 !important;
    border-right: 1px solid #172033 !important;
}

[data-testid="stSidebar"] > div:first-child {
    background: #080B12 !important;
}


/* ==========================================================
   LOGIN
   ========================================================== */

.cs-login-wrapper {
    width: min(430px, 92vw);
    margin: 7vh auto 0 auto;
}

.cs-login-card {
    background: #0B0F17;
    border: 1px solid #1E293B;
    border-radius: 20px;
    padding: 30px;
    box-shadow:
        0 20px 70px rgba(0,0,0,0.55),
        0 0 40px rgba(37,99,235,0.06);
}

.cs-login-logo {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    margin: 0 auto 22px auto;
}

.cs-login-logo img {
    display: block;
    object-fit: contain;
}


/* ==========================================================
   LOGIN FOOTER
   ========================================================== */

.cs-login-footer {
    text-align: center;
    margin-top: 18px;
    color: #475569;
    font-size: 11px;
}


/* ==========================================================
   SIDEBAR BRAND
   ========================================================== */

.cs-sidebar-brand {
    width: 100%;
    padding: 6px 2px 18px 2px;
    margin-bottom: 14px;
    border-bottom: 1px solid #172033;
}

.cs-sidebar-brand-row {
    width: 100%;
    display: flex;
    align-items: center;
    gap: 11px;
    min-height: 48px;
}

.cs-sidebar-logo-wrap {
    width: 46px;
    height: 46px;
    min-width: 46px;
    max-width: 46px;
    min-height: 46px;
    max-height: 46px;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    flex-shrink: 0;
}

.cs-sidebar-logo-wrap img {
    width: 46px !important;
    height: 46px !important;
    object-fit: contain;
}

.cs-sidebar-brand-text {
    min-width: 0;
    overflow: hidden;
}

.cs-sidebar-name {
    color: #FFFFFF;
    font-size: 15px;
    font-weight: 850;
    line-height: 1.15;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.cs-sidebar-subtitle {
    color: #64748B;
    font-size: 9px;
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: 0.7px;
}


/* ==========================================================
   SECTION LABEL
   ========================================================== */

.cs-section-label {
    color: #475569;
    font-size: 10px;
    font-weight: 850;
    letter-spacing: 1.3px;
    text-transform: uppercase;
    margin-top: 17px;
    margin-bottom: 7px;
}


/* ==========================================================
   USER CARD
   ========================================================== */

.cs-user-card {
    background: #0B0F17;
    border: 1px solid #172033;
    border-radius: 13px;
    padding: 13px;
    margin-top: 15px;
}

.user-label {
    color: #60A5FA;
    font-size: 9px;
    font-weight: 850;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.user-name {
    color: #FFFFFF;
    font-size: 14px;
    font-weight: 800;
    margin-top: 5px;
}

.user-login {
    color: #64748B;
    font-size: 10px;
    margin-top: 3px;
}

.user-role {
    display: inline-block;
    margin-top: 8px;
    padding: 4px 9px;
    background: #2563EB;
    color: #FFFFFF !important;
    border-radius: 999px;
    font-size: 9px;
    font-weight: 850;
}


/* ==========================================================
   MODULE HEADER
   ========================================================== */

.cs-page-title {
    color: #FFFFFF;
    font-size: 30px;
    font-weight: 900;
    letter-spacing: -0.7px;
    line-height: 1.15;
}

.cs-page-subtitle {
    color: #64748B;
    font-size: 13px;
    margin-top: 5px;
    margin-bottom: 25px;
}


/* ==========================================================
   CARDS
   ========================================================== */

.cs-card {
    background: #0B0F17;
    border: 1px solid #172033;
    border-radius: 15px;
    padding: 20px;
}

.cs-card-title {
    color: #FFFFFF;
    font-size: 18px;
    font-weight: 850;
}

.cs-card-subtitle {
    color: #64748B;
    font-size: 12px;
    margin-top: 7px;
}


/* ==========================================================
   KPI
   ========================================================== */

.cs-kpi {
    background: #0B0F17;
    border: 1px solid #172033;
    border-radius: 15px;
    padding: 18px;
    min-height: 110px;
}

.cs-kpi-label {
    color: #64748B;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

.cs-kpi-value {
    color: #FFFFFF;
    font-size: 24px;
    font-weight: 900;
    margin-top: 7px;
    overflow-wrap: anywhere;
}


/* ==========================================================
   BUTTONS
   ========================================================== */

div[data-testid="stButton"] > button {
    background: #111827 !important;
    color: #E2E8F0 !important;
    border: 1px solid #1E293B !important;
    border-radius: 9px !important;
}

div[data-testid="stButton"] > button:hover {
    background: #172554 !important;
    border-color: #2563EB !important;
    color: #FFFFFF !important;
}

div[data-testid="stFormSubmitButton"] > button {
    background: #2563EB !important;
    color: #FFFFFF !important;
    border: 0 !important;
    border-radius: 10px !important;
    font-weight: 800 !important;
}

div[data-testid="stFormSubmitButton"] > button:hover {
    background: #1D4ED8 !important;
}


/* ==========================================================
   INPUTS
   ========================================================== */

input,
textarea,
[data-baseweb="select"] > div {
    background: #0B0F17 !important;
    color: #FFFFFF !important;
    border-color: #1E293B !important;
}


/* ==========================================================
   LOGIN ERROR
   ========================================================== */

.cs-login-error {
    background: rgba(127,29,29,0.20);
    border: 1px solid rgba(248,113,113,0.30);
    border-radius: 9px;
    padding: 9px 12px;
    margin-top: 10px;
    color: #FCA5A5 !important;
    font-size: 12px;
}


/* ==========================================================
   ACTIVE NAVIGATION INDICATOR
   ========================================================== */

[data-testid="stSidebar"] div[data-testid="stButton"] button {
    text-align: left !important;
}

</style>
""",
        unsafe_allow_html=True,
    )


# ============================================================
# MODULE HEADER
# ============================================================

def render_module_header(
    title: str,
    subtitle: str,
) -> None:
    """
    Render the standard Creative Studios module header.
    """

    st.markdown(
        f"""
        <div class="cs-page-title">
            {title}
        </div>

        <div class="cs-page-subtitle">
            {subtitle}
        </div>
        """,
        unsafe_allow_html=True,
    )