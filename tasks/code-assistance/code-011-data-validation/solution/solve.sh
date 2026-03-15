#!/usr/bin/env bash
# Oracle solution for code-011-data-validation
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/validator.py" <<'PYTHON'
"""Data validation module."""

import re
from datetime import datetime


def validate_email(email: str) -> tuple[bool, str]:
    """Validate an email address."""
    if "@" not in email:
        return False, "Email must contain @"
    parts = email.split("@")
    if len(parts) != 2:
        return False, "Email must contain exactly one @"
    local, domain = parts
    if not local:
        return False, "Local part cannot be empty"
    if not domain:
        return False, "Domain cannot be empty"
    if "." not in domain:
        return False, "Domain must contain at least one dot"
    return True, ""


def validate_phone(phone: str) -> tuple[bool, str]:
    """Validate a phone number."""
    digits = re.sub(r"[^\d]", "", phone)
    # Remove leading country code (1) if present
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) != 10:
        return False, f"Phone must have 10 digits, got {len(digits)}"
    # Check original only has valid characters
    if not re.match(r"^[\d\s\-\+\(\)]+$", phone):
        return False, "Phone contains invalid characters"
    return True, ""


def validate_url(url: str) -> tuple[bool, str]:
    """Validate a URL."""
    if not url.startswith(("http://", "https://")):
        return False, "URL must start with http:// or https://"
    scheme_end = url.index("://") + 3
    rest = url[scheme_end:]
    if not rest or rest == "/":
        return False, "URL must have a domain"
    # Domain is everything up to the first /
    domain = rest.split("/")[0]
    if not domain:
        return False, "URL must have a domain"
    return True, ""


def validate_date(date_str: str) -> tuple[bool, str]:
    """Validate a date in YYYY-MM-DD format."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True, ""
    except ValueError as exc:
        return False, f"Invalid date: {exc}"


def validate_ip(ip: str) -> tuple[bool, str]:
    """Validate an IPv4 address."""
    parts = ip.split(".")
    if len(parts) != 4:
        return False, f"IPv4 must have 4 octets, got {len(parts)}"
    for part in parts:
        try:
            num = int(part)
        except ValueError:
            return False, f"Octet '{part}' is not a number"
        if num < 0 or num > 255:
            return False, f"Octet {num} out of range (0-255)"
    return True, ""
PYTHON

echo "Solution written to $WORKSPACE/validator.py"
