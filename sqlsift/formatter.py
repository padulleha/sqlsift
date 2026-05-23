"""Formatters for rendering DiffResult output in various formats."""

from typing import List, Dict, Any
from sqlsift.diff import DiffResult


def format_text(result: DiffResult, show_unchanged: bool = False) -> str:
    """Format a DiffResult as a human-readable text report."""
    lines: List[str] = []

    if result.column_mismatch:
        lines.append("[COLUMN MISMATCH]")
        lines.append(f"  Expected columns: {result.expected_columns}")
        lines.append(f"  Actual columns:   {result.actual_columns}")
        return "\n".join(lines)

    status = "PASS" if result.is_equal else "FAIL"
    lines.append(f"[{status}] Diff Summary")
    lines.append(f"  Added rows:    {len(result.added_rows)}")
    lines.append(f"  Removed rows:  {len(result.removed_rows)}")
    lines.append(f"  Unchanged rows:{len(result.unchanged_rows)}")

    if result.added_rows:
        lines.append("\nAdded rows (+):")
        for row in result.added_rows:
            lines.append(f"  + {_format_row(row)}")

    if result.removed_rows:
        lines.append("\nRemoved rows (-):")
        for row in result.removed_rows:
            lines.append(f"  - {_format_row(row)}")

    if show_unchanged and result.unchanged_rows:
        lines.append("\nUnchanged rows (=):")
        for row in result.unchanged_rows:
            lines.append(f"  = {_format_row(row)}")

    return "\n".join(lines)


def format_json(result: DiffResult) -> Dict[str, Any]:
    """Format a DiffResult as a JSON-serializable dictionary."""
    return {
        "is_equal": result.is_equal,
        "column_mismatch": result.column_mismatch,
        "expected_columns": result.expected_columns,
        "actual_columns": result.actual_columns,
        "added_rows": result.added_rows,
        "removed_rows": result.removed_rows,
        "unchanged_row_count": len(result.unchanged_rows),
        "summary": {
            "added": len(result.added_rows),
            "removed": len(result.removed_rows),
            "unchanged": len(result.unchanged_rows),
        },
    }


def format_csv(result: DiffResult) -> str:
    """Format a DiffResult as CSV with a leading status column."""
    if result.column_mismatch:
        return "error,Column mismatch detected"

    lines: List[str] = []
    columns = result.expected_columns or []
    header = "status," + ",".join(columns)
    lines.append(header)

    for row in result.added_rows:
        lines.append("added," + _row_to_csv(row, columns))
    for row in result.removed_rows:
        lines.append("removed," + _row_to_csv(row, columns))
    for row in result.unchanged_rows:
        lines.append("unchanged," + _row_to_csv(row, columns))

    return "\n".join(lines)


def _format_row(row: Dict[str, Any]) -> str:
    return "  ".join(f"{k}={v}" for k, v in row.items())


def _row_to_csv(row: Dict[str, Any], columns: List[str]) -> str:
    return ",".join(str(row.get(col, "")) for col in columns)
