import os
from pathlib import Path
import pytest
import csv
import json
import math
import numpy as np

@pytest.fixture
def workspace(request):
    """Resolve workspace from --workspace CLI option."""
    ws = request.config.getoption("--workspace")
    if ws:
        return Path(ws)
    return Path(os.environ.get("CLAW_WORKSPACE", os.environ.get("WORKSPACE", "workspace")))
@pytest.mark.weight(3)
def test_files_exist(workspace):
    item_analysis = workspace / "item_analysis.csv"
    exam_summary = workspace / "exam_summary.json"
    assert item_analysis.is_file(), "item_analysis.csv not found"
    assert exam_summary.is_file(), "exam_summary.json not found"

@pytest.mark.weight(5)
def test_item_analysis_content(workspace):
    # Load responses
    responses_file = workspace / "exam_responses.csv"
    with open(responses_file) as f:
        reader = csv.DictReader(f)
        data = list(reader)

    num_students = len(data)
    num_items = 30
    item_names = [f'item_{i+1}' for i in range(num_items)]

    # Extract responses and total scores
    item_responses = {item: [] for item in item_names}
    total_scores = []
    for row in data:
        total_scores.append(float(row['total_score']))
        for item in item_names:
            item_responses[item].append(int(row[item]))

    total_scores_np = np.array(total_scores)

    # Compute difficulty (p-value)
    difficulties = {item: np.mean(item_responses[item]) for item in item_names}

    # Identify top 27% and bottom 27%
    cutoff = int(math.ceil(0.27 * num_students))
    sorted_indices = np.argsort(total_scores_np)
    bottom_indices = sorted_indices[:cutoff]
    top_indices = sorted_indices[-cutoff:]

    # Compute discrimination index
    discrimination = {}
    for item in item_names:
        responses_np = np.array(item_responses[item])
        top_mean = np.mean(responses_np[top_indices])
        bottom_mean = np.mean(responses_np[bottom_indices])
        discrimination[item] = top_mean - bottom_mean

    # Compute point-biserial correlation
    point_biserial = {}
    for item in item_names:
        responses_np = np.array(item_responses[item])
        if np.std(responses_np) == 0 or np.std(total_scores_np) == 0:
            corr = 0.0
        else:
            corr = np.corrcoef(responses_np, total_scores_np)[0,1]
        point_biserial[item] = corr

    # Load item_analysis.csv
    item_analysis_file = workspace / "item_analysis.csv"
    with open(item_analysis_file) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == num_items, f"Expected {num_items} rows in item_analysis.csv, got {len(rows)}"

    for row in rows:
        item = row['item']
        assert item in item_names, f"Unexpected item name {item}"
        diff = float(row['difficulty'])
        disc = float(row['discrimination_index'])
        pb = float(row['point_biserial'])

        # Check difficulty close to computed
        assert abs(diff - difficulties[item]) < 0.05, f"Difficulty mismatch for {item}"

        # Check discrimination close
        assert abs(disc - discrimination[item]) < 0.1, f"Discrimination mismatch for {item}"

        # Check point-biserial close
        assert abs(pb - point_biserial[item]) < 0.1, f"Point-biserial mismatch for {item}"

@pytest.mark.weight(2)
def test_exam_summary_json(workspace):
    summary_file = workspace / "exam_summary.json"
    with open(summary_file) as f:
        summary = json.load(f)

    # Check keys
    for key in ['num_students', 'num_items', 'mean_total_score', 'std_total_score']:
        assert key in summary, f"Missing key {key} in exam_summary.json"

    # Check values
    assert isinstance(summary['num_students'], int) and summary['num_students'] > 0
    assert summary['num_items'] == 30

    # Load responses to verify mean and std
    responses_file = workspace / "exam_responses.csv"
    with open(responses_file) as f:
        reader = csv.DictReader(f)
        total_scores = [float(row['total_score']) for row in reader]

    mean_score = np.mean(total_scores)
    std_score = np.std(total_scores, ddof=0)

    assert abs(summary['mean_total_score'] - mean_score) < 0.01
    assert abs(summary['std_total_score'] - std_score) < 0.01
