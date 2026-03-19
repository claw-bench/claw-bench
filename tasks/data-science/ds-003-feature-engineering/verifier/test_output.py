import os
from pathlib import Path
import json
import pandas as pd
import pytest

@pytest.fixture
def workspace(request):
    """Resolve workspace from --workspace CLI option."""
    ws = request.config.getoption("--workspace")
    if ws:
        return Path(ws)
    return Path(os.environ.get("CLAW_WORKSPACE", os.environ.get("WORKSPACE", "workspace")))
@pytest.mark.weight(3)
def test_engineered_features_file_exists(workspace):
    ef_path = workspace / "engineered_features.csv"
    assert ef_path.exists(), "engineered_features.csv file not found"

@pytest.mark.weight(5)
def test_feature_report_file_exists(workspace):
    report_path = workspace / "feature_report.json"
    assert report_path.exists(), "feature_report.json file not found"

@pytest.mark.weight(8)
def test_engineered_features_content(workspace):
    ef_path = workspace / "engineered_features.csv"
    df = pd.read_csv(ef_path)

    # Must contain target column
    assert 'target' in df.columns, "target column missing in engineered_features.csv"

    # Must have exactly 11 columns: 10 features + target
    assert len(df.columns) == 11, f"Expected 11 columns (10 features + target), got {len(df.columns)}"

    # Check no missing values
    assert not df.isnull().values.any(), "Missing values found in engineered_features.csv"

@pytest.mark.weight(10)
def test_feature_report_content(workspace):
    report_path = workspace / "feature_report.json"
    with open(report_path, 'r') as f:
        report = json.load(f)

    # Check keys
    assert 'correlations' in report, "'correlations' key missing in feature_report.json"
    assert 'selected_features' in report, "'selected_features' key missing in feature_report.json"

    correlations = report['correlations']
    selected = report['selected_features']

    # correlations must be dict with feature names and float values
    assert isinstance(correlations, dict), "correlations must be a dictionary"
    assert all(isinstance(v, float) for v in correlations.values()), "All correlation values must be floats"

    # selected_features must be list of strings
    assert isinstance(selected, list), "selected_features must be a list"
    assert all(isinstance(f, str) for f in selected), "All selected features must be strings"

    # selected features must be subset of correlations keys
    assert set(selected).issubset(set(correlations.keys())), "Selected features must be in correlations keys"

    # selected features must be exactly 10
    assert len(selected) == 10, f"Expected 10 selected features, got {len(selected)}"

@pytest.mark.weight(12)
def test_feature_selection_correctness(workspace):
    # Verify that selected features are top 10 by absolute correlation
    report_path = workspace / "feature_report.json"
    with open(report_path, 'r') as f:
        report = json.load(f)

    correlations = report['correlations']
    selected = report['selected_features']

    # Sort features by absolute correlation descending
    sorted_feats = sorted(correlations.items(), key=lambda x: abs(x[1]), reverse=True)
    top_10_feats = [f for f, _ in sorted_feats[:10]]

    assert set(selected) == set(top_10_feats), "Selected features do not match top 10 by absolute correlation"
