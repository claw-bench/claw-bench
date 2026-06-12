"""Verifier for data-012: Simple Linear Regression Prediction."""

from pathlib import Path
import json
import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def model(workspace):
    path = workspace / "model.json"
    assert path.exists(), "model.json not found"
    return json.loads(path.read_text())


@pytest.fixture
def predictions(workspace):
    path = workspace / "predictions.json"
    assert path.exists(), "predictions.json not found"
    return json.loads(path.read_text())


def test_model_file_exists(workspace):
    assert (workspace / "model.json").exists()


def test_predictions_file_exists(workspace):
    assert (workspace / "predictions.json").exists()


def test_r_squared_above_threshold(model):
    assert model["r_squared"] > 0.7, f"r_squared {model['r_squared']} too low (expected > 0.7)"


def test_slope_reasonable(model):
    assert abs(model["slope"] - 2.4773) < 0.5, f"Slope {model['slope']} far from expected ~2.4773"


def test_intercept_reasonable(model):
    assert abs(model["intercept"] - 10.5283) < 5.0, f"Intercept {model['intercept']} far from expected ~10.5283"


def test_mse_reported(model):
    assert "mse" in model, "MSE not reported"
    assert model["mse"] > 0, "MSE should be positive"
    assert model["mse"] < 100, f"MSE {model['mse']} seems too high"


def test_predictions_count(predictions):
    assert len(predictions) == 3, f"Expected 3 predictions, got {len(predictions)}"


def test_predictions_have_correct_x(predictions):
    xs = [p["x"] for p in predictions]
    assert xs == [51, 52, 53], f"Expected x values [51, 52, 53], got {xs}"


def test_predictions_reasonable(predictions):
    for p in predictions:
        expected_y = 2.4773 * p["x"] + 10.5283
        assert abs(p["predicted_y"] - expected_y) < 5.0,             f"Prediction for x={p['x']}: {p['predicted_y']} far from expected ~{expected_y:.2f}"


def test_model_keys_complete(model):
    for key in ["slope", "intercept", "r_squared", "mse"]:
        assert key in model, f"Missing key: {key}"


def test_r_squared_in_valid_range(model):
    assert 0 <= model["r_squared"] <= 1.0, f"r_squared {model['r_squared']} out of [0, 1] range"


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
    path = workspace / "predictions.json"
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
    path = workspace / "predictions.json"
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
    path = workspace / "historical.csv"
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
