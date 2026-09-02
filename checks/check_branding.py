"""Creative Studios branding diagnostic."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP_FILE = ROOT / "streamlit_app.py"
LOGO_FILE = ROOT / "assets" / "creative_studios.png"


def main() -> int:
    if not APP_FILE.exists():
        print(f"BRANDING CHECK: FAILED\nMissing {APP_FILE}")
        return 1

    source = APP_FILE.read_text(encoding="utf-8")

    required = [
        "Creative Studios",
        "AEC Collaboration Platform",
        "render_sidebar",
        "st.sidebar.image",
        "unsafe_allow_html=True",
        "creative_studios.png",
    ]

    missing = [item for item in required if item not in source]

    if not LOGO_FILE.exists():
        missing.append("assets/creative_studios.png")

    if missing:
        print("BRANDING CHECK: FAILED")
        for item in missing:
            print(f"  - {item}")
        return 1

    print("BRANDING CHECK: PASSED")
    print("Current image logo and sidebar branding are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
