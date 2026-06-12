"""Verifier for debug-005: Performance Bug Fix — O(n²) to O(n)."""

import importlib.util
import random
import time
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def fixed_path(workspace):
    return workspace / "fixed.py"


@pytest.fixture
def fixed_module(fixed_path):
    assert fixed_path.exists(), "fixed.py not found in workspace"
    spec = importlib.util.spec_from_file_location("fixed", fixed_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def slow_module(workspace):
    path = workspace / "slow_search.py"
    if not path.exists():
        pytest.skip("slow_search.py not found for comparison")
    spec = importlib.util.spec_from_file_location("slow_search", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ── Core checks: find_duplicates correctness (weight 3) ─────────────────────

@pytest.mark.weight(3)
def test_file_exists(workspace):
    """fixed.py must exist in the workspace."""
    assert (workspace / "fixed.py").exists()


@pytest.mark.weight(3)
def test_find_duplicates_basic(fixed_module):
    """find_duplicates must identify duplicate values."""
    result = fixed_module.find_duplicates([1, 2, 3, 2, 4, 3, 5])
    assert result == [2, 3]


@pytest.mark.weight(3)
def test_find_duplicates_no_dupes(fixed_module):
    """find_duplicates with all unique values returns empty list."""
    assert fixed_module.find_duplicates([1, 2, 3, 4, 5]) == []


@pytest.mark.weight(3)
def test_find_duplicates_all_same(fixed_module):
    """find_duplicates with all same values returns that value."""
    assert fixed_module.find_duplicates([7, 7, 7, 7]) == [7]


# ── Core checks: find_common_elements correctness (weight 3) ────────────────

@pytest.mark.weight(3)
def test_find_common_basic(fixed_module):
    """find_common_elements must find shared elements."""
    result = fixed_module.find_common_elements([1, 2, 3, 4], [3, 4, 5, 6])
    assert result == [3, 4]


@pytest.mark.weight(3)
def test_find_common_no_overlap(fixed_module):
    """find_common_elements with no shared elements returns empty."""
    assert fixed_module.find_common_elements([1, 2], [3, 4]) == []


@pytest.mark.weight(3)
def test_find_common_with_duplicates_in_input(fixed_module):
    """find_common_elements must not produce duplicates in output."""
    result = fixed_module.find_common_elements([1, 1, 2, 2], [1, 2, 2, 3])
    assert result == [1, 2]


# ── Core checks: count_unique correctness (weight 3) ────────────────────────

@pytest.mark.weight(3)
def test_count_unique_basic(fixed_module):
    """count_unique must count distinct elements."""
    assert fixed_module.count_unique([1, 2, 3, 2, 1]) == 3


@pytest.mark.weight(3)
def test_count_unique_empty(fixed_module):
    """count_unique([]) must return 0."""
    assert fixed_module.count_unique([]) == 0


# ── Core checks: has_pair_with_sum correctness (weight 3) ───────────────────

@pytest.mark.weight(3)
def test_has_pair_true(fixed_module):
    """has_pair_with_sum must find a valid pair."""
    assert fixed_module.has_pair_with_sum([1, 3, 5, 7], 8) is True


@pytest.mark.weight(3)
def test_has_pair_false(fixed_module):
    """has_pair_with_sum must return False when no pair exists."""
    assert fixed_module.has_pair_with_sum([1, 2, 3], 100) is False


@pytest.mark.weight(3)
def test_has_pair_no_self_pair(fixed_module):
    """has_pair_with_sum([5], 10) must be False — can't pair element with itself."""
    assert fixed_module.has_pair_with_sum([5], 10) is False


# ── Performance checks (weight 3) ───────────────────────────────────────────

@pytest.mark.weight(3)
def test_find_duplicates_performance(fixed_module):
    """find_duplicates must complete on 50k elements in under 2 seconds."""
    random.seed(42)
    large_list = [random.randint(0, 25000) for _ in range(50000)]
    start = time.perf_counter()
    fixed_module.find_duplicates(large_list)
    elapsed = time.perf_counter() - start
    assert elapsed < 2.0, f"find_duplicates took {elapsed:.2f}s on 50k items (limit: 2s)"


@pytest.mark.weight(3)
def test_find_common_performance(fixed_module):
    """find_common_elements must complete on 50k elements in under 2 seconds."""
    random.seed(42)
    list_a = [random.randint(0, 25000) for _ in range(50000)]
    list_b = [random.randint(0, 25000) for _ in range(50000)]
    start = time.perf_counter()
    fixed_module.find_common_elements(list_a, list_b)
    elapsed = time.perf_counter() - start
    assert elapsed < 2.0, f"find_common_elements took {elapsed:.2f}s on 50k items (limit: 2s)"


@pytest.mark.weight(3)
def test_has_pair_performance(fixed_module):
    """has_pair_with_sum must complete on 50k elements in under 2 seconds."""
    random.seed(42)
    large_list = list(range(50000))
    start = time.perf_counter()
    fixed_module.has_pair_with_sum(large_list, 99997)
    elapsed = time.perf_counter() - start
    assert elapsed < 2.0, f"has_pair_with_sum took {elapsed:.2f}s on 50k items (limit: 2s)"


# ── Additional checks (weight 1) ────────────────────────────────────────────

@pytest.mark.weight(1)
def test_find_duplicates_strings(fixed_module):
    """find_duplicates should work with strings."""
    result = fixed_module.find_duplicates(["a", "b", "a", "c", "b"])
    assert result == ["a", "b"]


@pytest.mark.weight(1)
def test_count_unique_all_same(fixed_module):
    """count_unique with all identical items returns 1."""
    assert fixed_module.count_unique([42, 42, 42]) == 1


@pytest.mark.weight(1)
def test_has_pair_with_zero(fixed_module):
    """has_pair_with_sum must handle zero target."""
    assert fixed_module.has_pair_with_sum([-1, 0, 1], 0) is True


@pytest.mark.weight(1)
def test_no_extraneous_files(workspace):
    """Workspace should not contain debug/temp files."""
    bad_patterns = [".DS_Store", ".bak", ".tmp"]
    for f in workspace.iterdir():
        if f.is_file():
            for pat in bad_patterns:
                assert pat not in f.name, f"Extraneous file found: {f.name}"
