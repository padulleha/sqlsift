"""Integration tests for sqlsift.snapshot_cmd."""

import json
import sqlite3

import pytest

from sqlsift.snapshot_cmd import build_snapshot_parser, run_snapshot_cmd


@pytest.fixture()
def sqlite_config(tmp_path):
    """Write a minimal config + SQLite DB, return (config_path, db_path)."""
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE users (id INTEGER, name TEXT)")
    conn.execute("INSERT INTO users VALUES (1, 'Alice'), (2, 'Bob')")
    conn.commit()
    conn.close()

    config = {
        "environments": {
            "dev": {"driver": "sqlite", "database": str(db_path)}
        }
    }
    cfg_path = tmp_path / "config.json"
    cfg_path.write_text(json.dumps(config))
    return str(cfg_path), str(db_path)


def _make_args(config, env, query, output, label=""):
    parser = build_snapshot_parser()
    return parser.parse_args(
        ["--config", config, "--env", env, "--query", query, "--output", output, "--label", label]
    )


def test_run_snapshot_cmd_creates_file(sqlite_config, tmp_path):
    cfg_path, _ = sqlite_config
    out = str(tmp_path / "snap.json")
    args = _make_args(cfg_path, "dev", "SELECT * FROM users", out, label="ci")
    rc = run_snapshot_cmd(args)
    assert rc == 0
    with open(out) as fh:
        payload = json.load(fh)
    assert len(payload["rows"]) == 2
    assert payload["label"] == "ci"


def test_run_snapshot_cmd_bad_config(tmp_path):
    out = str(tmp_path / "snap.json")
    args = _make_args(str(tmp_path / "missing.json"), "dev", "SELECT 1", out)
    rc = run_snapshot_cmd(args)
    assert rc == 1


def test_run_snapshot_cmd_bad_environment(sqlite_config, tmp_path):
    cfg_path, _ = sqlite_config
    out = str(tmp_path / "snap.json")
    args = _make_args(cfg_path, "prod", "SELECT 1", out)
    rc = run_snapshot_cmd(args)
    assert rc == 1


def test_run_snapshot_cmd_bad_output(sqlite_config):
    cfg_path, _ = sqlite_config
    args = _make_args(cfg_path, "dev", "SELECT * FROM users", "/no_root/x/snap.json")
    rc = run_snapshot_cmd(args)
    assert rc == 1
