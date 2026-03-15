"""Verifier for file-001: Convert CSV to Markdown Table."""

from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def output_md(workspace):
    """Read and return the generated output.md contents."""
    path = workspace / "output.md"
    assert path.exists(), "output.md not found in workspace"
    return path.read_text().strip()


def test_output_file_exists(workspace):
    """output.md must exist in the workspace."""
    assert (workspace / "output.md").exists()


def test_has_header_row(output_md):
    """Output must contain a header row with Name, Age, City."""
    lines = output_md.splitlines()
    header = lines[0]
    assert "Name" in header
    assert "Age" in header
    assert "City" in header


def test_has_separator_row(output_md):
    """Output must contain a Markdown separator row (with ---)."""
    lines = output_md.splitlines()
    assert len(lines) >= 2, "Output must have at least a header and separator"
    separator = lines[1]
    assert "---" in separator


def test_correct_row_count(output_md):
    """Output must have 7 lines: 1 header + 1 separator + 5 data rows."""
    lines = [line for line in output_md.splitlines() if line.strip()]
    assert len(lines) == 7, f"Expected 7 lines, got {len(lines)}"


def test_pipe_delimited(output_md):
    """Every line must use pipe delimiters."""
    for line in output_md.splitlines():
        if line.strip():
            assert "|" in line, f"Line missing pipe delimiter: {line}"


def test_contains_all_data(output_md):
    """All five data entries must be present."""
    assert "Alice" in output_md
    assert "Bob" in output_md
    assert "Charlie" in output_md
    assert "Diana" in output_md
    assert "Eve" in output_md
    assert "New York" in output_md
    assert "San Francisco" in output_md
    assert "Chicago" in output_md
    assert "Seattle" in output_md
    assert "Boston" in output_md


def test_matches_expected(workspace, output_md):
    """Output should match the expected reference (normalizing whitespace in separators)."""
    expected_path = Path(__file__).parent / "expected" / "output.md"
    if expected_path.exists():
        expected = expected_path.read_text().strip()

        def _normalize(text: str) -> str:
            """Normalize markdown table whitespace so both `| --- |` and `|---|` match."""
            lines = []
            for line in text.splitlines():
                # Collapse whitespace around pipes and dashes in separator rows
                stripped = line.strip()
                if stripped and all(c in "|- " for c in stripped):
                    stripped = stripped.replace(" ", "")
                lines.append(stripped)
            return "\n".join(lines)

        assert _normalize(output_md) == _normalize(expected), (
            "Output does not match expected reference"
        )
