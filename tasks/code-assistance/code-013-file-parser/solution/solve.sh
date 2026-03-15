#!/usr/bin/env bash
# Oracle solution for code-013-file-parser
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/parser.py" <<'PYTHON'
"""Custom INI-like config file parser."""

import re


def _coerce_value(value: str):
    """Coerce a string value to int, bool, or leave as str."""
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    try:
        return int(value)
    except ValueError:
        return value


def parse_config_string(text: str) -> dict:
    """Parse a config string into a nested dict."""
    result = {}
    current_section = None

    for line_num, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()

        # Skip empty lines and comments
        if not stripped or stripped.startswith("#") or stripped.startswith(";"):
            continue

        # Section header
        section_match = re.match(r"^\[([^\]]+)\]$", stripped)
        if section_match:
            current_section = section_match.group(1).strip()
            if current_section not in result:
                result[current_section] = {}
            continue

        # Key = Value
        if "=" in stripped:
            if current_section is None:
                raise ValueError(
                    f"Line {line_num}: key-value pair before any section header"
                )
            key, _, value = stripped.partition("=")
            key = key.strip()
            value = value.strip()
            result[current_section][key] = _coerce_value(value)
            continue

        # Malformed line
        raise ValueError(f"Line {line_num}: malformed line: {stripped!r}")

    return result


def parse_config(filepath: str) -> dict:
    """Parse a config file into a nested dict."""
    with open(filepath, "r") as f:
        return parse_config_string(f.read())
PYTHON

echo "Solution written to $WORKSPACE/parser.py"
