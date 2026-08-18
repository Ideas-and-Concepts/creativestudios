"""
Creative Studios shared branding utilities.
"""

from __future__ import annotations

import html
from pathlib import Path

import streamlit as st


BASE_DIR = Path(__file__).resolve().parent.parent

LOGO_PATH = (
    BASE_DIR
    / "assets"
    / "Artboard 1.png"
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
    """Render the Creative Studios logo."""

    if logo_exists():

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
    Render one standardized Creative Studios module header.
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

        if logo_exists():

            st.image(
                str(LOGO_PATH),
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