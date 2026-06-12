"""Verifier for file-003: Find and Replace in Text File."""

from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def output_text(workspace):
    """Read and return the generated output.txt contents."""
    path = workspace / "output.txt"
    assert path.exists(), "output.txt not found in workspace"
    return path.read_text()


def test_output_file_exists(workspace):
    """output.txt must exist in the workspace."""
    assert (workspace / "output.txt").exists()


def test_no_foo_remaining(output_text):
    """No occurrences of 'foo' should remain in the output."""
    assert "foo" not in output_text, "Found remaining 'foo' in output"


def test_bar_count(output_text):
    """The output should contain exactly 20 occurrences of 'bar'."""
    count = output_text.count("bar")
    assert count == 20, f"Expected 20 occurrences of 'bar', got {count}"


def test_line_count_preserved(output_text):
    """The output should have exactly 20 lines."""
    lines = output_text.strip().splitlines()
    assert len(lines) == 20, f"Expected 20 lines, got {len(lines)}"


def test_line_structure_preserved(output_text):
    """Key phrases should be present with 'bar' replacing 'foo'."""
    assert "The bar project started in 2019." in output_text
    assert "We built bar to solve a common problem." in output_text
    assert "The bar ecosystem continued to expand." in output_text


def test_no_extra_modifications(output_text):
    """Lines not containing the replacement should be structurally intact."""
    assert "2019" in output_text
    assert "Security audits" in output_text
    assert "two weeks" in output_text
    assert "many countries" in output_text


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
