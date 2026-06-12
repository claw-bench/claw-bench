"""Verifier for code-003: Add Type Annotations."""

import ast
import importlib.util
import sys
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def utils_source(workspace):
    """Read the source code of utils.py."""
    path = workspace / "utils.py"
    assert path.exists(), "utils.py not found in workspace"
    return path.read_text()


@pytest.fixture
def utils_module(workspace):
    """Import utils.py from the workspace."""
    module_path = workspace / "utils.py"
    spec = importlib.util.spec_from_file_location("utils", str(module_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_file_parses(utils_source):
    """utils.py must be valid Python."""
    try:
        ast.parse(utils_source)
    except SyntaxError as exc:
        pytest.fail(f"utils.py has syntax errors: {exc}")


def test_all_functions_have_param_annotations(utils_source):
    """Every function parameter (except self) should have a type annotation."""
    tree = ast.parse(utils_source)
    functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    assert len(functions) >= 5, f"Expected at least 5 functions, found {len(functions)}"

    for func in functions:
        for arg in func.args.args:
            if arg.arg == "self":
                continue
            assert arg.annotation is not None, (
                f"Parameter '{arg.arg}' in function '{func.name}' lacks a type annotation"
            )


def test_all_functions_have_return_annotations(utils_source):
    """Every function should have a return type annotation."""
    tree = ast.parse(utils_source)
    functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

    for func in functions:
        assert func.returns is not None, (
            f"Function '{func.name}' lacks a return type annotation"
        )


def test_clamp_still_works(utils_module):
    """clamp must still function correctly."""
    assert utils_module.clamp(5, 1, 10) == 5
    assert utils_module.clamp(-1, 0, 10) == 0
    assert utils_module.clamp(100, 0, 10) == 10


def test_flatten_still_works(utils_module):
    """flatten must still function correctly."""
    assert utils_module.flatten([[1, 2], [3, 4]]) == [1, 2, 3, 4]
    assert utils_module.flatten([[], [1]]) == [1]


def test_merge_dicts_still_works(utils_module):
    """merge_dicts must still function correctly."""
    assert utils_module.merge_dicts({"a": 1}, {"b": 2}) == {"a": 1, "b": 2}
    assert utils_module.merge_dicts({"a": 1}, {"a": 2}) == {"a": 2}


def test_truncate_still_works(utils_module):
    """truncate must still function correctly."""
    assert utils_module.truncate("hello", 10) == "hello"
    assert utils_module.truncate("hello world", 8) == "hello..."


def test_safe_divide_still_works(utils_module):
    """safe_divide must still function correctly."""
    assert utils_module.safe_divide(10, 2) == 5.0
    assert utils_module.safe_divide(10, 0) is None


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
