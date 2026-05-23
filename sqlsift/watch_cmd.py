"""CLI entry-point for sqlsift watch mode."""

import argparse
import logging
import sys

from sqlsift.config import load_config, get_environment, ConfigError
from sqlsift.watch import watch, WatchError
from sqlsift.formatter import format_text

logging.basicConfig(level=logging.INFO, format="%(message)s")


def build_watch_parser(parent: argparse.ArgumentParser | None = None) -> argparse.ArgumentParser:
    parser = parent or argparse.ArgumentParser(
        prog="sqlsift-watch",
        description="Continuously diff query results between two environments.",
    )
    parser.add_argument("config", help="Path to sqlsift config file (JSON/YAML).")
    parser.add_argument("env_a", help="Baseline environment name.")
    parser.add_argument("env_b", help="Comparison environment name.")
    parser.add_argument("query", help="SQL query to execute on both environments.")
    parser.add_argument(
        "--interval",
        type=float,
        default=30.0,
        metavar="SECONDS",
        help="Polling interval in seconds (default: 30).",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=None,
        metavar="N",
        help="Maximum number of iterations (default: unlimited).",
    )
    return parser


def run_watch_cmd(args: argparse.Namespace) -> int:
    """Execute watch mode; returns exit code."""
    try:
        config = load_config(args.config)
    except ConfigError as exc:
        print(f"Config error: {exc}", file=sys.stderr)
        return 1

    try:
        get_environment(config, args.env_a)
        get_environment(config, args.env_b)
    except ConfigError as exc:
        print(f"Environment error: {exc}", file=sys.stderr)
        return 1

    def on_change(result, iteration):
        print(f"\n[iteration {iteration}] CHANGED")
        print(format_text(result))

    def on_stable(result, iteration):
        print(f"[iteration {iteration}] STABLE — no differences detected.")

    try:
        watch(
            config=config,
            env_a=args.env_a,
            env_b=args.env_b,
            query=args.query,
            interval=args.interval,
            max_iterations=args.iterations,
            on_change=on_change,
            on_stable=on_stable,
        )
    except WatchError as exc:
        print(f"Watch error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nWatch interrupted by user.")

    return 0


def main() -> None:  # pragma: no cover
    parser = build_watch_parser()
    args = parser.parse_args()
    sys.exit(run_watch_cmd(args))


if __name__ == "__main__":  # pragma: no cover
    main()
