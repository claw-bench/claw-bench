"""Verifier for code-015: Performance Optimization."""

import importlib.util
import time
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def slow_module(workspace):
    """Import slow.py from the workspace."""
    module_path = workspace / "slow.py"
    assert module_path.exists(), "slow.py not found in workspace"
    spec = importlib.util.spec_from_file_location("slow", str(module_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_file_exists(workspace):
    """slow.py must exist in the workspace."""
    assert (workspace / "slow.py").exists()


# --- Correctness Tests ---

def test_find_duplicates_correct(slow_module):
    """find_duplicates must return correct results."""
    assert slow_module.find_duplicates([1, 2, 3, 2, 4, 3]) == [2, 3]


def test_find_duplicates_no_dupes(slow_module):
    """find_duplicates with no duplicates."""
    assert slow_module.find_duplicates([1, 2, 3]) == []


def test_find_duplicates_all_same(slow_module):
    """find_duplicates where all items are the same."""
    assert slow_module.find_duplicates([5, 5, 5]) == [5]


def test_find_duplicates_empty(slow_module):
    """find_duplicates on empty list."""
    assert slow_module.find_duplicates([]) == []


def test_count_words_correct(slow_module):
    """count_words must return correct word counts."""
    result = slow_module.count_words("the cat sat on the mat")
    assert result["the"] == 2
    assert result["cat"] == 1
    assert result["sat"] == 1


def test_count_words_punctuation(slow_module):
    """count_words should strip punctuation."""
    result = slow_module.count_words("Hello, hello! HELLO.")
    assert result["hello"] == 3


def test_count_words_empty(slow_module):
    """count_words on empty string."""
    result = slow_module.count_words("")
    assert result == {}


def test_fibonacci_base_cases(slow_module):
    """fibonacci base cases."""
    assert slow_module.fibonacci(0) == 0
    assert slow_module.fibonacci(1) == 1


def test_fibonacci_small(slow_module):
    """fibonacci for small n."""
    assert slow_module.fibonacci(10) == 55


def test_fibonacci_larger(slow_module):
    """fibonacci for larger n."""
    assert slow_module.fibonacci(30) == 832040


# --- Performance Tests ---

def test_find_duplicates_performance(slow_module):
    """find_duplicates should handle 10000 items quickly."""
    items = list(range(5000)) + list(range(5000))  # 5000 duplicates
    start = time.time()
    result = slow_module.find_duplicates(items)
    elapsed = time.time() - start
    assert len(result) == 5000
    assert elapsed < 1.0, f"find_duplicates took {elapsed:.2f}s – should be under 1s"


def test_count_words_performance(slow_module):
    """count_words should handle large text quickly."""
    text = " ".join(["word"] * 5000 + ["other"] * 3000 + ["test"] * 2000)
    start = time.time()
    result = slow_module.count_words(text)
    elapsed = time.time() - start
    assert result["word"] == 5000
    assert elapsed < 1.0, f"count_words took {elapsed:.2f}s – should be under 1s"


def test_fibonacci_performance(slow_module):
    """fibonacci(35) should complete quickly with optimization."""
    start = time.time()
    result = slow_module.fibonacci(35)
    elapsed = time.time() - start
    assert result == 9227465
    assert elapsed < 1.0, f"fibonacci(35) took {elapsed:.2f}s – should be under 1s"
