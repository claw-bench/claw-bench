import os, pytest, json
from pathlib import Path

@pytest.fixture
def workspace(request):
    """Resolve workspace from --workspace CLI option."""
    ws = request.config.getoption("--workspace")
    if ws:
        return Path(ws)
    return Path(os.environ.get("CLAW_WORKSPACE", os.environ.get("WORKSPACE", "workspace")))
@pytest.fixture
def result(workspace):
    path = workspace / "learning_plans.json"
    assert path.exists()
    return json.loads(path.read_text())

@pytest.mark.weight(3)
def test_all_students(result):
    assert "students" in result
    assert len(result["students"]) == 15

@pytest.mark.weight(3)
def test_learning_path_order(result, workspace):
    prereqs = json.loads((workspace / "prerequisites.json").read_text())
    for sid, data in result["students"].items():
        path = data["learning_path"]
        for i, topic in enumerate(path):
            for prereq in prereqs.get(topic, []):
                if prereq in path:
                    assert path.index(prereq) < i, f"Prereq {prereq} should come before {topic}"

@pytest.mark.weight(2)
def test_summary(result):
    s = result["summary"]
    assert s["total_students"] == 15
    assert "avg_gap_count" in s
    assert "most_common_gap" in s
