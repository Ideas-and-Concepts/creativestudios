from pathlib import Path

import streamlit_app


def test_branding_asset_exists():
    root = Path(streamlit_app.__file__).resolve().parent
    logo = root / "assets" / "creative-studios.png"
    assert logo.exists()
    assert logo.is_file()
    assert logo.stat().st_size > 0


def test_sidebar_branding_configuration():
    source = Path(streamlit_app.__file__).read_text(encoding="utf-8")
    assert "Creative Studios" in source
    assert "AEC Collaboration Platform" in source
    assert "creative-studios.png" in source
    assert "st.sidebar.image" not in source
    assert "unsafe_allow_html=True" in source


def test_navigation_contains_current_modules():
    expected = {
        "Dashboard",
        "Projects",
        "Documents",
        "Architecture",
        "Engineering",
        "Drawings",
        "BOQ",
        "MEP",
        "Construction",
    }
    assert expected.issubset(set(streamlit_app.NAVIGATION))
