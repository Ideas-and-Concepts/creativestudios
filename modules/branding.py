"""
Creative Studios
Shared branding utilities.

Single source of truth for:
- Creative Studios logo
- Branding CSS
- Logo rendering
- Module headers
- Shared cards
- KPI cards
"""

from __future__ import annotations

import html
from pathlib import Path

import streamlit as st


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

ASSETS_DIR = BASE_DIR / "assets"

LOGO_PATH = ASSETS_DIR / "creative_studios.png"


# ============================================================
# BRAND CONSTANTS
# ============================================================

BRAND_NAME = "Creative Studios"

BRAND_SUBTITLE = "AEC Workspace"


# ============================================================
# LOGO VALIDATION
# ============================================================

def logo_exists() -> bool:
    """
    Return True when the Creative Studios logo exists.
    """

    return (
        LOGO_PATH.exists()
        and LOGO_PATH.is_file()
    )


# ============================================================
# SHARED BRANDING CSS
# ============================================================

def inject_branding_css() -> None:
    """
    Inject all shared Creative Studios branding CSS.

    This is the single source of truth for branding styles.
    """

    st.markdown(
        """
        <style>

        /* ==================================================
           GLOBAL
           ================================================== */

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
                    rgba(37, 99, 235, 0.10),
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


        /* ==================================================
           TYPOGRAPHY
           ================================================== */

        h1,
        h2,
        h3,
        h4,
        h5,
        h6 {
            color: #F8FAFC !important;
        }

        p,
        label {
            color: #CBD5E1;
        }


        /* ==================================================
           SIDEBAR
           ================================================== */

        [data-testid="stSidebar"] {
            background: #080B12 !important;
            border-right: 1px solid #172033 !important;
        }

        [data-testid="stSidebar"] > div:first-child {
            background: #080B12 !important;
        }


        /* ==================================================
           SIDEBAR BRAND
           ================================================== */

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
            white-space: nowrap;
        }

        .cs-sidebar-divider {
            width: 100%;
            height: 1px;
            background: #172033;
            margin-top: 14px;
            margin-bottom: 14px;
        }


        /* ==================================================
           LOGIN
           ================================================== */

        .cs-login-wrapper {
            width: min(430px, 92vw);
            margin: 7vh auto 0 auto;
        }

        .cs-login-card {
            background: #0B0F17;
            border: 1px solid #1E293B;
            border-radius: 20px;
            padding: 36px;
            box-shadow:
                0 20px 70px rgba(0, 0, 0, 0.55),
                0 0 40px rgba(37, 99, 235, 0.06);
        }

        .cs-login-logo {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 24px;
        }

        .cs-login-spacing {
            height: 2px;
        }

        .cs-login-footer {
            text-align: center;
            margin-top: 18px;
            color: #475569;
            font-size: 11px;
        }

        .cs-login-error {
            background: rgba(127, 29, 29, 0.20);
            border: 1px solid rgba(248, 113, 113, 0.30);
            border-radius: 9px;
            padding: 9px 12px;
            margin-top: 10px;
            color: #FCA5A5 !important;
            font-size: 12px;
        }


        /* ==================================================
           SECTION LABEL
           ================================================== */

        .cs-section-label {
            color: #475569;
            font-size: 10px;
            font-weight: 850;
            letter-spacing: 1.3px;
            text-transform: uppercase;
            margin-top: 17px;
            margin-bottom: 7px;
        }


        /* ==================================================
           ACTIVE SIDEBAR MODULE
           ================================================== */

        .cs-active-module {
            width: 100%;
            box-sizing: border-box;

            background: #172554;
            border: 1px solid #2563EB;
            border-radius: 9px;

            color: #FFFFFF;

            padding: 0.45rem 0.75rem;

            font-size: 14px;
            font-weight: 700;

            margin-bottom: 0.25rem;
        }

        .cs-active-indicator {
            color: #60A5FA;
            margin-right: 7px;
            font-size: 10px;
        }


        /* ==================================================
           USER CARD
           ================================================== */

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


        /* ==================================================
           MODULE HEADER
           ================================================== */

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


        /* ==================================================
           CARDS
           ================================================== */

        .cs-card {
            background: #0B0F17;
            border: 1px solid #172033;
            border-radius: 15px;
            padding: 20px;
        }

        .cs-card-label {
            color: #60A5FA;
            font-size: 11px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .cs-card-title {
            color: #FFFFFF;
            font-size: 18px;
            font-weight: 850;
            margin-top: 2px;
        }

        .cs-card-subtitle {
            color: #64748B;
            font-size: 12px;
            margin-top: 7px;
            line-height: 1.5;
        }


        /* ==================================================
           KPI
           ================================================== */

        .cs-kpi {
            background: #0B0F17;
            border: 1px solid #172033;
            border-radius: 15px;

            padding: 18px;
            min-height: 110px;

            box-sizing: border-box;
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


        /* ==================================================
           SETTINGS
           ================================================== */

        .cs-setting-row {
            color: #94A3B8;
            margin-top: 9px;
            font-size: 13px;
        }

        .cs-setting-row strong {
            color: #FFFFFF;
        }


        /* ==================================================
           BUTTONS
           ================================================== */

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


        /* ==================================================
           INPUTS
           ================================================== */

        input,
        textarea,
        [data-baseweb="select"] > div {
            background: #0B0F17 !important;
            color: #FFFFFF !important;
            border-color: #1E293B !important;
        }


        /* ==================================================
           RESPONSIVE
           ================================================== */

        @media (max-width: 900px) {

            .cs-page-title {
                font-size: 26px;
            }

            .cs-kpi {
                min-height: 95px;
                padding: 14px;
            }

            .cs-kpi-value {
                font-size: 20px;
            }
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# LOGO
# ============================================================

def render_logo(
    width: int = 76,
) -> None:
    """
    Render the Creative Studios logo using native Streamlit.

    No HTML image wrapper.
    No base64.
    No SVG recreation.
    No emoji dependency.
    """

    if not logo_exists():

        st.warning(
            "Creative Studios logo not found: "
            f"{LOGO_PATH}"
        )

        return

    st.image(
        str(LOGO_PATH),
        width=width,
    )


# ============================================================
# MODULE HEADER
# ============================================================

def render_module_header(
    title: str,
    subtitle: str,
) -> None:
    """
    Shared module header used by all modules.
    """

    safe_title = html.escape(
        str(title or "")
    )

    safe_subtitle = html.escape(
        str(subtitle or "")
    )

    st.markdown(
        f"""
        <div class="cs-page-title">
            {safe_title}
        </div>

        <div class="cs-page-subtitle">
            {safe_subtitle}
        </div>
        """,
        unsafe_allow_html=True,
    )