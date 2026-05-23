# Snapshots

The `snapshot` command captures a query result set from a live database and
persists it to a JSON file on disk. Snapshots can later be compared with
`sqlsift diff` or used as a baseline for regression testing without requiring
a live database connection.

## Usage

```bash
sqlsift snapshot \
  --config config.json \
  --env production \
  --query "SELECT id, status, total FROM orders ORDER BY id" \
  --output snapshots/orders_prod_2024-06-01.json \
  --label "pre-migration baseline"
```

### Options

| Flag | Required | Description |
|------|----------|-------------|
| `--config` | Yes | Path to your sqlsift config file |
| `--env` | Yes | Environment name defined in the config |
| `--query` | Yes | SQL query whose results will be captured |
| `--output` | Yes | Destination `.json` file for the snapshot |
| `--label` | No | Human-readable tag stored inside the file |

## Snapshot file format

Each snapshot is a self-describing JSON document:

```json
{
  "version": 1,
  "created_at": "2024-06-01T12:00:00+00:00",
  "label": "pre-migration baseline",
  "query": "SELECT id, status, total FROM orders ORDER BY id",
  "rows": [
    {"id": 1, "status": "shipped", "total": 99.99},
    {"id": 2, "status": "pending", "total": 14.50}
  ]
}
```

## Using snapshots in comparisons

Load a snapshot as the *baseline* side when running `sqlsift diff`:

```bash
sqlsift diff \
  --baseline snapshots/orders_prod_2024-06-01.json \
  --current  snapshots/orders_prod_2024-06-02.json
```

Or compare a snapshot against a live query result by passing the snapshot
path to `--baseline` while supplying `--config` / `--env` / `--query` for
the current side.

## Python API

```python
from sqlsift.snapshot import save_snapshot, load_snapshot_rows

# Save
save_snapshot(rows, "snap.json", label="v1", query="SELECT ...")

# Load
rows = load_snapshot_rows("snap.json")
```
