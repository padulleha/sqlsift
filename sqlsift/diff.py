"""Core diffing logic for comparing query result sets."""

from dataclasses import dataclass, field
from typing import Any, List, Optional, Set, Tuple


Row = Tuple[Any, ...]


@dataclass
class DiffResult:
    """Holds the outcome of comparing two query result sets."""

    added: List[Row] = field(default_factory=list)       # rows in right but not left
    removed: List[Row] = field(default_factory=list)     # rows in left but not right
    common: List[Row] = field(default_factory=list)      # rows present in both
    left_columns: List[str] = field(default_factory=list)
    right_columns: List[str] = field(default_factory=list)
    column_mismatch: bool = False

    @property
    def is_equal(self) -> bool:
        """Return True when both result sets are identical."""
        return not self.column_mismatch and not self.added and not self.removed

    def summary(self) -> str:
        if self.column_mismatch:
            return (
                f"Column mismatch — left: {self.left_columns}, "
                f"right: {self.right_columns}"
            )
        parts = []
        if self.added:
            parts.append(f"+{len(self.added)} added")
        if self.removed:
            parts.append(f"-{len(self.removed)} removed")
        if not parts:
            return f"Identical ({len(self.common)} rows)"
        return ", ".join(parts) + f" (common: {len(self.common)})"


def diff_results(
    left_columns: List[str],
    left_rows: List[Row],
    right_columns: List[str],
    right_rows: List[Row],
    key_columns: Optional[List[str]] = None,
) -> DiffResult:
    """Compare two result sets and return a DiffResult.

    Args:
        left_columns: Column names from the *baseline* query.
        left_rows: Data rows from the baseline query.
        right_columns: Column names from the *target* query.
        right_rows: Data rows from the target query.
        key_columns: Optional subset of columns to use as a composite key.
                     When None, the entire row is used as the key.

    Returns:
        A populated DiffResult instance.
    """
    result = DiffResult(
        left_columns=left_columns,
        right_columns=right_columns,
    )

    if left_columns != right_columns:
        result.column_mismatch = True
        return result

    if key_columns:
        key_indices = [left_columns.index(c) for c in key_columns]
        left_keyed = {tuple(row[i] for i in key_indices): row for row in left_rows}
        right_keyed = {tuple(row[i] for i in key_indices): row for row in right_rows}
        left_keys: Set = set(left_keyed)
        right_keys: Set = set(right_keyed)
        result.removed = [left_keyed[k] for k in left_keys - right_keys]
        result.added = [right_keyed[k] for k in right_keys - left_keys]
        result.common = [left_keyed[k] for k in left_keys & right_keys]
    else:
        left_set: Set[Row] = set(map(tuple, left_rows))
        right_set: Set[Row] = set(map(tuple, right_rows))
        result.removed = list(left_set - right_set)
        result.added = list(right_set - left_set)
        result.common = list(left_set & right_set)

    return result
