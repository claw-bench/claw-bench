"""Verifier for file-014: File Comparison and Diff."""

from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def diff_text(workspace):
    """Read and return the generated diff.txt contents."""
    path = workspace / "diff.txt"
    assert path.exists(), "diff.txt not found in workspace"
    return path.read_text().strip()


def test_output_file_exists(workspace):
    """diff.txt must exist in the workspace."""
    assert (workspace / "diff.txt").exists()


def test_uses_diff_markers(diff_text):
    """Output must use +, -, and space prefixes."""
    lines = diff_text.splitlines()
    has_plus = any(l.startswith("+ ") for l in lines)
    has_minus = any(l.startswith("- ") for l in lines)
    has_unchanged = any(l.startswith("  ") for l in lines)
    assert has_plus, "No added lines (+ prefix) found"
    assert has_minus, "No removed lines (- prefix) found"
    assert has_unchanged, "No unchanged lines (space prefix) found"


def test_detects_version_change(diff_text):
    """Should detect the version number change from 2.3.0 to 2.4.0."""
    assert "- # Version: 2.3.0" in diff_text or "- Version: 2.3.0" in diff_text.replace("#", "").strip() or "2.3.0" in diff_text
    assert "+ # Version: 2.4.0" in diff_text or "+ Version: 2.4.0" in diff_text.replace("#", "").strip() or "2.4.0" in diff_text


def test_detects_port_change(diff_text):
    """Should detect the port change from 8080 to 9090."""
    lines = diff_text.splitlines()
    removed_port = any("8080" in l and l.startswith("- ") for l in lines)
    added_port = any("9090" in l and l.startswith("+ ") for l in lines)
    assert removed_port, "Should show port 8080 as removed"
    assert added_port, "Should show port 9090 as added"


def test_detects_debug_change(diff_text):
    """Should detect the debug flag change from true to false."""
    lines = diff_text.splitlines()
    removed_debug = any("debug = true" in l and l.startswith("- ") for l in lines)
    added_debug = any("debug = false" in l and l.startswith("+ ") for l in lines)
    assert removed_debug, "Should show debug = true as removed"
    assert added_debug, "Should show debug = false as added"


def test_detects_added_line(diff_text):
    """Should detect the new 'prefix = myapp' line added in cache section."""
    lines = diff_text.splitlines()
    added_prefix = any("prefix" in l and l.startswith("+ ") for l in lines)
    assert added_prefix, "Should show 'prefix = myapp' as added"


def test_unchanged_lines_present(diff_text):
    """Unchanged lines should be included for context."""
    # [server] section header is unchanged
    lines = diff_text.splitlines()
    server_unchanged = any("[server]" in l and l.startswith("  ") for l in lines)
    assert server_unchanged, "[server] should appear as an unchanged line"


def test_detects_logging_level_change(diff_text):
    """Should detect logging level change from DEBUG to WARNING."""
    lines = diff_text.splitlines()
    removed_level = any("DEBUG" in l and l.startswith("- ") for l in lines)
    added_level = any("WARNING" in l and l.startswith("+ ") for l in lines)
    assert removed_level, "Should show level = DEBUG as removed"
    assert added_level, "Should show level = WARNING as added"


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
