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
