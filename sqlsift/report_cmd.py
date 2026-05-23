"""CLI sub-command: sqlsift report — run a query diff and emit an HTML report."""

from __future__ import annotations

import argparse
import sys
from typing import Optional

from sqlsift.config import ConfigError, load_config, get_environment
from sqlsift.connector import ConnectorError, get_connection, run_query
from sqlsift.diff import diff_results
from sqlsift.reporter import write_html_report


def build_report_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the *report* sub-command onto *subparsers*."""
    p = subparsers.add_parser(
        "report",
        help="Run a query diff between two environments and write an HTML report.",
    )
    p.add_argument("--config", required=True, help="Path to sqlsift config file.")
    p.add_argument("--source", required=True, help="Source environment name.")
    p.add_argument("--target", required=True, help="Target environment name.")
    p.add_argument("--query", required=True, help="SQL query to execute on both environments.")
    p.add_argument("--output", required=True, help="Path for the generated HTML report.")
    p.add_argument("--title", default=None, help="Optional report title (defaults to query text).")
    p.set_defaults(func=run_report_cmd)


def run_report_cmd(args: argparse.Namespace) -> int:
    """Execute the report sub-command; returns an exit code."""
    try:
        config = load_config(args.config)
    except ConfigError as exc:
        print(f"[sqlsift] Config error: {exc}", file=sys.stderr)
        return 1

    try:
        src_env = get_environment(config, args.source)
        tgt_env = get_environment(config, args.target)
    except ConfigError as exc:
        print(f"[sqlsift] Environment error: {exc}", file=sys.stderr)
        return 1

    try:
        src_conn = get_connection(src_env)
        tgt_conn = get_connection(tgt_env)
        src_rows = run_query(src_conn, args.query)
        tgt_rows = run_query(tgt_conn, args.query)
    except ConnectorError as exc:
        print(f"[sqlsift] Connector error: {exc}", file=sys.stderr)
        return 1

    result = diff_results(src_rows, tgt_rows)
    title: str = args.title or args.query

    write_html_report(result, path=args.output, title=title)
    print(f"[sqlsift] Report written to {args.output}")
    return 0 if (result.columns_match and not result.added and not result.removed) else 2


def main(argv: Optional[list[str]] = None) -> int:
    """Standalone entry-point for the report command."""
    parser = argparse.ArgumentParser(prog="sqlsift-report")
    subs = parser.add_subparsers(dest="command")
    build_report_parser(subs)

    # Allow running without sub-command prefix for convenience.
    parser.add_argument("--config")
    parser.add_argument("--source")
    parser.add_argument("--target")
    parser.add_argument("--query")
    parser.add_argument("--output")
    parser.add_argument("--title", default=None)
    parser.set_defaults(func=run_report_cmd)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
