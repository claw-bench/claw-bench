"""Verifier for code-004: Fix Syntax Errors."""

import ast
import importlib.util
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def broken_module(workspace):
    """Import the fixed broken.py from the workspace."""
    module_path = workspace / "broken.py"
    assert module_path.exists(), "broken.py not found in workspace"
    spec = importlib.util.spec_from_file_location("broken", str(module_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_file_exists(workspace):
    """broken.py must exist in the workspace."""
    assert (workspace / "broken.py").exists()


def test_no_syntax_errors(workspace):
    """broken.py must parse without SyntaxError."""
    source = (workspace / "broken.py").read_text()
    try:
        ast.parse(source)
    except SyntaxError as exc:
        pytest.fail(f"broken.py still has syntax errors: {exc}")


def test_greet(broken_module):
    """greet should return the correct greeting."""
    assert broken_module.greet("Alice") == "Hello, Alice!"
    assert broken_module.greet("World") == "Hello, World!"


def test_compute_average(broken_module):
    """compute_average should return the mean of a list."""
    assert broken_module.compute_average([1, 2, 3]) == 2.0
    assert broken_module.compute_average([10]) == 10.0


def test_compute_average_empty(broken_module):
    """compute_average should return 0.0 for an empty list."""
    assert broken_module.compute_average([]) == 0.0


def test_build_report(broken_module):
    """build_report should produce a formatted multi-line string."""
    result = broken_module.build_report("Test", ["a", "b"])
    assert "=== Test ===" in result
    assert "1. a" in result
    assert "2. b" in result
    assert "Total items: 2" in result


def test_build_report_empty(broken_module):
    """build_report should handle an empty item list."""
    result = broken_module.build_report("Empty", [])
    assert "Total items: 0" in result
