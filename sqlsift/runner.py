"""High-level runner that ties config, connector, and diff together.

Typical usage::

    from sqlsift.runner import compare_environments

    result = compare_environments(
        config_path="sqlsift.json",
        env_a="prod",
        env_b="staging",
        sql="SELECT id, name FROM users ORDER BY id",
    )
    print(result.summary())
"""

from __future__ import annotations

from typing import Any

from sqlsift.config import get_environment, load_config
from sqlsift.connector import run_query
from sqlsift.diff import DiffResult, diff_results


def compare_environments(
    config_path: str,
    env_a: str,
    env_b: str,
    sql: str,
) -> DiffResult:
    """Run *sql* against two named environments and return a :class:`DiffResult`.

    Parameters
    ----------
    config_path:
        Path to the sqlsift JSON/YAML config file.
    env_a:
        Name of the baseline environment ("left" side of the diff).
    env_b:
        Name of the comparison environment ("right" side of the diff).
    sql:
        Query to execute in both environments.
    """
    config = load_config(config_path)
    cfg_a = get_environment(config, env_a)
    cfg_b = get_environment(config, env_b)

    rows_a = run_query(cfg_a["driver"], cfg_a["dsn"], sql)
    rows_b = run_query(cfg_b["driver"], cfg_b["dsn"], sql)

    return diff_results(rows_a, rows_b)


def compare_raw(
    driver_a: str,
    dsn_a: str,
    driver_b: str,
    dsn_b: str,
    sql: str,
) -> DiffResult:
    """Run *sql* against two explicitly specified connections and diff the results.

    Useful when no config file is available (e.g. in tests or scripts).
    """
    rows_a = run_query(driver_a, dsn_a, sql)
    rows_b = run_query(driver_b, dsn_b, sql)
    return diff_results(rows_a, rows_b)
