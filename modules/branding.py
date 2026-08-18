"""
Creative Studios
Shared branding and UI helpers.

Single source of truth for:
- Creative Studios logo
- Branding CSS
- Module headers
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
# LOGO
# ============================================================

def render_logo(
    width: int = 76,
) -> None:
    """
    Render the Creative Studios logo using native Streamlit
    image rendering.

    The logo is intentionally not wrapped in an HTML image
    element.
    """

    if not LOGO_PATH.exists():

        st.warning(
            f"Creative Studios logo not found: {LOGO_PATH}"
        )

        return

    try:

        safe_width = int(width)

    except (
        TypeError,
        ValueError,
    ):

        safe_width = 76

    safe_width = max(
        20,
        min(
            safe_width,
            500,
        ),
    )

    st.image(
        str(LOGO_PATH),
        width=safe_width,
    )


# ============================================================
# SHARED BRANDING CSS
# ============================================================

def inject_branding_css() -> None:
    """
    Inject all shared Creative Studios branding styles.

    This is the single CSS source of truth used by
    streamlit_app.py and the individual modules.
    """

    st.markdown(
        """
        <style>

        /* ==================================================
           GLOBAL APPLICATION
           ================================================== */

        [data-testid="stAppViewContainer"] {
            background: #05070B;
            color: #F8FAFC;
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stSidebar"] {
            background: #080B12;
            border-right: 1px solid #172033;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }


        /* ==================================================
           SIDEBAR
           ================================================== */

        .cs-sidebar-name {
            color: #FFFFFF;
            font-size: 15px;
            font-weight: 850;
            line-height: 1.15;
        }

        .cs-sidebar-subtitle {
            color: #64748B;
            font-size: 9px;
            margin-top: 4px;
            text-transform: uppercase;
            letter-spacing: 0.7px;
        }

        .cs-sidebar-divider {
            width: 100%;
            height: 1px;
            background: #172033;
            margin-top: 14px;
            margin-bottom: 14px;
        }

        .cs-section-label {
            color: #64748B;
            font-size: 9px;
            font-weight: 800;
            letter-spacing: 1px;
            text-transform: uppercase;
            margin-top: 12px;
            margin-bottom: 8px;
        }


        /* ==================================================
           ACTIVE NAVIGATION
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
           PAGE / MODULE HEADER
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

            line-height: 1.5;
        }


        /* ==================================================
           REUSABLE CARDS
           ================================================== */

        .cs-card {
            background: #0B0F17;

            border: 1px solid #172033;

            border-radius: 15px;

            padding: 20px;

            box-sizing: border-box;
        }

        .cs-card-title {
            color: #FFFFFF;

            font-size: 18px;
            font-weight: 850;

            line-height: 1.25;
        }

        .cs-card-subtitle {
            color: #64748B;

            font-size: 12px;

            margin-top: 7px;

            line-height: 1.5;
        }

        .cs-card-label {
            color: #64748B;

            font-size: 10px;
            font-weight: 800;

            letter-spacing: 0.8px;
            text-transform: uppercase;

            margin-bottom: 7px;
        }


        /* ==================================================
           KPI CARDS
           ================================================== */

        .cs-kpi {
            background: #0B0F17;

            border: 1px solid #172033;

            border-radius: 15px;

            padding: 18px;

            min-height: 110px;

            box-sizing: border-box;

            width: 100%;
        }

        .cs-kpi-label {
            color: #64748B;

            font-size: 11px;

            text-transform: uppercase;

            letter-spacing: 0.8px;

            line-height: 1.25;
        }

        .cs-kpi-value {
            color: #FFFFFF;

            font-size: 24px;
            font-weight: 900;

            margin-top: 7px;

            overflow-wrap: anywhere;

            line-height: 1.15;
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

            overflow-wrap: anywhere;
        }

        .user-login {
            color: #64748B;

            font-size: 10px;

            margin-top: 3px;

            overflow-wrap: anywhere;
        }

        .user-role {
            display: inline-block;

            margin-top: 8px;

            padding: 4px 9px;

            background: #2563EB;

            color: #FFFFFF;

            border-radius: 999px;

            font-size: 9px;
            font-weight: 850;
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

            color: #FCA5A5;

            font-size: 12px;
        }


        /* ==================================================
           SETTINGS
           ================================================== */

        .cs-setting-row {
            color: #94A3B8;

            font-size: 13px;

            margin-top: 12px;
        }

        .cs-setting-row strong {
            color: #FFFFFF;

            margin-left: 5px;
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


        /* ==================================================
           LIGHT MODE SUPPORT
           ================================================== */

        @media (prefers-color-scheme: light) {

            [data-testid="stAppViewContainer"] {
                background: #F8FAFC;
                color: #0F172A;
            }

            [data-testid="stSidebar"] {
                background: #FFFFFF;
                border-right-color: #E2E8F0;
            }

            .cs-page-title,
            .cs-card-title,
            .cs-kpi-value,
            .user-name {
                color: #0F172A;
            }

            .cs-page-subtitle,
            .cs-card-subtitle,
            .cs-kpi-label,
            .user-login {
                color: #64748B;
            }

            .cs-card,
            .cs-kpi,
            .cs-user-card,
            .cs-login-card {
                background: #FFFFFF;
                border-color: #E2E8F0;
            }

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
    subtitle: str = "",
) -> None:
    """
    Render the shared Creative Studios module header.

    All module titles and subtitles are HTML escaped.
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