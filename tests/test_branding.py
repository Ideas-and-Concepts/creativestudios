import base64

import streamlit_app


def test_sidebar_branding_uses_svg_logo_and_46px_dimensions(
    monkeypatch,
):
    captured = {}

    def fake_markdown(body, **kwargs):
        captured["body"] = body
        captured["kwargs"] = kwargs

    # Streamlit's sidebar.markdown()
    monkeypatch.setattr(
        streamlit_app.st.sidebar,
        "markdown",
        fake_markdown,
    )

    # Call the existing sidebar renderer.
    monkeypatch.setattr(
        streamlit_app.st,
        "session_state",
        {
            "user": {
                "full_name": "Test User",
                "username": "test",
                "role": "Admin",
            },
            "active_module": "Overview",
        },
        raising=False,
    )

    streamlit_app.render_sidebar()

    html = captured["body"]

    # --------------------------------------------------------
    # 1. Base64 SVG data URI must be present.
    # --------------------------------------------------------

    marker = "data:image/svg+xml;base64,"

    assert marker in html

    # --------------------------------------------------------
    # 2. Extract and validate the base64 payload.
    # --------------------------------------------------------

    start = html.index(marker) + len(marker)

    encoded = html[start:].split('"', 1)[0]

    svg_bytes = base64.b64decode(
        encoded,
        validate=True,
    )

    svg = svg_bytes.decode("utf-8")

    assert "<svg" in svg
    assert 'xmlns="http://www.w3.org/2000/svg"' in svg

    # --------------------------------------------------------
    # 3. Verify Creative Studios branding SVG.
    # --------------------------------------------------------

    assert "#3B82F6" in svg
    assert "#1D4ED8" in svg

    # --------------------------------------------------------
    # 4. Sidebar logo must remain exactly 46px.
    # --------------------------------------------------------

    assert 'width="46"' in html
    assert 'height="46"' in html

    # Wrapper dimensions.
    assert "width:46px" in html
    assert "height:46px" in html

    # --------------------------------------------------------
    # 5. Company name and subtitle.
    # --------------------------------------------------------

    assert "Creative Studios" in html
    assert "AEC Workspace" in html

    # --------------------------------------------------------
    # 6. HTML rendering must be enabled.
    # --------------------------------------------------------

    assert (
        captured["kwargs"].get(
            "unsafe_allow_html"
        )
        is True
    )


def test_render_cs_logo_emits_base64_svg_and_requested_size(monkeypatch):
    captured = {}

    def fake_markdown(body, **kwargs):
        captured["body"] = body
        captured["kwargs"] = kwargs

    monkeypatch.setattr(
        streamlit_app.st,
        "markdown",
        fake_markdown,
    )

    streamlit_app.render_cs_logo(64)

    html = captured["body"]

    # --------------------------------------------------------
    # 1. The logo must be rendered as a data URI.
    # --------------------------------------------------------

    marker = "data:image/svg+xml;base64,"

    assert marker in html

    # --------------------------------------------------------
    # 2. Extract the base64 payload.
    # --------------------------------------------------------

    start = html.index(marker) + len(marker)

    encoded = html[start:].split('"', 1)[0]

    # Must be valid base64.
    svg_bytes = base64.b64decode(
        encoded,
        validate=True,
    )

    svg = svg_bytes.decode("utf-8")

    # --------------------------------------------------------
    # 3. Confirm this is actually the Creative Studios SVG.
    # --------------------------------------------------------

    assert "<svg" in svg
    assert 'xmlns="http://www.w3.org/2000/svg"' in svg

    # Branding-specific SVG elements.
    assert "#3B82F6" in svg
    assert "#1D4ED8" in svg
    assert 'stroke="white"' in svg

    # --------------------------------------------------------
    # 4. Requested size must be preserved.
    # --------------------------------------------------------

    assert 'width="64"' in html
    assert 'height="64"' in html

    assert "width:64px" in html
    assert "height:64px" in html

    # --------------------------------------------------------
    # 5. Rendering must use unsafe_allow_html.
    # --------------------------------------------------------

    assert (
        captured["kwargs"].get(
            "unsafe_allow_html"
        )
        is True
    )


def test_render_cs_logo_default_size_is_76(monkeypatch):
    captured = {}

    def fake_markdown(body, **kwargs):
        captured["body"] = body
        captured["kwargs"] = kwargs

    monkeypatch.setattr(
        streamlit_app.st,
        "markdown",
        fake_markdown,
    )

    # No size argument: verify the helper's default.
    streamlit_app.render_cs_logo()

    html = captured["body"]

    # <img> attributes
    assert 'width="76"' in html
    assert 'height="76"' in html

    # Wrapper inline styles
    assert "width:76px" in html
    assert "height:76px" in html

    # HTML rendering must be enabled.
    assert (
        captured["kwargs"].get(
            "unsafe_allow_html"
        )
        is True
    )