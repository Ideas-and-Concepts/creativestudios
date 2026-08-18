from pathlib import Path

import streamlit as st


BASE_DIR = Path(__file__).resolve().parent.parent

LOGO_PATH = (
    BASE_DIR
    / "assets"
    / "creative_studios_logo.png"
)


def logo_exists() -> bool:
    return (
        LOGO_PATH.exists()
        and LOGO_PATH.is_file()
    )


def render_login_branding() -> None:

    st.markdown(
        '<div class="cs-login-brand">',
        unsafe_allow_html=True,
    )

    if logo_exists():

        st.image(
            str(LOGO_PATH),
            width=76,
        )

    else:

        st.markdown(
            """
            <div class="cs-logo-fallback">
                CS
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="cs-brand-name">
            Creative Studios
        </div>

        <div class="cs-brand-subtitle">
            AEC Workspace
        </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_branding() -> None:

    st.sidebar.markdown(
        '<div class="cs-sidebar-brand">',
        unsafe_allow_html=True,
    )

    if logo_exists():

        st.sidebar.image(
            str(LOGO_PATH),
            width=46,
        )

    else:

        st.sidebar.markdown(
            """
            <div class="cs-sidebar-logo-fallback">
                CS
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.sidebar.markdown(
        """
        <div class="cs-sidebar-brand-text">

            <div class="cs-sidebar-name">
                Creative Studios
            </div>

            <div class="cs-sidebar-subtitle">
                AEC Workspace
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


def render_module_header(
    title: str,
    subtitle: str,
) -> None:

    col_logo, col_text = st.columns(
        [0.08, 0.92],
        vertical_alignment="center",
    )

    with col_logo:

        if logo_exists():

            st.image(
                str(LOGO_PATH),
                width=46,
            )

        else:

            st.markdown(
                """
                <div class="module-logo-fallback">
                    CS
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col_text:

        st.markdown(
            f"""
            <div class="cs-module-title">
                {title}
            </div>

            <div class="cs-module-subtitle">
                {subtitle}
            </div>
            """,
            unsafe_allow_html=True,
        )