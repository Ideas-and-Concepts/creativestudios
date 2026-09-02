from pathlib import Path

import pytest

from modules import database


class FakeCursor:
    def __init__(self, row=None):
        self.row = row
        self.executed = []

    def execute(self, query, params=None):
        self.executed.append((query, params))

    def fetchone(self):
        return self.row

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeConnection:
    def __init__(self, row=None):
        self.cursor_obj = FakeCursor(row)
        self.committed = False

    def cursor(self):
        return self.cursor_obj

    def commit(self):
        self.committed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_without_database_url_uses_json(monkeypatch, tmp_path: Path):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr(database, "DB_FILE", tmp_path / "workspace.json")

    assert database.database_backend() == "json"
    loaded = database.load_memory()

    assert loaded["projects"] == []
    assert (tmp_path / "workspace.json").exists()


def test_neon_failure_does_not_fallback_to_json(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("DATABASE_URL", "postgresql://test")
    monkeypatch.setattr(database, "DB_FILE", tmp_path / "workspace.json")

    stale = {"projects": [{"id": 99, "name": "STALE LOCAL COPY"}]}
    database._save_json(stale)

    def fail_connect():
        raise RuntimeError("simulated Neon outage")

    monkeypatch.setattr(database, "_neon_connect", fail_connect)

    with pytest.raises(RuntimeError, match="simulated Neon outage"):
        database.load_memory()


def test_successful_neon_load_updates_local_backup(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("DATABASE_URL", "postgresql://test")
    monkeypatch.setattr(database, "DB_FILE", tmp_path / "workspace.json")

    remote = {"projects": [{"id": 7, "name": "Remote Project"}]}
    connection = FakeConnection(row=(remote,))
    monkeypatch.setattr(database, "_neon_connect", lambda: connection)

    loaded = database.load_memory()

    assert loaded["projects"][0]["id"] == 7
    assert database.load_memory.__name__ == "load_memory"
    backup = database._load_json_file()
    assert backup["projects"][0]["name"] == "Remote Project"


def test_neon_save_failure_raises(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("DATABASE_URL", "postgresql://test")
    monkeypatch.setattr(database, "DB_FILE", tmp_path / "workspace.json")

    def fail_connect():
        raise RuntimeError("simulated Neon write outage")

    monkeypatch.setattr(database, "_neon_connect", fail_connect)

    with pytest.raises(RuntimeError, match="simulated Neon write outage"):
        database.save_memory({"projects": [{"id": 1, "name": "Project"}]})

    assert not (tmp_path / "workspace.json").exists()


def test_successful_neon_save_commits_and_creates_backup(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("DATABASE_URL", "postgresql://test")
    monkeypatch.setattr(database, "DB_FILE", tmp_path / "workspace.json")

    connection = FakeConnection()
    monkeypatch.setattr(database, "_neon_connect", lambda: connection)

    assert database.save_memory({"projects": [{"id": 1, "name": "Project"}]})
    assert connection.committed
    assert database._load_json_file()["projects"][0]["name"] == "Project"
