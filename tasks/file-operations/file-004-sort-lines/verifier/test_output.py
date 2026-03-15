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
