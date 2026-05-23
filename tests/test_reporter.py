"""Tests for sqlsift.reporter (HTML report generation)."""

import os
import tempfile

import pytest

from sqlsift.diff import DiffResult
from sqlsift.reporter import generate_html, write_html_report


PASS_RESULT = DiffResult(
    columns=["id", "name"],
    added=[],
    removed=[],
    columns_match=True,
)

FAIL_RESULT = DiffResult(
    columns=["id", "name"],
    added=[{"id": 3, "name": "Carol"}],
    removed=[{"id": 1, "name": "Alice"}],
    columns_match=True,
)

COLUMN_MISMATCH = DiffResult(
    columns=[],
    added=[],
    removed=[],
    columns_match=False,
)


def test_generate_html_contains_doctype():
    html = generate_html(PASS_RESULT)
    assert "<!DOCTYPE html>" in html


def test_generate_html_pass_badge():
    html = generate_html(PASS_RESULT, title="my_query")
    assert "badge-pass" in html
    assert "PASS" in html


def test_generate_html_fail_badge():
    html = generate_html(FAIL_RESULT, title="regression_check")
    assert "badge-fail" in html
    assert "FAIL" in html


def test_generate_html_title_escaped():
    html = generate_html(PASS_RESULT, title="<script>alert(1)</script>")
    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_generate_html_added_row_highlighted():
    html = generate_html(FAIL_RESULT)
    assert 'class="added"' in html
    assert "Carol" in html


def test_generate_html_removed_row_highlighted():
    html = generate_html(FAIL_RESULT)
    assert 'class="removed"' in html
    assert "Alice" in html


def test_generate_html_no_differences_message():
    html = generate_html(PASS_RESULT)
    assert "No differences found" in html


def test_generate_html_column_mismatch_no_table_headers():
    html = generate_html(COLUMN_MISMATCH)
    assert "No columns to display" in html


def test_generate_html_custom_timestamp():
    ts = "2024-01-01 00:00:00 UTC"
    html = generate_html(PASS_RESULT, timestamp=ts)
    assert ts in html


def test_write_html_report_creates_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "report.html")
        write_html_report(FAIL_RESULT, path=path, title="env_diff")
        assert os.path.isfile(path)
        content = open(path, encoding="utf-8").read()
        assert "<!DOCTYPE html>" in content
        assert "env_diff" in content
