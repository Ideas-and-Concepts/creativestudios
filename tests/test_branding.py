import base64

import streamlit_app


def test_render_sidebar_branding_without_expected_session_state(
    monkeypatch,
):
    captured = {}

    def fake_markdown(body, **kwargs):
        captured["body"] = body
        captured["kwargs"] = kwargs

    # Capture sidebar.markdown() output.
    monkeypatch.setattr(
        streamlit_app.st.sidebar,
        "markdown",
        fake_markdown,
    )

    # Simulate a fresh/partial session where the expected
    # authentication keys are absent.
    for key in (
        "user",
        "active_module",
        "authenticated",
    ):
        try:
            del streamlit_app.st.session_state[key]
        except KeyError:
            pass

    # Sidebar buttons must not interfere with this branding test.
    monkeypatch.setattr(
        streamlit_app.st.sidebar,
        "button",
        lambda *args, **kwargs: False,
    )

    streamlit_app.render_sidebar()

    html = captured["body"]

    # --------------------------------------------------------
    # Creative Studios branding must still exist.
    # --------------------------------------------------------

    assert "Creative Studios" in html
    assert "AEC Workspace" in html

    # --------------------------------------------------------
    # Logo must still be an embedded SVG.
    # --------------------------------------------------------

    marker = "data:image/svg+xml;base64,"

    assert marker in html

    encoded = html.split(marker, 1)[1].split('"', 1)[0]

    svg = base64.b64decode(
        encoded,
        validate=True,
    ).decode("utf-8")

    assert "<svg" in svg
    assert 'xmlns="http://www.w3.org/2000/svg"' in svg

    # --------------------------------------------------------
    # Sidebar logo dimensions.
    # --------------------------------------------------------

    assert 'width="46"' in html
    assert 'height="46"' in html

    assert "width:46px" in html
    assert "height:46px" in html

    # --------------------------------------------------------
    # HTML must actually be enabled.
    # --------------------------------------------------------

    assert (
        captured["kwargs"].get(
            "unsafe_allow_html"
        )
        is True
    )