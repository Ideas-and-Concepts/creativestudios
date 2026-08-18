"""
Creative Studios
Shared Database Identity Test

Verifies that render_active_module() passes the exact same
database object to every AEC workspace renderer.
"""

from unittest.mock import Mock

import pytest

import streamlit_app


# ============================================================
# MODULE / RENDERER MAPPING
# ============================================================

RENDERERS = [
    (
        "Projects",
        "render_projects_module",
    ),
    (
        "Documents",
        "render_documents_module",
    ),
    (
        "Drawings",
        "render_drawings_module",
    ),
    (
        "RFIs",
        "render_rfis_module",
    ),
    (
        "Tasks",
        "render_tasks_module",
    ),
    (
        "Approvals",
        "render_approvals_module",
    ),
]


# ============================================================
# TEST
# ============================================================

@pytest.mark.parametrize(
    "module_name, renderer_name",
    RENDERERS,
)
def test_render_active_module_passes_exact_same_db(
    monkeypatch,
    module_name,
    renderer_name,
):
    """
    Verify that render_active_module() passes the exact same
    db object received by the dispatcher to the selected
    renderer.
    """

    # --------------------------------------------------------
    # Create one unique database object.
    # --------------------------------------------------------

    db = {
        "users": [],
        "projects": [],
        "documents": [],
        "drawings": [],
        "rfis": [],
        "tasks": [],
        "approvals": [],
        "teams": [],
        "settings": {},
    }

    # --------------------------------------------------------
    # Create a mock renderer.
    # --------------------------------------------------------

    renderer = Mock(
        name=renderer_name
    )

    # --------------------------------------------------------
    # Replace the renderer used by streamlit_app.
    #
    # This is important:
    #
    # We patch the object inside streamlit_app rather than
    # patching the original module.
    # --------------------------------------------------------

    monkeypatch.setattr(
        streamlit_app,
        renderer_name,
        renderer,
    )

    # --------------------------------------------------------
    # Dispatch the module.
    # --------------------------------------------------------

    streamlit_app.render_active_module(
        module_name,
        db,
    )

    # --------------------------------------------------------
    # Renderer must have been called exactly once.
    # --------------------------------------------------------

    renderer.assert_called_once()

    # --------------------------------------------------------
    # Extract the actual database object passed by the
    # dispatcher.
    # --------------------------------------------------------

    received_db = renderer.call_args.args[0]

    # --------------------------------------------------------
    # Identity test.
    #
    # `is` is intentional.
    #
    # We don't merely want equal dictionaries.
    # We want the exact same Python object.
    # --------------------------------------------------------

    assert received_db is db

def test_all_six_renderers_receive_same_db(monkeypatch):
    """
    Verify that every AEC renderer receives the exact same
    database object when dispatched through
    render_active_module().
    """

    db = {
        "users": [],
        "projects": [],
        "documents": [],
        "drawings": [],
        "rfis": [],
        "tasks": [],
        "approvals": [],
        "teams": [],
        "settings": {},
    }

    mocks = {}

    # --------------------------------------------------------
    # Patch all six renderers.
    # --------------------------------------------------------

    for _, renderer_name in RENDERERS:

        renderer = Mock(
            name=renderer_name
        )

        mocks[renderer_name] = renderer

        monkeypatch.setattr(
            streamlit_app,
            renderer_name,
            renderer,
        )

    # --------------------------------------------------------
    # Dispatch every module.
    # --------------------------------------------------------

    for module_name, renderer_name in RENDERERS:

        streamlit_app.render_active_module(
            module_name,
            db,
        )

        renderer = mocks[renderer_name]

        renderer.assert_called_once()

        received_db = (
            renderer.call_args.args[0]
        )

        # ----------------------------------------------------
        # Exact object identity.
        # ----------------------------------------------------

        assert received_db is db

    # --------------------------------------------------------
    # Extra protection:
    #
    # All renderers must have received the same object as
    # each other, not merely an equivalent dictionary.
    # --------------------------------------------------------

    received_objects = [
        mock.call_args.args[0]
        for mock in mocks.values()
    ]

    first_db = received_objects[0]

    for received_db in received_objects[1:]:

        assert received_db is first_db