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


# ── Enhanced checks (auto-generated) ────────────────────────────────────────

@pytest.mark.weight(1)
def test_no_placeholder_values(workspace):
    """Output files must not contain placeholder/TODO markers."""
    placeholders = ["PLACEHOLDER", "CHANGEME"]
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html", ".xml"):
            content = f.read_text(errors="replace")
            for p in placeholders:
                assert p not in content, f"Placeholder '{p}' found in {f.name}"

@pytest.mark.weight(1)
def test_encoding_valid(workspace):
    """All text output files must be valid UTF-8."""
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html"):
            try:
                f.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                pytest.fail(f"{f.name} contains invalid UTF-8 encoding")

@pytest.mark.weight(1)
def test_no_extraneous_files(workspace):
    """Workspace should not contain debug/temp files."""
    bad_patterns = [".DS_Store", "Thumbs.db", ".bak", ".tmp"]
    for f in workspace.rglob("*"):
        if f.is_file():
            for pat in bad_patterns:
                assert pat not in f.name, f"Extraneous file found: {f.name}"

@pytest.mark.weight(1)
def test_output_not_excessively_large(workspace):
    """Output files should be reasonably sized (< 5MB each)."""
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html"):
            size_mb = f.stat().st_size / (1024 * 1024)
            assert size_mb < 5, f"{f.name} is {size_mb:.1f}MB, exceeds 5MB limit"

@pytest.mark.weight(2)
def test_json_parseable_if_present(workspace):
    """Any .json files in workspace must be valid JSON."""
    import json
    for f in workspace.iterdir():
        if f.is_file() and f.suffix == ".json":
            try:
                json.loads(f.read_text())
            except json.JSONDecodeError:
                pytest.fail(f"{f.name} is not valid JSON")
