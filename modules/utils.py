import base64
import hashlib
from pathlib import Path

LOGO_FILE = "logo.svg"

def ensure_logo_svg():
    """Generates a modern minimalist architectural grid vector SVG logo for the login screen."""
    svg_content = """<svg width="400" height="400" viewBox="0 0 400 400" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="archGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#0F172A"/>
            <stop offset="100%" stop-color="#2563EB"/>
        </linearGradient>
    </defs>
    <rect x="80" y="80" width="240" height="240" rx="24" stroke="url(#archGrad)" stroke-width="20" fill="none"/>
    <path d="M140 260V140H200L260 200V260" stroke="url(#archGrad)" stroke-width="20" stroke-linecap="round" stroke-linejoin="round"/>
    <circle cx="260" cy="140" r="16" fill="#06B6D4"/>
</svg>"""
    Path(LOGO_FILE).write_text(svg_content)

def get_logo_html(width=130):
    ensure_logo_svg()
    if Path(LOGO_FILE).exists():
        encoded = base64.b64encode(Path(LOGO_FILE).read_bytes()).decode()
        return f"""
        <div style="display: flex; justify-content: center; align-items: center; width: 100%; margin-bottom: 15px;">
            <img src="data:image/svg+xml;base64,{encoded}" width="{width}" style="display: block;" />
        </div>
        """
    return ""

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()
