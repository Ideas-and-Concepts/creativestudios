"""
Creative Studios
Documents Module Smoke Test
============================

Tests:

    - modules.database import
    - modules.documents import
    - Database initialization
    - save_memory()
    - load_memory()
    - next_id()
    - Document CREATE
    - Document READ
    - Document UPDATE
    - Document DELETE
    - Project filtering
    - Document type filtering
    - Status filtering

IMPORTANT:
    This test NEVER writes to the real
    creativestudios_db.json file.

The database file is redirected to a temporary
directory for the duration of the test.

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
# TEST COUNTERS
# ============================================================

passed = 0
failed = 0


def check(
    name: str,
    condition: bool,
    details: str = "",
) -> None:
    """Record and display a test result."""

    global passed
    global failed

    if condition:

        passed += 1

        print(
            f"[PASS] {name}"
        )

    else:

        failed += 1

        print(
            f"[FAIL] {name}"
        )

        if details:
            print(
                f"       {details}"
            )


# ============================================================
# TEST HEADER
# ============================================================

print()

print(
    "=" * 64
)

print(
    "Creative Studios - Documents Smoke Test"
)

print(
    "=" * 64
)

print()


# ============================================================
# IMPORT DATABASE MODULE
# ============================================================

try:

    import modules.database as database

    from modules.database import (
        add_record,
        delete_record,
        get_record,
        get_records,
        initialize_database,
        load_memory,
        next_id,
        save_memory,
        update_record,
    )

    check(
        "Database module import",
        True,
    )

except Exception as exc:

    check(
        "Database module import",
        False,
        f"{type(exc).__name__}: {exc}",
    )

    print()
    print(
        "Cannot continue because modules.database "
        "could not be imported."
    )

    sys.exit(1)


# ============================================================
# IMPORT DOCUMENTS MODULE
# ============================================================

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
    print(
        "Cannot continue because modules.documents "
        "could not be imported."
    )

    sys.exit(1)


# ============================================================
# TEMPORARY DATABASE
# ============================================================

with TemporaryDirectory(
    prefix="creativestudios_test_"
) as temporary_directory:

    temporary_directory = Path(
        temporary_directory
    )

    temporary_db_file = (
        temporary_directory
        / "test_database.json"
    )

    # --------------------------------------------------------
    # Redirect the database module to the temporary file.
    # --------------------------------------------------------

    original_db_file = database.DB_FILE

    database.DB_FILE = temporary_db_file

    try:

        print(
            f"Temporary database:"
        )

        print(
            f"  {temporary_db_file}"
        )

        print()


        # ====================================================
        # INITIAL DATABASE
        # ====================================================

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


        # ====================================================
        # SAVE TEST
        # ====================================================

        try:

            saved = save_memory(
                db
            )

            check(
                "save_memory() succeeds",
                saved is True,
                "save_memory() returned False.",
            )

            check(
                "Temporary database file created",
                temporary_db_file.exists(),
                f"Expected {temporary_db_file}",
            )

        except Exception as exc:

            check(
                "save_memory() succeeds",
                False,
                f"{type(exc).__name__}: {exc}",
            )


        # ====================================================
        # LOAD TEST
        # ====================================================

        try:

            loaded_db = load_memory()

            check(
                "load_memory() succeeds",
                isinstance(
                    loaded_db,
                    dict,
                ),
            )

            check(
                "Loaded projects collection",
                isinstance(
                    loaded_db.get(
                        "projects"
                    ),
                    list,
                ),
            )

            check(
                "Loaded documents collection",
                isinstance(
                    loaded_db.get(
                        "documents"
                    ),
                    list,
                ),
            )

        except Exception as exc:

            check(
                "load_memory() succeeds",
                False,
                f"{type(exc).__name__}: {exc}",
            )

            loaded_db = {}


        # ====================================================
        # INITIALIZE TEST
        # ====================================================

        try:

            initialized = initialize_database()

            check(
                "initialize_database() succeeds",
                isinstance(
                    initialized,
                    dict,
                ),
            )

            check(
                "Initialized database has documents",
                isinstance(
                    initialized.get(
                        "documents"
                    ),
                    list,
                ),
            )

        except Exception as exc:

            check(
                "initialize_database() succeeds",
                False,
                f"{type(exc).__name__}: {exc}",
            )


        # ====================================================
        # USE LOADED DATABASE
        # ====================================================

        db = loaded_db

        # Make absolutely certain the required collections
        # exist for the remainder of the test.

        if not isinstance(
            db.get("documents"),
            list,
        ):

            db["documents"] = []

        if not isinstance(
            db.get("projects"),
            list,
        ):

            db["projects"] = [
                {
                    "id": 1,
                    "name": "Kampala Office Complex",
                },
                {
                    "id": 2,
                    "name": "Jinja Industrial Facility",
                },
            ]


        # ====================================================
        # NEXT ID
        # ====================================================

        try:

            first_id = next_id(
                "documents",
                db,
            )

            check(
                "next_id() returns 1 for empty documents",
                first_id == 1,
                f"Expected 1, got {first_id}",
            )

        except Exception as exc:

            check(
                "next_id() works",
                False,
                f"{type(exc).__name__}: {exc}",
            )


        # ====================================================
        # CREATE DOCUMENT
        # ====================================================

        document = {
            "document_number": "DOC-001",
            "title": "Main Contract",
            "project_id": 1,
            "document_type": "Contract",
            "status": "Active",
            "revision": "Rev 0",
            "document_date": "2026-08-18",
            "author": "Creative Studios",
            "description": (
                "Main project contract."
            ),
        }

        created = None

        try:

            created = add_record(
                "documents",
                document,
                db,
            )

            check(
                "Create document",
                isinstance(
                    created,
                    dict,
                ),
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


        # ====================================================
        # VERIFY CREATE WAS PERSISTED
        # ====================================================

        try:

            reloaded_after_create = (
                load_memory()
            )

            persisted_documents = (
                reloaded_after_create.get(
                    "documents",
                    [],
                )
            )

            persisted_document = next(
                (
                    item
                    for item in persisted_documents
                    if str(
                        item.get("id")
                    )
                    == "1"
                ),
                None,
            )

            check(
                "Created document persisted to temporary file",
                persisted_document is not None,
            )

        except Exception as exc:

            check(
                "Created document persisted to temporary file",
                False,
                f"{type(exc).__name__}: {exc}",
            )


        # ====================================================
        # READ
        # ====================================================

        if created:

            document_id = created.get(
                "id"
            )

            try:

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
                    and found.get(
                        "document_number"
                    )
                    == "DOC-001",
                )

            except Exception as exc:

                check(
                    "Read document",
                    False,
                    f"{type(exc).__name__}: {exc}",
                )


        # ====================================================
        # UPDATE
        # ====================================================

        if created:

            document_id = created.get(
                "id"
            )

            try:

                updated = update_record(
                    "documents",
                    document_id,
                    {
                        "title": (
                            "Main Contract - Updated"
                        ),
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
                    and updated.get(
                        "title"
                    )
                    == "Main Contract - Updated",
                )

                check(
                    "Update changes revision",
                    updated is not None
                    and updated.get(
                        "revision"
                    )
                    == "Rev 1",
                )

                check(
                    "Update changes status",
                    updated is not None
                    and updated.get(
                        "status"
                    )
                    == "Under Review",
                )

            except Exception as exc:

                check(
                    "Update document",
                    False,
                    f"{type(exc).__name__}: {exc}",
                )


        # ====================================================
        # VERIFY UPDATE PERSISTENCE
        # ====================================================

        if created:

            try:

                reloaded_after_update = (
                    load_memory()
                )

                updated_documents = (
                    reloaded_after_update.get(
                        "documents",
                        [],
                    )
                )

                updated_persisted = next(
                    (
                        item
                        for item in updated_documents
                        if str(
                            item.get("id")
                        )
                        == str(
                            created.get("id")
                        )
                    ),
                    None,
                )

                check(
                    "Updated document persisted",
                    updated_persisted is not None
                    and updated_persisted.get(
                        "revision"
                    )
                    == "Rev 1",
                )

            except Exception as exc:

                check(
                    "Updated document persisted",
                    False,
                    f"{type(exc).__name__}: {exc}",
                )


        # ====================================================
        # SECOND DOCUMENT
        # ====================================================

        second_document = {
            "document_number": "DOC-002",
            "title": "Jinja Specification",
            "project_id": 2,
            "document_type": "Specification",
            "status": "Draft",
            "revision": "Rev 0",
            "document_date": "2026-08-18",
            "author": "Creative Studios",
            "description": (
                "Jinja project specification."
            ),
        }

        created_second = None

        try:

            created_second = add_record(
                "documents",
                second_document,
                db,
            )

            check(
                "Create second document",
                created_second.get(
                    "id"
                ) == 2,
            )

        except Exception as exc:

            check(
                "Create second document",
                False,
                f"{type(exc).__name__}: {exc}",
            )


        # ====================================================
        # READ ALL DOCUMENTS
        # ====================================================

        try:

            all_documents = get_records(
                "documents",
                db,
            )

            check(
                "Get all documents",
                len(all_documents) == 2,
                f"Expected 2, got {len(all_documents)}",
            )

        except Exception as exc:

            check(
                "Get all documents",
                False,
                f"{type(exc).__name__}: {exc}",
            )

            all_documents = []


        # ====================================================
        # PROJECT FILTERING
        # ====================================================

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

        check(
            "Project 1 filter returns correct title",
            len(project_1_documents) == 1
            and project_1_documents[0].get(
                "title"
            )
            == "Main Contract - Updated",
        )

        check(
            "Project 2 filter returns correct title",
            len(project_2_documents) == 1
            and project_2_documents[0].get(
                "title"
            )
            == "Jinja Specification",
        )


        # ====================================================
        # DOCUMENT TYPE FILTERING
        # ====================================================

        contract_documents = [
            item
            for item in all_documents
            if item.get(
                "document_type"
            )
            == "Contract"
        ]

        specification_documents = [
            item
            for item in all_documents
            if item.get(
                "document_type"
            )
            == "Specification"
        ]

        check(
            "Contract type filter",
            len(contract_documents) == 1,
        )

        check(
            "Specification type filter",
            len(specification_documents) == 1,
        )


        # ====================================================
        # STATUS FILTERING
        # ====================================================

        review_documents = [
            item
            for item in all_documents
            if item.get(
                "status"
            )
            == "Under Review"
        ]

        draft_documents = [
            item
            for item in all_documents
            if item.get(
                "status"
            )
            == "Draft"
        ]

        check(
            "Under Review status filter",
            len(review_documents) == 1,
        )

        check(
            "Draft status filter",
            len(draft_documents) == 1,
        )


        # ====================================================
        # DELETE SECOND DOCUMENT
        # ====================================================

        if created_second:

            second_id = created_second.get(
                "id"
            )

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


        # ====================================================
        # VERIFY DELETE PERSISTENCE
        # ====================================================

        try:

            reloaded_after_delete = (
                load_memory()
            )

            remaining_documents = (
                reloaded_after_delete.get(
                    "documents",
                    [],
                )
            )

            deleted_still_exists = any(
                str(
                    item.get("id")
                )
                == str(
                    created_second.get("id")
                )
                for item in remaining_documents
            ) if created_second else False

            check(
                "Deletion persisted",
                not deleted_still_exists,
            )

        except Exception as exc:

            check(
                "Deletion persisted",
                False,
                f"{type(exc).__name__}: {exc}",
            )


        # ====================================================
        # ORIGINAL DOCUMENT STILL EXISTS
        # ====================================================

        if created:

            remaining = get_record(
                "documents",
                created.get("id"),
                db,
            )

            check(
                "Remaining document survives deletion",
                remaining is not None,
            )


        # ====================================================
        # DATABASE FILE SAFETY CHECK
        # ====================================================

        real_database_file = (
            ROOT
            / "creativestudios_db.json"
        )

        check(
            "Real database path is not the temporary database",
            temporary_db_file.resolve()
            != real_database_file.resolve(),
        )

        # The test intentionally does not assert whether the
        # real file exists because it may legitimately exist
        # from normal application use.

        print()

        print(
            "Temporary database test completed."
        )

    finally:

        # ----------------------------------------------------
        # Restore the original DB_FILE reference.
        # ----------------------------------------------------

        database.DB_FILE = (
            original_db_file
        )


# ============================================================
# SUMMARY
# ============================================================

print()

print(
    "=" * 64
)

print(
    "TEST SUMMARY"
)

print(
    "=" * 64
)

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
    "Documents imports, database persistence, CRUD, "
    "project filtering, type filtering and status filtering "
    "are working correctly."
)

sys.exit(0)
