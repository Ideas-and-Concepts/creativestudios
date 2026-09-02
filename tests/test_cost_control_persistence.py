from pathlib import Path

from modules import database
from modules.module_utils import remove_record, save_new_record, save_updated_record


def test_cost_control_create_update_delete_persists(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(database, "DB_FILE", tmp_path / "creativestudios_db.json")

    db = database.initialize_database()
    project = save_new_record(db, "projects", {"name": "Test Project"})

    cost = save_new_record(
        db,
        "cost_control",
        {
            "project_id": project["id"],
            "cost_code": "CC-001",
            "description": "Concrete works",
            "cost_type": "Budget",
            "amount": 125000.50,
            "status": "Approved",
        },
    )

    assert cost["id"] == 1
    assert db["cost_control"][0]["amount"] == 125000.50

    reloaded = database.load_memory()
    assert reloaded["cost_control"][0]["description"] == "Concrete works"

    assert save_updated_record(
        reloaded,
        "cost_control",
        cost["id"],
        {"cost_type": "Actual Cost", "amount": 120000.25, "status": "Active"},
    )

    updated = database.load_memory()
    assert updated["cost_control"][0]["cost_type"] == "Actual Cost"
    assert updated["cost_control"][0]["amount"] == 120000.25

    assert remove_record(updated, "cost_control", cost["id"])
    assert database.load_memory()["cost_control"] == []
