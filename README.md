# sqlsift

> Utility to diff query result sets across database environments for regression testing.

---

## Installation

```bash
pip install sqlsift
```

Or install from source:

```bash
git clone https://github.com/yourname/sqlsift.git && cd sqlsift && pip install -e .
```

---

## Usage

Define your query and target environments in a config file, then run `sqlsift` to compare result sets:

```yaml
# sqlsift.yml
query: "SELECT id, name, status FROM orders WHERE created_at > '2024-01-01'"
environments:
  production:
    url: postgresql://user:pass@prod-host/mydb
  staging:
    url: postgresql://user:pass@staging-host/mydb
```

```bash
sqlsift run --config sqlsift.yml
```

**Example output:**

```
Comparing production vs staging...

  Row diff: 2 rows differ, 0 missing, 1 extra in staging

  ~ id=1042  status: "active" → "pending"
  ~ id=1087  name: "Acme Corp" → "ACME CORP"
  + id=2201  [only in staging]

Summary: 3 differences found.
```

You can also run comparisons directly from the CLI without a config file:

```bash
sqlsift diff \
  --source "postgresql://user:pass@prod/db" \
  --target "postgresql://user:pass@staging/db" \
  --query "SELECT * FROM users LIMIT 100"
```

---

## License

This project is licensed under the [MIT License](LICENSE).