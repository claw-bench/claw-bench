"""Verifier for mem-009: Sequential State Tracking."""

import json
from pathlib import Path

import pytest


EXPECTED_STATE = {
    "alpha": 150,
    "beta": 10,
    "epsilon": 125,
    "gamma": 65,
    "iota": 50,
    "kappa": 66,
    "lambda": 225,
    "theta": 42,
    "zeta": 335,
}


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def final_state(workspace):
    """Read and parse the final_state.json file."""
    path = workspace / "final_state.json"
    assert path.exists(), "final_state.json not found in workspace"
    return json.loads(path.read_text())


def test_output_file_exists(workspace):
    """final_state.json must exist in the workspace."""
    assert (workspace / "final_state.json").exists()


def test_valid_json(workspace):
    """final_state.json must be valid JSON."""
    path = workspace / "final_state.json"
    try:
        json.loads(path.read_text())
    except json.JSONDecodeError as e:
        pytest.fail(f"Invalid JSON: {e}")


def test_correct_variable_count(final_state):
    """There should be exactly 9 variables in the final state (delta was deleted)."""
    assert len(final_state) == len(EXPECTED_STATE), (
        f"Expected {len(EXPECTED_STATE)} variables, got {len(final_state)}. "
        f"Keys: {sorted(final_state.keys())}"
    )


def test_delta_deleted(final_state):
    """Variable 'delta' should not be in the final state (it was DELETEd)."""
    assert "delta" not in final_state, "delta should have been deleted"


def test_alpha_value(final_state):
    """alpha: SET 100, ADD 30 -> 130, MULTIPLY 2 -> 260, SWAP with zeta(200) -> 200, SUBTRACT 50 -> 150."""
    assert final_state.get("alpha") == EXPECTED_STATE["alpha"], (
        f"alpha: expected {EXPECTED_STATE['alpha']}, got {final_state.get('alpha')}"
    )


def test_beta_value(final_state):
    """beta: SET 50, ADD gamma(25) -> 75, SUBTRACT 10 -> 65, SWAP with gamma(10) -> 10."""
    assert final_state.get("beta") == EXPECTED_STATE["beta"], (
        f"beta: expected {EXPECTED_STATE['beta']}, got {final_state.get('beta')}"
    )


def test_gamma_value(final_state):
    """gamma: SET 25, MULTIPLY 4 -> 100, MOD 30 -> 10, SWAP with beta(65) -> 65."""
    assert final_state.get("gamma") == EXPECTED_STATE["gamma"], (
        f"gamma: expected {EXPECTED_STATE['gamma']}, got {final_state.get('gamma')}"
    )


def test_epsilon_value(final_state):
    """epsilon: SET delta(25), MULTIPLY 3 -> 75, ADD iota(50) -> 125."""
    assert final_state.get("epsilon") == EXPECTED_STATE["epsilon"], (
        f"epsilon: expected {EXPECTED_STATE['epsilon']}, got {final_state.get('epsilon')}"
    )


def test_zeta_value(final_state):
    """zeta: SET 200, SWAP with alpha(260) -> 260, ADD epsilon(75) -> 335."""
    assert final_state.get("zeta") == EXPECTED_STATE["zeta"], (
        f"zeta: expected {EXPECTED_STATE['zeta']}, got {final_state.get('zeta')}"
    )


def test_theta_value(final_state):
    """theta: SET 127, MOD 10 -> 7, MULTIPLY 6 -> 42."""
    assert final_state.get("theta") == EXPECTED_STATE["theta"], (
        f"theta: expected {EXPECTED_STATE['theta']}, got {final_state.get('theta')}"
    )


def test_iota_value(final_state):
    """iota: SET theta(42), ADD gamma(10) -> 52, SUBTRACT 2 -> 50."""
    assert final_state.get("iota") == EXPECTED_STATE["iota"], (
        f"iota: expected {EXPECTED_STATE['iota']}, got {final_state.get('iota')}"
    )


def test_kappa_value(final_state):
    """kappa: SET 999, DIVIDE 3 -> 333, MOD 100 -> 33, MULTIPLY 2 -> 66."""
    assert final_state.get("kappa") == EXPECTED_STATE["kappa"], (
        f"kappa: expected {EXPECTED_STATE['kappa']}, got {final_state.get('kappa')}"
    )


def test_lambda_value(final_state):
    """lambda: SET 0, ADD alpha(150) -> 150, ADD beta(10) -> 160, ADD gamma(65) -> 225."""
    assert final_state.get("lambda") == EXPECTED_STATE["lambda"], (
        f"lambda: expected {EXPECTED_STATE['lambda']}, got {final_state.get('lambda')}"
    )


def test_all_values_are_integers(final_state):
    """All values in the final state must be integers."""
    for key, value in final_state.items():
        assert isinstance(value, int), f"Value for '{key}' is {type(value).__name__}, expected int"


def test_keys_match_expected(final_state):
    """The set of keys must match exactly."""
    assert set(final_state.keys()) == set(EXPECTED_STATE.keys()), (
        f"Key mismatch. Expected: {sorted(EXPECTED_STATE.keys())}, Got: {sorted(final_state.keys())}"
    )


def test_complete_state_match(final_state):
    """The entire final state must match the expected state."""
    for key, expected_val in EXPECTED_STATE.items():
        actual_val = final_state.get(key)
        assert actual_val == expected_val, (
            f"Variable '{key}': expected {expected_val}, got {actual_val}"
        )


# ── Enhanced checks (auto-generated) ────────────────────────────────────────

@pytest.mark.weight(1)
def test_no_placeholder_values(workspace):
    """Output files must not contain placeholder/TODO markers."""
    placeholders = ["PLACEHOLDER", "CHANGEME", "your_"]
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html", ".xml"):
            content = f.read_text(errors="replace")
            for p in placeholders:
                assert p not in content, f"Placeholder '{p}' found in {f.name}"

@pytest.mark.weight(2)
def test_no_empty_critical_fields(workspace):
    """JSON output must not have empty-string or null values in top-level fields."""
    import json
    path = workspace / "final_state.json"
    if not path.exists():
        pytest.skip("output file not found")
    data = json.loads(path.read_text())
    items = data if isinstance(data, list) else [data]
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        for k, v in item.items():
            assert v is not None, f"Item {i}: field '{k}' is null"
            if isinstance(v, str):
                assert v.strip() != "", f"Item {i}: field '{k}' is empty string"

@pytest.mark.weight(1)
def test_encoding_valid(workspace):
    """All text output files must be valid UTF-8."""
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html"):
            try:
                f.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                pytest.fail(f"{f.name} contains invalid UTF-8 encoding")

@pytest.mark.weight(1)
def test_consistent_key_naming(workspace):
    """JSON keys should use a consistent naming convention."""
    import json, re
    path = workspace / "final_state.json"
    if not path.exists():
        pytest.skip("output file not found")
    data = json.loads(path.read_text())
    items = data if isinstance(data, list) else [data]
    all_keys = set()
    for item in items:
        if isinstance(item, dict):
            all_keys.update(item.keys())
    if len(all_keys) < 2:
        return
    snake = sum(1 for k in all_keys if re.match(r'^[a-z][a-z0-9_]*$', k))
    camel = sum(1 for k in all_keys if re.match(r'^[a-z][a-zA-Z0-9]*$', k) and not re.match(r'^[a-z][a-z0-9_]*$', k))
    pascal = sum(1 for k in all_keys if re.match(r'^[A-Z][a-zA-Z0-9]*$', k))
    dominant = max(snake, camel, pascal)
    consistency = dominant / len(all_keys) if all_keys else 1
    assert consistency >= 0.7, f"Key naming inconsistent: {snake} snake, {camel} camel, {pascal} pascal out of {len(all_keys)} keys"

@pytest.mark.weight(1)
def test_no_duplicate_entries(workspace):
    """Output should not contain exact duplicate rows/objects."""
    import json
    path = workspace / "final_state.json"
    if not path.exists():
        pytest.skip("output file not found")
    text = path.read_text().strip()
    if path.suffix == ".json":
        data = json.loads(text)
        if isinstance(data, list):
            serialized = [json.dumps(item, sort_keys=True) for item in data]
            dupes = len(serialized) - len(set(serialized))
            assert dupes == 0, f"Found {dupes} duplicate entries in {path.name}"
    elif path.suffix == ".csv":
        lines_list = text.splitlines()
        if len(lines_list) > 1:
            data_lines = lines_list[1:]
            dupes = len(data_lines) - len(set(data_lines))
            assert dupes == 0, f"Found {dupes} duplicate rows in {path.name}"

@pytest.mark.weight(1)
def test_no_extraneous_files(workspace):
    """Workspace should not contain debug/temp files."""
    bad_patterns = [".DS_Store", "Thumbs.db", ".log", ".bak", ".tmp"]
    for f in workspace.rglob("*"):
        if f.is_file():
            for pat in bad_patterns:
                assert pat not in f.name, f"Extraneous file found: {f.name}"

@pytest.mark.weight(1)
def test_output_not_excessively_large(workspace):
    """Output files should be reasonably sized (< 5MB each)."""
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html"):
            size_mb = f.stat().st_size / (1024 * 1024)
            assert size_mb < 5, f"{f.name} is {size_mb:.1f}MB, exceeds 5MB limit"
