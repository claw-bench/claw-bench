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
