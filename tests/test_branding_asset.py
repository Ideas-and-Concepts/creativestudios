from pathlib import Path

import pytest

from modules import branding


# ============================================================
# TEST 1: Logo asset exists
# ============================================================

def test_creative_studios_logo_exists():
    """
    The shared Creative Studios logo must exist in:
        assets/creative_studios_logo.png
    """

    assert branding.LOGO_PATH == (
        Path(branding.__file__).resolve().parent.parent
        / "assets"
        / "creative_studios_logo.png"
    )

    assert branding.LOGO_PATH.exists(), (
        f"Creative Studios logo was not found at: "
        f"{branding.LOGO_PATH}"
    )

    assert branding.LOGO_PATH.is_file(), (
        f"Creative Studios logo path is not a file: "
        f"{branding.LOGO_PATH}"
    )

    assert branding.LOGO_PATH.stat().st_size > 0, (
        "Creative Studios logo file is empty."
    )


# ============================================================
# TEST 2: Branding helpers use the same LOGO_PATH
# ============================================================

def test_branding_helpers_use_shared_logo_path():
    """
    Login, sidebar and module branding must all use the
    same shared LOGO_PATH rather than defining their own
    image path.
    """

    source = Path(branding.__file__).read_text(
        encoding="utf-8"
    )

    helpers = [
        "render_login_branding",
        "render_sidebar_branding",
        "render_module_header",
    ]

    for helper in helpers:

        assert f"def {helper}" in source, (
            f"{helper}() was not found in modules/branding.py"
        )

    # The module should define one shared LOGO_PATH.
    assert source.count("LOGO_PATH") >= 4, (
        "Expected LOGO_PATH to be defined and reused "
        "by the branding helpers."
    )

    # Make sure the hard-coded asset path isn't being
    # independently recreated by each helper.
    assert source.count(
        "creative_studios_logo.png"
    ) == 1, (
        "creative_studios_logo.png should be defined "
        "once through the shared LOGO_PATH."
    )


# ============================================================
# TEST 3: Missing PNG produces CS fallback
# ============================================================

def test_login_branding_shows_cs_fallback_when_logo_missing(
    monkeypatch,
):
    """
    If the PNG is missing, login branding should render
    the CS fallback instead of crashing.
    """

    monkeypatch.setattr(
        branding,
        "logo_exists",
        lambda: False,
    )

    captured = []

    def fake_markdown(
        body,
        *args,
        **kwargs,
    ):
        captured.append(body)

    monkeypatch.setattr(
        branding.st,
        "markdown",
        fake_markdown,
    )

    branding.render_login_branding()

    html = "\n".join(captured)

    assert "cs-logo-fallback" in html
    assert ">CS<" in html

    # The fallback should still preserve branding.
    assert "Creative Studios" in html
    assert "AEC Workspace" in html


# ============================================================
# TEST 4: Sidebar fallback
# ============================================================

def test_sidebar_branding_shows_cs_fallback_when_logo_missing(
    monkeypatch,
):
    """
    If the PNG is missing, sidebar branding should render
    the CS fallback.
    """

    monkeypatch.setattr(
        branding,
        "logo_exists",
        lambda: False,
    )

    captured = []

    def fake_markdown(
        body,
        *args,
        **kwargs,
    ):
        captured.append(body)

    monkeypatch.setattr(
        branding.st.stSidebar,
        "markdown",
        fake_markdown,
        raising=False,
    )

    # Streamlit exposes sidebar as st.sidebar.
    monkeypatch.setattr(
        branding.st.sidebar,
        "markdown",
        fake_markdown,
    )

    branding.render_sidebar_branding()

    html = "\n".join(captured)

    assert "cs-sidebar-logo-fallback" in html
    assert ">CS<" in html

    assert "Creative Studios" in html
    assert "AEC Workspace" in html


# ============================================================
# TEST 5: Module header fallback
# ============================================================

def test_module_header_shows_cs_fallback_when_logo_missing(
    monkeypatch,
):
    """
    If the PNG is missing, module headers should render
    the CS fallback.
    """

    monkeypatch.setattr(
        branding,
        "logo_exists",
        lambda: False,
    )

    captured = []

    def fake_markdown(
        body,
        *args,
        **kwargs,
    ):
        captured.append(body)

    class FakeColumn:

        def __enter__(self):
            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback,
        ):
            return False

        def markdown(
            self,
            body,
            *args,
            **kwargs,
        ):
            captured.append(body)

        def image(
            self,
            *args,
            **kwargs,
        ):
            captured.append(
                ("IMAGE", args, kwargs)
            )

    columns = [
        FakeColumn(),
        FakeColumn(),
    ]

    monkeypatch.setattr(
        branding.st,
        "columns",
        lambda *args, **kwargs: columns,
    )

    monkeypatch.setattr(
        branding.st,
        "markdown",
        fake_markdown,
    )

    branding.render_module_header(
        "Projects",
        "Project management workspace.",
    )

    html = "\n".join(
        str(item)
        for item in captured
    )

    assert "module-logo-fallback" in html
    assert "CS" in html

    assert "Projects" in html
    assert "Project management workspace." in html