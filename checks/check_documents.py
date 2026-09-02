"""Creative Studios documents module smoke test."""

from __future__ import annotations

import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    import modules.database as database
    from modules.documents import render_documents_module

    if not callable(render_documents_module):
        print("Documents renderer is not callable.")
        return 1

    original_db_file = database.DB_FILE

    with TemporaryDirectory(prefix="creativestudios_documents_") as temp_dir:
        database.DB_FILE = Path(temp_dir) / "database.json"
        try:
            db = database.initialize_database()
            if not isinstance(db.get("documents"), list):
                print("Documents collection is invalid.")
                return 1

            document = database.add_record(
                "documents",
                {
                    "document_number": "DOC-001",
                    "title": "Main Contract",
                    "project_id": 1,
                    "document_type": "Contract",
                    "status": "Active",
                    "revision": "Rev 0",
                },
                db,
            )

            assert database.get_record("documents", document["id"], db) is not None

            updated = database.update_record(
                "documents",
                document["id"],
                {"revision": "Rev 1", "status": "Under Review"},
                db,
            )
            assert updated is not None
            assert updated["revision"] == "Rev 1"

            assert database.delete_record("documents", document["id"], db) is True
            assert database.get_record("documents", document["id"], db) is None
            assert database.save_memory(db) is True

        finally:
            database.DB_FILE = original_db_file

    print("Documents smoke test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
