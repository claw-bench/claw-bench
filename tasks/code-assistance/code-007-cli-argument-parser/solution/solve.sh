#!/usr/bin/env bash
# Oracle solution for code-007-cli-argument-parser
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/cli.py" <<'PYTHON'
"""CLI argument parser module."""

import argparse


def create_parser():
    """Create and return the argument parser."""
    parser = argparse.ArgumentParser(description="Data conversion tool")
    parser.add_argument("--input", required=True, help="Path to the input file")
    parser.add_argument("--output", required=True, help="Path to the output file")
    parser.add_argument(
        "--format",
        choices=["csv", "json"],
        default="json",
        help="Output format (csv or json)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="Enable verbose output",
    )
    return parser


def main():
    """Parse arguments and print them."""
    parser = create_parser()
    args = parser.parse_args()
    print(f"Input:   {args.input}")
    print(f"Output:  {args.output}")
    print(f"Format:  {args.format}")
    print(f"Verbose: {args.verbose}")


if __name__ == "__main__":
    main()
PYTHON

echo "Solution written to $WORKSPACE/cli.py"
