"""
Creative Studios shared branding utilities.

Single canonical branding asset:
    assets/creative_studios.png

All Streamlit branding uses the native st.image() renderer.
"""

from __future__ import annotations

import html
from pathlib import Path

import streamlit as st


# ============================================================
# BRAND ASSET
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

LOGO_PATH = (
    BASE_DIR
    / "assets"
    / "creative_studios.png"
)


def logo_exists() -> bool:
    """Return True when the Creative Studios logo exists."""

    return (
        LOGO_PATH.exists()
        and LOGO_PATH.is_file()
    )


def render_logo(
    width: int = 52,
) -> None:
    """
    Render the canonical Creative Studios PNG
    using Streamlit's native image renderer.
    """

    if not logo_exists():
        return

    st.image(
        str(LOGO_PATH),
        width=width,
    )


def render_module_header(
    title: str,
    subtitle: str = "",
    logo_width: int = 52,
) -> None:
    """
    Render the standardized Creative Studios
    module header.

    The logo is rendered natively with st.image().
    """

    safe_title = html.escape(
        str(title or "Creative Studios")
    )

    safe_subtitle = html.escape(
        str(subtitle or "")
    )

    logo_col, content_col = st.columns(
        [0.08, 0.92],
        vertical_alignment="center",
    )

    with logo_col:

        render_logo(
            width=logo_width,
        )

    with content_col:

        st.markdown(
            f"""
            <div style="
                padding-top:2px;
            ">

                <div style="
                    color:#FFFFFF;
                    font-size:30px;
                    font-weight:900;
                    letter-spacing:-0.7px;
                    line-height:1.15;
                ">
                    {safe_title}
                </div>

                <div style="
                    color:#64748B;
                    font-size:13px;
                    margin-top:5px;
                    margin-bottom:25px;
                ">
                    {safe_subtitle}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


def branding_status() -> dict[str, object]:
    """
    Return branding diagnostics for debugging.
    """

    return {
        "logo_path": str(LOGO_PATH),
        "logo_exists": logo_exists(),
        "logo_is_file": LOGO_PATH.is_file(),
    }