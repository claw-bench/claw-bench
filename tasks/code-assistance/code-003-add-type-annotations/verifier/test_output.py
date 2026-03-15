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
