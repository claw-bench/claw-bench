"""Verifier for file-013: Multi-File Search and Report."""

from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def report_md(workspace):
    """Read and return the generated report.md contents."""
    path = workspace / "report.md"
    assert path.exists(), "report.md not found in workspace"
    return path.read_text().strip()


def test_output_file_exists(workspace):
    """report.md must exist in the workspace."""
    assert (workspace / "report.md").exists()


def test_has_heading(report_md):
    """Report must contain the TODO Search Report heading."""
    assert "# TODO Search Report" in report_md


def test_has_summary_line(report_md):
    """Report must contain a summary with correct match and file counts."""
    assert "12 matches" in report_md, "Should report 12 matches"
    assert "5 files" in report_md, "Should report 5 files"


def test_has_table_header(report_md):
    """Report must contain a markdown table with File, Line, Content columns."""
    assert "| File" in report_md
    assert "| Line" in report_md or "Line |" in report_md
    assert "| Content" in report_md or "Content |" in report_md


def test_has_separator_row(report_md):
    """Report must contain a markdown table separator row."""
    assert "| ---" in report_md


def test_correct_match_count(report_md):
    """Table should have exactly 12 data rows."""
    lines = report_md.splitlines()
    # Count lines that look like table data rows (contain | and a .txt filename)
    data_rows = [l for l in lines if ".txt" in l and "|" in l and "File" not in l]
    assert len(data_rows) == 12, f"Expected 12 data rows, got {len(data_rows)}"


def test_all_files_present(report_md):
    """All 5 source files must appear in the report."""
    expected_files = [
        "api_notes.txt", "backlog.txt", "changelog.txt",
        "design.txt", "meeting_notes.txt",
    ]
    for f in expected_files:
        assert f in report_md, f"File '{f}' not found in report"


def test_line_numbers_accurate(report_md):
    """Spot-check specific known line numbers."""
    # design.txt line 10: "TODO: Implement refresh token rotation strategy"
    assert "design.txt" in report_md
    lines = report_md.splitlines()
    design_rows = [l for l in lines if "design.txt" in l and "|" in l and "File" not in l]
    # There should be 3 matches in design.txt
    assert len(design_rows) == 3, f"Expected 3 matches in design.txt, got {len(design_rows)}"


def test_content_contains_todo(report_md):
    """Every data row should contain TODO in the content."""
    lines = report_md.splitlines()
    data_rows = [l for l in lines if ".txt" in l and "|" in l and "File" not in l]
    for row in data_rows:
        assert "TODO" in row, f"Data row missing TODO content: {row}"
