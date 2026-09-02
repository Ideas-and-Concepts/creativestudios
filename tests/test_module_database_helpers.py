from pathlib import Path

from modules import database
from modules.module_utils import remove_record, save_new_record, save_updated_record


def test_module_helpers_persist_create_update_delete(monkeypatch, tmp_path: Path):
    db_file = tmp_path / "creativestudios_db.json"
    monkeypatch.setattr(database, "DB_FILE", db_file)

    db = database.initialize_database()

    created = save_new_record(
        db,
        "tasks",
        {
            "project_id": 1,
            "title": "Prepare structural review",
            "status": "Not Started",
        },
    )

    assert created["id"] == 1
    assert len(db["tasks"]) == 1
    assert db["tasks"][0]["title"] == "Prepare structural review"

    reloaded = database.load_memory()
    assert reloaded["tasks"][0]["title"] == "Prepare structural review"

    assert save_updated_record(
        reloaded,
        "tasks",
        created["id"],
        {"status": "Completed", "progress": 100},
    )

    updated = database.load_memory()
    assert updated["tasks"][0]["status"] == "Completed"
    assert updated["tasks"][0]["progress"] == 100

    assert remove_record(updated, "tasks", created["id"])
    assert database.load_memory()["tasks"] == []
