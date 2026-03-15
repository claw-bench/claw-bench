"""Verifier for file-005: Merge Multiple Files."""

from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def merged_lines(workspace):
    """Read and return the lines from merged.txt."""
    path = workspace / "merged.txt"
    assert path.exists(), "merged.txt not found in workspace"
    return [line for line in path.read_text().strip().splitlines() if line.strip()]


def test_output_file_exists(workspace):
    """merged.txt must exist in the workspace."""
    assert (workspace / "merged.txt").exists()


def test_single_header(merged_lines):
    """The header 'Name,Score,Grade' should appear exactly once."""
    header_count = sum(1 for line in merged_lines if line.strip() == "Name,Score,Grade")
    assert header_count == 1, f"Expected 1 header line, got {header_count}"


def test_header_is_first_line(merged_lines):
    """The header must be the first line."""
    assert merged_lines[0].strip() == "Name,Score,Grade", (
        f"First line should be the header, got: '{merged_lines[0]}'"
    )


def test_correct_total_lines(merged_lines):
    """The output should have 13 lines: 1 header + 12 data lines."""
    assert len(merged_lines) == 13, f"Expected 13 lines, got {len(merged_lines)}"


def test_all_data_present(merged_lines):
    """All 12 data entries must be present."""
    content = "\n".join(merged_lines)
    expected_names = [
        "Alice", "Bob", "Charlie", "Diana",
        "Eva", "Frank", "Grace",
        "Henry", "Iris", "Jack", "Kate", "Leo",
    ]
    for name in expected_names:
        assert name in content, f"Missing data for: {name}"


def test_correct_order(merged_lines):
    """Data from part1 must come before part2, which must come before part3."""
    data_lines = merged_lines[1:]  # skip header
    names = [line.split(",")[0] for line in data_lines]
    # part1 names should come first
    alice_idx = names.index("Alice")
    diana_idx = names.index("Diana")
    # part2 names should come next
    eva_idx = names.index("Eva")
    grace_idx = names.index("Grace")
    # part3 names should come last
    henry_idx = names.index("Henry")
    leo_idx = names.index("Leo")
    assert diana_idx < eva_idx, "part1 data should come before part2 data"
    assert grace_idx < henry_idx, "part2 data should come before part3 data"
    assert alice_idx < diana_idx, "part1 internal order should be preserved"
    assert henry_idx < leo_idx, "part3 internal order should be preserved"
