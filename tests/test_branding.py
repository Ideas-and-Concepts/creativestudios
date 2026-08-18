import base64

import streamlit_app


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