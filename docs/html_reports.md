# HTML Reports

`sqlsift` can generate self-contained HTML diff reports for easy visual review of query result-set differences across environments.

## Quick Start

```bash
# Using the report sub-command directly:
python -m sqlsift.report_cmd \
  --config config.json \
  --source dev \
  --target prod \
  --query "SELECT id, name, status FROM orders ORDER BY id" \
  --output diff_report.html \
  --title "Orders table regression"
```

Open `diff_report.html` in any browser — no external dependencies required.

## Exit Codes

| Code | Meaning |
|------|---------|
| `0`  | Environments match — no differences found. |
| `1`  | Configuration or connection error. |
| `2`  | Diff found — rows were added or removed. |

## Python API

```python
from sqlsift.diff import diff_results
from sqlsift.reporter import generate_html, write_html_report

src_rows = [{"id": 1, "name": "Alice"}]
tgt_rows = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]

result = diff_results(src_rows, tgt_rows)

# Get HTML string
html = generate_html(result, title="my query")

# Or write directly to a file
write_html_report(result, path="report.html", title="my query")
```

## Report Anatomy

- **Green rows** (`+`) — rows present in the *target* but not the *source*.
- **Red rows** (`-`) — rows present in the *source* but not the *target*.
- A **PASS** badge is shown when both environments return identical result sets.
- A **FAIL** badge is shown when differences or column mismatches are detected.

## Configuration File

The report command uses the same `config.json` format as the rest of `sqlsift`:

```json
{
  "environments": {
    "dev":  { "driver": "sqlite", "database": "dev.db" },
    "prod": { "driver": "postgresql", "host": "db.prod.example.com",
              "port": 5432, "database": "app", "user": "ro", "password": "s3cr3t" }
  }
}
```
