"""Unit tests for sqlsift.snapshot."""

import json
import os

import pytest

from sqlsift.snapshot import (
    SnapshotError,
    load_snapshot,
    load_snapshot_rows,
    save_snapshot,
)

SAMPLE_ROWS = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]


def test_save_and_load_roundtrip(tmp_path):
    path = str(tmp_path / "snap.json")
    save_snapshot(SAMPLE_ROWS, path, label="test", query="SELECT 1")
    payload = load_snapshot(path)
    assert payload["rows"] == SAMPLE_ROWS
    assert payload["label"] == "test"
    assert payload["query"] == "SELECT 1"
    assert "created_at" in payload
    assert payload["version"] == 1


def test_save_creates_parent_dirs(tmp_path):
    path = str(tmp_path / "nested" / "dir" / "snap.json")
    save_snapshot(SAMPLE_ROWS, path)
    assert os.path.exists(path)


def test_load_snapshot_rows_returns_list(tmp_path):
    path = str(tmp_path / "snap.json")
    save_snapshot(SAMPLE_ROWS, path)
    rows = load_snapshot_rows(path)
    assert rows == SAMPLE_ROWS


def test_load_snapshot_missing_file(tmp_path):
    with pytest.raises(SnapshotError, match="not found"):
        load_snapshot(str(tmp_path / "ghost.json"))


def test_load_snapshot_invalid_json(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("not json")
    with pytest.raises(SnapshotError, match="Cannot read"):
        load_snapshot(str(bad))


def test_load_snapshot_missing_rows_key(tmp_path):
    snap = tmp_path / "snap.json"
    snap.write_text(json.dumps({"version": 1}))
    with pytest.raises(SnapshotError, match="missing 'rows' key"):
        load_snapshot(str(snap))


def test_load_snapshot_rows_not_list(tmp_path):
    snap = tmp_path / "snap.json"
    snap.write_text(json.dumps({"rows": "oops"}))
    with pytest.raises(SnapshotError, match="must be a list"):
        load_snapshot(str(snap))


def test_save_snapshot_bad_path():
    with pytest.raises(SnapshotError, match="Cannot write"):
        save_snapshot(SAMPLE_ROWS, "/no_such_root/x/y/snap.json")
