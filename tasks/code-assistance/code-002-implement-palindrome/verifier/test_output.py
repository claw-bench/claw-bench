"""Verifier for code-002: Implement a Palindrome Checker."""

import importlib.util
import sys
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def palindrome_module(workspace):
    """Import palindrome.py from the workspace."""
    module_path = workspace / "palindrome.py"
    assert module_path.exists(), "palindrome.py not found in workspace"
    spec = importlib.util.spec_from_file_location("palindrome", str(module_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_file_exists(workspace):
    """palindrome.py must exist in the workspace."""
    assert (workspace / "palindrome.py").exists(), "palindrome.py not found"


def test_function_exists(palindrome_module):
    """is_palindrome function must be defined."""
    assert hasattr(palindrome_module, "is_palindrome"), (
        "Function is_palindrome not found in palindrome.py"
    )


def test_racecar(palindrome_module):
    """'racecar' is a palindrome."""
    assert palindrome_module.is_palindrome("racecar") is True


def test_hello(palindrome_module):
    """'hello' is not a palindrome."""
    assert palindrome_module.is_palindrome("hello") is False


def test_empty_string(palindrome_module):
    """Empty string is a palindrome."""
    assert palindrome_module.is_palindrome("") is True


