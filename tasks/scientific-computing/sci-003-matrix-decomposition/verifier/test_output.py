import os
from pathlib import Path
import json
import numpy as np
import pytest

@pytest.fixture
def workspace(request):
    """Resolve workspace from --workspace CLI option."""
    ws = request.config.getoption("--workspace")
    if ws:
        return Path(ws)
    return Path(os.environ.get("CLAW_WORKSPACE", os.environ.get("WORKSPACE", "workspace")))
@pytest.mark.weight(3)
def test_svd_analysis_file_exists(workspace):
    file = workspace / "svd_analysis.json"
    assert file.exists(), "svd_analysis.json file does not exist"

@pytest.mark.weight(5)
def test_svd_analysis_content(workspace):
    file = workspace / "svd_analysis.json"
    data = json.loads(file.read_text())

    # Check keys
    assert "singular_values" in data
    assert "reconstruction_errors" in data
    assert "optimal_k" in data

    sv = data["singular_values"]
    rec_err = data["reconstruction_errors"]
    optimal_k = data["optimal_k"]

    # Check singular_values is list of floats, length 20
    assert isinstance(sv, list)
    assert len(sv) == 20
    assert all(isinstance(x, (float, int)) for x in sv)

    # Check reconstruction_errors keys and values
    expected_ks = ["1", "2", "3", "5", "10", "15", "20"]
    assert set(rec_err.keys()) == set(expected_ks)
    for k in expected_ks:
        val = rec_err[k]
        assert isinstance(val, (float, int))
        assert val >= 0

    # Check optimal_k is one of the keys
    assert str(optimal_k) in expected_ks

@pytest.mark.weight(7)
def test_reconstruction_error_correctness(workspace):
    # Load original matrix
    data_matrix_path = workspace / "data_matrix.csv"
    matrix = np.loadtxt(data_matrix_path, delimiter=",")

    # Load svd analysis
    svd_path = workspace / "svd_analysis.json"
    data = json.loads(svd_path.read_text())

    sv = np.array(data["singular_values"])
    rec_err = data["reconstruction_errors"]
    optimal_k = data["optimal_k"]

    # Recompute SVD
    U, s, VT = np.linalg.svd(matrix, full_matrices=False)

    # Check singular values close
    np.testing.assert_allclose(sv, s, rtol=1e-4, atol=1e-6)

    # For each k, reconstruct and compute error
    for k_str, err_reported in rec_err.items():
        k = int(k_str)
        Uk = U[:, :k]
        sk = np.diag(s[:k])
        Vk = VT[:k, :]
        reconstructed = Uk @ sk @ Vk
        err_computed = np.linalg.norm(matrix - reconstructed, ord='fro')
        assert abs(err_computed - err_reported) < 1e-4, f"Reconstruction error mismatch for k={k}"

    # Check optimal_k is the k with minimum error
    errors = {int(k): v for k, v in rec_err.items()}
    min_k = min(errors, key=errors.get)
    assert optimal_k == min_k, f"optimal_k {optimal_k} is not the minimum error k {min_k}"
