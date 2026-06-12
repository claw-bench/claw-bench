"""Verifier for the CRT scoring + logistic reasoning task.

The verifier independently recomputes the expected per-participant scores from
the raw inputs and checks the structure and sanity of the logistic model.
"""

import csv
import json
import math
import os
from pathlib import Path

import pytest

TOL = 1e-9


@pytest.fixture
def workspace(request):
    """Resolve workspace from --workspace CLI option (fallback to env/default)."""
    ws = request.config.getoption("--workspace")
    if ws:
        return Path(ws)
    return Path(os.environ.get("CLAW_WORKSPACE", os.environ.get("WORKSPACE", "workspace")))


def load_items(workspace):
    with open(workspace / "crt_items.json", encoding="utf-8") as f:
        items = json.load(f)
    return {it["id"]: it for it in items}, len(items)


def classify(answer, item):
    if abs(answer - item["correct"]) <= TOL:
        return "correct"
    if abs(answer - item["intuitive"]) <= TOL:
        return "intuitive"
    return "other"


def expected_participants(workspace):
    item_by_id, num_items = load_items(workspace)
    agg = {}
    with open(workspace / "responses.csv", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            pid = row["participant_id"]
            item = item_by_id[row["item_id"]]
            cls = classify(float(row["answer"]), item)
            p = agg.setdefault(pid, {"crt_score": 0, "intuitive_count": 0})
            if cls == "correct":
                p["crt_score"] += 1
            elif cls == "intuitive":
                p["intuitive_count"] += 1
    for p in agg.values():
        p["accuracy"] = round(p["crt_score"] / num_items, 3)
    return agg, num_items


def load_analysis(workspace):
    path = workspace / "analysis.json"
    assert path.exists(), f"analysis.json not found at {path}"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@pytest.mark.weight(2)
def test_output_exists(workspace):
    assert (workspace / "analysis.json").exists(), "analysis.json not produced"


@pytest.mark.weight(3)
def test_structure_and_num_items(workspace):
    analysis = load_analysis(workspace)
    _, num_items = load_items(workspace)
    assert analysis["num_items"] == num_items
    assert isinstance(analysis["participants"], dict)
    assert isinstance(analysis["logistic"], dict)
    assert analysis["logistic"]["feature"] == "intuitive_count"


@pytest.mark.weight(4)
def test_all_participants_present(workspace):
    analysis = load_analysis(workspace)
    expected, _ = expected_participants(workspace)
    assert sorted(analysis["participants"].keys()) == sorted(expected.keys())


@pytest.mark.weight(6)
def test_per_participant_scoring(workspace):
    analysis = load_analysis(workspace)
    expected, num_items = expected_participants(workspace)
    for pid, exp in expected.items():
        got = analysis["participants"][pid]
        assert got["crt_score"] == exp["crt_score"], f"{pid} crt_score"
        assert got["intuitive_count"] == exp["intuitive_count"], f"{pid} intuitive_count"
        assert abs(got["accuracy"] - exp["accuracy"]) <= 1e-6, f"{pid} accuracy"
        assert 0 <= got["crt_score"] <= num_items


@pytest.mark.weight(5)
def test_logistic_slope_negative(workspace):
    """More intuitive answers must predict lower probability of being correct."""
    analysis = load_analysis(workspace)
    coef = analysis["logistic"]["coef"]
    assert isinstance(coef, (int, float))
    assert coef < 0, f"logistic slope on intuitive_count should be negative, got {coef}"


@pytest.mark.weight(5)
def test_logistic_discriminates(workspace):
    """The fitted model should be sane: low intuitive_count -> higher P(correct)
    than high intuitive_count, and intercept finite."""
    analysis = load_analysis(workspace)
    coef = analysis["logistic"]["coef"]
    intercept = analysis["logistic"]["intercept"]
    assert math.isfinite(coef) and math.isfinite(intercept)

    def p(x):
        return 1.0 / (1.0 + math.exp(-(coef * x + intercept)))

    _, num_items = load_items(workspace)
    assert p(0) > p(num_items), "P(correct) should fall as intuitive_count rises"
