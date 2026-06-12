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
