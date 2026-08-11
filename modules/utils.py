"""
Creative Studios
Utility Functions
"""

import base64
import hashlib
from pathlib import Path


# ============================================================
# PROJECT PATH
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
    Return a SHA-256 hash for a password.
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
    Make sure logo.svg exists.
    """

    logo_path = Path(LOGO_FILE)

    if logo_path.exists():
        return

    svg = """
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 200 200">

    <defs>
        <linearGradient
            id="blue"
            x1="0%"
            y1="0%"
            x2="100%"
            y2="100%">

            <stop
                offset="0%"
                stop-color="#1D4ED8"/>

            <stop
                offset="100%"
                stop-color="#3B82F6"/>

        </linearGradient>
    </defs>

    <rect
        width="200"
        height="200"
        rx="40"
        fill="url(#blue)"/>

    <text
        x="100"
        y="120"
        text-anchor="middle"
        font-family="Arial, Helvetica, sans-serif"
        font-size="82"
        font-weight="700"
        fill="white">
        CS
    </text>

</svg>
"""

    try:
        logo_path.write_text(
            svg.strip(),
            encoding="utf-8",
        )

    except OSError:
        pass


# ============================================================
# LOGO HTML
# ============================================================

def get_logo_html(
    width: int = 130,
) -> str:
    """
    Return the logo as embedded base64 HTML.
    """

    logo_path = Path(LOGO_FILE)

    if not logo_path.exists():
        ensure_logo_svg()

    if not logo_path.exists():
        return ""

    try:

        data = logo_path.read_bytes()

        encoded = base64.b64encode(
            data
        ).decode("utf-8")

        return (
            '<div style="text-align:center;">'
            f'<img src="data:image/svg+xml;base64,{encoded}" '
            f'width="{int(width)}" '
            'alt="Creative Studios Logo">'
            '</div>'
        )

    except OSError:
        return ""