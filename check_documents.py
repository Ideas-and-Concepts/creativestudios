"""
Creative Studios
Documents Module Smoke Test

Purpose:
    Verify the Documents module and JSON database contract
    without starting Streamlit.

Run:
    python check_documents.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from tempfile import TemporaryDirectory


# ============================================================
# PROJECT ROOT
# ============================================================

ROOT = Path(__file__).resolve().parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ============================================================
# TEST HELPERS
# ============================================================

passed = 0
failed = 0


def check(
    name: str,
    condition: bool,
    details: str = "",
) -> None:
    """Report a test result."""

    global passed
    global failed

    if condition:
        passed += 1
        print(f"[PASS] {name}")

    else:
        failed += 1
        print(f"[FAIL] {name}")

        if details:
            print(f"       {details}")


# ============================================================
# IMPORT TEST
# ============================================================

print()
print("=" * 60)
print("Creative Studios - Documents Smoke Test")
print("=" * 60)
print()

try:

    from modules.database import (
        add_record,
        delete_record,
        get_record,
        get_records,
        next_id,
        save_memory,
        update_record,
    )

    check(
        "Database functions import",
        True,
    )

except Exception as exc:

    check(
        "Database functions import",
        False,
        f"{type(exc).__name__}: {exc}",
    )

    print()
    print("Database import failed. Stopping.")
    sys.exit(1)


try:

    from modules.documents import (
        render_documents_module,
    )

    check(
        "Documents module import",
        callable(
            render_documents_module
        ),
    )

except Exception as exc:

    check(
        "Documents module import",
        False,
        f"{type(exc).__name__}: {exc}",
    )

    print()
    print("Documents import failed. Stopping.")
    sys.exit(1)


# ============================================================
# TEST DATABASE
# ============================================================

db = {
    "users": [],
    "projects": [
        {
            "id": 1,
            "name": "Kampala Office Complex",
            "status": "Active",
        },
        {
            "id": 2,
            "name": "Jinja Industrial Facility",
            "status": "Planning",
        },
    ],
    "documents": [],
    "drawings": [],
    "rfis": [],
    "tasks": [],
    "teams": [],
    "settings": {},
}


# ============================================================
# DATABASE COLLECTION TEST
# ============================================================

documents = get_records(
    "documents",
    db,
)

check(
    "Documents collection exists",
    isinstance(documents, list),
)


# ============================================================
# NEXT ID
# ============================================================

first_id = next_id(
    "documents",
    db,
)

check(
    "next_id() returns 1 for empty collection",
    first_id == 1,
    f"Expected 1, got {first_id}",
)


# ============================================================
# CREATE
# ============================================================

document = {
    "document_number": "DOC-001",
    "title": "Main Contract",
    "project_id": 1,
    "document_type": "Contract",
    "status": "Active",
    "revision": "Rev 0",
    "document_date": "2026-08-18",
    "author": "Creative Studios",
    "description": "Main project contract.",
}


try:

    created = add_record(
        "documents",
        document,
        db,
    )

    check(
        "Create document",
        isinstance(created, dict),
    )

    check(
        "Created document receives ID",
        created.get("id") == 1,
        f"Created record: {created}",
    )

except Exception as exc:

    check(
        "Create document",
        False,
        f"{type(exc).__name__}: {exc}",
    )

    created = None


# ============================================================
# READ
# ============================================================

if created:

    document_id = created["id"]

    found = get_record(
        "documents",
        document_id,
        db,
    )

    check(
        "Read document",
        found is not None,
    )

    check(
        "Read returns correct document",
        found is not None
        and found.get("document_number")
        == "DOC-001",
    )


# ============================================================
# UPDATE
# ============================================================

if created:

    try:

        updated = update_record(
            "documents",
            document_id,
            {
                "title": "Main Contract - Updated",
                "revision": "Rev 1",
                "status": "Under Review",
            },
            db,
        )

        check(
            "Update document",
            updated is not None,
        )

        check(
            "Update changes title",
            updated is not None
            and updated.get("title")
            == "Main Contract - Updated",
        )

        check(
            "Update changes revision",
            updated is not None
            and updated.get("revision")
            == "Rev 1",
        )

        check(
            "Update changes status",
            updated is not None
            and updated.get("status")
            == "Under Review",
        )

    except Exception as exc:

        check(
            "Update document",
            False,
            f"{type(exc).__name__}: {exc}",
        )


# ============================================================
# PROJECT FILTERING
# ============================================================

all_documents = get_records(
    "documents",
    db,
)

project_1_documents = [
    item
    for item in all_documents
    if str(
        item.get("project_id")
    )
    == "1"
]

project_2_documents = [
    item
    for item in all_documents
    if str(
        item.get("project_id")
    )
    == "2"
]

check(
    "Project filter returns Project 1 document",
    len(project_1_documents) == 1,
)

check(
    "Project filter excludes Project 2",
    len(project_2_documents) == 0,
)


# ============================================================
# SECOND DOCUMENT
# ============================================================

second_document = {
    "document_number": "DOC-002",
    "title": "Jinja Specification",
    "project_id": 2,
    "document_type": "Specification",
    "status": "Draft",
    "revision": "Rev 0",
    "document_date": "2026-08-18",
    "author": "Creative Studios",
}


try:

    created_second = add_record(
        "documents",
        second_document,
        db,
    )

    check(
        "Create second document",
        created_second.get("id") == 2,
    )

except Exception as exc:

    check(
        "Create second document",
        False,
        f"{type(exc).__name__}: {exc}",
    )

    created_second = None


# ============================================================
# PROJECT FILTER WITH TWO PROJECTS
# ============================================================

all_documents = get_records(
    "documents",
    db,
)

project_1_documents = [
    item
    for item in all_documents
    if str(
        item.get("project_id")
    )
    == "1"
]

project_2_documents = [
    item
    for item in all_documents
    if str(
        item.get("project_id")
    )
    == "2"
]

check(
    "Project 1 filter",
    len(project_1_documents) == 1,
)

check(
    "Project 2 filter",
    len(project_2_documents) == 1,
)


# ============================================================
# TYPE FILTER
# ============================================================

contract_documents = [
    item
    for item in all_documents
    if item.get("document_type")
    == "Contract"
]

specification_documents = [
    item
    for item in all_documents
    if item.get("document_type")
    == "Specification"
]

check(
    "Document type filter: Contract",
    len(contract_documents) == 1,
)

check(
    "Document type filter: Specification",
    len(specification_documents) == 1,
)


# ============================================================
# STATUS FILTER
# ============================================================

review_documents = [
    item
    for item in all_documents
    if item.get("status")
    == "Under Review"
]

draft_documents = [
    item
    for item in all_documents
    if item.get("status")
    == "Draft"
]

check(
    "Status filter: Under Review",
    len(review_documents) == 1,
)

check(
    "Status filter: Draft",
    len(draft_documents) == 1,
)


# ============================================================
# DELETE
# ============================================================

if created_second:

    second_id = created_second["id"]

    try:

        deleted = delete_record(
            "documents",
            second_id,
            db,
        )

        check(
            "Delete document",
            deleted is True,
        )

        deleted_record = get_record(
            "documents",
            second_id,
            db,
        )

        check(
            "Deleted document no longer exists",
            deleted_record is None,
        )

    except Exception as exc:

        check(
            "Delete document",
            False,
            f"{type(exc).__name__}: {exc}",
        )


# ============================================================
# ORIGINAL DOCUMENT STILL EXISTS
# ============================================================

if created:

    remaining = get_record(
        "documents",
        created["id"],
        db,
    )

    check(
        "Remaining document survives deletion",
        remaining is not None,
    )


# ============================================================
# DATABASE SAVE TEST
# ============================================================

try:

    saved = save_memory(db)

    # The smoke test database intentionally has the normal
    # in-memory structure. save_memory() should accept it.
    check(
        "Database save contract",
        saved is True,
        "save_memory() returned False.",
    )

except Exception as exc:

    check(
        "Database save contract",
        False,
        f"{type(exc).__name__}: {exc}",
    )


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 60)
print("TEST SUMMARY")
print("=" * 60)

print(
    f"Passed: {passed}"
)

print(
    f"Failed: {failed}"
)

print(
    f"Total:  {passed + failed}"
)

print()

if failed:

    print(
        "RESULT: FAILED"
    )

    sys.exit(1)

print(
    "RESULT: PASSED"
)

print(
    "Documents CRUD, project filtering, "
    "database contract and module import are OK."
)

sys.exit(0)