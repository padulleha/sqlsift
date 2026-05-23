"""Configuration loader for sqlsift.

Supports YAML / JSON config files that describe one or more named
environments, each with a driver, DSN, and optional default query.

Example config (YAML)::

    environments:
      prod:
        driver: sqlite
        dsn: /data/prod.db
      staging:
        driver: sqlite
        dsn: /data/staging.db
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False


class ConfigError(Exception):
    """Raised when the config file is invalid or missing."""


def _load_raw(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix in (".yaml", ".yml"):
        if not _YAML_AVAILABLE:
            raise ConfigError("PyYAML is required to load YAML config files")
        return yaml.safe_load(text) or {}
    if path.suffix == ".json":
        return json.loads(text)
    raise ConfigError(f"Unsupported config file format: '{path.suffix}'")


def load_config(path: str | Path) -> dict[str, Any]:
    """Load and validate a sqlsift config file.

    Returns the parsed config dict with an ``'environments'`` key.
    """
    p = Path(path)
    if not p.exists():
        raise ConfigError(f"Config file not found: '{p}'")
    raw = _load_raw(p)
    if "environments" not in raw or not isinstance(raw["environments"], dict):
        raise ConfigError("Config must contain an 'environments' mapping")
    for name, env in raw["environments"].items():
        for required in ("driver", "dsn"):
            if required not in env:
                raise ConfigError(
                    f"Environment '{name}' is missing required key '{required}'"
                )
    return raw


def get_environment(config: dict[str, Any], name: str) -> dict[str, Any]:
    """Return the environment config dict for *name*."""
    envs = config.get("environments", {})
    if name not in envs:
        available = ", ".join(envs.keys()) or "(none)"
        raise ConfigError(
            f"Unknown environment '{name}'. Available: {available}"
        )
    return envs[name]
