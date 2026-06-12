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
