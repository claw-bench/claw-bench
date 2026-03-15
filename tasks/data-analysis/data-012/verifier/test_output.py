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
