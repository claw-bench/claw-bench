"""Verifier for file-008: Deduplicate Lines."""

from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def unique_lines(workspace):
    """Read and return the lines from unique.txt."""
    path = workspace / "unique.txt"
    assert path.exists(), "unique.txt not found in workspace"
    return [line for line in path.read_text().strip().splitlines() if line.strip()]


EXPECTED_UNIQUE = [
    "apple",
    "banana",
    "cherry",
    "date",
    "elderberry",
    "fig",
    "grape",
    "honeydew",
    "kiwi",
    "lemon",
    "mango",
    "nectarine",
    "orange",
]


def test_output_file_exists(workspace):
    """unique.txt must exist in the workspace."""
    assert (workspace / "unique.txt").exists()


def test_correct_line_count(unique_lines):
    """The output should contain exactly 13 unique lines."""
    assert len(unique_lines) == 13, f"Expected 13 lines, got {len(unique_lines)}"


def test_no_duplicates(unique_lines):
    """No duplicate lines should exist."""
    assert len(unique_lines) == len(set(unique_lines)), "Found duplicate lines in output"


def test_all_unique_lines_present(unique_lines):
    """All 13 expected unique values must be present."""
    for item in EXPECTED_UNIQUE:
        assert item in unique_lines, f"Missing line: {item}"


def test_order_preserved(unique_lines):
    """The order of first occurrences must be preserved."""
    assert unique_lines[0] == "apple", f"First line should be 'apple', got '{unique_lines[0]}'"
    assert unique_lines[1] == "banana", f"Second line should be 'banana', got '{unique_lines[1]}'"
    assert unique_lines[2] == "cherry", f"Third line should be 'cherry', got '{unique_lines[2]}'"
    # Verify elderberry comes after date and before fig
    date_idx = unique_lines.index("date")
    elder_idx = unique_lines.index("elderberry")
    fig_idx = unique_lines.index("fig")
    assert date_idx < elder_idx < fig_idx, "Order not preserved for date/elderberry/fig"


def test_last_line(unique_lines):
    """The last unique line should be 'orange'."""
    assert unique_lines[-1] == "orange", f"Last line should be 'orange', got '{unique_lines[-1]}'"
