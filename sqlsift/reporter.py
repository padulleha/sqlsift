"""HTML report generation for sqlsift diff results."""

from __future__ import annotations

import html
from datetime import datetime
from typing import Optional

from sqlsift.diff import DiffResult

_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>sqlsift Report — {title}</title>
  <style>
    body {{ font-family: monospace; margin: 2rem; background: #fafafa; }}
    h1 {{ color: #333; }}
    .meta {{ color: #666; font-size: 0.9rem; margin-bottom: 1rem; }}
    .badge-pass {{ background:#2ecc71;color:#fff;padding:2px 8px;border-radius:4px; }}
    .badge-fail {{ background:#e74c3c;color:#fff;padding:2px 8px;border-radius:4px; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; }}
    th {{ background: #34495e; color: #fff; padding: 6px 10px; text-align: left; }}
    td {{ padding: 5px 10px; border-bottom: 1px solid #ddd; }}
    .added {{ background: #d4efdf; }}
    .removed {{ background: #fadbd8; }}
    .unchanged {{ background: #fff; }}
  </style>
</head>
<body>
  <h1>sqlsift Diff Report</h1>
  <div class="meta">
    <strong>Query:</strong> {title}<br>
    <strong>Generated:</strong> {timestamp}<br>
    <strong>Status:</strong> {badge}
  </div>
  <p>{summary}</p>
  {table}
</body>
</html>
"""


def _badge(passed: bool) -> str:
    cls = "badge-pass" if passed else "badge-fail"
    label = "PASS" if passed else "FAIL"
    return f'<span class="{cls}">{label}</span>'


def _build_table(result: DiffResult) -> str:
    if not result.columns:
        return "<p><em>No columns to display.</em></p>"

    headers = "".join(f"<th>{html.escape(c)}</th>" for c in result.columns)
    rows_html: list[str] = []

    for row in result.added:
        cells = "".join(f"<td>{html.escape(str(row.get(c, '')))}</td>" for c in result.columns)
        rows_html.append(f'<tr class="added"><td>+</td>{cells}</tr>')

    for row in result.removed:
        cells = "".join(f"<td>{html.escape(str(row.get(c, '')))}</td>" for c in result.columns)
        rows_html.append(f'<tr class="removed"><td>-</td>{cells}</tr>')

    if not rows_html:
        rows_html.append('<tr class="unchanged"><td colspan="100%"><em>No differences found.</em></td></tr>')

    body = "\n".join(rows_html)
    return (
        f"<table><thead><tr><th>#</th>{headers}</tr></thead>"
        f"<tbody>{body}</tbody></table>"
    )


def generate_html(
    result: DiffResult,
    title: str = "query",
    timestamp: Optional[str] = None,
) -> str:
    """Return a complete HTML report for *result*."""
    if timestamp is None:
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    from sqlsift.diff import summary as diff_summary

    passed = result.columns_match and not result.added and not result.removed
    return _HTML_TEMPLATE.format(
        title=html.escape(title),
        timestamp=timestamp,
        badge=_badge(passed),
        summary=html.escape(diff_summary(result)),
        table=_build_table(result),
    )


def write_html_report(
    result: DiffResult,
    path: str,
    title: str = "query",
) -> None:
    """Write an HTML report to *path*."""
    content = generate_html(result, title=title)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
