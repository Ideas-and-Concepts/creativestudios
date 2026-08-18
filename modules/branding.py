"""
Creative Studios
Shared application branding.

Canonical branding asset
------------------------
assets/creative_studios.png

This module provides:
- Shared Creative Studios logo path
- Native Streamlit logo rendering
- Shared module headers
- Safe logo existence checking

All application modules should import branding
from this module instead of defining their own
logo implementation.
"""

from __future__ import annotations

import html
from pathlib import Path

import streamlit as st


# ============================================================
# PATHS
# ============================================================

# modules/branding.py
MODULES_DIR = Path(__file__).resolve().parent

# Project root
BASE_DIR = MODULES_DIR.parent

# Canonical assets directory
ASSETS_DIR = BASE_DIR / "assets"

# Single Creative Studios branding asset
LOGO_PATH = ASSETS_DIR / "creative_studios.png"


# ============================================================
# LOGO HELPERS
# ============================================================

def logo_exists() -> bool:
    """
    Return True when the canonical Creative Studios
    PNG logo exists and is a regular file.
    """

    return (
        LOGO_PATH.exists()
        and LOGO_PATH.is_file()
    )


def render_logo(
    width: int = 100,
) -> None:
    """
    Render the Creative Studios logo using native
    Streamlit image rendering.

    Parameters
    ----------
    width:
        Display width of the logo in pixels.

    Notes
    -----
    The function intentionally uses st.image()
    rather than:
    - SVG
    - base64
    - HTML <img>
    - emoji
    - external URLs
    """

    if not logo_exists():

        st.warning(
            "Creative Studios logo not found at "
            "assets/creative_studios.png"
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
    subtitle: str = "",
) -> None:
    """
    Render the standard Creative Studios module header.

    The canonical Creative Studios logo is displayed
    above the module title.

    Existing modules can continue using:

        from modules.branding import render_module_header

        render_module_header(
            "Projects",
            "Manage project records."
        )
    """

    safe_title = html.escape(
        str(title or "")
    )

    safe_subtitle = html.escape(
        str(subtitle or "")
    )

    # --------------------------------------------------------
    # Header container
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="cs-module-header">
            <div class="cs-module-header-logo">
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Native Streamlit logo
    # --------------------------------------------------------

    if logo_exists():

        st.image(
            str(LOGO_PATH),
            width=54,
        )

    else:

        st.markdown(
            """
            <div class="cs-branding-warning">
                Creative Studios logo not found.
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # Header text
    # --------------------------------------------------------

    st.markdown(
        f"""
            </div>

            <div class="cs-module-header-content">

                <div class="cs-page-title">
                    {safe_title}
                </div>

                <div class="cs-page-subtitle">
                    {safe_subtitle}
                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# BRANDING CSS
# ============================================================

def inject_branding_css() -> None:
    """
    Inject CSS required by the shared branding components.

    This is optional. streamlit_app.py may call it if it
    wants branding-specific CSS separated from global CSS.
    """

    st.markdown(
        """
        <style>

        /* ==================================================
           CREATIVE STUDIOS MODULE HEADER
           ================================================== */

        .cs-module-header {

            display: flex;

            align-items: center;

            gap: 16px;

            margin-bottom: 25px;

            padding-bottom: 14px;

            border-bottom:
                1px solid #172033;
        }

        .cs-module-header-logo {

            width: 54px;

            min-width: 54px;

            height: 54px;

            min-height: 54px;

            display: flex;

            align-items: center;

            justify-content: center;

            flex-shrink: 0;
        }

        .cs-module-header-logo
        [data-testid="stImage"] {

            margin: 0 !important;

            padding: 0 !important;
        }

        .cs-module-header-logo img {

            width: 54px !important;

            height: 54px !important;

            max-width: 54px !important;

            max-height: 54px !important;

            object-fit: contain;
        }

        .cs-module-header-content {

            min-width: 0;

            flex: 1;
        }


        /* ==================================================
           PAGE TITLE
           ================================================== */

        .cs-page-title {

            color: #FFFFFF;

            font-size: 30px;

            font-weight: 900;

            letter-spacing: -0.7px;

            line-height: 1.15;
        }


        /* ==================================================
           PAGE SUBTITLE
           ================================================== */

        .cs-page-subtitle {

            color: #64748B;

            font-size: 13px;

            margin-top: 5px;
        }


        /* ==================================================
           BRANDING WARNING
           ================================================== */

        .cs-branding-warning {

            color: #FCA5A5;

            background:
                rgba(127, 29, 29, 0.20);

            border:
                1px solid
                rgba(248, 113, 113, 0.25);

            border-radius: 8px;

            padding: 7px;

            font-size: 9px;

            text-align: center;

            width: 54px;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# BACKWARD-COMPATIBLE ALIASES
# ============================================================

# Some application code may refer to the asset using
# BRAND_LOGO_PATH. Keep this alias so existing code does
# not break if it already imports it.

BRAND_LOGO_PATH = LOGO_PATH


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "BASE_DIR",
    "ASSETS_DIR",
    "LOGO_PATH",
    "BRAND_LOGO_PATH",
    "logo_exists",
    "render_logo",
    "render_module_header",
    "inject_branding_css",
]