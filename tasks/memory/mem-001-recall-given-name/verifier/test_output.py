"""Verifier for mem-001: Recall Given Name."""

import pytest
from pathlib import Path


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


def test_recall_file_exists(workspace):
    """recall.txt must exist in the workspace."""
    assert (workspace / "recall.txt").exists(), "recall.txt not found"


def test_recall_correct_name(workspace):
    """recall.txt must contain the name 'Cassandra Whitfield'."""
    content = (workspace / "recall.txt").read_text().strip()
    assert content == "Cassandra Whitfield", (
        f"Expected 'Cassandra Whitfield', got '{content}'"
    )


def test_high_quantity_count_exists(workspace):
    """high_quantity_count.txt must exist."""
    assert (workspace / "high_quantity_count.txt").exists(), (
        "high_quantity_count.txt not found"
    )


def test_high_quantity_count_correct(workspace):
    """Items with quantity > 50: Widget A(120), Bolt M6(200), Cable USB-C(75),
    Nail 2in(500), Bracket L(88), Fuse 5A(60) = 6 items."""
    content = (workspace / "high_quantity_count.txt").read_text().strip()
    assert content == "6", f"Expected '6', got '{content}'"


def test_notes_upper_exists(workspace):
    """notes_upper.txt must exist."""
    assert (workspace / "notes_upper.txt").exists(), "notes_upper.txt not found"


def test_notes_upper_content(workspace):
    """notes_upper.txt must contain uppercase version of notes.txt."""
    content = (workspace / "notes_upper.txt").read_text().strip()
    assert "MEETING WITH DESIGN TEAM AT THREE PM" in content
    assert "REVIEW QUARTERLY BUDGET REPORT" in content
    assert content == content.upper(), "Content is not fully uppercase"


def test_file_list_exists(workspace):
    """file_list.txt must exist."""
    assert (workspace / "file_list.txt").exists(), "file_list.txt not found"


def test_file_list_content(workspace):
    """file_list.txt must list original files sorted alphabetically."""
    content = (workspace / "file_list.txt").read_text().strip()
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    assert "inventory.csv" in lines
    assert "notes.txt" in lines


# ── Enhanced checks (auto-generated) ────────────────────────────────────────

@pytest.mark.weight(1)
def test_no_placeholder_values(workspace):
    """Output files must not contain placeholder/TODO markers."""
    placeholders = ["PLACEHOLDER", "CHANGEME", "your_"]
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
    path = workspace / "inventory.csv"
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
    bad_patterns = [".DS_Store", "Thumbs.db", ".log", ".bak", ".tmp"]
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
