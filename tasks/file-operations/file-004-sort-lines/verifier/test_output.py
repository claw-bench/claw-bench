"""Verifier for file-004: Sort Lines Alphabetically."""

from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def sorted_lines(workspace):
    """Read and return the lines from sorted.txt."""
    path = workspace / "sorted.txt"
    assert path.exists(), "sorted.txt not found in workspace"
    return [line for line in path.read_text().strip().splitlines() if line.strip()]


def test_output_file_exists(workspace):
    """sorted.txt must exist in the workspace."""
    assert (workspace / "sorted.txt").exists()


def test_correct_line_count(sorted_lines):
    """The output must contain exactly 15 lines."""
    assert len(sorted_lines) == 15, f"Expected 15 lines, got {len(sorted_lines)}"


def test_alphabetical_order(sorted_lines):
    """Lines must be in alphabetical order."""
    for i in range(len(sorted_lines) - 1):
        assert sorted_lines[i] <= sorted_lines[i + 1], (
            f"Not in order: '{sorted_lines[i]}' should come before '{sorted_lines[i + 1]}'"
        )


def test_all_names_present(sorted_lines):
    """All 15 original names must be present."""
    expected = [
        "Alice Wang",
        "Bob Carter",
        "Charlie Davis",
        "Diana Lopez",
        "Eve Sullivan",
        "Frank Nguyen",
        "George Palmer",
        "Hannah Park",
        "Isaac Bell",
        "Jack Robinson",
        "Kevin Mitchell",
        "Lucy Grant",
        "Megan Foster",
        "Nathan Hayes",
        "Olivia Thompson",
    ]
    for name in expected:
        assert name in sorted_lines, f"Missing name: {name}"


def test_first_and_last(sorted_lines):
    """The first name should be Alice Wang and the last Olivia Thompson."""
    assert sorted_lines[0] == "Alice Wang", f"First line should be 'Alice Wang', got '{sorted_lines[0]}'"
    assert sorted_lines[-1] == "Olivia Thompson", (
        f"Last line should be 'Olivia Thompson', got '{sorted_lines[-1]}'"
    )


def test_no_duplicates(sorted_lines):
    """There should be no duplicate lines."""
    assert len(sorted_lines) == len(set(sorted_lines)), "Found duplicate lines in output"


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
