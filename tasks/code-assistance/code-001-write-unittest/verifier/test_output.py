"""Verifier for code-001: Write Unit Tests for Calculator."""

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


def test_test_file_exists(workspace):
    """test_calculator.py must exist in the workspace."""
    assert (workspace / "test_calculator.py").exists(), (
        "test_calculator.py not found in workspace"
    )


def test_calculator_module_exists(workspace):
    """calculator.py must still be present."""
    assert (workspace / "calculator.py").exists(), (
        "calculator.py not found in workspace"
    )


def test_tests_pass(workspace):
    """All tests in test_calculator.py must pass when executed with pytest."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(workspace / "test_calculator.py"), "-v"],
        capture_output=True,
        text=True,
        cwd=str(workspace),
        timeout=60,
    )
    assert result.returncode == 0, (
        f"Tests did not pass.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )


def test_minimum_test_count(workspace):
    """The test file must contain at least 4 test functions."""
    content = (workspace / "test_calculator.py").read_text()
    test_count = content.count("def test_")
    assert test_count >= 4, (
        f"Expected at least 4 test functions, found {test_count}"
    )


def test_covers_divide_by_zero(workspace):
    """The test file should test division by zero."""
    content = (workspace / "test_calculator.py").read_text()
    assert "ValueError" in content, (
        "Tests should verify that divide by zero raises ValueError"
    )


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
