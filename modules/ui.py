"""
Creative Studios
AEC Collaboration Platform

Shared UI Helpers
-----------------
SVG logos, module icons, branding and common visual components.

This module does NOT depend on Streamlit session state
and does not load the database.
"""

from __future__ import annotations

from html import escape


# ============================================================
# SVG ICONS
# ============================================================

SVG_ICONS = {
    "home": """
        <path d="M3 10.5 12 3l9 7.5"/>
        <path d="M5.5 9.5V21h13V9.5"/>
        <path d="M9.5 21v-6h5v6"/>
    """,

    "projects": """
        <path d="M3 7h7l2 2h9v10H3z"/>
        <path d="M3 7V5h6l2 2"/>
    """,

    "documents": """
        <path d="M6 3h8l4 4v14H6z"/>
        <path d="M14 3v5h5"/>
        <path d="M9 13h6"/>
        <path d="M9 17h6"/>
    """,

    "drawings": """
        <path d="M4 19 18 5l3 3L7 22H4z"/>
        <path d="m14 6 3 3"/>
        <path d="M4 4h6"/>
        <path d="M4 8h6"/>
    """,

    "rfi": """
        <circle cx="12" cy="12" r="9"/>
        <path d="M9.5 9a2.5 2.5 0 1 1 4.2 1.8c-.9.8-1.7 1.2-1.7 2.7"/>
        <path d="M12 17h.01"/>
    """,

    "tasks": """
        <rect x="4" y="4" width="16" height="16" rx="2"/>
        <path d="m8 12 2.5 2.5L16 9"/>
    """,

    "approvals": """
        <circle cx="12" cy="12" r="9"/>
        <path d="m8 12 2.5 2.5L16 9"/>
    """,

    "boq": """
        <path d="M4 4h16v16H4z"/>
        <path d="M8 8h8"/>
        <path d="M8 12h8"/>
        <path d="M8 16h5"/>
    """,

    "site": """
        <path d="M4 20V9l8-5 8 5v11"/>
        <path d="M8 20v-6h8v6"/>
        <path d="M12 4v4"/>
    """,

    "team": """
        <circle cx="12" cy="8" r="3"/>
        <path d="M6 21v-2a6 6 0 0 1 12 0v2"/>
        <path d="M4 12a3 3 0 0 1 3-3"/>
        <path d="M20 12a3 3 0 0 0-3-3"/>
    """,

    "settings": """
        <circle cx="12" cy="12" r="3"/>
        <path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-1.7 1.7-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.6v.1h-2.4v-.1a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1L8 17l.1-.1a1.7 1.7 0 0 0 .3-1.9 1.7 1.7 0 0 0-1.6-1H6v-2.4h.1a1.7 1.7 0 0 0 1.6-1 1.7 1.7 0 0 0-.3-1.9L7.3 8.6 9 6.9l.1.1a1.7 1.7 0 0 0 1.9.3 1.7 1.7 0 0 0 1-1.6v-.1h2.4v.1a1.7 1.7 0 0 0 1 1.6 1.7 1.7 0 0 0 1.9-.3l.1-.1 1.7 1.7-.1.1a1.7 1.7 0 0 0-.3 1.9 1.7 1.7 0 0 0 1.6 1h.1V14h-.1a1.7 1.7 0 0 0-1.6 1z"/>
    """,

    "logout": """
        <path d="M10 4H5v16h5"/>
        <path d="M14 8l4 4-4 4"/>
        <path d="M18 12H8"/>
    """,

    "search": """
        <circle cx="11" cy="11" r="7"/>
        <path d="m20 20-4-4"/>
    """,

    "plus": """
        <path d="M12 5v14"/>
        <path d="M5 12h14"/>
    """,

    "menu": """
        <path d="M4 7h16"/>
        <path d="M4 12h16"/>
        <path d="M4 17h16"/>
    """,
}


# ============================================================
# SVG ICON RENDERER
# ============================================================

def svg_icon(
    name: str,
    size: int = 22,
    stroke: str = "#60A5FA",
) -> str:
    """
    Return an inline SVG icon.

    The SVG is embedded directly into the HTML.
    No image files or icon fonts are required.
    """

    body = SVG_ICONS.get(
        name,
        SVG_ICONS["home"],
    )

    safe_stroke = escape(
        stroke,
        quote=True,
    )

    return f"""
    <svg
        width="{int(size)}"
        height="{int(size)}"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
        focusable="false"
        style="
            display:block;
            width:{int(size)}px;
            height:{int(size)}px;
            flex-shrink:0;
        "
    >
        <g
            stroke="{safe_stroke}"
            stroke-width="1.8"
            stroke-linecap="round"
            stroke-linejoin="round"
        >
            {body}
        </g>
    </svg>
    """


# ============================================================
# CREATIVE STUDIOS LOGO
# ============================================================

def cs_logo_svg(
    size: int = 74,
) -> str:
    """
    Return the Creative Studios inline SVG logo.

    This is deliberately independent of emoji fonts.
    """

    size = int(size)

    return f"""
    <svg
        width="{size}"
        height="{size}"
        viewBox="0 0 74 74"
        xmlns="http://www.w3.org/2000/svg"
        role="img"
        aria-label="Creative Studios"
        style="
            display:block;
            width:{size}px;
            height:{size}px;
        "
    >

        <defs>

            <linearGradient
                id="csLogoGradient{size}"
                x1="0"
                y1="0"
                x2="1"
                y2="1"
            >
                <stop
                    offset="0%"
                    stop-color="#3B82F6"
                />

                <stop
                    offset="100%"
                    stop-color="#1D4ED8"
                />
            </linearGradient>

        </defs>

        <rect
            x="1"
            y="1"
            width="72"
            height="72"
            rx="19"
            fill="url(#csLogoGradient{size})"
        />

        <!-- C -->

        <path
            d="
                M31 24
                C27 21 21 21 17 25
                C13 29 13 36 17 40
                C21 44 27 44 31 41
            "
            fill="none"
            stroke="#FFFFFF"
            stroke-width="4"
            stroke-linecap="round"
        />

        <!-- S -->

        <path
            d="
                M55 25
                C51 21 43 21 40 25
                C37 29 41 32 47 34
                C53 36 57 38 54 43
                C51 47 43 47 39 43
            "
            fill="none"
            stroke="#FFFFFF"
            stroke-width="4"
            stroke-linecap="round"
        />

        <!-- Construction point -->

        <circle
            cx="18"
            cy="51"
            r="3"
            fill="#FFFFFF"
        />

        <circle
            cx="56"
            cy="51"
            r="3"
            fill="#FFFFFF"
        />

        <path
            d="M18 51h38"
            stroke="#FFFFFF"
            stroke-width="2"
            stroke-linecap="round"
            opacity="0.65"
        />

    </svg>
    """


# ============================================================
# MODULE ICON MAP
# ============================================================

MODULE_ICONS = {
    "Overview": "home",
    "Projects": "projects",
    "Documents": "documents",
    "Drawings": "drawings",
    "Approvals": "approvals",
    "BOQ": "boq",
    "RFIs": "rfi",
    "Site Logs": "site",
    "Tasks": "tasks",
    "Team": "team",
    "Settings": "settings",
}


# ============================================================
# MODULE EMOJIS
# ============================================================

MODULE_EMOJIS = {
    "Overview": "🏠",
    "Projects": "🏗️",
    "Documents": "📄",
    "Drawings": "📐",
    "Approvals": "✅",
    "BOQ": "📋",
    "RFIs": "❓",
    "Site Logs": "🏢",
    "Tasks": "☑️",
    "Team": "👥",
    "Settings": "⚙️",
}


# ============================================================
# MODULE HEADER
# ============================================================

def render_module_header(
    st,
    title: str,
    subtitle: str,
    icon_name: str | None = None,
    emoji: str | None = None,
) -> None:
    """
    Render a consistent module header.

    SVG is the primary icon.
    Emoji is secondary and optional.
    """

    if icon_name is None:

        icon_name = MODULE_ICONS.get(
            title,
            "home",
        )

    if emoji is None:

        emoji = MODULE_EMOJIS.get(
            title,
            "",
        )

    icon = svg_icon(
        icon_name,
        size=25,
        stroke="#60A5FA",
    )

    st.markdown(
        f"""
        <div class="cs-module-header">

            <div class="cs-module-header-icon">
                {icon}
            </div>

            <div class="cs-module-header-content">

                <div class="cs-module-header-title">

                    <span class="cs-emoji">
                        {escape(emoji)}
                    </span>

                    {escape(title)}

                </div>

                <div class="cs-module-header-subtitle">
                    {escape(subtitle)}
                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# SIDEBAR BRANDING
# ============================================================

def render_sidebar_brand(
    st,
) -> None:
    """
    Render Creative Studios branding inside the sidebar.
    """

    logo = cs_logo_svg(46)

    st.sidebar.markdown(
        f"""
        <div class="cs-sidebar-brand">

            <div class="cs-sidebar-brand-row">

                <div class="cs-sidebar-logo">
                    {logo}
                </div>

                <div class="cs-sidebar-brand-text">

                    <div class="cs-sidebar-name">
                        Creative Studios
                    </div>

                    <div class="cs-sidebar-subtitle">
                        AEC Workspace
                    </div>

                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# LOGIN BRANDING
# ============================================================

def render_login_brand(
    st,
) -> None:
    """
    Render the login-page Creative Studios branding.
    """

    logo = cs_logo_svg(74)

    st.markdown(
        f"""
        <div class="cs-login-brand">

            <div class="cs-logo">
                {logo}
            </div>

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