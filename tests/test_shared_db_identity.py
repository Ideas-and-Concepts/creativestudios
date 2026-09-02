from unittest.mock import Mock

import pytest

import streamlit_app


RENDERERS = [
    (name, renderer_name)
    for name, (_, renderer_name) in streamlit_app.MODULE_IMPORTS.items()
]


@pytest.mark.parametrize("module_name, renderer_name", RENDERERS)
def test_render_module_passes_exact_same_db(monkeypatch, module_name, renderer_name):
    db = {"projects": [], "documents": [], "settings": {}}
    renderer = Mock(name=renderer_name)

    module_path, _ = streamlit_app.MODULE_IMPORTS[module_name]
    module = __import__(module_path, fromlist=[renderer_name])
    monkeypatch.setattr(module, renderer_name, renderer)

    streamlit_app.render_module(module_name, db)

    renderer.assert_called_once_with(db)
    assert renderer.call_args.args[0] is db


def test_all_registered_renderers_receive_same_db(monkeypatch):
    db = {"projects": [], "documents": [], "settings": {}}
    mocks = {}

    for module_name, (module_path, renderer_name) in streamlit_app.MODULE_IMPORTS.items():
        module = __import__(module_path, fromlist=[renderer_name])
        renderer = Mock(name=renderer_name)
        mocks[renderer_name] = renderer
        monkeypatch.setattr(module, renderer_name, renderer)
        streamlit_app.render_module(module_name, db)

    for renderer in mocks.values():
        renderer.assert_called_once_with(db)
        assert renderer.call_args.args[0] is db
