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
