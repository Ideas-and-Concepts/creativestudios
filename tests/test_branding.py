from pathlib import Path

import streamlit_app
from modules.settings import PAGE_KEYS, get_page_configuration


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
    assert "st.sidebar.image" in source
    assert "Inter" in source
    assert "Space Grotesk" in source
    assert "#2f80ed" in source
    assert "#f6f7f9" in source
    assert "#030509" not in source
    assert "width=88" not in source
    assert "unsafe_allow_html=True" in source


def test_navigation_contains_all_registered_modules():
    expected = set(streamlit_app.MODULE_IMPORTS)
    assert expected == set(streamlit_app.NAVIGATION)


def test_navigation_groups_cover_all_modules_once():
    grouped = [page for pages in streamlit_app.MODULE_GROUPS.values() for page in pages]
    assert set(grouped) == set(streamlit_app.NAVIGATION)
    assert len(grouped) == len(set(grouped))
    assert grouped.count("Dashboard") == 1
    assert grouped.count("Settings") == 1


def test_page_configuration_preserves_all_registered_pages():
    order, labels = get_page_configuration({"settings": {}})
    assert order == PAGE_KEYS
    assert set(labels) == set(PAGE_KEYS)


def test_page_configuration_accepts_persistent_custom_order_and_labels():
    database = {
        "settings": {
            "page_order": ["Settings", "Projects", "Dashboard"],
            "page_labels": {"Settings": "Workspace Admin", "Projects": "Jobs"},
        }
    }
    order, labels = get_page_configuration(database)
    assert order[:3] == ["Settings", "Projects", "Dashboard"]
    assert set(order) == set(PAGE_KEYS)
    assert labels["Settings"] == "Workspace Admin"
    assert labels["Projects"] == "Jobs"
