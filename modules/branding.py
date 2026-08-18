"""
Creative Studios
Shared Branding Module
"""

from __future__ import annotations

import html
from pathlib import Path

import streamlit as st


BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
LOGO_PATH = ASSETS_DIR / "creative_studios.png"


def render_logo(width: int = 76) -> None:
    try:
        logo_width = int(width)
    except (TypeError, ValueError):
        logo_width = 76
    logo_width = max(20, min(logo_width, 500))

    if not LOGO_PATH.exists():
        st.warning(f"Creative Studios logo not found: {LOGO_PATH}")
        return

    st.image(str(LOGO_PATH), width=logo_width)


def inject_branding_css() -> None:
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
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        /* ==================================================
           SIDEBAR
           ================================================== */
        [data-testid="stSidebar"] {
            background: #080B12;
            border-right: 1px solid #172033;
        }
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
            line-height: 1.5;
        }

        /* ==================================================
           GENERIC CARD
           ================================================== */
        .cs-card {
            background: #0B0F17;
            border: 1px solid #172033;
            border-radius: 15px;
            padding: 20px;
            box-sizing: border-box;
            width: 100%;
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
            line-height: 1.15;
            overflow-wrap: anywhere;
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
            box-sizing: border-box;
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
            box-sizing: border-box;
            box-shadow: 0 20px 70px rgba(0, 0, 0, 0.55), 0 0 40px rgba(37, 99, 235, 0.06);
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
           PROJECT CARD
           ================================================== */
        .cs-project-card {
            background: #0B0F17;
            border: 1px solid #172033;
            border-radius: 15px;
            padding: 18px;
            margin-bottom: 15px;
            box-sizing: border-box;
        }
        .cs-project-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 10px;
        }
        .cs-project-name {
            color: #FFFFFF;
            font-size: 17px;
            font-weight: 850;
            line-height: 1.3;
        }
        .cs-project-meta {
            color: #64748B;
            font-size: 12px;
            margin-top: 6px;
            line-height: 1.5;
        }
        .cs-status {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 999px;
            font-size: 11px;
            font-weight: 800;
            white-space: nowrap;
        }
        .cs-status-active {
            background: rgba(34, 197, 94, 0.15);
            color: #4ADE80;
            border: 1px solid rgba(34, 197, 94, 0.35);
        }
        .cs-status-default {
            background: rgba(100, 116, 139, 0.15);
            color: #94A3B8;
            border: 1px solid rgba(100, 116, 139, 0.35);
        }

        /* ==================================================
           STREAMLIT BUTTONS
           ================================================== */
        [data-testid="stSidebar"] button {
            border-radius: 9px;
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


def render_module_header(title: str, subtitle: str = "") -> None:
    safe_title = html.escape(str(title or ""))
    safe_subtitle = html.escape(str(subtitle or ""))
    st.markdown(
        f"""
        <div class="cs-page-title">{safe_title}</div>
        <div class="cs-page-subtitle">{safe_subtitle}</div>
        """,
        unsafe_allow_html=True,
    )


__all__ = [
    "BASE_DIR",
    "ASSETS_DIR",
    "LOGO_PATH",
    "inject_branding_css",
    "render_logo",
    "render_module_header",
]