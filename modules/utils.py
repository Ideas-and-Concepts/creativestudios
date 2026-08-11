"""
Creative Studios
Utility Functions

Shared helpers for:
- Logo management
- Password hashing
- UI utilities
"""

import base64
import hashlib
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

LOGO_FILE = str(
    BASE_DIR / "logo.svg"
)


# ============================================================
# PASSWORD HASHING
# ============================================================

def hash_password(password: str) -> str:
    """
    Create a SHA-256 password hash.

    The same function is used by both the database bootstrap
    process and the authentication module.
    """

    if password is None:
        password = ""

    return hashlib.sha256(
        str(password).encode("utf-8")
    ).hexdigest()


# ============================================================
# LOGO
# ============================================================

def ensure_logo_svg() -> None:
    """
    Ensure that the Creative Studios logo exists.

    If logo.svg is missing, create a clean fallback logo.
    """

    logo_path = Path(LOGO_FILE)

    if logo_path.exists():
        return

    svg_content = """
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 200 200"
     width="200"
     height="200">

    <defs>
        <linearGradient
            id="bg"
            x1="0%"
            y1="0%"
            x2="100%"
            y2="100%">

            <stop
                offset="0%"
                style="stop-color:#1D4ED8"/>

            <stop
                offset="100%"
                style="stop-color:#3B82F6"/>

        </linearGradient>
    </defs>

    <rect
        width="200"
        height="200"
        rx="40"
        fill="url(#bg)"/>

    <text
        x="100"
        y="115"
        font-family="Arial, Helvetica, sans-serif"
        font-size="110"
        font-weight="bold"
        fill="#FFFFFF"
        text-anchor="middle"
        letter-spacing="10">
        CS
    </text>

</svg>
"""

    try:

        logo_path.write_text(
            svg_content.strip(),
            encoding="utf-8",
        )

    except OSError:
        # Do not crash the application if the deployment
        # environment does not permit writing.
        pass


# ============================================================
# LOGO HTML
# ============================================================

def get_logo_html(
    width: int = 130,
) -> str:
    """
    Return the logo as an embedded base64 image.
    """

    logo_path = Path(LOGO_FILE)

    if not logo_path.exists():
        ensure_logo_svg()

    if not logo_path.exists():
        return ""

    try:

        svg_bytes = logo_path.read_bytes()

        encoded = base64.b64encode(
            svg_bytes
        ).decode("utf-8")

        return (
            '<div style="text-align:center;">'
            f'<img src="data:image/svg+xml;base64,'
            f'{encoded}" '
            f'width="{int(width)}" '
            'alt="Creative Studios Logo">'
            '</div>'
        )

    except (
        OSError,
        ValueError,
    ):
        return ""