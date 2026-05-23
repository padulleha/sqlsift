"""Tests for sqlsift.formatter module."""

import json
import pytest
from sqlsift.diff import diff_results
from sqlsift.formatter import format_text, format_json, format_csv


ROWS_A = [
    {"id": 1, "name": "Alice", "score": 95},
    {"id": 2, "name": "Bob", "score": 80},
]

ROWS_B = [
    {"id": 1, "name": "Alice", "score": 95},
    {"id": 3, "name": "Carol", "score": 88},
]


def test_format_text_pass():
    result = diff_results(ROWS_A, ROWS_A)
    output = format_text(result)
    assert "[PASS]" in output
    assert "Added rows:    0" in output
    assert "Removed rows:  0" in output


def test_format_text_fail():
    result = diff_results(ROWS_A, ROWS_B)
    output = format_text(result)
    assert "[FAIL]" in output
    assert "Added rows:    1" in output
    assert "Removed rows:  1" in output
    assert "Carol" in output
    assert "Bob" in output


def test_format_text_column_mismatch():
    cols_a = [{"id": 1}]
    cols_b = [{"id": 1, "extra": "x"}]
    result = diff_results(cols_a, cols_b)
    output = format_text(result)
    assert "COLUMN MISMATCH" in output


def test_format_text_show_unchanged():
    result = diff_results(ROWS_A, ROWS_B)
    output = format_text(result, show_unchanged=True)
    assert "Unchanged rows" in output
    assert "Alice" in output


def test_format_json_structure():
    result = diff_results(ROWS_A, ROWS_B)
    output = format_json(result)
    assert "is_equal" in output
    assert "added_rows" in output
    assert "removed_rows" in output
    assert "summary" in output
    assert output["summary"]["added"] == 1
    assert output["summary"]["removed"] == 1
    assert output["is_equal"] is False


def test_format_json_serializable():
    result = diff_results(ROWS_A, ROWS_A)
    output = format_json(result)
    # Should not raise
    serialized = json.dumps(output)
    assert "is_equal" in serialized


def test_format_csv_header():
    result = diff_results(ROWS_A, ROWS_B)
    output = format_csv(result)
    lines = output.strip().split("\n")
    assert lines[0].startswith("status,")
    assert "id" in lines[0]
    assert "name" in lines[0]


def test_format_csv_rows():
    result = diff_results(ROWS_A, ROWS_B)
    output = format_csv(result)
    assert "added" in output
    assert "removed" in output
    assert "unchanged" in output


def test_format_csv_column_mismatch():
    cols_a = [{"id": 1}]
    cols_b = [{"id": 1, "extra": "x"}]
    result = diff_results(cols_a, cols_b)
    output = format_csv(result)
    assert "error" in output
