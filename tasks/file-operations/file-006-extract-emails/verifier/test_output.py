"""Verifier for file-006: Extract Emails from Text."""

import re
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def email_lines(workspace):
    """Read and return the lines from emails.txt."""
    path = workspace / "emails.txt"
    assert path.exists(), "emails.txt not found in workspace"
    return [line.strip() for line in path.read_text().strip().splitlines() if line.strip()]


EXPECTED_EMAILS = sorted([
    "alice.chen@techcorp.com",
    "bob.kumar@techcorp.com",
    "carol.jones@infrastructure.io",
    "compliance@techcorp.com",
    "diana.ross@globalmarketing.com",
    "frank.weber@auditpartners.net",
    "helen.zhao@techcorp.com",
    "press@globalmarketing.com",
])


def test_output_file_exists(workspace):
    """emails.txt must exist in the workspace."""
    assert (workspace / "emails.txt").exists()


def test_correct_count(email_lines):
    """The output should contain exactly 8 email addresses."""
    assert len(email_lines) == 8, f"Expected 8 emails, got {len(email_lines)}"


def test_valid_email_format(email_lines):
    """Each line must be a valid email address."""
    email_re = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    for email in email_lines:
        assert email_re.match(email), f"Invalid email format: {email}"


def test_sorted_alphabetically(email_lines):
    """Emails must be in alphabetical order."""
    for i in range(len(email_lines) - 1):
        assert email_lines[i] <= email_lines[i + 1], (
            f"Not sorted: '{email_lines[i]}' should come before '{email_lines[i + 1]}'"
        )


def test_all_expected_emails_found(email_lines):
    """All 8 expected email addresses must be present."""
    for email in EXPECTED_EMAILS:
        assert email in email_lines, f"Missing email: {email}"


def test_no_extra_emails(email_lines):
    """No unexpected email addresses should be present."""
    for email in email_lines:
        assert email in EXPECTED_EMAILS, f"Unexpected email: {email}"
