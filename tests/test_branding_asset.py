from pathlib import Path

import pytest

import streamlit_app


def test_creative_studios_logo_is_readable_png():
    """Verify that the configured Creative Studios logo is a readable PNG."""
    logo_path = streamlit_app.LOGO_PATH

    assert logo_path is not None

    logo_path = Path(logo_path)

    assert logo_path.exists(), f"Creative Studios logo not found: {logo_path}"
    assert logo_path.is_file(), f"Creative Studios logo is not a file: {logo_path}"
    assert logo_path.stat().st_size > 0, "Creative Studios logo file is empty."

    try:
        from PIL import Image
    except ImportError:
        pytest.skip("Pillow is not installed; PNG readability check skipped.")

    with Image.open(logo_path) as image:
        assert image.format == "PNG"
        width, height = image.size
        assert width > 0
        assert height > 0
        image.verify()
