"""Verifier for debug-001: Fix Python Syntax Errors."""

import ast
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def fixed_path(workspace):
    return workspace / "fixed.py"


@pytest.fixture
def fixed_source(fixed_path):
    assert fixed_path.exists(), "fixed.py not found in workspace"
    return fixed_path.read_text()


@pytest.fixture
def fixed_module(fixed_path):
    spec = importlib.util.spec_from_file_location("fixed", fixed_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ── Core checks (weight 3) ──────────────────────────────────────────────────

@pytest.mark.weight(3)
def test_file_exists(workspace):
    """fixed.py must exist in the workspace."""
    assert (workspace / "fixed.py").exists(), "fixed.py not found"


@pytest.mark.weight(3)
def test_parses_without_syntax_error(fixed_source):
    """The fixed file must parse as valid Python."""
    try:
        ast.parse(fixed_source)
    except SyntaxError as e:
        pytest.fail(f"fixed.py has a syntax error: {e}")


@pytest.mark.weight(3)
def test_colon_fix(fixed_source):
    """The missing colon after the if-statement must be added."""
    tree = ast.parse(fixed_source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "greet":
            if_nodes = [n for n in ast.walk(node) if isinstance(n, ast.If)]
            assert len(if_nodes) >= 1, "greet() should contain an if-statement"
            break
    else:
        pytest.fail("greet function not found")


@pytest.mark.weight(3)
def test_indentation_fix(fixed_source):
    """The return statement in calculate_sum must be properly indented."""
    tree = ast.parse(fixed_source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "calculate_sum":
            returns = [n for n in ast.walk(node) if isinstance(n, ast.Return)]
            assert len(returns) >= 1, "calculate_sum must have a return statement"
            ret = returns[0]
            for_nodes = [n for n in ast.walk(node) if isinstance(n, ast.For)]
            assert len(for_nodes) >= 1, "calculate_sum must have a for loop"
            assert ret.col_offset <= for_nodes[0].col_offset, \
                "return should be at function body level, not inside the for loop"
            break


@pytest.mark.weight(3)
def test_parenthesis_fix(fixed_source):
    """The unclosed parenthesis in format_output must be closed."""
    tree = ast.parse(fixed_source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "format_output":
            assigns = [n for n in ast.walk(node) if isinstance(n, ast.Assign)]
            assert len(assigns) >= 1, "format_output must assign result"
            break
    else:
        pytest.fail("format_output function not found")


@pytest.mark.weight(3)
def test_runs_without_error(fixed_path):
    """The fixed file must execute without any errors."""
    proc = subprocess.run(
        [sys.executable, str(fixed_path)],
        capture_output=True, text=True, timeout=10
    )
    assert proc.returncode == 0, f"fixed.py crashed: {proc.stderr}"


@pytest.mark.weight(3)
def test_greet_world(fixed_module):
    """greet('World') should return 'Hello, World!'."""
    assert fixed_module.greet("World") == "Hello, World!"


@pytest.mark.weight(3)
def test_greet_other(fixed_module):
    """greet('Alice') should return 'Hi, Alice!'."""
    assert fixed_module.greet("Alice") == "Hi, Alice!"


@pytest.mark.weight(3)
def test_calculate_sum_basic(fixed_module):
    """calculate_sum([1, 2, 3, 4, 5]) should return 15."""
    assert fixed_module.calculate_sum([1, 2, 3, 4, 5]) == 15


@pytest.mark.weight(3)
def test_format_output_basic(fixed_module):
    """format_output([1, 2, 3, 4, 5]) should return 'Output: 1, 2, 3, 4, 5'."""
    assert fixed_module.format_output([1, 2, 3, 4, 5]) == "Output: 1, 2, 3, 4, 5"


# ── Additional checks (weight 1) ────────────────────────────────────────────

@pytest.mark.weight(1)
def test_calculate_sum_empty(fixed_module):
    """calculate_sum([]) should return 0."""
    assert fixed_module.calculate_sum([]) == 0


@pytest.mark.weight(1)
def test_calculate_sum_single(fixed_module):
    """calculate_sum([42]) should return 42."""
    assert fixed_module.calculate_sum([42]) == 42


@pytest.mark.weight(1)
def test_calculate_sum_negative(fixed_module):
    """calculate_sum([-1, -2, 3]) should return 0."""
    assert fixed_module.calculate_sum([-1, -2, 3]) == 0


@pytest.mark.weight(1)
def test_format_output_single(fixed_module):
    """format_output([42]) should return 'Output: 42'."""
    assert fixed_module.format_output([42]) == "Output: 42"


@pytest.mark.weight(1)
def test_main_output(fixed_path):
    """main() should print the expected output lines."""
    proc = subprocess.run(
        [sys.executable, str(fixed_path)],
        capture_output=True, text=True, timeout=10
    )
    output = proc.stdout.strip()
    assert "Hello, World!" in output
    assert "Sum: 15" in output
    assert "Output: 1, 2, 3, 4, 5" in output


@pytest.mark.weight(1)
def test_functions_exist(fixed_module):
    """All expected functions must be defined."""
    for name in ("greet", "calculate_sum", "format_output", "main"):
        assert hasattr(fixed_module, name), f"Function '{name}' not found"
        assert callable(getattr(fixed_module, name)), f"'{name}' is not callable"


@pytest.mark.weight(1)
def test_no_extraneous_files(workspace):
    """Workspace should not contain debug/temp files."""
    bad_patterns = [".DS_Store", ".bak", ".tmp"]
    for f in workspace.iterdir():
        if f.is_file():
            for pat in bad_patterns:
                assert pat not in f.name, f"Extraneous file found: {f.name}"


@pytest.mark.weight(1)
def test_encoding_valid(workspace):
    """All text output files must be valid UTF-8."""
    for f in workspace.iterdir():
        if f.is_file() and f.suffix == ".py":
            try:
                f.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                pytest.fail(f"{f.name} contains invalid UTF-8 encoding")
