"""Database connector module for sqlsift.

Provides a unified interface to execute queries against different
database backends and return results as lists of row dicts.
"""

from __future__ import annotations

from typing import Any

try:
    import sqlite3
except ImportError:  # pragma: no cover
    sqlite3 = None  # type: ignore


SUPPORTED_DRIVERS = ("sqlite",)


class ConnectorError(Exception):
    """Raised when a connection or query error occurs."""


def _connect_sqlite(dsn: str):
    """Return a sqlite3 connection for *dsn* (a file path or ':memory:')."""
    if sqlite3 is None:  # pragma: no cover
        raise ConnectorError("sqlite3 module is not available")
    try:
        conn = sqlite3.connect(dsn)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.OperationalError as exc:
        raise ConnectorError(f"Cannot connect to SQLite database '{dsn}': {exc}") from exc


def get_connection(driver: str, dsn: str) -> Any:
    """Return a DB-API 2 connection for the given *driver* and *dsn*.

    Parameters
    ----------
    driver:
        One of the supported driver names (e.g. ``"sqlite"``)..
    dsn:
        Driver-specific connection string.
    """
    if driver == "sqlite":
        return _connect_sqlite(dsn)
    raise ConnectorError(
        f"Unsupported driver '{driver}'. Supported: {SUPPORTED_DRIVERS}"
    )


def run_query(driver: str, dsn: str, sql: str) -> list[dict[str, Any]]:
    """Execute *sql* and return results as a list of column-keyed dicts.

    Parameters
    ----------
    driver:
        Database driver name.
    dsn:
        Connection string / path.
    sql:
        SQL query to execute.
    """
    conn = get_connection(driver, dsn)
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        columns = [desc[0] for desc in cursor.description or []]
        rows = [{col: val for col, val in zip(columns, row)} for row in cursor.fetchall()]
        return rows
    except Exception as exc:
        raise ConnectorError(f"Query failed: {exc}") from exc
    finally:
        conn.close()
