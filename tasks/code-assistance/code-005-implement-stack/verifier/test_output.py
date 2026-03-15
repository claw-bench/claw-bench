"""Verifier for code-005: Implement a Stack Class."""

import importlib.util
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def stack_class(workspace):
    """Import Stack class from workspace/stack.py."""
    module_path = workspace / "stack.py"
    assert module_path.exists(), "stack.py not found in workspace"
    spec = importlib.util.spec_from_file_location("stack", str(module_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert hasattr(mod, "Stack"), "Stack class not found in stack.py"
    return mod.Stack


def test_file_exists(workspace):
    """stack.py must exist in the workspace."""
    assert (workspace / "stack.py").exists()


def test_push_and_pop(stack_class):
    """push then pop should return the same item."""
    s = stack_class()
    s.push(42)
    assert s.pop() == 42


def test_lifo_order(stack_class):
    """Items should come out in LIFO order."""
    s = stack_class()
    s.push(1)
    s.push(2)
    s.push(3)
    assert s.pop() == 3
    assert s.pop() == 2
    assert s.pop() == 1


def test_pop_empty_raises(stack_class):
    """pop on empty stack should raise IndexError."""
    s = stack_class()
    with pytest.raises(IndexError, match="pop from empty stack"):
        s.pop()


def test_peek(stack_class):
    """peek should return top item without removing it."""
    s = stack_class()
    s.push("hello")
    assert s.peek() == "hello"
    assert s.size() == 1  # still there


def test_peek_empty_raises(stack_class):
    """peek on empty stack should raise IndexError."""
    s = stack_class()
    with pytest.raises(IndexError, match="peek at empty stack"):
        s.peek()


def test_is_empty(stack_class):
    """is_empty should reflect whether the stack has items."""
    s = stack_class()
    assert s.is_empty() is True
    s.push(1)
    assert s.is_empty() is False
    s.pop()
    assert s.is_empty() is True


def test_size(stack_class):
    """size should track the number of items."""
    s = stack_class()
    assert s.size() == 0
    s.push("a")
    s.push("b")
    assert s.size() == 2
    s.pop()
    assert s.size() == 1


def test_mixed_types(stack_class):
    """Stack should handle mixed types."""
    s = stack_class()
    s.push(1)
    s.push("two")
    s.push([3])
    assert s.pop() == [3]
    assert s.pop() == "two"
    assert s.pop() == 1
