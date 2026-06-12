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


# ── Enhanced checks (auto-generated) ────────────────────────────────────────

@pytest.mark.weight(1)
def test_no_placeholder_values(workspace):
    """Output files must not contain placeholder/TODO markers."""
    placeholders = ["PLACEHOLDER", "CHANGEME"]
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html", ".xml"):
            content = f.read_text(errors="replace")
            for p in placeholders:
                assert p not in content, f"Placeholder '{p}' found in {f.name}"

@pytest.mark.weight(2)
def test_no_empty_critical_fields(workspace):
    """JSON output must not have empty-string or null values in top-level fields."""
    import json
    path = workspace / "tasks.json"
    if not path.exists():
        pytest.skip("output file not found")
    data = json.loads(path.read_text())
    items = data if isinstance(data, list) else [data]
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        non_empty = [
            v for v in item.values()
            if v is not None and (not isinstance(v, str) or v.strip() != "")
        ]
        assert non_empty, f"Item {i}: all fields are empty or null"

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
def test_consistent_key_naming(workspace):
    """JSON keys should use a consistent naming convention."""
    import json, re
    path = workspace / "tasks.json"
    if not path.exists():
        pytest.skip("output file not found")
    data = json.loads(path.read_text())
    items = data if isinstance(data, list) else [data]
    all_keys = set()
    for item in items:
        if isinstance(item, dict):
            all_keys.update(item.keys())
    if len(all_keys) < 2:
        return
    snake = sum(1 for k in all_keys if re.match(r'^[a-z][a-z0-9_]*$', k))
    camel = sum(1 for k in all_keys if re.match(r'^[a-z][a-zA-Z0-9]*$', k) and not re.match(r'^[a-z][a-z0-9_]*$', k))
    pascal = sum(1 for k in all_keys if re.match(r'^[A-Z][a-zA-Z0-9]*$', k))
    dominant = max(snake, camel, pascal)
    classified = snake + camel + pascal
    if classified == 0:
        return
    consistency = dominant / classified
    assert consistency >= 0.7, f"Key naming inconsistent: {snake} snake, {camel} camel, {pascal} pascal out of {len(all_keys)} keys"

@pytest.mark.weight(1)
def test_no_duplicate_entries(workspace):
    """Output should not contain exact duplicate rows/objects."""
    import json
    path = workspace / "tasks.json"
    if not path.exists():
        pytest.skip("output file not found")
    text = path.read_text().strip()
    if path.suffix == ".json":
        data = json.loads(text)
        if isinstance(data, list):
            serialized = [json.dumps(item, sort_keys=True) for item in data]
            dupes = len(serialized) - len(set(serialized))
            assert dupes == 0, f"Found {dupes} duplicate entries in {path.name}"
    elif path.suffix == ".csv":
        lines_list = text.splitlines()
        if len(lines_list) > 1:
            data_lines = lines_list[1:]
            dupes = len(data_lines) - len(set(data_lines))
            assert dupes == 0, f"Found {dupes} duplicate rows in {path.name}"

@pytest.mark.weight(1)
def test_no_extraneous_files(workspace):
    """Workspace should not contain debug/temp files."""
    bad_patterns = [".DS_Store", "Thumbs.db", ".bak", ".tmp"]
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
