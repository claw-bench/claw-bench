import os
from pathlib import Path
import pytest
import csv
import json
from math import isclose
from scipy.stats import ttest_ind
import numpy as np

@pytest.fixture
def workspace(request):
    """Resolve workspace from --workspace CLI option."""
    ws = request.config.getoption("--workspace")
    if ws:
        return Path(ws)
    return Path(os.environ.get("CLAW_WORKSPACE", os.environ.get("WORKSPACE", "workspace")))
@pytest.mark.weight(3)
def test_deg_results_file_exists(workspace):
    deg_file = workspace / "deg_results.csv"
    assert deg_file.exists(), "deg_results.csv file does not exist"

@pytest.mark.weight(3)
def test_expression_summary_exists(workspace):
    summary_file = workspace / "expression_summary.json"
    assert summary_file.exists(), "expression_summary.json file does not exist"

@pytest.mark.weight(5)
def test_deg_results_content(workspace):
    expr_file = workspace / "expression_matrix.csv"
    deg_file = workspace / "deg_results.csv"

    # Read expression matrix
    with open(expr_file, newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        data = list(reader)

    gene_names = [row[0] for row in data]
    control_indices = [i for i, h in enumerate(header) if h.endswith("_Control")]
    treated_indices = [i for i, h in enumerate(header) if h.endswith("_Treated")]

    # Extract expression values as floats
    expr_values = {}
    for row in data:
        gene = row[0]
        vals = list(map(float, row[1:]))
        expr_values[gene] = vals

    # Read deg_results
    with open(deg_file, newline="") as f:
        reader = csv.DictReader(f)
        deg_results = list(reader)

    # Check all genes present
    deg_genes = [r['gene'] for r in deg_results]
    assert set(deg_genes) == set(gene_names), "Mismatch in genes between input and deg_results"

    # Check fold_change and p_value correctness
    for r in deg_results:
        gene = r['gene']
        fold_change = float(r['fold_change'])
        p_value = float(r['p_value'])
        significant = r['significant']

        vals = expr_values[gene]
        control_vals = [vals[i-1] for i in control_indices]  # -1 because vals excludes gene col
        treated_vals = [vals[i-1] for i in treated_indices]

        # Compute mean on original scale
        mean_control = np.mean(control_vals)
        mean_treated = np.mean(treated_vals)

        # Fold change
        expected_fc = mean_treated / mean_control if mean_control != 0 else float('inf')

        # Check fold change approx equal (4 decimals)
        assert isclose(fold_change, round(expected_fc,4), rel_tol=1e-4), f"Fold change mismatch for {gene}"

        # Compute t-test
        t_stat, p_val = ttest_ind(treated_vals, control_vals, equal_var=False)

        # p-value approx equal (6 decimals)
        assert isclose(p_value, round(p_val,6), rel_tol=1e-6), f"P-value mismatch for {gene}"

        # Check significant field
        expected_sig = "True" if p_val < 0.05 else "False"
        assert significant == expected_sig, f"Significance mismatch for {gene}"

@pytest.mark.weight(4)
def test_expression_summary_content(workspace):
    summary_file = workspace / "expression_summary.json"
    deg_file = workspace / "deg_results.csv"

    with open(summary_file) as f:
        summary = json.load(f)

    with open(deg_file, newline="") as f:
        reader = csv.DictReader(f)
        deg_results = list(reader)

    total_genes = len(deg_results)
    sig_genes = [r for r in deg_results if r['significant'] == 'True']
    num_sig = len(sig_genes)
    if num_sig > 0:
        mean_fc = sum(float(r['fold_change']) for r in sig_genes) / num_sig
    else:
        mean_fc = 0.0

    # Check keys
    assert 'total_genes' in summary
    assert 'significant_genes' in summary
    assert 'mean_fold_change_significant' in summary

    # Check values
    assert summary['total_genes'] == total_genes
    assert summary['significant_genes'] == num_sig
    assert isclose(summary['mean_fold_change_significant'], mean_fc, rel_tol=1e-4)
