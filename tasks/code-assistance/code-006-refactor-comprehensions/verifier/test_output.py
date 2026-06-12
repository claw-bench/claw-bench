"""Verifier for code-006: Refactor to List Comprehensions."""

import ast
import importlib.util
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def process_module(workspace):
    """Import process.py from the workspace."""
    module_path = workspace / "process.py"
    assert module_path.exists(), "process.py not found in workspace"
    spec = importlib.util.spec_from_file_location("process", str(module_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def process_source(workspace):
    """Read and parse the source of process.py."""
    return (workspace / "process.py").read_text()


def _get_function_node(source, name):
    """Find a FunctionDef node by name."""
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def _has_list_comprehension(func_node):
    """Check if a function body contains a ListComp."""
    for node in ast.walk(func_node):
        if isinstance(node, ast.ListComp):
            return True
    return False


def _has_for_loop_with_append(func_node):
    """Check if a function has a for-loop that appends to a list."""
    for node in ast.walk(func_node):
        if isinstance(node, ast.For):
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    if isinstance(child.func, ast.Attribute) and child.func.attr == "append":
                        return True
    return False


def test_get_even_numbers_output(process_module):
    """get_even_numbers must return correct results."""
    assert process_module.get_even_numbers([1, 2, 3, 4, 5, 6]) == [2, 4, 6]
    assert process_module.get_even_numbers([]) == []
    assert process_module.get_even_numbers([1, 3, 5]) == []


def test_get_uppercased_output(process_module):
    """get_uppercased must return correct results."""
    assert process_module.get_uppercased(["hello", "world"]) == ["HELLO", "WORLD"]
    assert process_module.get_uppercased([]) == []


def test_get_lengths_output(process_module):
    """get_lengths must return correct results."""
    assert process_module.get_lengths(["a", "bb", "ccc"]) == [1, 2, 3]


def test_filter_positive_output(process_module):
    """filter_positive must return correct results."""
    assert process_module.filter_positive([-1, 0, 1, 2, -3]) == [1, 2]
    assert process_module.filter_positive([]) == []


def test_uses_comprehension_get_even(process_source):
    """get_even_numbers should use a list comprehension."""
    func = _get_function_node(process_source, "get_even_numbers")
    assert func is not None, "get_even_numbers not found"
    assert _has_list_comprehension(func), "get_even_numbers should use a list comprehension"


def test_uses_comprehension_get_uppercased(process_source):
    """get_uppercased should use a list comprehension."""
    func = _get_function_node(process_source, "get_uppercased")
    assert func is not None, "get_uppercased not found"
    assert _has_list_comprehension(func), "get_uppercased should use a list comprehension"


def test_uses_comprehension_get_lengths(process_source):
    """get_lengths should use a list comprehension."""
    func = _get_function_node(process_source, "get_lengths")
    assert func is not None, "get_lengths not found"
    assert _has_list_comprehension(func), "get_lengths should use a list comprehension"


def test_uses_comprehension_filter_positive(process_source):
    """filter_positive should use a list comprehension."""
    func = _get_function_node(process_source, "filter_positive")
    assert func is not None, "filter_positive not found"
    assert _has_list_comprehension(func), "filter_positive should use a list comprehension"


def test_no_for_loop_append(process_source):
    """None of the four functions should use for-loop + append pattern."""
    for name in ("get_even_numbers", "get_uppercased", "get_lengths", "filter_positive"):
        func = _get_function_node(process_source, name)
        assert func is not None, f"{name} not found"
        assert not _has_for_loop_with_append(func), (
            f"{name} still uses a for-loop with append"
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
