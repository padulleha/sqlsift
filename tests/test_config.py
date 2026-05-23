"""Tests for sqlsift.config."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sqlsift.config import ConfigError, get_environment, load_config


MINIMAL_CONFIG = {
    "environments": {
        "prod": {"driver": "sqlite", "dsn": "/data/prod.db"},
        "staging": {"driver": "sqlite", "dsn": "/data/staging.db"},
    }
}


@pytest.fixture()
def config_file(tmp_path: Path) -> Path:
    p = tmp_path / "sqlsift.json"
    p.write_text(json.dumps(MINIMAL_CONFIG), encoding="utf-8")
    return p


def test_load_config_json(config_file: Path):
    cfg = load_config(config_file)
    assert "environments" in cfg
    assert "prod" in cfg["environments"]


def test_load_config_missing_file(tmp_path: Path):
    with pytest.raises(ConfigError, match="not found"):
        load_config(tmp_path / "missing.json")


def test_load_config_unsupported_format(tmp_path: Path):
    p = tmp_path / "config.toml"
    p.write_text("[environments]\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="Unsupported config file format"):
        load_config(p)


def test_load_config_missing_environments_key(tmp_path: Path):
    p = tmp_path / "bad.json"
    p.write_text(json.dumps({"foo": "bar"}), encoding="utf-8")
    with pytest.raises(ConfigError, match="'environments'"):
        load_config(p)


def test_load_config_env_missing_dsn(tmp_path: Path):
    bad = {"environments": {"prod": {"driver": "sqlite"}}}
    p = tmp_path / "bad.json"
    p.write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(ConfigError, match="missing required key 'dsn'"):
        load_config(p)


def test_get_environment_known(config_file: Path):
    cfg = load_config(config_file)
    env = get_environment(cfg, "prod")
    assert env["driver"] == "sqlite"
    assert env["dsn"] == "/data/prod.db"


def test_get_environment_unknown(config_file: Path):
    cfg = load_config(config_file)
    with pytest.raises(ConfigError, match="Unknown environment 'dev'"):
        get_environment(cfg, "dev")
