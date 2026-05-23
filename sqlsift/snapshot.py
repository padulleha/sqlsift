"""Snapshot management: save and load query result sets to/from disk."""

import json
import os
from datetime import datetime, timezone
from typing import Any

SNAPSHOT_VERSION = 1


class SnapshotError(Exception):
    """Raised when a snapshot operation fails."""


def save_snapshot(
    rows: list[dict[str, Any]],
    path: str,
    label: str = "",
    query: str = "",
) -> None:
    """Persist *rows* to *path* as a JSON snapshot file."""
    payload = {
        "version": SNAPSHOT_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "label": label,
        "query": query,
        "rows": rows,
    }
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, default=str)
    except OSError as exc:
        raise SnapshotError(f"Cannot write snapshot to '{path}': {exc}") from exc


def load_snapshot(path: str) -> dict[str, Any]:
    """Load and validate a snapshot file, returning its full payload dict."""
    if not os.path.exists(path):
        raise SnapshotError(f"Snapshot file not found: '{path}'")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        raise SnapshotError(f"Cannot read snapshot '{path}': {exc}") from exc

    if "rows" not in payload:
        raise SnapshotError(f"Invalid snapshot '{path}': missing 'rows' key")
    if not isinstance(payload["rows"], list):
        raise SnapshotError(f"Invalid snapshot '{path}': 'rows' must be a list")
    return payload


def load_snapshot_rows(path: str) -> list[dict[str, Any]]:
    """Convenience wrapper — returns only the rows list from a snapshot."""
    return load_snapshot(path)["rows"]
