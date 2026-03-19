import os
from pathlib import Path
import csv
import json
import pytest

@pytest.fixture
def workspace(request):
    """Resolve workspace from --workspace CLI option."""
    ws = request.config.getoption("--workspace")
    if ws:
        return Path(ws)
    return Path(os.environ.get("CLAW_WORKSPACE", os.environ.get("WORKSPACE", "workspace")))
@pytest.mark.weight(3)
def test_output_files_exist(workspace):
    assert (workspace / "stats_results.csv").exists(), "stats_results.csv not found"
    assert (workspace / "stats_summary.json").exists(), "stats_summary.json not found"

@pytest.mark.weight(5)
def test_stats_results_content(workspace):
    results_path = workspace / "stats_results.csv"
    with results_path.open() as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert len(rows) == 1, "stats_results.csv should have exactly one row"
    row = rows[0]
    # Check required columns
    for col in ['test', 'statistic', 'p_value', 'effect_size', 'significant']:
        assert col in row, f"Column {col} missing in stats_results.csv"
    # Check test name
    assert row['test'] in ['t-test', 'ANOVA'], "Invalid test name"
    # Check numeric fields
    try:
        stat = float(row['statistic'])
        pval = float(row['p_value'])
        effect = float(row['effect_size'])
    except ValueError:
        pytest.fail("statistic, p_value, and effect_size must be floats")
    # p_value in [0,1]
    assert 0 <= pval <= 1, "p_value out of range"
    # significant is boolean string
    assert row['significant'].lower() in ['true', 'false'], "significant must be true or false"

@pytest.mark.weight(5)
def test_stats_summary_json(workspace):
    summary_path = workspace / "stats_summary.json"
    with summary_path.open() as f:
        data = json.load(f)
    # Check keys
    for key in ['test', 'statistic', 'p_value', 'effect_size', 'significant']:
        assert key in data, f"Key {key} missing in stats_summary.json"
    # Check types
    assert data['test'] in ['t-test', 'ANOVA'], "Invalid test name in summary"
    assert isinstance(data['statistic'], (int, float)), "statistic must be numeric"
    assert isinstance(data['p_value'], (int, float)), "p_value must be numeric"
    assert 0 <= data['p_value'] <= 1, "p_value out of range in summary"
    assert isinstance(data['effect_size'], (int, float)), "effect_size must be numeric"
    assert isinstance(data['significant'], bool), "significant must be boolean"

@pytest.mark.weight(7)
def test_statistical_correctness(workspace):
    import pandas as pd
    from scipy import stats

    # Load input data
    df = pd.read_csv(workspace / "experiment_data.csv")
    groups = df['group'].unique()
    measurements = [df.loc[df['group'] == g, 'measurement'].values.astype(float) for g in groups]

    # Load output
    with open(workspace / "stats_summary.json") as f:
        summary = json.load(f)

    alpha = 0.05

    if len(groups) == 2:
        # t-test
        t_stat, p_val = stats.ttest_ind(measurements[0], measurements[1], equal_var=False)
        # Compute Cohen's d
        n1, n2 = len(measurements[0]), len(measurements[1])
        mean1, mean2 = measurements[0].mean(), measurements[1].mean()
        s1, s2 = measurements[0].std(ddof=1), measurements[1].std(ddof=1)
        s_pooled = ((n1 -1)*s1**2 + (n2 -1)*s2**2) / (n1 + n2 -2)
        cohen_d = (mean1 - mean2) / (s_pooled ** 0.5)
        cohen_d = abs(cohen_d)

        # Check test name
        assert summary['test'] == 't-test'
        # Check statistic close
        assert abs(summary['statistic'] - t_stat) < 1e-3
        # Check p_value close
        assert abs(summary['p_value'] - p_val) < 1e-4
        # Check effect size close
        assert abs(summary['effect_size'] - cohen_d) < 0.05
        # Check significance
        assert summary['significant'] == (p_val < alpha)

    else:
        # ANOVA
        f_stat, p_val = stats.f_oneway(*measurements)
        # Eta squared effect size
        # eta_sq = SS_between / SS_total
        grand_mean = df['measurement'].mean()
        ss_between = sum(len(m) * (m.mean() - grand_mean)**2 for m in measurements)
        ss_total = sum((df['measurement'] - grand_mean)**2)
        eta_sq = ss_between / ss_total if ss_total > 0 else 0

        # Check test name
        assert summary['test'] == 'ANOVA'
        # Check statistic close
        assert abs(summary['statistic'] - f_stat) < 1e-3
        # Check p_value close
        assert abs(summary['p_value'] - p_val) < 1e-4
        # Check effect size close
        assert abs(summary['effect_size'] - eta_sq) < 0.05
        # Check significance
        assert summary['significant'] == (p_val < alpha)
