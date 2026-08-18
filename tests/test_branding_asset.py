from pathlib import Path

import pytest

from modules import branding


def test_creative_studios_logo_is_readable_png():
    """
    Verify that the shared Creative Studios logo is a readable
    PNG with nonzero dimensions.

    If Pillow is not installed, skip this test clearly rather
    than failing the entire test suite.
    """

    try:
        from PIL import Image
    except ImportError:
        pytest.skip(
            "Pillow is not installed; skipping PNG "
            "readability and dimension check."
        )

    logo_path = Path(branding.LOGO_PATH)

    assert logo_path.exists(), (
        f"Creative Studios logo not found: {logo_path}"
    )

    assert logo_path.is_file(), (
        f"Creative Studios logo is not a file: {logo_path}"
    )

    assert logo_path.stat().st_size > 0, (
        "Creative Studios logo file is empty."
    )

    # Pillow must be able to open the file.
    with Image.open(logo_path) as image:

        # Verify the actual file format.
        assert image.format == "PNG", (
            f"Expected PNG, got {image.format!r}"
        )

        # Verify the image is actually readable.
        image.verify()

    # Re-open after verify(), because Pillow invalidates the
    # image object after verify().
    with Image.open(logo_path) as image:

        width, height = image.size

        assert width > 0, (
            f"Logo width must be greater than zero, got {width}"
        )

        assert height > 0, (
            f"Logo height must be greater than zero, got {height}"
        )