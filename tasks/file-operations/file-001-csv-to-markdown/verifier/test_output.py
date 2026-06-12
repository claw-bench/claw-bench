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
def test_no_duplicate_entries(workspace):
    """Output should not contain exact duplicate rows/objects."""
    import json
    path = workspace / "sample.csv"
    if not path.exists():
        pytest.skip("output file not found")
    text = path.read_text().strip()
    if path.suffix == ".json":
        data = json.loads(text)
        if isinstance(data, list):
            serialized = [json.dumps(item, sort_keys=True) for item in data]
            dupes = len(serialized) - len(set(serialized))
            assert dupes == 0, f"Found {dupes} duplicate entries in {path.name}"
    elif path.suffix == ".csv":
        lines_list = text.splitlines()
        if len(lines_list) > 1:
            data_lines = lines_list[1:]
            dupes = len(data_lines) - len(set(data_lines))
            assert dupes == 0, f"Found {dupes} duplicate rows in {path.name}"

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
