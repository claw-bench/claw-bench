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
