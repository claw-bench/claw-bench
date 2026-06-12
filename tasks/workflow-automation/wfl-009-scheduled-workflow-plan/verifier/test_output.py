"""Verifier for wfl-009: Scheduled Workflow Plan with Critical Path."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def schedule(workspace):
    """Load the schedule."""
    path = workspace / "schedule.json"
    assert path.exists(), "schedule.json not found"
    return json.loads(path.read_text())


@pytest.fixture
def critical_path(workspace):
    """Load the critical path."""
    path = workspace / "critical_path.json"
    assert path.exists(), "critical_path.json not found"
    return json.loads(path.read_text())


@pytest.fixture
def tasks_input(workspace):
    """Load original tasks."""
    return json.loads((workspace / "tasks.json").read_text())


@pytest.fixture
def schedule_by_id(schedule):
    """Create lookup by task ID."""
    return {t["id"]: t for t in schedule["tasks"]}


def test_schedule_exists(workspace):
    """schedule.json must exist."""
    assert (workspace / "schedule.json").exists()


def test_critical_path_exists(workspace):
    """critical_path.json must exist."""
    assert (workspace / "critical_path.json").exists()


def test_all_tasks_scheduled(schedule):
    """All 12 tasks must be in the schedule."""
    assert len(schedule["tasks"]) == 12


def test_schedule_has_required_fields(schedule):
    """Each task in schedule must have all required timing fields."""
    required = {"id", "name", "duration", "earliest_start", "earliest_finish",
                "latest_start", "latest_finish", "slack"}
    for task in schedule["tasks"]:
        assert required.issubset(set(task.keys())), (
            f"Task {task.get('id')} missing fields: {required - set(task.keys())}"
        )


def test_earliest_finish_equals_start_plus_duration(schedule):
    """earliest_finish must equal earliest_start + duration for all tasks."""
    for task in schedule["tasks"]:
        expected = task["earliest_start"] + task["duration"]
        assert task["earliest_finish"] == expected, (
            f"Task {task['id']}: EF should be {expected}, got {task['earliest_finish']}"
        )


def test_latest_finish_equals_start_plus_duration(schedule):
    """latest_finish must equal latest_start + duration for all tasks."""
    for task in schedule["tasks"]:
        expected = task["latest_start"] + task["duration"]
        assert task["latest_finish"] == expected, (
            f"Task {task['id']}: LF should be {expected}, got {task['latest_finish']}"
        )


def test_slack_correct(schedule):
    """Slack must equal latest_start - earliest_start."""
    for task in schedule["tasks"]:
        expected = task["latest_start"] - task["earliest_start"]
        assert task["slack"] == expected, (
            f"Task {task['id']}: slack should be {expected}, got {task['slack']}"
        )


def test_no_negative_slack(schedule):
    """No task should have negative slack."""
    for task in schedule["tasks"]:
        assert task["slack"] >= 0, f"Task {task['id']} has negative slack: {task['slack']}"


def test_dependencies_respected(schedule, tasks_input):
    """No task starts before all its dependencies finish."""
    sched_map = {t["id"]: t for t in schedule["tasks"]}
    input_map = {t["id"]: t for t in tasks_input}
    for task in tasks_input:
        for dep_id in task["dependencies"]:
            dep_finish = sched_map[dep_id]["earliest_finish"]
            task_start = sched_map[task["id"]]["earliest_start"]
            assert task_start >= dep_finish, (
                f"Task {task['id']} starts at {task_start} but dependency "
                f"{dep_id} finishes at {dep_finish}"
            )


def test_total_duration_correct(schedule):
    """Total duration should be 29 time units."""
    # Critical path: T1(3) + T2(5) + T5(4) + T8(7) + T10(3) + T11(4) + T12(2) = 28
    # OR: T1(3) + T2(5) + T4(3) + T8(7) + T10(3) + T11(4) + T12(2) = 27
    # Let me recompute: T1(3)->T2(5)->T5(4)->T8(7)->T10(3)->T11(4)->T12(2) = 28
    # T1->T2->T4->T7: 3+5+3=11, T7 needs T6 too: T3(ES=8,EF=10)->T6(ES=10,EF=14)->T7(ES=14,EF=20)
    # T8 needs T5(EF=12) and T4(EF=11), so T8 starts at 12, finishes at 19
    # T10 starts at 19, finishes 22; T9 starts 20, finishes 23
    # T11 starts at 23, finishes 27; T12 starts 27, finishes 29
    assert schedule["total_duration"] == 29, (
        f"Expected total duration 29, got {schedule['total_duration']}"
    )


def test_critical_path_has_path(critical_path):
    """Critical path must have a path array."""
    assert "path" in critical_path
    assert isinstance(critical_path["path"], list)
    assert len(critical_path["path"]) > 0


def test_critical_path_total_duration(critical_path):
    """Critical path total_duration must be 29."""
    assert critical_path["total_duration"] == 29


def test_critical_path_tasks_have_zero_slack(schedule, critical_path):
    """All tasks on the critical path must have 0 slack."""
    sched_map = {t["id"]: t for t in schedule["tasks"]}
    for tid in critical_path["path"]:
        assert sched_map[tid]["slack"] == 0, (
            f"Critical path task {tid} has non-zero slack: {sched_map[tid]['slack']}"
        )


def test_critical_path_valid_dependency_chain(critical_path, tasks_input):
    """Critical path must form a valid dependency chain."""
    input_map = {t["id"]: t for t in tasks_input}
    path = critical_path["path"]
    for i in range(1, len(path)):
        current = path[i]
        previous = path[i - 1]
        deps = input_map[current]["dependencies"]
        assert previous in deps, (
            f"Critical path broken: {current} does not depend on {previous}"
        )


def test_t1_starts_at_zero(schedule_by_id):
    """T1 has no dependencies and should start at 0."""
    assert schedule_by_id["T1"]["earliest_start"] == 0


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
