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
    path = workspace / "question_bank.json"
    assert path.exists()
    return json.loads(path.read_text())

@pytest.mark.weight(3)
def test_question_count(result):
    assert "questions" in result
    assert len(result["questions"]) >= 30

@pytest.mark.weight(3)
def test_difficulty_distribution(result):
    stats = result["statistics"]
    assert stats["by_difficulty"]["easy"] >= 10
    assert stats["by_difficulty"]["medium"] >= 10
    assert stats["by_difficulty"]["hard"] >= 10

@pytest.mark.weight(2)
def test_question_structure(result):
    for q in result["questions"]:
        assert "id" in q
        assert "objective_id" in q
        assert "difficulty" in q
        assert q["difficulty"] in ["easy", "medium", "hard"]
        assert "question" in q
        assert "answer" in q

@pytest.mark.weight(2)
def test_objectives_covered(result):
    assert result["statistics"]["objectives_covered"] == 10
