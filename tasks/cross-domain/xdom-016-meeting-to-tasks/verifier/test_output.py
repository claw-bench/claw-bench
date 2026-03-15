"""Verifier for xdom-016: Convert Meeting Notes to Project Tasks."""

import json
from datetime import datetime
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def tasks_data(workspace):
    """Read and return the tasks.json contents."""
    path = workspace / "tasks.json"
    assert path.exists(), "tasks.json not found in workspace"
    return json.loads(path.read_text())


def test_tasks_file_exists(workspace):
    """tasks.json must exist in the workspace."""
    assert (workspace / "tasks.json").exists()


def test_task_count(tasks_data):
    """Should have exactly 6 tasks."""
    assert len(tasks_data["tasks"]) == 6


def test_high_priority_count(tasks_data):
    """Should have 3 high-priority tasks."""
    assert tasks_data["high_priority_count"] == 3


def test_total_estimate_days(tasks_data):
    """Total estimate should be 16 days."""
    assert tasks_data["total_estimate_days"] == 16


def test_all_tasks_have_required_fields(tasks_data):
    """Every task must have all required fields."""
    required = {"id", "title", "assignee", "priority", "deadline", "estimate_days", "dependencies"}
    for task in tasks_data["tasks"]:
        missing = required - set(task.keys())
        assert not missing, f"Task {task.get('id', '?')} missing fields: {missing}"


def test_mike_has_two_tasks(tasks_data):
    """Mike should be assigned 2 tasks."""
    mike_tasks = [t for t in tasks_data["tasks"] if t["assignee"] == "Mike"]
    assert len(mike_tasks) == 2


def test_lisa_has_two_tasks(tasks_data):
    """Lisa should be assigned 2 tasks."""
    lisa_tasks = [t for t in tasks_data["tasks"] if t["assignee"] == "Lisa"]
    assert len(lisa_tasks) == 2


def test_tom_has_two_tasks(tasks_data):
    """Tom should be assigned 2 tasks."""
    tom_tasks = [t for t in tasks_data["tasks"] if t["assignee"] == "Tom"]
    assert len(tom_tasks) == 2


def test_checkout_ui_depends_on_payment_api(tasks_data):
    """The checkout UI task should depend on the payment API task."""
    tasks = tasks_data["tasks"]
    # Find the payment API task (Mike, high priority, 5 day estimate)
    api_task = None
    ui_task = None
    for t in tasks:
        title_lower = t["title"].lower()
        if "payment" in title_lower and "api" in title_lower and t["assignee"] == "Mike":
            api_task = t
        if ("checkout" in title_lower or "payment" in title_lower) and "ui" in title_lower and t["assignee"] == "Lisa":
            ui_task = t
    assert api_task is not None, "Could not find payment API task assigned to Mike"
    assert ui_task is not None, "Could not find checkout UI task assigned to Lisa"
    assert api_task["id"] in ui_task["dependencies"], (
        f"Checkout UI ({ui_task['id']}) should depend on payment API ({api_task['id']})"
    )


def test_all_deadlines_valid_march_2026(tasks_data):
    """All deadlines should be valid dates in March 2026."""
    for task in tasks_data["tasks"]:
        deadline = task["deadline"]
        dt = datetime.strptime(deadline, "%Y-%m-%d")
        assert dt.year == 2026, f"Task {task['id']} deadline year is not 2026"
        assert dt.month == 3, f"Task {task['id']} deadline month is not March"


def test_estimate_days_sum(tasks_data):
    """Sum of individual estimate_days should equal total_estimate_days."""
    total = sum(t["estimate_days"] for t in tasks_data["tasks"])
    assert total == tasks_data["total_estimate_days"]


def test_priorities_valid(tasks_data):
    """All priorities should be high, medium, or low."""
    valid = {"high", "medium", "low"}
    for task in tasks_data["tasks"]:
        assert task["priority"] in valid, f"Task {task['id']} has invalid priority: {task['priority']}"


def test_task_ids_sequential(tasks_data):
    """Task IDs should be sequential TASK-001 through TASK-006."""
    ids = [t["id"] for t in tasks_data["tasks"]]
    expected = [f"TASK-{i:03d}" for i in range(1, 7)]
    assert sorted(ids) == expected
