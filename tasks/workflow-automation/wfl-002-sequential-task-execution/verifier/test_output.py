"""Verifier for wfl-002: Sequential Task Execution."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def results(workspace):
    """Load the results JSON."""
    path = workspace / "results.json"
    assert path.exists(), "results.json not found in workspace"
    return json.loads(path.read_text())


@pytest.fixture
def input_text(workspace):
    """Read the input text."""
    path = workspace / "input.txt"
    assert path.exists(), "input.txt not found"
    return path.read_text()


def test_results_file_exists(workspace):
    """results.json must exist."""
    assert (workspace / "results.json").exists()


def test_results_is_list_of_three(results):
    """Results must contain exactly 3 task entries."""
    assert isinstance(results, list), "results.json must be a JSON array"
    assert len(results) == 3, f"Expected 3 results, got {len(results)}"


def test_all_tasks_present(results):
    """All three task names must be present."""
    task_names = {r["task"] for r in results}
    assert "count_lines" in task_names, "count_lines task missing"
    assert "count_words" in task_names, "count_words task missing"
    assert "count_chars" in task_names, "count_chars task missing"


def test_correct_execution_order(results):
    """Tasks must be in the order specified by tasks.json."""
    expected_order = ["count_lines", "count_words", "count_chars"]
    actual_order = [r["task"] for r in results]
    assert actual_order == expected_order, (
        f"Expected order {expected_order}, got {actual_order}"
    )


def test_order_field_sequential(results):
    """Each result must have an order field with correct 1-based index."""
    for i, r in enumerate(results):
        assert "order" in r, f"Result {i} missing 'order' field"
        assert r["order"] == i + 1, (
            f"Expected order {i + 1} for task {r['task']}, got {r['order']}"
        )


def test_count_lines_correct(results, input_text):
    """Line count must match non-empty lines in input."""
    lines_result = next(r for r in results if r["task"] == "count_lines")
    non_empty = [l for l in input_text.strip().split("\n") if l.strip()]
    assert lines_result["result"] == len(non_empty), (
        f"Expected {len(non_empty)} lines, got {lines_result['result']}"
    )


def test_count_words_correct(results, input_text):
    """Word count must match whitespace-separated tokens."""
    words_result = next(r for r in results if r["task"] == "count_words")
    word_count = len(input_text.split())
    assert words_result["result"] == word_count, (
        f"Expected {word_count} words, got {words_result['result']}"
    )


def test_count_chars_correct(results, input_text):
    """Character count must match total chars (excluding final trailing newline)."""
    chars_result = next(r for r in results if r["task"] == "count_chars")
    char_count = len(input_text.rstrip("\n"))
    assert chars_result["result"] == char_count, (
        f"Expected {char_count} chars, got {chars_result['result']}"
    )
