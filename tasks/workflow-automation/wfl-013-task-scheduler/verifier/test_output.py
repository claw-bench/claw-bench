"""Verifier for wfl-013: Task Scheduler."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return request.config.getoption("--workspace")


@pytest.fixture
def schedule(workspace):
    path = Path(workspace) / "schedule.json"
    assert path.exists(), "schedule.json not found in workspace"
    return json.loads(path.read_text())


@pytest.fixture
def tasks(workspace):
    path = Path(workspace) / "tasks.json"
    return json.loads(path.read_text())


def test_output_file_exists(workspace):
    assert (Path(workspace) / "schedule.json").exists()


def test_all_tasks_scheduled(schedule, tasks):
    scheduled_ids = {s["id"] for s in schedule}
    task_ids = {t["id"] for t in tasks}
    assert scheduled_ids == task_ids, f"Missing: {task_ids - scheduled_ids}"


def test_entry_structure(schedule):
    for entry in schedule:
        assert "id" in entry
        assert "start_time" in entry
        assert "end_time" in entry
        assert entry["end_time"] > entry["start_time"]


def test_no_overlaps(schedule):
    for i in range(len(schedule) - 1):
        assert schedule[i]["end_time"] <= schedule[i + 1]["start_time"], \
            f"{schedule[i]['id']} overlaps with {schedule[i+1]['id']}"


def test_dependencies_respected(schedule, tasks):
    task_map = {t["id"]: t for t in tasks}
    end_times = {s["id"]: s["end_time"] for s in schedule}
    start_times = {s["id"]: s["start_time"] for s in schedule}
    for entry in schedule:
        deps = task_map[entry["id"]]["dependencies"]
        for dep in deps:
            assert end_times[dep] <= start_times[entry["id"]], \
                f"{entry['id']} starts before dependency {dep} finishes"


def test_durations_correct(schedule, tasks):
    task_map = {t["id"]: t for t in tasks}
    for entry in schedule:
        expected_dur = task_map[entry["id"]]["duration_minutes"]
        actual_dur = entry["end_time"] - entry["start_time"]
        assert actual_dur == expected_dur, \
            f"{entry['id']}: expected duration {expected_dur}, got {actual_dur}"


def test_starts_at_zero(schedule):
    assert schedule[0]["start_time"] == 0, "First task should start at time 0"


def test_priority_ordering(schedule, tasks):
    """Among root tasks (no deps), higher priority ones should be scheduled first."""
    task_map = {t["id"]: t for t in tasks}
    root_tasks = [t["id"] for t in tasks if not t["dependencies"]]
    schedule_order = [s["id"] for s in schedule if s["id"] in root_tasks]
    # T7 (pri 1, deadline 50), T1 (pri 1, deadline 60), T3 (pri 1, deadline 100)
    # should come before T6 (pri 4)
    t6_idx = schedule_order.index("T6")
    for tid in ["T7", "T1", "T3"]:
        assert schedule_order.index(tid) < t6_idx, \
            f"{tid} should be scheduled before T6"
