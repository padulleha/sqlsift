"""CLI sub-command: sqlsift snapshot — capture a query result set to disk."""

import argparse
import sys

from sqlsift.config import ConfigError, get_environment, load_config
from sqlsift.connector import ConnectorError, get_connection, run_query
from sqlsift.snapshot import SnapshotError, save_snapshot


def build_snapshot_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    kwargs: dict = dict(
        description="Run a SQL query and save the results as a snapshot file."
    )
    if parent is not None:
        parser = parent.add_parser("snapshot", **kwargs)
    else:
        parser = argparse.ArgumentParser(prog="sqlsift snapshot", **kwargs)

    parser.add_argument("--config", required=True, help="Path to sqlsift config file")
    parser.add_argument("--env", required=True, help="Environment name from config")
    parser.add_argument("--query", required=True, help="SQL query to execute")
    parser.add_argument("--output", required=True, help="Destination snapshot file (.json)")
    parser.add_argument("--label", default="", help="Optional human-readable label")
    return parser


def run_snapshot_cmd(args: argparse.Namespace) -> int:
    """Execute the snapshot sub-command. Returns exit code."""
    try:
        cfg = load_config(args.config)
        env = get_environment(cfg, args.env)
    except ConfigError as exc:
        print(f"Config error: {exc}", file=sys.stderr)
        return 1

    try:
        conn = get_connection(env)
        rows = run_query(conn, args.query)
        conn.close()
    except ConnectorError as exc:
        print(f"Connection error: {exc}", file=sys.stderr)
        return 1

    try:
        save_snapshot(rows, args.output, label=args.label, query=args.query)
    except SnapshotError as exc:
        print(f"Snapshot error: {exc}", file=sys.stderr)
        return 1

    print(f"Snapshot saved: {args.output} ({len(rows)} row(s))")
    return 0


def main() -> None:  # pragma: no cover
    parser = build_snapshot_parser()
    sys.exit(run_snapshot_cmd(parser.parse_args()))


if __name__ == "__main__":  # pragma: no cover
    main()
