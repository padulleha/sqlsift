"""Tests for sqlsift.connector."""

from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

import pytest

from sqlsift.connector import ConnectorError, get_connection, run_query


@pytest.fixture()
def sqlite_db(tmp_path: Path) -> Path:
    """Create a small SQLite database and return its path."""
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE users (id INTEGER, name TEXT, age INTEGER)")
    conn.executemany(
        "INSERT INTO users VALUES (?, ?, ?)",
        [(1, "Alice", 30), (2, "Bob", 25), (3, "Carol", 35)],
    )
    conn.commit()
    conn.close()
    return db_path


def test_get_connection_sqlite(sqlite_db: Path):
    conn = get_connection("sqlite", str(sqlite_db))
    assert conn is not None
    conn.close()


def test_get_connection_unsupported_driver():
    with pytest.raises(ConnectorError, match="Unsupported driver"):
        get_connection("postgres", "host=localhost dbname=mydb")


def test_get_connection_bad_path():
    with pytest.raises(ConnectorError, match="Cannot connect"):
        get_connection("sqlite", "/nonexistent/path/db.sqlite")


def test_run_query_returns_dicts(sqlite_db: Path):
    rows = run_query("sqlite", str(sqlite_db), "SELECT id, name FROM users ORDER BY id")
    assert len(rows) == 3
    assert rows[0] == {"id": 1, "name": "Alice"}
    assert rows[2] == {"id": 3, "name": "Carol"}


def test_run_query_empty_result(sqlite_db: Path):
    rows = run_query("sqlite", str(sqlite_db), "SELECT * FROM users WHERE id = 999")
    assert rows == []


def test_run_query_invalid_sql(sqlite_db: Path):
    with pytest.raises(ConnectorError, match="Query failed"):
        run_query("sqlite", str(sqlite_db), "SELECT * FROM nonexistent_table")


def test_run_query_in_memory():
    rows = run_query("sqlite", ":memory:", "SELECT 42 AS answer")
    assert rows == [{"answer": 42}]
