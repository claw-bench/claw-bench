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


# ── Enhanced checks (auto-generated) ────────────────────────────────────────

@pytest.mark.weight(1)
def test_no_placeholder_values(workspace):
    """Output files must not contain placeholder/TODO markers."""
    placeholders = ["PLACEHOLDER", "CHANGEME", "your_"]
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
    bad_patterns = [".DS_Store", "Thumbs.db", ".log", ".bak", ".tmp"]
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
