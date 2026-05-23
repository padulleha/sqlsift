"""Tests for sqlsift.report_cmd CLI sub-command."""

import json
import os
import sqlite3
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from sqlsift.diff import DiffResult
from sqlsift.report_cmd import run_report_cmd


def _make_args(**kwargs):
    defaults = dict(
        config="cfg.json",
        source="dev",
        target="prod",
        query="SELECT 1",
        output="out.html",
        title=None,
    )
    defaults.update(kwargs)
    ns = MagicMock()
    for k, v in defaults.items():
        setattr(ns, k, v)
    return ns


@pytest.fixture()
def sqlite_config(tmp_path):
    db_path = str(tmp_path / "test.db")
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE t (id INTEGER, name TEXT)")
    conn.execute("INSERT INTO t VALUES (1, 'Alice')")
    conn.commit()
    conn.close()

    cfg = {
        "environments": {
            "dev": {"driver": "sqlite", "database": db_path},
            "prod": {"driver": "sqlite", "database": db_path},
        }
    }
    cfg_path = str(tmp_path / "config.json")
    with open(cfg_path, "w") as f:
        json.dump(cfg, f)
    return cfg_path, db_path


def test_run_report_cmd_creates_html(sqlite_config, tmp_path):
    cfg_path, _ = sqlite_config
    out_path = str(tmp_path / "report.html")
    args = _make_args(config=cfg_path, source="dev", target="prod",
                      query="SELECT id, name FROM t", output=out_path)
    rc = run_report_cmd(args)
    assert rc == 0
    assert os.path.isfile(out_path)
    assert "<!DOCTYPE html>" in open(out_path).read()


def test_run_report_cmd_bad_config(tmp_path):
    args = _make_args(config=str(tmp_path / "nonexistent.json"))
    rc = run_report_cmd(args)
    assert rc == 1


def test_run_report_cmd_bad_environment(tmp_path):
    cfg = {"environments": {"dev": {"driver": "sqlite", "database": ":memory:"}}}
    cfg_path = str(tmp_path / "c.json")
    with open(cfg_path, "w") as f:
        json.dump(cfg, f)
    args = _make_args(config=cfg_path, source="dev", target="missing")
    rc = run_report_cmd(args)
    assert rc == 1


def test_run_report_cmd_diff_found_returns_2(sqlite_config, tmp_path):
    cfg_path, db_path = sqlite_config
    # Create a second db with different data
    db2 = str(tmp_path / "prod.db")
    conn2 = sqlite3.connect(db2)
    conn2.execute("CREATE TABLE t (id INTEGER, name TEXT)")
    conn2.execute("INSERT INTO t VALUES (2, 'Bob')")
    conn2.commit()
    conn2.close()

    cfg = {
        "environments": {
            "dev": {"driver": "sqlite", "database": db_path},
            "prod": {"driver": "sqlite", "database": db2},
        }
    }
    cfg_path2 = str(tmp_path / "cfg2.json")
    with open(cfg_path2, "w") as f:
        json.dump(cfg, f)

    out_path = str(tmp_path / "report2.html")
    args = _make_args(config=cfg_path2, source="dev", target="prod",
                      query="SELECT id, name FROM t", output=out_path)
    rc = run_report_cmd(args)
    assert rc == 2
    assert os.path.isfile(out_path)
