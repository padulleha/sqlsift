"""Command-line interface for sqlsift diff output formatting."""

import argparse
import json
import sys
from typing import List, Dict, Any

from sqlsift.diff import diff_results
from sqlsift.formatter import format_text, format_json, format_csv


def load_json_rows(path: str) -> List[Dict[str, Any]]:
    """Load a JSON file containing a list of row dicts."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError(f"Expected a JSON array in {path}, got {type(data).__name__}")
        return data
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Error reading {path}: {exc}", file=sys.stderr)
        sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sqlsift",
        description="Diff query result sets across database environments.",
    )
    parser.add_argument(
        "baseline",
        metavar="BASELINE",
        help="Path to baseline result set JSON file.",
    )
    parser.add_argument(
        "current",
        metavar="CURRENT",
        help="Path to current result set JSON file.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "csv"],
        default="text",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--show-unchanged",
        action="store_true",
        default=False,
        help="Include unchanged rows in text output.",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with code 1 if differences are found.",
    )
    return parser


def main(argv: List[str] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    baseline_rows = load_json_rows(args.baseline)
    current_rows = load_json_rows(args.current)

    result = diff_results(baseline_rows, current_rows)

    if args.format == "json":
        print(json.dumps(format_json(result), indent=2))
    elif args.format == "csv":
        print(format_csv(result))
    else:
        print(format_text(result, show_unchanged=args.show_unchanged))

    if args.exit_code and not result.is_equal:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
