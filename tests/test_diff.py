"""Unit tests for sqlsift.diff module."""

import pytest
from sqlsift.diff import diff_results, DiffResult


COLS = ["id", "name", "value"]


def test_identical_result_sets():
    rows = [(1, "alice", 10), (2, "bob", 20)]
    result = diff_results(COLS, rows, COLS, rows)
    assert result.is_equal
    assert len(result.common) == 2
    assert result.summary().startswith("Identical")


def test_added_rows():
    left = [(1, "alice", 10)]
    right = [(1, "alice", 10), (2, "bob", 20)]
    result = diff_results(COLS, left, COLS, right)
    assert not result.is_equal
    assert len(result.added) == 1
    assert len(result.removed) == 0
    assert (2, "bob", 20) in result.added


def test_removed_rows():
    left = [(1, "alice", 10), (2, "bob", 20)]
    right = [(1, "alice", 10)]
    result = diff_results(COLS, left, COLS, right)
    assert not result.is_equal
    assert len(result.removed) == 1
    assert len(result.added) == 0


def test_column_mismatch():
    left_cols = ["id", "name"]
    right_cols = ["id", "email"]
    result = diff_results(left_cols, [], right_cols, [])
    assert result.column_mismatch
    assert not result.is_equal
    assert "mismatch" in result.summary().lower()


def test_empty_result_sets():
    result = diff_results(COLS, [], COLS, [])
    assert result.is_equal
    assert len(result.common) == 0


def test_key_columns_detects_update_as_add_remove():
    left = [(1, "alice", 10)]
    right = [(1, "alice", 99)]  # same key, different value
    result = diff_results(COLS, left, COLS, right, key_columns=["id"])
    # key exists in both, so it lands in common (key-based match)
    assert len(result.common) == 1
    assert len(result.added) == 0
    assert len(result.removed) == 0


def test_key_columns_missing_key():
    left = [(1, "alice", 10), (2, "bob", 20)]
    right = [(1, "alice", 10)]
    result = diff_results(COLS, left, COLS, right, key_columns=["id"])
    assert len(result.removed) == 1
    assert len(result.common) == 1


def test_summary_shows_counts():
    left = [(1, "a", 1), (2, "b", 2)]
    right = [(1, "a", 1), (3, "c", 3)]
    result = diff_results(COLS, left, COLS, right)
    summary = result.summary()
    assert "+1 added" in summary
    assert "-1 removed" in summary
