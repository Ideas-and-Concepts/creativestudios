"""
Creative Studios
Branding smoke test.

Checks that the source contains the required CSS and
HTML branding markers without starting Streamlit.
"""

from pathlib import Path


APP_FILE = (
    Path(__file__).resolve()
    / "streamlit_app.py"
)

source = APP_FILE.read_text(
    encoding="utf-8"
)


REQUIRED = [
    ".cs-logo",
    ".cs-logo-text",
    ".cs-sidebar-logo",
    ".cs-sidebar-logo-text",
    ".cs-brand-name",
    ".cs-brand-subtitle",
    "render_login_brand",
    "render_sidebar_brand",
    "unsafe_allow_html=True",
]


missing = [
    item
    for item in REQUIRED
    if item not in source
]


if missing:

    print("BRANDING CHECK: FAILED")

    print("\nMissing:")

    for item in missing:
        print(f"  - {item}")

    raise SystemExit(1)


print(
    "BRANDING CHECK: PASSED"
)

print(
    "Login CSS/branding markers found."
)

print(
    "Sidebar CSS/branding markers found."
)

print(
    "unsafe_allow_html=True found."
)