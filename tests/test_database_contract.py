from modules.database import (
    initialize_database,
    load_memory,
    save_memory,
    add_record,
    update_record,
    delete_record,
    get_record,
    get_records,
    next_id,
)


def test_database_contract():

    db = initialize_database()

    required_collections = [
        "users",
        "projects",
        "documents",
        "drawings",
        "rfis",
        "tasks",
        "approvals",
        "teams",
    ]

    for collection in required_collections:

        assert collection in db

        assert isinstance(
            db[collection],
            list,
        )


def test_approvals_crud_contract():

    db = initialize_database()

    approval_id = next_id(
        "approvals",
        db,
    )

    record = add_record(
        "approvals",
        {
            "id": approval_id,
            "title": "Database Contract Test",
            "status": "Pending",
        },
        db,
    )

    assert record["id"] == approval_id

    found = get_record(
        "approvals",
        approval_id,
        db,
    )

    assert found is not None

    assert found["title"] == (
        "Database Contract Test"
    )

    updated = update_record(
        "approvals",
        approval_id,
        {
            "status": "Approved",
        },
        db,
    )

    assert updated is not None

    assert updated["status"] == "Approved"

    records = get_records(
        "approvals",
        db,
    )

    assert any(
        str(record.get("id"))
        == str(approval_id)
        for record in records
    )

    deleted = delete_record(
        "approvals",
        approval_id,
        db,
    )

    assert deleted is True

    assert get_record(
        "approvals",
        approval_id,
        db,
    ) is None

    assert save_memory(db) is True

    reloaded = load_memory()

    assert get_record(
        "approvals",
        approval_id,
        reloaded,
    ) is None