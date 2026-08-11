import base64
from pathlib import Path

LOGO_FILE = "logo.svg"

def ensure_logo_svg():
    """Create a clean SVG logo (CS monogram) if it doesn't already exist."""
    logo_path = Path(LOGO_FILE)
    if not logo_path.exists():
        svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#1e3a8a"/>
      <stop offset="100%" style="stop-color:#3b82f6"/>
    </linearGradient>
  </defs>
  <rect width="200" height="200" rx="40" fill="url(#bg)"/>
  <text x="100" y="115" font-family="Arial, Helvetica, sans-serif" font-size="110" font-weight="bold" fill="#ffffff" text-anchor="middle" letter-spacing="10">CS</text>
</svg>'''
        with open(logo_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)

def get_logo_html(width=130):
    """Return an HTML <img> tag with the base64-encoded logo, scaled to the given width."""
    logo_path = Path(LOGO_FILE)
    if logo_path.exists():
        with open(logo_path, 'rb') as f:
            svg_bytes = f.read()
        b64 = base64.b64encode(svg_bytes).decode('utf-8')
        return f'<img src="data:image/svg+xml;base64,{b64}" width="{width}" alt="Creative Studios Logo">'
    return ""