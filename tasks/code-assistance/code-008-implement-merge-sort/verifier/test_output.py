"""Verifier for code-008: Implement Merge Sort."""

import importlib.util
import time
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def sorting_module(workspace):
    """Import sorting.py from the workspace."""
    module_path = workspace / "sorting.py"
    assert module_path.exists(), "sorting.py not found in workspace"
    spec = importlib.util.spec_from_file_location("sorting", str(module_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_file_exists(workspace):
    """sorting.py must exist in the workspace."""
    assert (workspace / "sorting.py").exists()


def test_function_exists(sorting_module):
    """merge_sort function must exist."""
    assert hasattr(sorting_module, "merge_sort"), "merge_sort not found"


def test_sort_integers(sorting_module):
    """Should sort a list of integers."""
    assert sorting_module.merge_sort([3, 1, 4, 1, 5, 9, 2, 6]) == [1, 1, 2, 3, 4, 5, 6, 9]


def test_sort_strings(sorting_module):
    """Should sort a list of strings."""
    assert sorting_module.merge_sort(["banana", "apple", "cherry"]) == ["apple", "banana", "cherry"]


def test_empty_list(sorting_module):
    """Should handle empty list."""
    assert sorting_module.merge_sort([]) == []


def test_single_element(sorting_module):
    """Should handle single-element list."""
    assert sorting_module.merge_sort([42]) == [42]


def test_duplicates(sorting_module):
    """Should handle duplicates correctly."""
    assert sorting_module.merge_sort([5, 3, 5, 3, 1]) == [1, 3, 3, 5, 5]


def test_already_sorted(sorting_module):
    """Should handle already-sorted list."""
    assert sorting_module.merge_sort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]


def test_reverse_sorted(sorting_module):
    """Should handle reverse-sorted list."""
    assert sorting_module.merge_sort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]


def test_does_not_modify_original(sorting_module):
    """Original list must not be modified."""
    original = [3, 1, 2]
    copy = original.copy()
    sorting_module.merge_sort(original)
    assert original == copy, "Original list was modified"


def test_performance(sorting_module):
    """Should handle 10000 elements in reasonable time (O(n log n))."""
    import random
    data = list(range(10000))
    random.shuffle(data)
    start = time.time()
    result = sorting_module.merge_sort(data)
    elapsed = time.time() - start
    assert result == sorted(data)
    assert elapsed < 5.0, f"Took {elapsed:.2f}s – too slow for 10000 elements"
