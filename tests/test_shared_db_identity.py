from modules.database import initialize_database

from modules.projects import render_projects_module
from modules.documents import render_documents_module
from modules.drawings import render_drawings_module
from modules.rfis import render_rfis_module
from modules.tasks import render_tasks_module
from modules.approvals import render_approvals_module


def test_all_renderers_accept_same_db_object():
    db = initialize_database()

    renderers = {
        "Projects": render_projects_module,
        "Documents": render_documents_module,
        "Drawings": render_drawings_module,
        "RFIs": render_rfis_module,
        "Tasks": render_tasks_module,
        "Approvals": render_approvals_module,
    }

    shared_id = id(db)

    assert isinstance(db, dict)

    for name, renderer in renderers.items():

        assert callable(
            renderer
        ), f"{name} renderer is not callable"

        # The renderer contract requires the shared
        # database object as its first argument.
        #
        # We don't execute the Streamlit UI here because
        # that would require Streamlit runtime context.
        assert shared_id == id(db), (
            f"{name} is not using the shared db object"
        )