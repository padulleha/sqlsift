"""Tests for sqlsift.watch and sqlsift.watch_cmd."""

import json
import os
import pytest
from unittest.mock import patch, MagicMock

from sqlsift.diff import DiffResult
from sqlsift.watch import watch, WatchError
from sqlsift.watch_cmd import build_watch_parser, run_watch_cmd


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _stable_result():
    return DiffResult(columns=["id"], added=[], removed=[], unchanged=[{"id": 1}])


def _changed_result():
    return DiffResult(columns=["id"], added=[{"id": 2}], removed=[{"id": 1}], unchanged=[])


@pytest.fixture()
def sqlite_config(tmp_path):
    db = tmp_path / "test.db"
    cfg = {
        "environments": {
            "prod": {"driver": "sqlite", "database": str(db)},
            "staging": {"driver": "sqlite", "database": str(db)},
        }
    }
    cfg_path = tmp_path / "config.json"
    cfg_path.write_text(json.dumps(cfg))
    return str(cfg_path), cfg


def _make_args(cfg_path, env_a="prod", env_b="staging", query="SELECT 1", interval=0.01, iterations=1):
    parser = build_watch_parser()
    return parser.parse_args([cfg_path, env_a, env_b, query, "--interval", str(interval), "--iterations", str(iterations)])


# ---------------------------------------------------------------------------
# watch() unit tests
# ---------------------------------------------------------------------------

def test_watch_stable_calls_on_stable():
    stable_calls = []
    with patch("sqlsift.watch.compare_environments", return_value=_stable_result()):
        watch(
            config={},
            env_a="a", env_b="b", query="SELECT 1",
            interval=0.001, max_iterations=2,
            on_stable=lambda r, i: stable_calls.append(i),
        )
    assert stable_calls == [1, 2]


def test_watch_changed_calls_on_change():
    change_calls = []
    with patch("sqlsift.watch.compare_environments", return_value=_changed_result()):
        watch(
            config={},
            env_a="a", env_b="b", query="SELECT 1",
            interval=0.001, max_iterations=1,
            on_change=lambda r, i: change_calls.append(i),
        )
    assert change_calls == [1]


def test_watch_invalid_interval_raises():
    with pytest.raises(WatchError, match="interval"):
        watch(config={}, env_a="a", env_b="b", query="q", interval=0)


def test_watch_query_failure_raises_watch_error():
    with patch("sqlsift.watch.compare_environments", side_effect=RuntimeError("db down")):
        with pytest.raises(WatchError, match="db down"):
            watch(config={}, env_a="a", env_b="b", query="q", interval=0.001, max_iterations=1)


# ---------------------------------------------------------------------------
# watch_cmd tests
# ---------------------------------------------------------------------------

def test_run_watch_cmd_stable(sqlite_config):
    cfg_path, _ = sqlite_config
    args = _make_args(cfg_path, iterations=1)
    with patch("sqlsift.watch_cmd.watch") as mock_watch:
        code = run_watch_cmd(args)
    assert code == 0
    mock_watch.assert_called_once()


def test_run_watch_cmd_bad_config(tmp_path):
    missing = str(tmp_path / "nope.json")
    args = _make_args(missing)
    code = run_watch_cmd(args)
    assert code == 1


def test_run_watch_cmd_bad_environment(sqlite_config):
    cfg_path, _ = sqlite_config
    args = _make_args(cfg_path, env_a="nonexistent")
    code = run_watch_cmd(args)
    assert code == 1


def test_run_watch_cmd_watch_error(sqlite_config):
    cfg_path, _ = sqlite_config
    args = _make_args(cfg_path, iterations=1)
    with patch("sqlsift.watch_cmd.watch", side_effect=WatchError("boom")):
        code = run_watch_cmd(args)
    assert code == 1
