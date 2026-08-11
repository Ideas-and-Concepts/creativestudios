import base64
import hashlib
from pathlib import Path

LOGO_FILE = "logo.svg"

def ensure_logo_svg():
    """Generates the transparent Pisces-inspired vector SVG logo."""
    svg_content = """<svg width="500" height="500" viewBox="0 0 500 500" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="piscesGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#2563EB"/>
            <stop offset="100%" stop-color="#06B6D4"/>
        </linearGradient>
    </defs>
    <path d="M150 250H350" stroke="url(#piscesGrad)" stroke-width="32" stroke-linecap="round"/>
    <path d="M190 150C135 205 135 295 190 350" stroke="url(#piscesGrad)" stroke-width="32" stroke-linecap="round" fill="none"/>
    <path d="M310 150C365 205 365 295 310 350" stroke="url(#piscesGrad)" stroke-width="32" stroke-linecap="round" fill="none"/>
</svg>"""
    Path(LOGO_FILE).write_text(svg_content)

def get_logo_html(width=130):
    ensure_logo_svg()
    if Path(LOGO_FILE).exists():
        encoded = base64.b64encode(Path(LOGO_FILE).read_bytes()).decode()
        return f"""
        <div style="display: flex; justify-content: center; align-items: center; width: 100%; margin-bottom: 20px;">
            <img src="data:image/svg+xml;base64,{encoded}" width="{width}" style="display: block;" />
        </div>
        """
    return ""

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

