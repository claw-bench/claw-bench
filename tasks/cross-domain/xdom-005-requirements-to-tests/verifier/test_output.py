"""Verifier for xdom-005: Requirements to Tests."""

import ast
import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def test_plan(workspace):
    path = workspace / "test_plan.json"
    assert path.exists(), "test_plan.json not found"
    with open(path) as f:
        return json.load(f)


@pytest.fixture
def test_stubs_source(workspace):
    path = workspace / "test_stubs.py"
    assert path.exists(), "test_stubs.py not found"
    return path.read_text()


def test_test_plan_exists(workspace):
    """test_plan.json must exist."""
    assert (workspace / "test_plan.json").exists()


def test_test_stubs_exists(workspace):
    """test_stubs.py must exist."""
    assert (workspace / "test_stubs.py").exists()


def test_plan_covers_all_requirements(test_plan):
    """Test plan must cover REQ-001 through REQ-008."""
    cases = test_plan.get("test_cases", [])
    req_ids = {c.get("requirement_id") for c in cases}
    for i in range(1, 9):
        req = f"REQ-{i:03d}"
        assert req in req_ids, f"{req} not covered in test plan"


def test_plan_has_required_fields(test_plan):
    """Each test case must have requirement_id, test_functions, and priority."""
    for case in test_plan.get("test_cases", []):
        assert "requirement_id" in case
        assert "test_functions" in case
        assert len(case["test_functions"]) >= 1, f"No test functions for {case['requirement_id']}"
        assert "priority" in case


def test_plan_priority_values_valid(test_plan):
    """Priority must be one of: critical, high, medium, low."""
    valid = {"critical", "high", "medium", "low"}
    for case in test_plan.get("test_cases", []):
        assert case["priority"] in valid, f"Invalid priority: {case['priority']}"


def test_stubs_is_valid_python(test_stubs_source):
    """test_stubs.py must be valid Python (parseable by ast)."""
    try:
        ast.parse(test_stubs_source)
    except SyntaxError as e:
        pytest.fail(f"test_stubs.py has syntax error: {e}")


def test_stubs_have_test_functions(test_stubs_source):
    """test_stubs.py must contain functions starting with test_."""
    tree = ast.parse(test_stubs_source)
    test_funcs = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")]
    assert len(test_funcs) >= 8, f"Expected at least 8 test functions, got {len(test_funcs)}"


def test_stubs_have_assertions(test_stubs_source):
    """Each test function must contain at least one assert statement."""
    tree = ast.parse(test_stubs_source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            asserts = [n for n in ast.walk(node) if isinstance(n, ast.Assert)]
            assert len(asserts) >= 1, f"Function {node.name} has no assert statements"


def test_stubs_have_docstrings(test_stubs_source):
    """Test functions should have docstrings."""
    tree = ast.parse(test_stubs_source)
    funcs_with_docs = 0
    total_test_funcs = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            total_test_funcs += 1
            if (node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, (ast.Constant, ast.Str))):
                funcs_with_docs += 1
    assert funcs_with_docs >= total_test_funcs * 0.5, \
        f"At least half of test functions should have docstrings ({funcs_with_docs}/{total_test_funcs})"


def test_plan_functions_exist_in_stubs(test_plan, test_stubs_source):
    """All functions listed in test_plan.json must exist in test_stubs.py."""
    tree = ast.parse(test_stubs_source)
    defined_funcs = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
    for case in test_plan.get("test_cases", []):
        for func_name in case.get("test_functions", []):
            assert func_name in defined_funcs, \
                f"Function '{func_name}' from test plan not found in test_stubs.py"


def test_minimum_total_test_functions(test_plan):
    """At least 16 test functions total across all requirements."""
    total = sum(len(c.get("test_functions", [])) for c in test_plan.get("test_cases", []))
    assert total >= 16, f"Expected at least 16 total test functions, got {total}"
